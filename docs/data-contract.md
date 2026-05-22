# Attempt log data contract

The source contract is one row per provider attempt. The canonical schema is `schemas/attempt.v1.json`.

## Required fields

| Field | Requirement |
|---|---|
| `schema_version` | SDK/event payloads use `attempt.v1`; Supabase tables may encode the version by table/view contract. |
| `generation_id` | Stable identifier shared by all attempts for the same workload. |
| `model` | Canonical model identifier used by the application. |
| `provider` | Provider submitted to for this attempt. |
| `outcome` | One of `used`, `cancelled`, `discarded`, `failed`, or `pending`. |
| `attempt_order` | 1 for the first provider, 2+ for failover attempts. |
| `submitted_at` | RFC 3339 timestamp when the provider attempt was submitted. |

Databricks source tables or adapter views must also expose `id` for Bronze lineage and de-duplication. SDK insert payloads may omit `id` when Supabase generates it.

## Optional fields

| Field | Meaning |
|---|---|
| `account_id` | Tenant/account identifier; keep region-local where required. |
| `provider_model_id` | Provider-native model id if different from `model`. |
| `prediction_id` | Provider job id for reconciliation. |
| `estimated_cost` | Estimated or actual provider cost for this attempt in USD. |
| `was_cancelled` | Whether the attempt was cancelled. |
| `cancel_available` | Whether cancellation was available for the provider attempt. |
| `resolved_at` | Terminal timestamp; null while pending. |
| `error_message` | Sanitized coarse error class/message. |
| `metadata` | Small operational metadata bag. Do not store secrets or raw prompts. |

## Outcome semantics

| Outcome | Meaning for ranking |
|---|---|
| `used` | The attempt produced the output used by the generation. Counts toward success. |
| `failed` | Provider attempt failed. Counts toward wasted attempts. |
| `discarded` | Provider returned a result that was not used. Counts toward wasted attempts. |
| `cancelled` | Attempt was cancelled. Counts toward wasted attempts unless your product excludes user cancellations. |
| `pending` | Not terminal. Exclude from terminal success/waste calculations until resolved. |

## Timestamp rules

- Use UTC RFC 3339 timestamps.
- `submitted_at` is required.
- `resolved_at` should be greater than or equal to `submitted_at` for terminal attempts.
- Pending attempts may have `resolved_at = null`.
- Gold rankings should record `computed_at` when the ranking was produced.

## Region and model normalization

- Use one canonical `region` value per deployment, such as `us`, `eu`, or `apac`.
- The Databricks bundle writes the configured deployment region into Bronze and Gold rows; keep each Supabase source region-local.
- Keep model identifiers stable across providers.
- Put provider-native model names in `provider_model_id`.
- Do not mix regions in one Gold ranking artifact.
- Keep raw provider credentials, request bodies, and unnecessary PII out of the source table.
