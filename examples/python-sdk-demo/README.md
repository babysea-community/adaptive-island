# Python SDK Demo

Seeds a local Redis stand-in with a synthetic adaptive-island ranking payload shaped after the documented BabySea Upstash cache contract and shows `adaptive_island.Selector` returning deterministic provider order.

Local Redis is only a developer smoke-test stand-in. Production/community deployments should read Upstash-backed keys exported from Databricks.

## Prerequisites

- Python 3.10+
- Local Redis on `localhost:6379` as a developer stand-in for Upstash

## Run

```bash
# 1. Start local Redis if needed
docker run --rm -d --name adaptive-island-redis -p 6379:6379 redis:7-alpine

# 2. Install the SDK
pip install -e ../../client/python redis

# 3. Run the demo
python demo.py
```

Stop Redis with `docker stop adaptive-island-redis` when finished.

## What it does

1. Seeds the local cache at `predictive:ranking:us:demo/model`.
2. Calls `rank(...)` and prints the cache-derived provider order.
3. Emits an `attempt.v1` event shaped for `provider_cost_log`.

## Expected output

```text
seeded predictive:ranking:us:demo/model

rank(...) result:
  1. fast
  2. mid
  3. slow

Last decision source: cached-ranking
```

If you delete the cache key and re-run, `Last decision source` becomes `fallback` and the returned order is the caller-provided fallback list after removing duplicate providers.
