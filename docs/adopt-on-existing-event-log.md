# Adopt adaptive-island on an Existing Event Log

`adaptive-island` reads a federated source named `provider_cost_log`. If your application already logs provider attempts under different names, create one adapter view instead of rewriting historical data.

## Required shape

The view must expose the columns described in [`../schemas/attempt.v1.json`](../schemas/attempt.v1.json), using the operational BabySea-style fields:

- `id`
- `account_id`
- `generation_id`
- `provider`
- `provider_model_id`
- `prediction_id`
- `model`
- `estimated_cost`
- `outcome`
- `attempt_order`
- `was_cancelled`
- `cancel_available`
- `submitted_at`
- `resolved_at`
- `error_message`
- `metadata`

## Worked example

Suppose your legacy table already has similar fields:

```sql
CREATE TABLE public.provider_attempt_events (
  id              bigserial primary key,
  account_id      uuid,
  generation_id   uuid,
  provider        text,
  model           text,
  estimated_cost  numeric,
  outcome         text,
  attempt_order   int,
  submitted_at    timestamptz,
  resolved_at     timestamptz,
  error_message   text,
  metadata        jsonb
);
```

Create a Databricks SQL view in a catalog/schema that the bundle can read:

```sql
CREATE SCHEMA IF NOT EXISTS my_catalog.public;

CREATE OR REPLACE VIEW my_catalog.public.provider_cost_log AS
SELECT
  CAST(id AS BIGINT)                                                        AS id,
  CAST(account_id AS STRING)                                                AS account_id,
  CAST(generation_id AS STRING)                                             AS generation_id,
  CAST(provider AS STRING)                                                  AS provider,
  CAST(NULL AS STRING)                                                      AS provider_model_id,
  CAST(NULL AS STRING)                                                      AS prediction_id,
  CAST(model AS STRING)                                                     AS model,
  CAST(estimated_cost AS DOUBLE)                                            AS estimated_cost,
  CAST(outcome AS STRING)                                                   AS outcome,
  CAST(GREATEST(COALESCE(attempt_order, 1), 1) AS INT)                      AS attempt_order,
  CAST(false AS BOOLEAN)                                                    AS was_cancelled,
  CAST(false AS BOOLEAN)                                                    AS cancel_available,
  CAST(submitted_at AS TIMESTAMP)                                           AS submitted_at,
  CAST(resolved_at AS TIMESTAMP)                                            AS resolved_at,
  CAST(error_message AS STRING)                                             AS error_message,
  CAST(metadata AS STRING)                                                  AS metadata
FROM `your_federated_catalog`.public.provider_attempt_events
WHERE submitted_at IS NOT NULL;
```

Then deploy:

```bash
databricks bundle deploy --target prod \
  --var catalog=my_catalog \
  --var region=us \
  --var federation_connection=my_catalog \
  --var source_schema=public \
  --var source_table=provider_cost_log \
  --var cache_url_secret_scope=adaptive-island-prod \
  --var cache_url_secret_key=upstash-cache-url
```

If the source can contain bad timestamps, filter `resolved_at >= submitted_at` in the adapter view or let Silver drop negative-latency rows before Gold scoring.

## Why a view?

- No data copy.
- No historical backfill.
- No second source of truth.
- The mapping is version-controlled and reviewable.

## Validate

```sql
SELECT
  COUNT(*) AS rows,
  AVG(CAST(outcome = 'used' AS DOUBLE)) AS success_rate,
  COUNT(DISTINCT model) AS distinct_models,
  COUNT(DISTINCT provider) AS distinct_providers
FROM my_catalog.medallion.bronze_provider_attempts;
```

If `success_rate = 0.0` or `distinct_models = 0`, inspect the `outcome` mapping. Many systems use `success`, `completed`, or `ok`; the adaptive-island terminal success value is `used`.
