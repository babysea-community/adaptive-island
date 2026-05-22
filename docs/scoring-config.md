# Scoring configuration

The default Gold ranking score is intentionally explainable:

```text
score = success_rate       * 1.0
      - wasted_rate        * 0.5
      - latency_p95_norm   * 0.3
```

A portable configuration can be represented as:

```yaml
weights:
  success_rate: 1.0
  wasted_rate: -0.5
  latency_p95_norm: -0.3
window_hours: 24
ttl_hours: 48
```

## Fields

| Field | Meaning |
|---|---|
| `weights.success_rate` | Reward providers whose attempts end in `used`. |
| `weights.wasted_rate` | Penalize attempts that fail, are discarded, or are cancelled. |
| `weights.latency_p95_norm` | Penalize slower p95 latency after normalization. |
| `window_hours` | Rolling lookback used by Gold ranking. |
| `ttl_hours` | Cache TTL; keep it longer than the export cadence. |

## Operational guidance

- Keep the score monotonic and explainable before adding model-based ranking.
- Keep a deterministic tie-breaker, such as lower p95 latency then provider name.
- Tune per region if provider behavior differs materially by region.
- Document every weight change with the evaluation window and before/after metrics.
