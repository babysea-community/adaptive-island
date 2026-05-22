# Local synthetic demo

This demo proves the core idea without Databricks, Supabase, or Upstash credentials:

1. Read a CSV of provider attempts.
2. Compute a deterministic ranking JSON with the same cache shape.
3. Use the JSON directly in SDK tests, or paste it into a local Redis stand-in for an optional cache check.
4. Delete or corrupt the key to verify fail-open fallback behavior.

The script is a developer demo, not the production architecture. Production deployments should use Supabase as the source, Databricks Bronze/Silver/Gold for ranking, and Upstash for serving.

## Run

```bash
python rank_from_csv.py attempts.csv \
  --model black-forest-labs/flux-schnell \
  --region us
```

Expected top provider for the sample data is `provider_b` because `provider_a` has more recent failures and higher p95 latency.

## SDK fail-open check without cache credentials

Build the TypeScript SDK, then run the in-memory cache demo:

```bash
cd ../../client/typescript
npm run build
cd ../../examples/local-synthetic-demo
node sdk-cache-demo.mjs
```

Expected behavior:

- valid ranking JSON returns `provider_b` first with `source: "cached-ranking"`;
- malformed JSON returns the caller fallback after removing duplicate providers;
- missing cache key returns the caller fallback after removing duplicate providers.

## Optional local cache check with Redis stand-in

```bash
python rank_from_csv.py attempts.csv \
  --model black-forest-labs/flux-schnell \
  --region us > ranking.json
redis-cli set 'predictive:ranking:us:black-forest-labs/flux-schnell' "$(cat ranking.json)"
```

Then point the TypeScript or Python SDK at the local Redis stand-in. If you delete the key or replace the value with malformed JSON, `rank()` should return your fallback list after removing duplicate providers.
