# Databricks Asset Bundle Example

This is the recommended deployment surface for `adaptive-island`.

## Run

```bash
databricks bundle validate --target prod \
  --var cache_url_secret_scope=adaptive-island-prod \
  --var cache_url_secret_key=upstash-cache-url

databricks bundle deploy --target prod \
  --var cache_url_secret_scope=adaptive-island-prod \
  --var cache_url_secret_key=upstash-cache-url
```

## Configure

Edit `databricks.yml` or pass bundle variables to point at your Unity Catalog catalog and Lakehouse Federation connection. Store the Upstash URL in a Databricks secret scope; pass only the non-secret scope/key names to the bundle. Re-deploy after changing values.

For the full walkthrough, see [`docs/deploy-on-databricks.md`](../../docs/deploy-on-databricks.md).

## Multi-region

Deploy once per region by overriding the variables:

```bash
databricks bundle deploy --target prod \
  --var catalog=adaptive_island_us \
  --var region=us \
  --var federation_connection=adaptive_island_us_supabase_catalog \
  --var cache_url_secret_scope=adaptive-island-us \
  --var cache_url_secret_key=upstash-cache-url

databricks bundle deploy --target prod \
  --var catalog=adaptive_island_eu \
  --var region=eu \
  --var federation_connection=adaptive_island_eu_supabase_catalog \
  --var cache_url_secret_scope=adaptive-island-eu \
  --var cache_url_secret_key=upstash-cache-url

databricks bundle deploy --target prod \
  --var catalog=adaptive_island_apac \
  --var region=apac \
  --var federation_connection=adaptive_island_apac_supabase_catalog \
  --var cache_url_secret_scope=adaptive-island-apac \
  --var cache_url_secret_key=upstash-cache-url
```

Each deploy targets a different workspace (configure via `~/.databrickscfg` profiles). No data flows between regions.
