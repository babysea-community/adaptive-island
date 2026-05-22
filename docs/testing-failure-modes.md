# Failure-mode test checklist

`adaptive-island` promises fail-open runtime behavior. Tests should prove that the SDK returns caller-provided fallback order, after removing duplicate providers, whenever cache ranking cannot be trusted.

## Cache payload cases

| Case | Expected SDK behavior |
|---|---|
| Missing cache key | Return deduplicated fallback order. |
| Empty cache value | Return deduplicated fallback order. |
| Malformed JSON | Return deduplicated fallback order. |
| Missing `computed_at` | Return deduplicated fallback order. |
| Invalid `computed_at` | Return deduplicated fallback order. |
| Expired `computed_at` under local max-age | Return deduplicated fallback order. |
| Missing `providers_ranked` | Return deduplicated fallback order. |
| Empty `providers_ranked` | Return deduplicated fallback order. |
| Missing score for a ranked provider | Return deduplicated fallback order. |
| Non-finite score | Return deduplicated fallback order. |
| Ranked provider not in fallback allowlist | Filter it out; serve the remaining ranked subset only. |
| All ranked providers outside fallback allowlist | Return deduplicated fallback order. |
| Fallback provider not in ranking | Excluded from the ranked subset; the cached ranking is the source of truth when a non-empty intersection exists. |

## Infrastructure cases

| Case | Expected behavior |
|---|---|
| Upstash connection error | Return deduplicated fallback order. |
| Upstash timeout | Return deduplicated fallback order. |
| Databricks paused | Serve last cache value until TTL expires; then fallback. |
| Lakeflow export job fails | Serve last cache value until TTL expires; then fallback. |
| Adaptive routing disabled | Skip cache reads and return deduplicated fallback order. |
| Provider down at execution time | Caller failover loop tries the next provider in order. |

## Regression rule

No request-path code should throw solely because Databricks or Upstash is unavailable. Only invalid caller input, such as an empty fallback list, should throw before returning a provider order.
