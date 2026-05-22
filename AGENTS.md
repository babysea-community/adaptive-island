# adaptive-island

`adaptive-island` is an open-source implementation inspired by BabySea's documented Databricks routing system.
See [README.md](README.md) for the full story. This primitive is grounded in BabySea's internal production Databricks implementation.

This file mirrors the README so deploys, IDEs, and tooling that read `AGENTS.md` see the same context.

## Layout

| Path | Purpose |
|---|---|
| `pipelines/` | Lakeflow Spark Declarative Pipelines (Bronze \u2192 Silver \u2192 Gold on Delta Lake) |
| `training/` | Optional offline MLflow value-model training using the documented BabySea feature/target shape |
| `jobs/` | Lakeflow Jobs (export to Upstash cache, scheduled retrain) |
| `client/python/` | Python SDK |
| `client/typescript/` | TypeScript SDK |
| `schemas/` | JSON Schemas: `attempt.v1.json`, `ranking.v1.json` |
| `examples/databricks-asset-bundle/` | One-command Databricks deploy |
| `examples/real-stack-smoke/` | Disposable Databricks + Supabase + Upstash smoke validation |
| `examples/docker-compose-local/` | Local dev stack (no Databricks) |
| `examples/local-synthetic-demo/` | Credentials-free local ranking walkthrough and TypeScript SDK fail-open demo |
| `docs/` | Architecture, lifecycle, scoring, data-contract, testing, deployment, and adoption guides |

## Conventions

- **Apache 2.0** license. Apply the header in every source file.
- **Schemas are the contract.** Bronze ingest, SDKs, and cache payloads reference the JSON Schemas in `schemas/`.
- **Versioned events.** Every event carries a `schema_version` field. Never break v1 in place \u2014 publish v2 alongside.
- **Fail-open everywhere.** No code path that touches a customer request may depend on Databricks or raise on a missing/malformed cache value. Fall back to the caller-provided provider order.
- **BabySea-grounded only.** Do not add stochastic routing, propensity logging, IPS/SNIPS promotion gates, or request-path Databricks calls unless they are documented in BabySea's internal production implementation and implemented here.
- **Stack-specific public contract.** OSS code and docs must stay within Databricks + Supabase + Upstash unless a new stack is implemented and validated.
- **Supabase/Upstash terminology.** Public docs should say Supabase and Upstash. Use PostgreSQL only for Databricks Lakehouse Federation's PostgreSQL connector, Supabase-compatible endpoint details, or local developer stand-ins. Use Redis only for Upstash's Redis protocol/client library, URL scheme, or local developer stand-ins.
- **Grounding source.** Validate production-inspired claims against BabySea's internal production implementation; if it is not there and implemented here, do not claim it.
- **Python:** type-annotated, `ruff` + `pyright`, no implicit `Any`.
- **TypeScript:** strict mode, no `any`.
