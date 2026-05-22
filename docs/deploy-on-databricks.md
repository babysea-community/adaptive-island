# Deploy on Databricks

This guide deploys `adaptive-island` into a Databricks workspace with a Databricks Asset Bundle. It is the production-grade community path for the supported stack: Supabase as the operational source, Databricks as the learning path, and Upstash as the serving cache.

## Prerequisites

- Databricks workspace with Unity Catalog enabled.
- Databricks CLI v0.218 or later.
- Supabase source reachable through Databricks Lakehouse Federation.
- A source table or adapter view exposing the Databricks `provider_cost_log` projection: database-generated `id` plus the v1 attempt fields. The table/view may omit SDK-only `schema_version`.
- Upstash cache for exported rankings.

## Deployment rules

- Use one Databricks workspace/catalog, Supabase source, and Upstash cache per deployment region.
- Grant the Databricks federation principal read-only access to `provider_cost_log` or its adapter view.
- Store the Upstash URL in a Databricks secret scope; pass only scope/key names to jobs.
- Run the export job once before relying on cached rankings.
- Treat the Docker Compose example as a local smoke stack only, not a production substitute for Databricks + Supabase + Upstash.

## 1. Prepare Supabase

For a new deployment, run:

```sql
-- Supabase SQL editor
-- See ../examples/supabase-provider-cost-log/provider_cost_log.sql
```

For an existing event log, create an adapter view using [`../examples/adopt-existing-log/adapter_view.sql`](../examples/adopt-existing-log/adapter_view.sql).

## 2. Configure Lakehouse Federation

Create a Databricks PostgreSQL connection to the Supabase database because Lakehouse Federation connects to Supabase through its PostgreSQL-compatible endpoint. Expose the source schema as a Unity Catalog foreign catalog. The bundle variable `federation_connection` should point to that foreign catalog name, for example:

```text
my_supabase_connection_catalog
```

Grant the Databricks principal read access only to the source table/view.

## 3. Configure credentials

Use environment variables or a Databricks CLI profile for Databricks auth. Do not commit tokens.

```bash
export DATABRICKS_HOST="https://<workspace>.cloud.databricks.com"
export DATABRICKS_TOKEN="<token>"
```

Store the Upstash URL in a Databricks secret scope. Use the Databricks UI or a secure CI secret writer so the credential-bearing URL is not committed, pasted into bundle variables, or stored in job parameters.

Example names used below:

```text
scope: adaptive-island-prod
key:   upstash-cache-url
```

For Upstash URLs shown as `redis://...`, keep `cache_tls=auto` for `*.upstash.io` hosts or pass `--var cache_tls=true`. The URL itself still stays in the secret scope.

## 4. Validate

```bash
cd examples/databricks-asset-bundle

databricks bundle validate --target prod \
  --var catalog=adaptive_island_us \
  --var region=us \
  --var federation_connection=my_supabase_connection_catalog \
  --var source_schema=public \
  --var source_table=provider_cost_log \
  --var cache_url_secret_scope=adaptive-island-prod \
  --var cache_url_secret_key=upstash-cache-url
```

### Optional real-stack smoke before deploy

Before promoting a new workspace or region, run the disposable smoke harness from
the repository root. It authenticates to Databricks, creates a temporary
Supabase schema, computes a ranking, writes a smoke-scoped Upstash key, verifies
the SDK cache read, and cleans up by default.

```bash
python -m venv /tmp/adaptive-island-smoke-venv
. /tmp/adaptive-island-smoke-venv/bin/activate
python -m pip install 'psycopg[binary]>=3.2' 'redis>=5.0' 'pyyaml>=6.0'

export DATABRICKS_HOST='https://<workspace>.cloud.databricks.com'
export DATABRICKS_TOKEN='<token>'
export SUPABASE_PROJECT_ID='<project-ref>'
export SUPABASE_DB_PASSWORD='<database-password>'
export ADAPTIVE_ISLAND_CACHE_URL='redis://default:<token>@<host>:6379'

python examples/real-stack-smoke/validate.py
```

If direct Supabase database access resolves to an IPv6-only host from your CI or
dev container, use Supavisor instead:

```bash
export SUPABASE_DB_HOST='aws-1-us-east-1.pooler.supabase.com'
export SUPABASE_DB_PORT='6543'
export SUPABASE_DB_USER='postgres.<project-ref>'
```

## 5. Deploy

```bash
databricks bundle deploy --target prod \
  --var catalog=adaptive_island_us \
  --var region=us \
  --var federation_connection=my_supabase_connection_catalog \
  --var source_schema=public \
  --var source_table=provider_cost_log \
  --var cache_url_secret_scope=adaptive-island-prod \
  --var cache_url_secret_key=upstash-cache-url
```

This creates:

- Lakeflow Spark Declarative Pipeline `adaptive-island-pipeline-<region>`.
- Medallion tables in `<catalog>.medallion`.
- Lakeflow Job `adaptive-island-export-rankings-<region>`.
- Lakeflow Job `adaptive-island-train-model-<region>`.

## 6. First run

Run the export job once so the cache is populated before production traffic relies on it:

```bash
databricks bundle run adaptive_island_export_rankings --target prod
```

Optional MLflow training:

```bash
databricks bundle run adaptive_island_train_model --target prod
```

## 7. Verify

Check Databricks:

```sql
select count(*) from adaptive_island_us.medallion.bronze_provider_attempts;
select count(*) from adaptive_island_us.medallion.silver_provider_attempts;
select * from adaptive_island_us.medallion.gold_provider_ranking_by_model limit 10;
```

Check cache without placing the secret URL in command arguments. Read the URL from your secret manager into an environment variable for the subprocess, then unset it:

```bash
ADAPTIVE_ISLAND_CACHE_URL="$(your-secret-manager-read-command)" python - <<'PY'
import os
import redis

url = os.environ["ADAPTIVE_ISLAND_CACHE_URL"]
use_tls = url.startswith("redis://") or ".upstash.io" in url
if use_tls and url.startswith("redis://"):
  url = "redis://" + url[len("redis://"):]

client = redis.from_url(url, socket_timeout=10)
value = client.get("predictive:ranking:us:black-forest-labs/flux-schnell")
print("present" if value else "missing")
PY
unset ADAPTIVE_ISLAND_CACHE_URL
```

## Bundle variables

| Variable | Default | Purpose |
|---|---|---|
| `catalog` | `adaptive_island` | Writable Unity Catalog catalog |
| `region` | `us` | Region label written into Gold/cache |
| `federation_connection` | `adaptive_island_supabase_catalog` | Federated Supabase source catalog |
| `source_schema` | `public` | Source schema |
| `source_table` | `provider_cost_log` | Source table or adapter view |
| `cache_url_secret_scope` | required | Databricks secret scope containing the Upstash URL |
| `cache_url_secret_key` | required | Databricks secret key containing the Upstash URL |
| `cache_tls` | `auto` | Upstash TLS mode: `auto`, `true`, `false` |
| `cache_ttl_seconds` | `172800` | Cache TTL, default 48 h |
| `ranking_window_hours` | `24` | Gold rolling window |
| `min_train_rows` | `100` | Minimum rows for optional MLflow training |

## Multi-region

Deploy separately per region with separate source catalogs and caches:

```bash
# US
--var catalog=adaptive_island_us --var region=us --var cache_url_secret_scope=adaptive-island-us --var cache_url_secret_key=upstash-cache-url

# EU
--var catalog=adaptive_island_eu --var region=eu --var cache_url_secret_scope=adaptive-island-eu --var cache_url_secret_key=upstash-cache-url

# APAC
--var catalog=adaptive_island_apac --var region=apac --var cache_url_secret_scope=adaptive-island-apac --var cache_url_secret_key=upstash-cache-url
```

Keep raw attempt logs region-local.

## Tear down

```bash
databricks bundle destroy --target prod
```

Tables and registered model versions may remain in Unity Catalog; drop them manually if you need a clean wipe.
