# Docker Compose Local Stack

Run a minimum local smoke stack for `adaptive-island` without Databricks, Supabase, or Upstash credentials.

## Start

```bash
docker compose up -d
```

This gives you:

- PostgreSQL on `localhost:5432` as a developer-only stand-in for Supabase
- Redis on `localhost:6379` as a developer-only stand-in for the Upstash ranking cache
- MLflow on `http://localhost:5000` with a file-backed tracking store

This stack is only for local smoke checks. Production/community deployments use Supabase, Databricks, and Upstash.

## Try the SDK

```bash
cd ../../client/python
pip install -e .
python - <<'PY'
from adaptive_island import Selector
sel = Selector(cache_url="redis://localhost:6379")
print(sel.rank(model_id="demo/model", region="us", fallback=["a", "b", "c"]))
PY
```

The cache is empty, so the SDK returns the fallback order after removing duplicate providers.

## Seed a ranking

```bash
redis-cli SET 'predictive:ranking:us:demo/model' '{"providers_ranked":["b","a"],"scores":{"b":0.9,"a":0.3},"attempts_total":42,"window_hours":24,"computed_at":"2026-04-29T00:00:00Z"}'
```

Re-run the SDK call; the result should be `['b', 'a']`. The cached providers are filtered against the fallback list; when at least one ranked provider is allowed, the cached ranking is the source of truth and unranked fallback providers are not appended.

## Stop

```bash
docker compose down -v
```
