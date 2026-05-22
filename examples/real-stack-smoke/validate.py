#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Validate adaptive-island against Databricks, Supabase, and Upstash."""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "client" / "python"))

from adaptive_island import Selector  # noqa: E402
from adaptive_island.selector import redis_url_for_tls, should_use_tls_for_cache_url  # noqa: E402


class SmokeError(RuntimeError):
    """Raised when a required stack check fails."""


def _env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if value is None or value == "":
        raise SmokeError(f"missing required environment variable: {name}")
    return value


def _json_get(url: str, token: str, *, timeout: int = 15) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise SmokeError(
            f"Databricks API returned HTTP {exc.code} for {urllib.parse.urlparse(url).path}"
        ) from exc
    except urllib.error.URLError as exc:
        raise SmokeError("Databricks API request failed") from exc

    parsed = json.loads(body)
    if not isinstance(parsed, dict):
        raise SmokeError("Databricks API returned a non-object response")
    return parsed


def validate_databricks() -> dict[str, Any]:
    host = _env("DATABRICKS_HOST").rstrip("/")
    token = _env("DATABRICKS_TOKEN")
    parsed_host = urllib.parse.urlparse(host)
    if parsed_host.scheme != "https" or not parsed_host.netloc:
        raise SmokeError("DATABRICKS_HOST must be an https URL with a host name")
    if (
        "databricks" not in parsed_host.netloc
        and os.environ.get("ADAPTIVE_ISLAND_ALLOW_NON_DATABRICKS_HOST") != "1"
    ):
        raise SmokeError(
            "DATABRICKS_HOST does not look like a Databricks domain. Set "
            "ADAPTIVE_ISLAND_ALLOW_NON_DATABRICKS_HOST=1 only for trusted private mirrors."
        )

    try:
        _json_get(f"{host}/api/2.0/current-user/me", token)
    except SmokeError:
        _json_get(f"{host}/api/2.0/preview/scim/v2/Me", token)

    warehouses_visible: int | None = None
    try:
        warehouses = _json_get(f"{host}/api/2.0/sql/warehouses", token).get("warehouses", [])
        if isinstance(warehouses, list):
            warehouses_visible = len(warehouses)
    except SmokeError:
        warehouses_visible = None

    bundle = validate_bundle_shape()
    return {
        "host": parsed_host.netloc,
        "authenticated": True,
        "sql_warehouses_visible": warehouses_visible,
        "bundle": bundle,
    }


def validate_bundle_shape() -> dict[str, Any]:
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise SmokeError("install pyyaml>=6.0 to validate the Databricks bundle shape") from exc

    bundle_path = ROOT / "examples" / "databricks-asset-bundle" / "databricks.yml"
    with bundle_path.open("r", encoding="utf-8") as handle:
        bundle = yaml.safe_load(handle)

    resources = bundle.get("resources", {}) if isinstance(bundle, dict) else {}
    pipelines = resources.get("pipelines", {}) if isinstance(resources, dict) else {}
    jobs = resources.get("jobs", {}) if isinstance(resources, dict) else {}
    variables = bundle.get("variables", {}) if isinstance(bundle, dict) else {}
    required_variables = {
        "catalog",
        "region",
        "federation_connection",
        "source_schema",
        "source_table",
        "cache_url_secret_scope",
        "cache_url_secret_key",
    }

    missing_variables = sorted(required_variables - set(variables.keys()))
    if missing_variables:
        raise SmokeError(f"Databricks bundle is missing variables: {missing_variables}")
    if "adaptive_island_pipeline" not in pipelines:
        raise SmokeError("Databricks bundle is missing adaptive_island_pipeline")
    if "adaptive_island_export_rankings" not in jobs:
        raise SmokeError("Databricks bundle is missing adaptive_island_export_rankings")

    return {
        "path": str(bundle_path.relative_to(ROOT)),
        "pipelines": sorted(pipelines.keys()),
        "jobs": sorted(jobs.keys()),
    }


def _supabase_connect():
    try:
        import psycopg
    except ModuleNotFoundError as exc:
        raise SmokeError("install psycopg[binary]>=3.2 to validate Supabase") from exc

    try:
        dsn = os.environ.get("SUPABASE_DB_DSN")
        if dsn:
            return psycopg.connect(dsn, connect_timeout=15)

        project_id = _env("SUPABASE_PROJECT_ID")
        return psycopg.connect(
            host=os.environ.get("SUPABASE_DB_HOST", f"db.{project_id}.supabase.co"),
            port=int(os.environ.get("SUPABASE_DB_PORT", "5432")),
            dbname=os.environ.get("SUPABASE_DB_NAME", "postgres"),
            user=os.environ.get("SUPABASE_DB_USER", "postgres"),
            password=_env("SUPABASE_DB_PASSWORD"),
            sslmode=os.environ.get("SUPABASE_DB_SSLMODE", "require"),
            connect_timeout=15,
        )
    except Exception as exc:  # noqa: BLE001 - optional dependency exposes several error types.
        raise SmokeError(
            "Supabase connection failed. If the direct database host is "
            "IPv6-only from your runner, set SUPABASE_DB_HOST/PORT/USER to the "
            "project's IPv4-compatible Supavisor pooler, usually "
            "SUPABASE_DB_USER=postgres.<project-ref>."
        ) from exc


def validate_supabase(run_id: str, *, region: str, model: str, keep: bool) -> dict[str, Any]:
    try:
        from psycopg import sql
    except ModuleNotFoundError as exc:
        raise SmokeError("install psycopg[binary]>=3.2 to validate Supabase") from exc

    schema = f"adaptive_island_smoke_{run_id}"
    table = sql.Identifier(schema, "provider_cost_log")
    base = datetime.now(UTC) - timedelta(minutes=40)
    attempts = _sample_attempts(base, model)
    ranking_rows: list[dict[str, Any]] = []

    with _supabase_connect() as conn:
        conn.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        try:
            conn.execute(
                sql.SQL(
                    """
                    CREATE TABLE {table} (
                      id bigint generated always as identity primary key,
                      account_id text,
                      generation_id text not null,
                      provider text not null,
                      provider_model_id text,
                      prediction_id text,
                      model text not null,
                      estimated_cost numeric(12, 6),
                      outcome text not null default 'pending',
                      attempt_order integer not null default 1,
                      was_cancelled boolean not null default false,
                      cancel_available boolean not null default false,
                      submitted_at timestamptz not null default now(),
                      resolved_at timestamptz,
                      error_message text,
                      metadata jsonb not null default '{{}}'::jsonb,
                      created_at timestamptz not null default now(),
                      updated_at timestamptz not null default now(),
                      constraint provider_cost_log_outcome_check
                        check (outcome in ('used', 'cancelled', 'discarded', 'failed', 'pending')),
                      constraint provider_cost_log_attempt_order_check
                        check (attempt_order >= 1),
                      constraint provider_cost_log_estimated_cost_check
                        check (estimated_cost is null or estimated_cost >= 0),
                      constraint provider_cost_log_resolved_after_submitted_check
                        check (resolved_at is null or resolved_at >= submitted_at)
                    )
                    """
                ).format(table=table)
            )
            with conn.cursor() as cur:
                cur.executemany(
                    sql.SQL(
                        """
                        INSERT INTO {table} (
                          generation_id, provider, provider_model_id, prediction_id, model,
                          estimated_cost, outcome, attempt_order, was_cancelled,
                          cancel_available, submitted_at, resolved_at, error_message, metadata
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                    ).format(table=table),
                    attempts,
                )
                cur.execute(_ranking_sql(table, region))
                columns = [desc.name for desc in cur.description or []]
                ranking_rows = [dict(zip(columns, row, strict=True)) for row in cur.fetchall()]
        finally:
            if not keep:
                conn.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))

    if not ranking_rows:
        raise SmokeError("Supabase scoring query produced no ranking rows")

    return {
        "schema": schema,
        "schema_kept": keep,
        "attempt_rows_inserted": len(attempts),
        "ranking_rows": ranking_rows,
    }


def _sample_attempts(base: datetime, model: str) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    samples = [
        ("cloudflare", "used", 1.0, 0.0008),
        ("cloudflare", "used", 1.2, 0.0008),
        ("cloudflare", "used", 1.1, 0.0008),
        ("replicate", "used", 1.7, 0.0023),
        ("replicate", "used", 1.9, 0.0023),
        ("replicate", "failed", 3.0, 0.0023),
        ("fal", "used", 2.4, 0.0019),
        ("fal", "failed", 3.5, 0.0019),
        ("fal", "discarded", 2.8, 0.0019),
    ]
    for index, (provider, outcome, latency_seconds, estimated_cost) in enumerate(samples, start=1):
        submitted_at = base + timedelta(seconds=index * 30)
        resolved_at = submitted_at + timedelta(seconds=latency_seconds)
        rows.append(
            (
                f"gen_smoke_{index}",
                provider,
                model,
                f"pred_smoke_{index}",
                model,
                estimated_cost,
                outcome,
                1,
                outcome == "cancelled",
                True,
                submitted_at,
                resolved_at,
                None if outcome == "used" else f"smoke_{outcome}",
                json.dumps({"adaptive_island_smoke": True}),
            )
        )
    return rows


def _ranking_sql(table: Any, region: str) -> Any:
    from psycopg import sql

    return sql.SQL(
        """
        WITH silver AS (
          SELECT
            model,
            {region}::text AS region,
            provider,
            outcome,
            EXTRACT(EPOCH FROM (resolved_at - submitted_at)) * 1000.0 AS latency_ms,
            CASE WHEN outcome = 'used' THEN 1 ELSE 0 END AS is_success,
            CASE WHEN outcome IN ('failed', 'discarded', 'cancelled') THEN 1 ELSE 0 END AS is_wasted
          FROM {table}
          WHERE outcome IN ('used', 'failed', 'discarded', 'cancelled')
            AND resolved_at IS NOT NULL
            AND submitted_at >= now() - interval '24 hours'
        ), per_pair AS (
          SELECT
            model,
            region,
            provider,
            COUNT(*)::bigint AS attempts,
            SUM(is_success)::double precision AS succeeded,
            SUM(is_wasted)::double precision AS wasted,
            percentile_cont(0.95) WITHIN GROUP (ORDER BY latency_ms) AS latency_p95_ms
          FROM silver
          GROUP BY model, region, provider
        ), scored AS (
          SELECT
            p.*,
            CASE WHEN attempts > 0 THEN succeeded / attempts ELSE 0.0 END AS success_rate,
            CASE WHEN attempts > 0 THEN wasted / attempts ELSE 0.0 END AS wasted_rate,
            CASE
              WHEN MAX(COALESCE(latency_p95_ms, 0)) OVER (PARTITION BY model, region) > 0
              THEN latency_p95_ms / MAX(COALESCE(latency_p95_ms, 0)) OVER (PARTITION BY model, region)
              ELSE 0.0
            END AS latency_p95_norm
          FROM per_pair p
        )
        SELECT
          model,
          region,
          provider,
          attempts,
          ROUND((
            success_rate * 1.0
            - wasted_rate * 0.5
            - latency_p95_norm * 0.3
          )::numeric, 6)::double precision AS score,
          ROUND(latency_p95_ms::numeric, 3)::double precision AS latency_p95_ms
        FROM scored
        ORDER BY score DESC, latency_p95_ms ASC, provider ASC
        """
    ).format(table=table, region=sql.Literal(region))


def validate_upstash(
    *,
    model: str,
    region: str,
    ranking_rows: list[dict[str, Any]],
    keep: bool,
) -> dict[str, Any]:
    try:
        import redis
    except ModuleNotFoundError as exc:
        raise SmokeError("install redis>=5.0 to validate Upstash") from exc

    cache_url = _env("ADAPTIVE_ISLAND_CACHE_URL")
    use_tls = should_use_tls_for_cache_url(cache_url)
    client = redis.from_url(
        redis_url_for_tls(cache_url, use_tls),
        socket_connect_timeout=10,
        socket_timeout=10,
    )

    providers = [str(row["provider"]) for row in ranking_rows]
    scores = {str(row["provider"]): float(row["score"]) for row in ranking_rows}
    attempts_total = sum(int(row["attempts"]) for row in ranking_rows)
    payload = {
        "providers_ranked": providers,
        "scores": scores,
        "attempts_total": attempts_total,
        "window_hours": 24,
        "computed_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    key = f"predictive:ranking:{region}:{model}"
    allow_overwrite = os.environ.get("ADAPTIVE_ISLAND_SMOKE_ALLOW_OVERWRITE") == "1"
    previous_value = client.get(key)
    previous_ttl = client.ttl(key) if previous_value is not None else None
    if previous_value is not None and not allow_overwrite:
        raise SmokeError(
            f"Upstash key {key!r} already exists; refusing to overwrite it. "
            "Use a smoke-only ADAPTIVE_ISLAND_REGION/ADAPTIVE_ISLAND_MODEL or set "
            "ADAPTIVE_ISLAND_SMOKE_ALLOW_OVERWRITE=1 to restore the prior value after the run."
        )

    selector = Selector(
        cache_url=cache_url,
        max_cache_age_seconds=600,
        cache_socket_timeout_seconds=5.0,
    )
    ranked: list[str]
    restored_existing_key = False
    try:
        client.set(key, json.dumps(payload), ex=300)
        ranked = selector.rank(
            model_id=model,
            region=region,
            fallback=["replicate", "fal", "cloudflare"],
        )
    finally:
        if previous_value is not None:
            if previous_ttl is not None and previous_ttl > 0:
                client.set(key, previous_value, ex=previous_ttl)
            else:
                client.set(key, previous_value)
            restored_existing_key = True
        elif not keep:
            client.delete(key)

    if ranked[0] != providers[0]:
        raise SmokeError(
            f"SDK did not return cached top provider; expected {providers[0]!r}, got {ranked[0]!r}"
        )
    if selector.last_decision is None or selector.last_decision.source != "cached-ranking":
        raise SmokeError("SDK did not report cached-ranking decision")

    return {
        "key": key,
        "key_kept": keep,
        "restored_existing_key": restored_existing_key,
        "providers_ranked": ranked,
        "attempts_total": attempts_total,
        "decision": selector.last_decision.source,
    }


def main() -> int:
    run_id = str(int(time.time()))
    region = os.environ.get("ADAPTIVE_ISLAND_REGION", "smoke")
    model = os.environ.get("ADAPTIVE_ISLAND_MODEL", f"adaptive-island-smoke/{run_id}")
    keep = os.environ.get("ADAPTIVE_ISLAND_SMOKE_KEEP") == "1"

    databricks = validate_databricks()
    supabase = validate_supabase(run_id, region=region, model=model, keep=keep)
    upstash = validate_upstash(
        model=model,
        region=region,
        ranking_rows=supabase["ranking_rows"],
        keep=keep,
    )

    result = {
        "ok": True,
        "validated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "region": region,
        "model": model,
        "databricks": databricks,
        "supabase": supabase,
        "upstash": upstash,
    }

    result_path = os.environ.get("ADAPTIVE_ISLAND_SMOKE_RESULT")
    if result_path:
        Path(result_path).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SmokeError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2), file=sys.stderr)
        raise SystemExit(1) from exc
