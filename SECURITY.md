# Security policy

## Reporting vulnerabilities

Please report vulnerabilities privately through GitHub's **Report a vulnerability** flow on the public `babysea-community/adaptive-island` repository. If that flow is unavailable, contact the maintainers at `dev@babysea.ai`.

Do not open public issues for suspected vulnerabilities, exposed secrets, private attempt logs, customer metadata, provider credentials, or deployment details that include sensitive information.

## Supported versions

`adaptive-island` is a production-grade OSS primitive for the supported Databricks + Supabase + Upstash stack. Security fixes target the latest public release and the `main` branch.

## Runtime security model

`adaptive-island` keeps Databricks off the request path. Request-time code reads one Upstash key and must fail open to the caller-provided fallback order when the cache is missing, malformed, stale, disabled, or unavailable.

Supabase is the operational source for attempt rows, Databricks is the offline learning path, and Upstash is the serving cache. The cache payload contains provider IDs, scores, attempt counts, window size, and `computed_at`; it must not contain provider credentials, raw prompts, request bodies, generated media, or customer PII.

## Security ownership matrix

| Surface              | Boundary in adaptive-island                                                                   | Operator responsibility                                                                 |
| :------------------- | :-------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------- |
| Supabase source      | `provider_cost_log` or adapter view stores provider attempts consumed through Lakehouse Federation. | Keep RLS/role access tight, minimize metadata, and configure backups/retention.          |
| Databricks learning  | Lakehouse Federation, Lakeflow, Delta, Unity Catalog, and optional MLflow training run offline. | Grant read-only source access, isolate catalogs by region, and protect workspace tokens. |
| Upstash cache        | `predictive:ranking:<region>:<model>` stores the runtime ranking artifact.                     | Store URLs/tokens in secret managers and monitor TTL, freshness, and key ownership.      |
| SDK runtime          | TypeScript/Python SDKs validate cache payloads and fail open to fallback.                      | Always pass deterministic fallback providers and track decision source.                  |
| Schemas              | `attempt.v1` and `ranking.v1` are the public data contracts.                                   | Publish breaking changes as new schema versions instead of mutating v1.                  |
| Repository guardrail | Sentry Project Check validates repository-specific Sentry code-guard wiring only.              | Keep `SENTRY_AUTH_TOKEN` in CI secrets and keep ownership rules configured.              |
| Supply chain         | Package Check validates TS lint/coverage/build/local demo/package dry-run plus Python pytest/ruff; CodeQL scans TS/Python and Codecov uploads TS coverage. | Keep checks green and review dependency updates before production deployment.            |

## Sentry code guard

The public OSS repository is connected to a private, repository-specific Sentry project for repository ownership, Seer-assisted review, and issue routing. The Sentry organization slug and project slug are intentionally not committed to this public repo.

This repo keeps Sentry as a repository guardrail, not runtime telemetry. It ships `scripts/sentry-project-check.mjs` and a scheduled `Sentry Project Check` workflow that verifies the configured project slug, active status, `other` platform, and Code Guard ownership rules. The workflow uses GitHub Actions secrets. Local runs may read ignored `.sentryclirc` defaults for org/project/url, but `SENTRY_AUTH_TOKEN` must stay in an environment variable or secret store. No Sentry SDK, DSN, tracing, or runtime telemetry is included in this package.

## Secret handling

- Keep Databricks personal access tokens, Supabase database credentials, and Upstash URLs in secret managers or deployment environment variables.
- Store Databricks cache URLs in secret scopes; do not hard-code them in bundle files, notebooks, or exported job definitions.
- Do not log Upstash URLs, Supabase passwords, Databricks tokens, provider API keys, or raw customer prompts.
- Keep `SENTRY_AUTH_TOKEN` in GitHub Actions secrets or an environment-backed secret manager. Do not put tokens in `.sentryclirc`.
- Keep non-token Sentry defaults such as org, project, and URL in GitHub Actions secrets or ignored local config when local checks need them.
- The real-stack smoke harness prints sanitized identifiers/counts only; treat its optional result file as operational evidence and review it before sharing.

## Operational guardrails

Before production deployment, run the relevant package checks from the adaptive-island project:

```bash
python -m pytest tests/python
python -m ruff check .
python -m pyright
cd client/typescript
npm run lint
npm run test:coverage
npm run build
node ../../examples/local-synthetic-demo/sdk-cache-demo.mjs
```

For Databricks deployment changes, also run:

```bash
cd examples/databricks-asset-bundle
databricks bundle validate --target prod \
  --var cache_url_secret_scope=adaptive-island-prod \
  --var cache_url_secret_key=upstash-cache-url
```

Before first production traffic in a region, run the real-stack smoke harness with Databricks, Supabase, and Upstash credentials from a secret manager:

```bash
python examples/real-stack-smoke/validate.py
```

The public Package Check workflow runs TypeScript lint/coverage/build/local demo/package dry-run, uploads TypeScript coverage to Codecov, and runs Python pytest/ruff. CodeQL scans JavaScript/TypeScript and Python. The Sentry Project Check workflow validates repository guardrail wiring.

## Incident response

For suspected key exposure, cache poisoning, source-log leakage, regional data drift, or abnormal provider routing:

1. Revoke or rotate the exposed provider, Supabase, Databricks, Upstash, or Sentry secret at the provider first.
2. Update the hosting, CI, Databricks secret scope, or Lakehouse Federation credential store.
3. Rerun package checks for code changes; rerun `databricks bundle validate` and the real-stack smoke harness for stack changes.
4. Review Supabase access logs, Databricks job and pipeline runs, Upstash key history/TTL, SDK decision-source metrics, and provider usage.
5. Delete or overwrite only smoke-scoped cache keys during investigation unless you are intentionally restoring a production key from a known-good export.
6. Open a private vulnerability report if the issue affects the public primitive, not only one private deployment.

## Data minimization

- Attempt logs should store provider, model, outcome, timing, cost, cancellation state, and bounded metadata needed for routing quality.
- Avoid storing raw prompts, generated media URLs, customer PII, or provider secrets in the attempt log.
- Normalize `model` before writing logs, and keep source logs region-local or assign region through reviewed Databricks bundle configuration before ranking.
- Set retention on raw Bronze/Silver tables according to your data-retention policy; request-path cache payloads should contain only provider IDs, scores, counts, and timestamps.
- Treat provider attempt logs, account ids, cache keys, Sentry project details, bucket/resource names, and smoke artifacts as private deployment data unless you have explicitly sanitized them.
