# Architecture

`adaptive-island` packages a cache-first adaptive provider-selection loop grounded in BabySea's documented Databricks routing implementation and generalized for community-owned Databricks, Supabase, and Upstash deployments.

The grounding source is BabySea's internal production Databricks implementation. Public OSS claims should stay inside the shipped loop documented there: Supabase `provider_cost_log` ➜ Databricks Bronze/Silver/Gold ➜ Upstash `predictive:ranking:<region>:<model>` ➜ cache-first runtime fallback.

## Grounding and terminology

| OSS term | BabySea production analogue | Stack boundary |
|---|---|---|
| `provider_cost_log` | Supabase provider attempt log | Operational source of truth; one row per provider submission. |
| Bronze provider attempts | Federated Delta materialized view over the source log | Databricks reads Supabase through Lakehouse Federation. |
| Silver provider attempts | Typed latency/success/waste/failover projection | Databricks derives fields used by Gold and optional MLflow training. |
| Gold provider ranking by model | `gold_provider_ranking_by_model` | Databricks emits ranked providers, scores, attempt totals, window, and `computed_at`. |
| Upstash ranking key | `predictive:ranking:<region>:<model>` | Runtime cache contract read by SDK/API code. |
| Fallback order | First concrete provider order for a model | Deterministic fail-open order when cache is unavailable or adaptive routing is disabled. |

The OSS uses neutral table names where helpful, but every shipped component maps to this Databricks ➜ Upstash ➜ Supabase loop. Features outside that loop are outside this primitive.

## Production-grade contract

`adaptive-island` is production-grade for the supported community stack when these invariants hold:

- Supabase remains the operational source of truth for one row per provider attempt.
- Databricks remains the learning path: Lakehouse Federation reads Supabase, Lakeflow Spark Declarative Pipelines materialize Bronze/Silver/Gold on Delta Lake, and Lakeflow Jobs export Gold rankings.
- Upstash remains the serving cache for `predictive:ranking:<region>:<model>`.
- Runtime code reads one cache key, validates `ranking.v1`, filters ranked providers to the caller allowlist, and fails open to deterministic fallback.
- Regional stacks stay isolated; use separate Supabase, Databricks, and Upstash resources for `us`, `eu`, and `apac` or your own region labels.
- Breaking source or cache payload changes require a new schema version.

## Stack and claim boundary

| Included in current version | Boundary |
|---|---|
| Supabase operational source | `provider_cost_log` or an adapter view with the same contract. |
| Databricks learning path | Unity Catalog, Lakehouse Federation, Lakeflow Spark Declarative Pipelines, Delta Lake, Lakeflow Jobs, and optional offline MLflow training. |
| Upstash serving cache | Key/value cache for `predictive:ranking:<region>:<model>`. |
| SDK/API runtime | Cache-first `rank()`/`pick()` plus deterministic caller-provided fallback. |

| Not included in current version | Reason |
|---|---|
| Request-path Databricks dependency | BabySea serves from cache/fallback; Databricks improves later requests. |
| Stochastic exploration, propensity logging, IPS/SNIPS gates | Not part of the documented BabySea path generalized here. |
| Non-Upstash production cache, queues, search indexes, or alternate warehouses | Not implemented or validated in this repo. |
| Managed hosted service | This is a self-deployed OSS primitive for the stated stack. |

Local Docker Compose uses PostgreSQL and Redis only as developer stand-ins for Supabase and Upstash. Production/community adoption should use Supabase, Databricks, and Upstash.

## Control loop

```text
application provider attempts
        │
        ▼
Supabase provider_cost_log
        │ Lakehouse Federation
        ▼
Bronze provider attempts on Delta
        ▼
Silver typed attempts
        ▼
Gold provider ranking by model
        │ Lakeflow export job
        ▼
Upstash predictive:ranking:<region>:<model>
        │
        ▼
SDK/API provider order + application failover
```

The request path reads one cache key and falls back to the caller-provided order. Databricks is on the learning path, not the request path.

## Source contract

The operational source is `provider_cost_log`, modeled after BabySea's documented production attempt log. One row represents one provider submission. The Supabase table may include generated and maintenance columns, but the Databricks source projection requires:

- `id`
- `generation_id`
- `account_id`
- `model`
- `provider`
- `provider_model_id`
- `prediction_id`
- `estimated_cost`
- `outcome`
- `attempt_order`
- `was_cancelled`
- `cancel_available`
- `submitted_at`
- `resolved_at`
- `error_message`
- `metadata`

See [`../schemas/attempt.v1.json`](../schemas/attempt.v1.json) and [`../examples/supabase-provider-cost-log/provider_cost_log.sql`](../examples/supabase-provider-cost-log/provider_cost_log.sql).

`attempt.v1` covers both SDK insert events and Databricks source projections. SDK payloads include `schema_version` and may omit the database-generated `id`; the Supabase source table or adapter view must expose `id` and may omit `schema_version` because the table itself is the versioned source contract.

## Medallion tables

All tables live in one Unity Catalog schema, default `<catalog>.medallion`.

| Layer | Table | Grain | Purpose |
|---|---|---|---|
| Bronze | `bronze_provider_attempts` | provider attempt | Federated source copy with lineage |
| Silver | `silver_provider_attempts` | provider attempt | Typed latency, success, wasted, failover fields |
| Gold | `gold_provider_ranking_by_model` | model + region | Runtime ranking exported to cache |

## Gold scoring

Gold aggregates recent attempts by `(model, region, provider)` and computes:

```text
score = success_rate       * 1.0
      - wasted_rate        * 0.5
      - latency_p95_norm   * 0.3
```

Providers are sorted by score descending, with lower `latency_p95_ms` as a tie-breaker. Defaults:

- ranking window: 24 h
- cache TTL: 48 h
- export cadence: daily

## Cache contract

Key:

```text
predictive:ranking:<region>:<model>
```

Value:

```json
{
  "providers_ranked": ["replicate", "fal", "cloudflare"],
  "scores": {
    "replicate": 0.81,
    "fal": 0.42,
    "cloudflare": -0.05
  },
  "attempts_total": 137,
  "window_hours": 24,
  "computed_at": "2026-04-29T02:31:15Z"
}
```

See [`../schemas/ranking.v1.json`](../schemas/ranking.v1.json).

## Optional offline MLflow path

The MLflow training job trains a value-prediction model from Silver and registers it in Unity Catalog as `<catalog>.ml.predictive_routing` for offline analysis and promotion review. Runtime provider selection remains cache/fallback only and does not call Databricks Model Serving.

## Fail-open ladder

| Failure | Runtime behavior |
|---|---|
| Databricks unavailable | Serve last exported cache value until TTL expires |
| Cache unavailable | Return caller-provided fallback order |
| Cache value malformed | Return caller-provided fallback order |
| Adaptive routing disabled | Skip cache reads and return caller-provided fallback order |
| Provider failure | Application failover tries the next provider |

## Multi-region

Deploy one isolated Databricks + Supabase + Upstash stack per region:

- Supabase source
- Databricks workspace/catalog
- Upstash cache
- MLflow experiment/model

Do not move raw attempt logs across regions unless your compliance program explicitly permits it.

## Enterprise deployment assumptions

- Deploy one isolated stack per region and keep Supabase source data region-local.
- Grant Databricks read-only access to the source table or adapter view.
- Store the Upstash URL in a Databricks secret scope; never pass it as a bundle variable or job parameter.
- Keep `provider_cost_log` free of provider credentials, raw request bodies, and unnecessary PII.
- Keep the cache TTL longer than the Lakeflow export cadence so API traffic can fail open during Databricks pauses.
- Validate the first deployment with the real-stack smoke harness before sending production traffic through cached rankings.
