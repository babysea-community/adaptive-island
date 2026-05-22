-- Adapter view example.
--
-- If your existing event log uses different column names than the
-- adaptive-island provider_cost_log contract, expose a view that aliases
-- the columns to the expected shape.
--
-- Edit the SOURCE_TABLE/SOURCE_CATALOG names and the column casts
-- to match your schema, then run:
--
--   databricks sql exec --warehouse-id <id> --file adapter_view.sql
--
-- See ../../docs/adopt-on-existing-event-log.md for the full guide.

CREATE SCHEMA IF NOT EXISTS my_catalog.public;

CREATE OR REPLACE VIEW my_catalog.public.provider_cost_log AS
SELECT
  CAST(id AS BIGINT)                                                       AS id,
  CAST(account_id AS STRING)                                               AS account_id,
  CAST(generation_id AS STRING)                                            AS generation_id,
  CAST(provider AS STRING)                                                 AS provider,
  CAST(provider_model_id AS STRING)                                        AS provider_model_id,
  CAST(prediction_id AS STRING)                                            AS prediction_id,
  CAST(model AS STRING)                                                    AS model,
  CAST(estimated_cost AS DOUBLE)                                           AS estimated_cost,
  CAST(outcome AS STRING)                                                  AS outcome,
  CAST(GREATEST(COALESCE(attempt_order, 1), 1) AS INT)                     AS attempt_order,
  CAST(COALESCE(was_cancelled, false) AS BOOLEAN)                          AS was_cancelled,
  CAST(COALESCE(cancel_available, false) AS BOOLEAN)                       AS cancel_available,
  CAST(submitted_at AS TIMESTAMP)                                          AS submitted_at,
  CAST(resolved_at AS TIMESTAMP)                                           AS resolved_at,
  CAST(error_message AS STRING)                                            AS error_message,
  CAST(metadata AS STRING)                                                 AS metadata
FROM `your_federated_catalog`.public.provider_cost_log
WHERE submitted_at IS NOT NULL;
