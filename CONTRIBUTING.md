# Contributing

Thanks for improving Adaptive Island.

Adaptive Island is a fail-open provider-ranking primitive extracted from BabySea's production routing pattern. Good contributions keep the runtime selector deterministic and safe when telemetry, cache, Databricks, or local stand-ins are unavailable.

## Contribution guidelines

- Keep all contributions under Apache 2.0. By submitting a PR you agree to license it under Apache 2.0.
- Preserve v1 schemas. If a change requires breaking `schemas/attempt.v1.json` or `schemas/ranking.v1.json`, publish a v2 alongside it.
- Preserve fail-open behavior. Any code path reachable from `Selector.rank(...)` or `Selector.pick(...)` must never depend on Databricks and must fall back on missing or malformed cache data.
- Keep runtime behavior aligned with the verified BabySea pattern: Supabase attempt logs, Databricks medallion ranking, Upstash cache export, deterministic fallback.
- Keep production scope narrow. Do not document or implement alternate production warehouses, queues, caches, online exploration systems, or promotion gates in this primitive.
- Keep the TypeScript and Python SDK behavior in sync when changing selector logic or payload contracts.
- Prefer focused changes. Avoid unrelated refactors in SDK code, schemas, bundle config, or deployment docs.

## Documentation standard

Adaptive Island docs are part of the public runtime contract. Keep them factual, operator-ready, and tied to behavior that exists in this repository.

- Start from the README contract: what the primitive is, what it is not, how to deploy it, how to validate it, and how to recover it.
- Use exact environment variable names, bundle variables, cache key shapes, schema names, commands, and file paths.
- Keep the stack boundary explicit: production docs use Databricks, Supabase, and Upstash. PostgreSQL and Redis appear only for Lakehouse Federation, Supabase-compatible endpoints, Upstash's Redis protocol, or local stand-ins.
- Document validation steps beside operational claims. If a guide says a path is production-ready, include the check, workflow, or smoke harness that proves it.
- Keep security guidance concrete: where secrets live, which values must not be logged, how keys are rotated, and what should never be posted publicly.
- Update `CHANGELOG.md` for user-visible docs, configuration, security, SDK behavior, schema, deployment, or operations changes.
- Avoid roadmap language in the public contract. New features stay out of README claims until implemented, documented, and validated for this stack.

When a change touches these areas, review the matching docs before opening a PR:

| Change area                    | Required docs to review                                                  |
| :----------------------------- | :----------------------------------------------------------------------- |
| SDK ranking or fail-open logic | README runtime flow, `docs/testing-failure-modes.md`, client READMEs     |
| Cache payload or key shape     | README cache section, `schemas/ranking.v1.json`, export job docs         |
| Attempt-log source contract    | README quick start, `docs/data-contract.md`, adapter and Supabase examples |
| Databricks bundle variables    | README production readiness, `docs/deploy-on-databricks.md`, bundle README |
| Scoring formula or window      | README architecture, `docs/scoring-config.md`, `docs/evaluation-metrics.md` |
| Sentry or CI workflows         | README production readiness, `SECURITY.md`, this contributing guide       |
| Security or secret handling    | README production readiness, `SECURITY.md`, real-stack smoke docs         |

## Development flow

### Python SDK

```bash
git clone https://github.com/babysea-community/adaptive-island
cd adaptive-island
pip install -e "./client/python[dev]"
ruff check client/python
pyright client/python
pytest tests/python
```

### TypeScript SDK

The published SDK targets Node.js 18+ at runtime. Local TypeScript SDK development uses the Vitest 4/Vite 8 toolchain and requires Node.js 20.19+ or 22.12+.

```bash
cd client/typescript
npm install
npm run lint
npm run test:coverage
npm run build
```

### Full local stack

```bash
cd examples/docker-compose-local
docker compose up
```

## Before opening a pull request

Run the checks that match your change:

```bash
ruff check client/python
pyright client/python
pytest tests/python
cd client/typescript && npm run lint && npm run test:coverage && npm run build
```

If you touched schemas, examples, bundle config, or docs, validate the relevant examples and generated artifacts before opening the PR.

## Issue triage

- `bug` - reproducible defect, with logs, a failing test, or a minimal reproduction.
- `proposal` - scoped design idea with the user problem, implementation sketch, and validation path.
- `good first issue` - small, well-scoped change that can be validated without production credentials.

## Conduct

See [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md). Be respectful, assume good faith, and keep discussion focused on the work and the people using it.

## Security-sensitive changes

Open security fixes privately through the process in [`SECURITY.md`](SECURITY.md). Do not include real Databricks tokens, Supabase passwords, Upstash URLs, provider credentials, Sentry tokens, customer data, private attempt logs, raw prompts, generated media URLs, production cache keys, or deployment details in public issues, pull requests, test fixtures, logs, or screenshots.
