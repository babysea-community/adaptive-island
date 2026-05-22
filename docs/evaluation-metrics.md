# Evaluation metrics

Use evaluation reports to prove that adaptive ranking improves execution without making the request path fragile.

## Minimum report

| Metric | Baseline fallback | Adaptive ranking | Why it matters |
|---|---:|---:|---|
| Success rate | 0.91 | 0.96 | More workloads reach a usable terminal output. |
| P95 latency | 12.4s | 8.7s | Users wait less. |
| Wasted attempt rate | 0.18 | 0.09 | Fewer paid or failed attempts are discarded. |
| Gold ranking score | 0.72 | 0.81 | Ranking improves the documented success/waste/latency tradeoff. |
| Mean attempts per generation | 1.32 | 1.14 | Failover pressure falls. |

Numbers above are illustrative. Replace them with results from your own synthetic demo, staging traffic, or production shadow analysis.

## Suggested synthetic demo

1. Create attempt rows where Provider A starts fast and healthy.
2. Add a later window where Provider A becomes slow/failing and Provider B improves.
3. Run the local ranking script or Databricks Gold job over each window.
4. Confirm the cache ranking flips from A-first to B-first.
5. Delete or corrupt the cache key and confirm the SDK returns fallback.

## Rollout checklist

- Compare against the deterministic fallback order used before rollout.
- Evaluate each `(region, model)` separately.
- Watch for provider allowlist filtering; ranked providers outside fallback should be ignored by the SDK.
- Keep dashboards for cache hit rate, fallback rate, malformed payload count, and stale ranking count.
