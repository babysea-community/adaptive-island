"""
adaptive-island/jobs/export_rankings.py

Lakeflow Job: read the Gold provider ranking and ship it to Upstash.

Cache TTL is deliberately longer than the refresh cadence so SDKs keep serving
the last good ranking if Databricks is paused or a scheduled run fails.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from typing import Literal


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--catalog", required=True)
    p.add_argument("--region", required=True)
    p.add_argument(
        "--cache-url",
        help=(
            "Upstash URL. Intended for local/dev runs only; production "
            "Databricks jobs should use --cache-url-secret-scope and "
            "--cache-url-secret-key."
        ),
    )
    p.add_argument(
        "--cache-url-secret-scope",
        help="Databricks secret scope containing the Upstash URL.",
    )
    p.add_argument(
        "--cache-url-secret-key",
        help="Databricks secret key containing the Upstash URL.",
    )
    p.add_argument("--cache-ttl-seconds", type=int, default=48 * 3600)
    p.add_argument(
        "--cache-tls",
        choices=["auto", "true", "false"],
        default="auto",
        help="Use TLS for Upstash. auto enables TLS for Upstash hosts or redis:// URLs.",
    )
    return p.parse_args()


def _should_use_tls(cache_url: str, mode: Literal["auto", "true", "false"]) -> bool:
    if mode == "true":
        return True
    if mode == "false":
        return False
    return cache_url.startswith("redis://") or ".upstash.io" in cache_url


def _redis_url_for_tls(cache_url: str, use_tls: bool) -> str:
    """Normalize redis:// Upstash URLs to redis:// for redis-py."""
    if use_tls and cache_url.startswith("redis://"):
        return "redis://" + cache_url[len("redis://") :]
    return cache_url


def _resolve_cache_url(args: argparse.Namespace, spark) -> str:
    """Resolve the Upstash URL without requiring it in bundle/job parameters."""
    has_secret_ref = bool(args.cache_url_secret_scope or args.cache_url_secret_key)
    if args.cache_url and has_secret_ref:
        raise ValueError(
            "adaptive-island: pass either --cache-url or a Databricks secret "
            "scope/key pair, not both."
        )
    if args.cache_url:
        return args.cache_url

    env_url = os.environ.get("ADAPTIVE_ISLAND_CACHE_URL")
    if env_url and not has_secret_ref:
        return env_url

    if bool(args.cache_url_secret_scope) != bool(args.cache_url_secret_key):
        raise ValueError(
            "adaptive-island: --cache-url-secret-scope and "
            "--cache-url-secret-key must be provided together."
        )
    if args.cache_url_secret_scope and args.cache_url_secret_key:
        return _get_databricks_secret(
            spark,
            scope=args.cache_url_secret_scope,
            key=args.cache_url_secret_key,
        )

    raise ValueError(
        "adaptive-island: provide a Databricks secret scope/key pair or set "
        "ADAPTIVE_ISLAND_CACHE_URL for local/dev runs."
    )


def _get_databricks_secret(spark, *, scope: str, key: str) -> str:
    try:
        from pyspark.dbutils import DBUtils

        dbutils = DBUtils(spark)
    except Exception:  # noqa: BLE001 - Databricks also exposes dbutils globally.
        dbutils = globals().get("dbutils")

    if dbutils is None:
        raise RuntimeError(
            "adaptive-island: Databricks dbutils is required when resolving "
            "the cache URL from a secret scope."
        )

    value = dbutils.secrets.get(scope=scope, key=key)
    if not value:
        raise ValueError("adaptive-island: cache URL secret is empty.")
    return value


def main() -> int:
    args = _parse_args()
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.getOrCreate()
    cache_url = _resolve_cache_url(args, spark)
    rows = (
        spark.read.table(f"`{args.catalog}`.medallion.gold_provider_ranking_by_model")
        .orderBy("model", "region")
        .toPandas()
    )

    if rows.empty:
        print("adaptive-island: nothing to export.")
        return 0

    import redis  # Upstash uses the Redis protocol; local Redis is for smoke tests.

    client = redis.from_url(
        _redis_url_for_tls(cache_url, _should_use_tls(cache_url, args.cache_tls)),
        socket_timeout=10,
    )

    written = 0
    for row in rows.itertuples(index=False):
        model = row.model
        region = row.region or args.region
        payload = {
            "providers_ranked": list(row.providers_ranked or []),
            "scores": {k: float(v) for k, v in (row.scores or {}).items()},
            "attempts_total": int(row.attempts_total or 0),
            "window_hours": int(row.window_hours or 0),
            "computed_at": _iso(row.computed_at),
        }
        key = f"predictive:ranking:{region}:{model}"
        client.set(key, json.dumps(payload), ex=args.cache_ttl_seconds)
        written += 1

    print(f"adaptive-island: wrote {written} ranking keys to cache.")
    return 0


def _iso(value) -> str:
    if value is None:
        return datetime.now(UTC).isoformat().replace("+00:00", "Z")
    if isinstance(value, str):
        return value
    if hasattr(value, "isoformat"):
        return value.isoformat().replace("+00:00", "Z")
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
