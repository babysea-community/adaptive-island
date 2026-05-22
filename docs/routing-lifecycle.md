# Routing lifecycle

`adaptive-island` keeps Databricks on the learning path, not the request path.

```text
Provider attempts
  -> Supabase provider_cost_log
  -> Databricks Bronze provider_attempts
  -> Databricks Silver typed_attempts
  -> Databricks Gold provider_ranking_by_model
  -> Lakeflow export job
  -> Upstash predictive:ranking:<region>:<model>
  -> SDK rank()/pick()
  -> caller failover loop
```

## 1. Application logs attempts

Every provider submission writes one attempt row to Supabase. A single generation can produce multiple attempt rows if failover occurs.

Minimum request-path responsibility:

- log the provider actually tried
- log the canonical model and deploy the source under one configured region
- log the attempt order
- record terminal outcome when known
- keep secrets, raw prompts, and raw request bodies out of metadata

## 2. Databricks reads Supabase

Lakehouse Federation reads the regional Supabase source. Databricks should have read-only access to the source table or adapter view.

## 3. Bronze de-duplicates raw attempts

Bronze preserves source lineage and stable attempt identity. This layer is intentionally close to the operational source.

## 4. Silver normalizes typed attempts

Silver derives typed latency, success, wasted-attempt, cost, and failover fields. It is the feature layer used by Gold and optional MLflow training.

## 5. Gold computes rankings

Gold aggregates recent attempts by `(model, region, provider)` and computes a deterministic score. Providers are sorted best-first for each `(model, region)`.

## 6. Lakeflow exports cache payloads

The export job writes one Upstash key per `(region, model)`:

```text
predictive:ranking:<region>:<model>
```

The payload must match `schemas/ranking.v1.json`.

## 7. Runtime reads one cache key

The SDK reads and validates the cache value. If the cache is missing, malformed, stale by local max-age, or unavailable, the SDK returns the caller-provided fallback order after removing duplicate providers.

## 8. Caller executes failover

`rank()` returns an ordered provider list. The application still owns the provider call loop and should try the next provider when the current provider fails.

## Request-path guarantee

Databricks improves later rankings. It is not required to serve the current request. The current request only needs the cache and a deterministic fallback list.
