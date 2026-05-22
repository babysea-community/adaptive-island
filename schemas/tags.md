# Unity Catalog tags

`adaptive-island` ships with a recommended Unity Catalog tag taxonomy for lineage, governance, and monitoring.

## Tag keys

| Key | Values | Applied to |
|---|---|---|
| `adaptive_island.layer` | `bronze` \| `silver` \| `gold` \| `ml` | catalogs, schemas, tables |
| `adaptive_island.region` | `us` \| `eu` \| `apac` \| custom | catalogs, schemas, tables |
| `adaptive_island.contains_pii` | `true` \| `false` | columns |
| `adaptive_island.feature_for_model` | `true` \| `false` | optional MLflow feature columns |
| `adaptive_island.routing_signal` | `true` \| `false` | columns used to compute provider rankings |

## Why each one matters

- `layer`: lets governance teams distinguish raw, curated, and runtime-contract tables.
- `region`: supports regional isolation and access policies.
- `contains_pii`: lets downstream processors avoid copying sensitive fields.
- `feature_for_model`: lets ML reviewers list every optional model input.
- `routing_signal`: marks columns such as `provider`, `model`, `outcome`, `submitted_at`, and `resolved_at` that directly affect rankings.

## Example

```sql
ALTER TABLE main.medallion.bronze_provider_attempts
  SET TAGS ('adaptive_island.layer' = 'bronze', 'adaptive_island.region' = 'us');

ALTER TABLE main.medallion.silver_provider_attempts
  ALTER COLUMN provider SET TAGS ('adaptive_island.routing_signal' = 'true');
```
