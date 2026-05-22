# Real-stack smoke validation

This harness validates the public `adaptive-island` contract against real Databricks, Supabase, and Upstash services without committing or printing credentials. It is a real-service contract smoke test; it does not replace `databricks bundle deploy` plus a first pipeline/export run for production rollout.

It performs four checks:

1. Authenticates to the Databricks workspace API and inspects the local Databricks Asset Bundle shape.
2. Connects to Supabase, creates a disposable schema with a `provider_cost_log` table, inserts provider-attempt rows, computes the Gold scoring formula, and drops the schema by default.
3. Writes the computed ranking to Upstash under `predictive:ranking:<region>:<model>` with a short TTL.
4. Runs the Python SDK `Selector.rank()` against that Upstash key and deletes the key by default.

## Install dependencies

Use an isolated environment:

```bash
python -m venv /tmp/adaptive-island-smoke-venv
. /tmp/adaptive-island-smoke-venv/bin/activate
python -m pip install 'psycopg[binary]>=3.2' 'redis>=5.0' 'pyyaml>=6.0'
```

## Required environment variables

```bash
export DATABRICKS_HOST='https://<workspace>.cloud.databricks.com'
export DATABRICKS_TOKEN='<databricks-token>'

export SUPABASE_PROJECT_ID='<project-ref>'
export SUPABASE_DB_PASSWORD='<database-password>'
# Optional overrides if your project requires a pooler or custom user:
# export SUPABASE_DB_HOST='db.<project-ref>.supabase.co'
# export SUPABASE_DB_PORT='5432'
# export SUPABASE_DB_USER='postgres'
# export SUPABASE_DB_NAME='postgres'

export ADAPTIVE_ISLAND_CACHE_URL='redis://default:<token>@<host>:6379'
```

If your runner cannot reach the direct Supabase database host because it resolves to IPv6 only, use the project's Supavisor pooler instead:

```bash
export SUPABASE_DB_HOST='aws-<pooler-id>-<region>.pooler.supabase.com'
export SUPABASE_DB_PORT='6543'
export SUPABASE_DB_USER='postgres.<project-ref>'
```

Optional:

```bash
export ADAPTIVE_ISLAND_REGION='us'
export ADAPTIVE_ISLAND_MODEL='black-forest-labs/flux-schnell'
export ADAPTIVE_ISLAND_SMOKE_KEEP='1'        # keep temp schema/key for manual inspection
export ADAPTIVE_ISLAND_SMOKE_RESULT='/tmp/adaptive-island-smoke.json'
export ADAPTIVE_ISLAND_SMOKE_ALLOW_OVERWRITE='1'  # only if you intentionally test an existing cache key; prior value is restored
```

By default the key uses `region=smoke` and `model=adaptive-island-smoke/<run-id>` so production ranking keys are not touched. If the target key already exists, the script refuses to overwrite it unless `ADAPTIVE_ISLAND_SMOKE_ALLOW_OVERWRITE=1` is set; in that case the prior value and TTL are restored after the SDK read.

## Run

From the repository root:

```bash
python examples/real-stack-smoke/validate.py
```

The output is a sanitized JSON summary. It includes object names and counts only; it never prints tokens, database passwords, or Upstash URLs.

## Cleanup

By default the script drops the temporary Supabase schema and deletes the temporary Upstash key before exiting. If `ADAPTIVE_ISLAND_SMOKE_KEEP=1`, remove them manually after inspection.
