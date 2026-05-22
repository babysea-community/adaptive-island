# Adopt on an Existing Event Log

If your application already logs provider attempts under different column names, you do not need to rewrite anything. Expose a single SQL view that maps your schema to the provider-attempt contract in [`attempt.v1`](../../schemas/attempt.v1.json), then point the bundle at it.

## Apply the adapter view

1. Open [`adapter_view.sql`](adapter_view.sql) and edit:
   - `my_catalog` to a Unity Catalog catalog where you can create the adapter view.
   - `your_federated_catalog` to the foreign catalog backed by your Lakehouse Federation connection.
   - The `SELECT` clause to alias your real columns to the v1 contract names.
2. Run it through any SQL warehouse:

   ```bash
   databricks sql exec --warehouse-id <warehouse-id> --file adapter_view.sql
   ```

3. Then deploy the bundle pointing `federation_connection` at the catalog that contains the adapter view:

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

## Validate

Quick sanity check after the first pipeline refresh:

```sql
SELECT
  COUNT(*) AS rows,
   AVG(CAST(outcome = 'used' AS DOUBLE)) AS success_rate,
   COUNT(DISTINCT model) AS models,
  COUNT(DISTINCT provider) AS providers
FROM my_catalog.medallion.bronze_provider_attempts;
```

If `success_rate = 0.0` or `models = 0`, your column mapping is likely wrong. The most common cause is misreading the `outcome` enum, for example mapping `success` when the operational value should be `used`.

For the full design rationale, see [`docs/adopt-on-existing-event-log.md`](../../docs/adopt-on-existing-event-log.md).
