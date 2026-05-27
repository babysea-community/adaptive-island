<div align="center">

<p>
  <img src="public/icon.png" width="120" alt="Adaptive Island icon" />
</p>

<h1>
  Adaptive Island
</h1>

<p>
  Cache-first provider selection engine for multi-provider inference workloads. Built with Databricks, Supabase, and Upstash.
</p>

<p>
  <strong>Every workload makes the next workload smarter</strong>
</p>

<br />

<strong>Project details</strong>

[![BabySea Blog](https://custom-icon-badges.demolab.com/badge/babysea-blog-0D9488?style=for-the-badge&logo=babysea&logoColor=white)](https://babysea.ai/blog/how-babysea-built-adaptive-provider-selection-on-databricks)
[![BabySea OSS Primitive](https://custom-icon-badges.demolab.com/badge/oss-primitive-EA580c?style=for-the-badge&logo=babysea&logoColor=white)](#babysea-oss-taxonomy)
[![BabySea OSS Status Production](https://custom-icon-badges.demolab.com/badge/oss_status-production-C026D3?style=for-the-badge&logo=babysea&logoColor=white)](#status)
[![License](https://custom-icon-badges.demolab.com/badge/license-apache_2.0-059669?style=for-the-badge&logo=apache&logoColor=white)](LICENSE)

<br/>

<strong>Checks</strong>

[![GitLabCI](https://img.shields.io/gitlab/pipeline-status/babysea/adaptive-island?branch=main&style=for-the-badge&label=gitlabci&logo=gitlab&logoColor=white&color=FC6D26)](https://gitlab.com/babysea/adaptive-island/-/commits/main)
[![CircleCI](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fcircleci.com%2Fapi%2Fv1.1%2Fproject%2Fcircleci%2F2uTLcwc4naeNuKDP41es88%2F2J2hRNFoYs3zzDnuULUTR3%2Ftree%2Fmain%3Flimit%3D1&query=%24%5B0%5D.status&style=for-the-badge&logo=circleci&logoColor=white&label=circleci&color=003740)](https://dl.circleci.com/status-badge/redirect/circleci/2uTLcwc4naeNuKDP41es88/2J2hRNFoYs3zzDnuULUTR3/tree/main)
[![Codecov](https://img.shields.io/codecov/c/github/babysea-community/adaptive-island?style=for-the-badge&label=codecov&logo=codecov&logoColor=white&color=FF0077&token=agMk6Yntq6)](https://codecov.io/github/babysea-community/adaptive-island)
[![Sentry](https://img.shields.io/github/actions/workflow/status/babysea-community/adaptive-island/sentry-check.yml?style=for-the-badge&label=sentry&logo=sentry&logoColor=white&color=181225)](https://github.com/babysea-community/adaptive-island/actions/workflows/sentry-check.yml)
[![CodeQL](https://img.shields.io/github/actions/workflow/status/babysea-community/adaptive-island/codeql.yml?style=for-the-badge&label=codeql&logo=github&logoColor=white)](https://github.com/babysea-community/adaptive-island/actions/workflows/codeql.yml)
[![Package](https://img.shields.io/github/actions/workflow/status/babysea-community/adaptive-island/publish-check.yml?style=for-the-badge&label=package&logo=npm&logoColor=white)](https://github.com/babysea-community/adaptive-island/actions/workflows/publish-check.yml)

<br/>

<strong>Built with</strong>

[![Databricks](https://img.shields.io/badge/databricks-EE3D2C?style=for-the-badge&logo=databricks&logoColor=white)](https://www.databricks.com)
[![Supabase](https://img.shields.io/badge/supabase-249361?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)
[![Upstash](https://img.shields.io/badge/upstash-00E9A3?style=for-the-badge&logo=upstash&logoColor=white)](https://upstash.com)
[![Apache Spark](https://img.shields.io/badge/apache_spark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)](https://spark.apache.org)
[![Delta Lake](https://custom-icon-badges.demolab.com/badge/delta_lake-00ADD4?style=for-the-badge&logo=server&logoColor=white)](https://delta.io)
[![MLflow](https://img.shields.io/badge/mlflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white)](https://mlflow.org)

<br/>

<img src="public/card.png" alt="Adaptive Island card" />

</div>

<br/>

## BabySea OSS taxonomy

BabySea open source projects are organized into three categories:

[![BabySea OSS SDK](https://custom-icon-badges.demolab.com/badge/oss-sdk-7C3AED?style=for-the-badge&logo=babysea&logoColor=white)](#babysea-oss-taxonomy)
[![BabySea OSS Primitive](https://custom-icon-badges.demolab.com/badge/oss-primitive-EA580c?style=for-the-badge&logo=babysea&logoColor=white)](#babysea-oss-taxonomy)
[![BabySea OSS Starter](https://custom-icon-badges.demolab.com/badge/oss-starter-2563EB?style=for-the-badge&logo=babysea&logoColor=white)](#babysea-oss-taxonomy)

| Category      | Description                                                                                                                                       |
| :------------ | :------------------------------------------------------------------------------------------------------------------------------------------------ |
| **SDK**       | Typed developer entry points for creating, tracking, and managing BabySea workloads from application code.                                        |
| **Primitive** | Reusable infrastructure boundaries extracted from BabySea's execution control plane. Each primitive focuses on one system concern.                |
| **Starter**   | Deployable reference applications that combine product UI, auth, storage, and BabySea execution patterns. Some starters may also include billing. |

## Status

BabySea OSS projects are published into three status levels:

[![BabySea OSS Status Working](https://custom-icon-badges.demolab.com/badge/oss_status-working-DB2777?style=for-the-badge&logo=babysea&logoColor=white)](#status)
[![BabySea OSS Status Production](https://custom-icon-badges.demolab.com/badge/oss_status-production-C026D3?style=for-the-badge&logo=babysea&logoColor=white)](#status)
[![BabySea OSS Status Alpha](https://custom-icon-badges.demolab.com/badge/oss_status-alpha-D97706?style=for-the-badge&logo=babysea&logoColor=white)](#status)

| Status         | Description                                                                                                                                                                          |
| :------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Working**    | Fully implemented and deployable. All documented capabilities function as described. Suitable for personal and small-team use. No breaking-change guarantees between versions.       |
| **Production** | Working plus a hardened public runtime contract. Validated against a stated infrastructure stack with deterministic behavior, explicit failure modes, and a documented upgrade path. |
| **Alpha**      | Early-stage implementation. Core structure exists but some capabilities may be incomplete, undocumented, or subject to breaking changes. Not recommended for production deployments. |

`adaptive-island` is a **production** OSS primitive. It packages the BabySea-style provider-ranking loop for community deployments that use Supabase as the operational source, Databricks as the offline learning path, and Upstash as the request-path cache. See [`CHANGELOG.md`](CHANGELOG.md).

## Table of contents

1. [Overview](#1-overview)
    - [What this is](#what-this-is)
    - [Short version](#short-version)
    - [Production lineage](#production-lineage)
    - [Grounding rule](#grounding-rule)
    - [Adoption path](#adoption-path)
2. [Stack contract](#2-stack-contract)
3. [Terminology](#3-terminology)
4. [Boundaries](#4-boundaries)
5. [Architecture](#5-architecture)
6. [Quick start](#6-quick-start)
    - [Create the Supabase source table](#create-the-supabase-source-table)
    - [Deploy on Databricks](#deploy-on-databricks)
    - [Use the TypeScript SDK](#use-the-typescript-sdk)
    - [Use the Python SDK](#use-the-python-sdk)
    - [Validate against real services](#validate-against-real-services)
7. [Core capabilities](#7-core-capabilities)
    - [Why it's different](#why-its-different)
    - [The source event you log](#the-source-event-you-log)
    - [The cache value you read](#the-cache-value-you-read)
    - [Runtime selection flow](#runtime-selection-flow)
    - [Fail-open by design](#fail-open-by-design)
8. [Production readiness](#8-production-readiness)
    - [Enterprise posture](#enterprise-posture)
    - [Configuration surface](#configuration-surface)
    - [Production deployment](#production-deployment)
    - [Release gates](#release-gates)
    - [Production checklist](#production-checklist)
    - [Monitoring](#monitoring)
    - [Backup and disaster recovery](#backup-and-disaster-recovery)
    - [Secret rotation](#secret-rotation)
    - [Troubleshooting](#troubleshooting)
9. [Version surface](#9-version-surface)
10. [Community](#10-community)
    - [Who's using it](#whos-using-it)
    - [Related projects](#related-projects)
    - [Contributing](#contributing)
11. [License](#11-license)

---

## 1. Overview

### What this is

`adaptive-island` is a cache-first provider selection primitive for multi-provider inference workloads. Your runtime logs provider attempts to Supabase, Databricks computes provider rankings offline, Upstash serves the latest ranking, and the SDK turns that cache value into an ordered provider list.

The package keeps Databricks off the request path. Runtime code reads one cache key, validates the payload, filters it against allowed providers, and falls back to a deterministic order whenever the cache cannot be trusted.

### Short version

Provider performance changes constantly. `adaptive-island` lets every workload improve later routing while the current request remains simple: read Upstash, validate, rank, and fail open.

### Production lineage

The architecture mirrors BabySea's production provider-ranking loop behind `generation_provider_order: "fastest"`. The public repo uses neutral names and community-owned infrastructure, but the shape stays the same: Supabase attempt logs, Databricks Bronze/Silver/Gold computation, Gold export to Upstash, and SDK-side validation before dispatch.

### Grounding rule

Public OSS behavior is limited to the Databricks -> Upstash -> Supabase ranking loop implemented here. Supabase attempt logs, Databricks ranking jobs, Upstash cache export, cache-first SDK validation, and deterministic fail-open behavior are in scope. Request-path Databricks serving, online exploration, queues, hosted APIs, provider SDK calls, and private BabySea catalogs are out of scope.

### Adoption path

If you operate a multi-provider inference stack, log one provider-attempt row per dispatch attempt, deploy the Databricks bundle, export rankings to Upstash, and call the SDK from your runtime with an explicit fallback provider order. You bring Databricks, Supabase, Upstash, and your provider clients. The island handles cached ranking.

## 2. Stack contract

| Layer                  | Required stack                                                         | Runtime responsibility                                                                                      |
| :--------------------- | :--------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------- |
| Operational source     | Supabase `provider_cost_log`                                           | Store one row per provider attempt with outcome, timestamps, cost estimate, region, model, and attempt order. |
| Learning path          | Databricks Lakehouse Federation, Lakeflow, Delta Lake, Unity Catalog   | Read Supabase into Bronze/Silver/Gold tables and compute one ranking artifact per `(model, region)`.        |
| Offline model training | Databricks MLflow                                                      | Train and evaluate ranking/value models from Silver attempts without becoming a request-path dependency.     |
| Serving cache          | Upstash                                                                | Store `predictive:ranking:<region>:<model>` payloads with a TTL longer than the export cadence.             |
| Application runtime    | TypeScript or Python SDK                                               | Read one cache key, validate the payload, filter providers, and fail open to the caller fallback.            |

No other data platform, queue, search index, online-exploration service, or hosted inference gateway is part of this version contract.

Production-grade means the shipped runtime contract is deterministic and ready for the stated stack:

- Supabase is the operational source of truth for provider attempts.
- Databricks is the learning path, not the request path.
- Upstash is the serving cache for the Gold ranking payload.
- Region isolation is explicit; use separate regional resources for production `us`, `eu`, `apac`, or your own labels.
- Secrets live in Supabase, Databricks, Upstash, or deployment secret managers and never appear in ranking payloads.
- Breaking data-contract changes require new schema versions instead of mutating `attempt.v1` or `ranking.v1` in place.

## 3. Terminology

| Term                    | Meaning in this package                                                                                                           |
| :---------------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| Provider attempt        | One submitted call to an inference provider. A single generation can produce multiple attempts when failover happens.              |
| Wasted attempt          | An attempt with `failed`, `discarded`, or `cancelled` outcome. It may still carry provider cost, so it lowers ranking score.       |
| Databricks Gold ranking | The deterministic Databricks output exported to Upstash. It is the default production routing artifact.                            |
| Upstash ranking key     | A cache entry named `predictive:ranking:<region>:<model>` containing the Gold ranking payload.                                     |
| Fallback order          | The explicit provider list your runtime passes to the SDK. It is returned whenever cache validation or connectivity fails.         |
| Value model             | Optional MLflow model trained from Silver attempts for offline analysis and promotion review. It is never required on the request path. |

## 4. Boundaries

- Not a provider router, hosted inference gateway, or provider SDK wrapper.
- Not a request-path Databricks dependency.
- Not a stochastic online-exploration or propensity-logging system.
- Not an off-policy promotion gate or managed ML platform.
- Not an alternate warehouse/cache abstraction; this version is Databricks + Supabase + Upstash.
- Not BabySea's private routing catalog, provider credentials, or production telemetry.
- Not production Docker Compose; local demos are developer smoke stacks only.

## 5. Architecture

```text
Supabase provider_cost_log
        |  Lakehouse Federation
        v
Databricks Bronze provider attempts
        v
Databricks Silver typed attempts
        v
Databricks Gold provider ranking by model and region
        |  Lakeflow export job
        v
Upstash predictive:ranking:<region>:<model>
        |
        v
SDK/API rank() -> provider failover loop
```

The default ranking is intentionally explainable:

```text
score = success_rate     * 1.0
      - wasted_rate      * 0.5
      - latency_p95_norm * 0.3
```

The default window is 24 hours, and the default cache TTL is 48 hours. See [`docs/scoring-config.md`](docs/scoring-config.md) for scoring configuration and [`docs/evaluation-metrics.md`](docs/evaluation-metrics.md) for synthetic evaluation guidance.

## 6. Quick start

### Create the Supabase source table

Run the example table in your Supabase SQL editor, or adapt your existing log with a view:

- New source table: [`examples/supabase-provider-cost-log/provider_cost_log.sql`](examples/supabase-provider-cost-log/provider_cost_log.sql)
- Existing log adapter: [`examples/adopt-existing-log/`](examples/adopt-existing-log)

The required operational shape is documented in [`schemas/attempt.v1.json`](schemas/attempt.v1.json). Databricks source tables or adapter views must expose `id` for Bronze lineage and de-duplication. For required fields, optional fields, outcomes, timestamp semantics, and region/model normalization rules, see [`docs/data-contract.md`](docs/data-contract.md).

### Deploy on Databricks

```bash
git clone https://github.com/babysea-community/adaptive-island
cd adaptive-island/examples/databricks-asset-bundle

export DATABRICKS_HOST="https://<your-workspace>.cloud.databricks.com"
export DATABRICKS_TOKEN="<your-token>"

# Store the Upstash URL in a Databricks secret scope first.
# Pass only the non-secret scope/key names to the bundle.
databricks bundle validate --target prod \
  --var catalog=adaptive_island_us \
  --var region=us \
  --var federation_connection=<your_federated_catalog> \
  --var cache_url_secret_scope=adaptive-island-prod \
  --var cache_url_secret_key=upstash-cache-url

databricks bundle deploy --target prod \
  --var catalog=adaptive_island_us \
  --var region=us \
  --var federation_connection=<your_federated_catalog> \
  --var cache_url_secret_scope=adaptive-island-prod \
  --var cache_url_secret_key=upstash-cache-url
```

See [`docs/deploy-on-databricks.md`](docs/deploy-on-databricks.md) for the full sequence and [`docs/routing-lifecycle.md`](docs/routing-lifecycle.md) for the lifecycle from attempt logs to cache reads.

### Use the TypeScript SDK

Install the SDK from source until the npm package is published:

```bash
cd client/typescript
npm install
npm run build

cd /path/to/your-app
npm install /path/to/adaptive-island/client/typescript
```

```typescript
import { Selector, resolveAdaptiveRoutingEnabled } from 'adaptive-island';

const selector = new Selector({
  cache: {
    async get(key) {
      return await yourUpstashClient.get(key);
    },
  },
  maxCacheAgeSeconds: 48 * 60 * 60,
  adaptiveRoutingEnabled: resolveAdaptiveRoutingEnabled(
    process.env.ADAPTIVE_ROUTING_ENABLED,
  ),
});

const providers = await selector.rank({
  modelId: 'black-forest-labs/flux-schnell',
  region: 'us',
  fallback: ['replicate', 'fal', 'cloudflare'],
});
```

Try `providers[0]` first, then fail over through the rest in order.

### Use the Python SDK

Install the SDK from source until the PyPI package is published:

```bash
cd client/python
pip install -e .
```

```python
from adaptive_island import Selector

selector = Selector(
    cache_url="redis://default:<token>@<host>:6379",
    max_cache_age_seconds=48 * 60 * 60,
)

providers = selector.rank(
    model_id="black-forest-labs/flux-schnell",
    region="us",
    fallback=["replicate", "fal", "cloudflare"],
)
```

If adaptive routing is disabled, cache data is unavailable, or payload validation fails, `rank()` returns the caller-provided fallback after removing duplicate providers.

### Validate against real services

Run the reusable smoke harness from a temporary checkout or CI job after setting Databricks, Supabase, and Upstash credentials as environment variables. It creates a disposable Supabase schema, writes a short-lived Upstash ranking key, verifies Databricks API access, and runs the SDK against the cache without printing secrets.

See [`examples/real-stack-smoke/`](examples/real-stack-smoke) for the exact environment variables and cleanup behavior. For a credentials-free walkthrough, see [`examples/local-synthetic-demo/`](examples/local-synthetic-demo).

## 7. Core capabilities

### Why it's different

Provider ranking needs to learn, but the learning system should not be able to block a request. `adaptive-island` separates the slow path from the hot path: Supabase logs attempts, Databricks learns offline, Upstash serves the compact result, and the SDK fails open.

| Problem                                  | How `adaptive-island` solves it                                                                                          |
| :--------------------------------------- | :----------------------------------------------------------------------------------------------------------------------- |
| **Provider rankings drift.**             | Recent attempt logs feed a Bronze/Silver/Gold pipeline that recomputes rankings from success, waste, and latency.        |
| **Learning systems are risky live.**     | Databricks never sits on the request path; runtime reads one Upstash key and falls back on any issue.                    |
| **Routing needs regional isolation.**    | Rankings are exported per `(model, region)`, with isolated regional resources recommended for production.                |
| **Malformed cache payloads are unsafe.** | SDKs validate shape, finite scores, timestamps, provider allowlists, TTL, and optional max-age before returning a ranking. |
| **Operators need explanations.**         | The default score is explicit and documented instead of hidden behind a black-box router.                                |

### The source event you log

```jsonc
{
  "schema_version": "attempt.v1",
  "generation_id": "gen_01JK0...",
  "account_id": "acct_123",
  "model": "black-forest-labs/flux-schnell",
  "provider": "replicate",
  "provider_model_id": "black-forest-labs/flux-schnell",
  "prediction_id": "pred_abc",
  "estimated_cost": 0.0023,
  "outcome": "used",
  "attempt_order": 1,
  "was_cancelled": false,
  "cancel_available": true,
  "submitted_at": "2026-04-29T14:22:08Z",
  "resolved_at": "2026-04-29T14:22:11Z",
  "error_message": null,
  "metadata": {}
}
```

### The cache value you read

Key:

```text
predictive:ranking:us:black-forest-labs/flux-schnell
```

Value:

```json
{
  "providers_ranked": ["replicate", "fal", "cloudflare"],
  "scores": {
    "replicate": 0.81,
    "fal": 0.42,
    "cloudflare": -0.05
  },
  "attempts_total": 137,
  "window_hours": 24,
  "computed_at": "2026-04-29T02:31:15Z"
}
```

This is the runtime contract. The SDK rejects missing providers, non-finite scores, invalid timestamps, stale payloads, unsupported providers, and malformed JSON.

### Runtime selection flow

1. Normalize the requested `modelId` and `region`.
2. Build the Upstash key `predictive:ranking:<region>:<model>`.
3. Return fallback immediately when adaptive routing is disabled.
4. Read and parse the cached ranking payload.
5. Validate schema, scores, `computed_at`, and optional max age.
6. Remove providers that are not in the caller fallback/allowlist.
7. Return ranked providers that also appear in the fallback/allowlist; if none remain, return the fallback order.

### Fail-open by design

| Failure                                             | Behavior                                                   |
| :-------------------------------------------------- | :--------------------------------------------------------- |
| Databricks paused or export job fails               | Upstash keeps serving the last ranking until TTL expires.  |
| Upstash unavailable                                 | SDK returns the caller-provided fallback order.            |
| Ranking missing, malformed, TTL-expired, or too old | SDK returns the caller-provided fallback order.            |
| Adaptive routing disabled                           | SDK skips cache reads and returns fallback directly.       |
| Provider down                                       | Caller fails over through the ordered provider list.       |

Databricks improves later requests, but it is not required to serve the current one. See [`docs/testing-failure-modes.md`](docs/testing-failure-modes.md) for failure modes that should remain covered in tests.

## 8. Production readiness

`adaptive-island` is production-grade for the stated stack, not a managed BabySea service. Treat this section as the operating contract for a self-hosted provider-ranking loop: every claim should map to implemented code, a schema, a bundle variable, or a validation command.

### Enterprise posture

| Area          | Control in adaptive-island                                                                                       | How to verify                                                                                      |
| :------------ | :--------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------- |
| Source data   | Supabase `provider_cost_log` or an adapter view is the operational source for one row per provider attempt.       | Apply `examples/supabase-provider-cost-log/provider_cost_log.sql` or validate your adapter view.   |
| Learning path | Databricks Lakehouse Federation and Lakeflow compute Bronze, Silver, and Gold tables on Delta Lake.              | Run `databricks bundle validate`, deploy the bundle, then inspect `<catalog>.medallion` tables.    |
| Serving path  | Upstash stores `predictive:ranking:<region>:<model>` payloads exported from Gold.                                | Run the export job and read one smoke key without printing the cache URL.                          |
| Runtime       | TypeScript and Python SDKs read one cache key, validate required `ranking.v1` runtime fields, filter to the caller fallback, and fail open. | Run SDK unit tests and the local synthetic demo.                                                   |
| Isolation     | Region is explicit in the Databricks bundle config, Bronze projection, Upstash key, and deployment variables; source logs should remain region-local. | Deploy separate resources for `us`, `eu`, `apac`, or your own labels and confirm region-local keys. |
| Observability | Sentry is a repository code guard only; runtime packages include no Sentry SDK, DSN, tracing, or telemetry.       | Keep the Sentry Project Check workflow green and inspect package dependencies before release.      |
| Supply chain  | Package Check validates TS lint/coverage/build/local demo/package dry-run plus Python pytest/ruff; CodeQL scans TS/Python and Codecov uploads TypeScript coverage. | Keep GitHub Actions green before publishing or promoting a fork.                                   |

### Configuration surface

| Setting or variable                         | Required    | Scope             | Notes                                                                                          |
| :------------------------------------------ | :---------- | :---------------- | :--------------------------------------------------------------------------------------------- |
| `catalog`                                   | Yes         | Databricks bundle | Writable Unity Catalog catalog for `medallion` and optional `ml` schemas.                      |
| `region`                                    | Yes         | Databricks bundle | Region label written into Gold rows and Upstash keys. Defaults to `us`.                        |
| `federation_connection`                     | Yes         | Databricks bundle | Lakehouse Federation catalog for the Supabase source.                                          |
| `source_schema`                             | No          | Databricks bundle | Source schema inside the federated catalog. Defaults to `public`.                              |
| `source_table`                              | No          | Databricks bundle | Source table or adapter view matching the `provider_cost_log` contract.                        |
| `cache_url_secret_scope`                    | Yes         | Databricks bundle | Secret scope containing the Upstash URL.                                                       |
| `cache_url_secret_key`                      | Yes         | Databricks bundle | Secret key containing the Upstash URL.                                                         |
| `cache_tls`                                 | No          | Databricks bundle | `auto`, `true`, or `false`; defaults to `auto` for Upstash-friendly TLS behavior.               |
| `cache_ttl_seconds`                         | No          | Databricks bundle | Cache TTL. Defaults to `172800` seconds, or 48 hours.                                          |
| `ranking_window_hours`                      | No          | Databricks bundle | Gold rolling window. Defaults to `24`.                                                         |
| `min_train_rows`                            | No          | Databricks bundle | Optional MLflow training skip threshold. Defaults to `100`.                                    |
| `ADAPTIVE_ISLAND_CACHE_URL`                 | Conditional | SDK/local/smoke   | Upstash URL for Python SDK, local export runs, and smoke validation. Store as a secret.         |
| `ADAPTIVE_ROUTING_ENABLED`                  | No          | SDK runtime       | `false`, `0`, `off`, or `disabled` skips cache reads and returns fallback.                      |
| `DATABRICKS_HOST`, `DATABRICKS_TOKEN`       | Conditional | CLI/smoke         | Required for Databricks CLI and real-stack smoke validation.                                   |
| `SUPABASE_PROJECT_ID`, `SUPABASE_DB_PASSWORD` | Conditional | Smoke             | Required by the real-stack smoke harness unless `SUPABASE_DB_DSN` is set.                      |
| `SUPABASE_DB_DSN`                           | No          | Smoke             | Optional full Supabase database DSN for smoke validation.                                      |
| `SUPABASE_DB_HOST`, `SUPABASE_DB_PORT`, `SUPABASE_DB_USER`, `SUPABASE_DB_NAME`, `SUPABASE_DB_SSLMODE` | No | Smoke | Optional Supabase connection overrides, including Supavisor pooler settings.                   |
| `ADAPTIVE_ISLAND_REGION`, `ADAPTIVE_ISLAND_MODEL` | No    | Smoke             | Optional smoke key labels. Defaults avoid production ranking keys.                             |
| `ADAPTIVE_ISLAND_SMOKE_KEEP`, `ADAPTIVE_ISLAND_SMOKE_RESULT`, `ADAPTIVE_ISLAND_SMOKE_ALLOW_OVERWRITE` | No | Smoke | Optional smoke cleanup/result controls. Use overwrite only for intentional key-restore tests.  |
| `SENTRY_ORG`, `SENTRY_PROJECT`, `SENTRY_AUTH_TOKEN` | No   | CI                | Optional repository code-guard wiring. Not runtime telemetry.                                  |

### Production deployment

Use separate Supabase, Databricks, and Upstash resources for each production data region. Keep raw attempt logs region-local unless your compliance program explicitly allows cross-region movement.

For a new deployment, create or adapt the Supabase source table, configure Lakehouse Federation, store the Upstash URL in a Databricks secret scope, validate the Databricks Asset Bundle, deploy it, run the export job once, then enable cache-backed routing in application code. See [`docs/deploy-on-databricks.md`](docs/deploy-on-databricks.md) for the full sequence.

For an existing event log, create a reviewed adapter view instead of copying historical data. See [`docs/adopt-on-existing-event-log.md`](docs/adopt-on-existing-event-log.md) and [`examples/adopt-existing-log/`](examples/adopt-existing-log).

Local Docker Compose and local Redis are developer smoke stand-ins only. Production/community deployments use Supabase, Databricks, and Upstash.

### Release gates

| Gate                                            | Purpose                                                            | Required before production |
| :---------------------------------------------- | :----------------------------------------------------------------- | :------------------------- |
| `python -m pytest tests/python`                 | Verifies Python SDK fail-open and cache-hit behavior.              | Yes                        |
| `python -m ruff check .`                        | Enforces Python lint rules for SDK, tests, jobs, and examples.     | Yes                        |
| `python -m pyright`                             | Type-checks the scoped Python SDK configuration locally.           | Yes for SDK changes        |
| `npm run lint` in `client/typescript`           | Type-checks the TypeScript SDK.                                    | Yes for SDK changes        |
| `npm run test:coverage` in `client/typescript`  | Verifies TypeScript SDK fail-open and ranked-subset behavior and emits Codecov coverage. | Yes for SDK changes        |
| `npm run build` in `client/typescript`          | Verifies package build output and declarations.                    | Yes for SDK changes        |
| `node examples/local-synthetic-demo/sdk-cache-demo.mjs` | Proves local cache-hit, malformed-cache fallback, and missing-key fallback. | Yes for SDK behavior changes |
| `databricks bundle validate --target prod`      | Verifies Databricks Asset Bundle shape and variables.              | Yes for deployment changes |
| `python examples/real-stack-smoke/validate.py`  | Validates Databricks, Supabase, Upstash, and SDK integration with real services. | Yes before first production region |
| CodeQL, Package Check, Sentry Check             | Verifies CI security, package, and repository guardrail health.    | Yes when enabled in GitHub |

### Production checklist

- [ ] Supabase source table or adapter view exposes the required `provider_cost_log` projection, including database-generated `id`.
- [ ] Attempt logs contain no provider credentials, raw prompts, raw request bodies, unnecessary PII, or generated media URLs.
- [ ] Databricks has read-only access to the source table or adapter view.
- [ ] One isolated Databricks workspace/catalog, Supabase source, and Upstash cache exists per data region.
- [ ] Upstash URL is stored in a Databricks secret scope, not bundle variables, notebooks, job parameters, or logs.
- [ ] Cache TTL is longer than the export cadence; default is 48 hours for a daily export.
- [ ] Pipeline and export job have run at least once before application traffic relies on cached rankings.
- [ ] Every SDK call passes a deterministic fallback provider list.
- [ ] Application runtime keeps Databricks off the request path and uses only Upstash plus fallback.
- [ ] Breaking data-contract changes are published as new schema versions.
- [ ] Package Check and CodeQL are green before publishing or promoting a fork; Sentry Project Check is green when repository guardrail wiring is configured.

### Monitoring

Monitor the learning path and the request path separately:

- Supabase attempt-log row volume, terminal outcome mix, and rejected/invalid rows.
- Databricks pipeline freshness, failed expectations, Gold row counts, and export job status.
- Upstash key freshness, TTL, cache hit rate, fallback rate, malformed payload count, and stale ranking count.
- SDK decision source: `cached-ranking`, `fallback`, or `adaptive-disabled`.
- Provider-level success rate, p95 latency, wasted attempt rate, and mean attempts per generation.

Sentry in this repository is only a code-guard/project-wiring check. It does not collect runtime telemetry from the SDKs, pipelines, or jobs.

### Backup and disaster recovery

- Enable Supabase backups or point-in-time recovery according to the retention requirements for attempt logs.
- Treat Databricks Bronze and Silver tables as recoverable from Supabase; verify replay by rebuilding a non-production catalog.
- Keep Gold tables and Upstash keys disposable. They should be rebuildable from source attempts and the current scoring config.
- Store Databricks bundle variables, secret-scope names, source-table names, and regional resource owners in a private runbook.
- Test recovery by deleting a smoke cache key and confirming SDK fallback, then rerunning the export job to repopulate it.

### Secret rotation

| Secret family                         | Rotate when                                                        | Minimum follow-up                                                                  |
| :------------------------------------ | :----------------------------------------------------------------- | :--------------------------------------------------------------------------------- |
| Databricks tokens                     | Maintainer access changes, suspected exposure, or scheduled audit. | Update CLI/CI secrets, run `databricks bundle validate`, and verify workspace auth. |
| Supabase database credentials         | Database owner changes, suspected exposure, or connection policy changes. | Update Lakehouse Federation/CI secrets and rerun the real-stack smoke harness.      |
| Upstash URL/token                     | Cache operator changes, suspected exposure, or cache project migration. | Update Databricks secret scope and rerun the export job plus SDK cache-read smoke.  |
| `SENTRY_AUTH_TOKEN`                   | CI maintainer changes, source project changes, or exposure.        | Run `node scripts/sentry-project-check.mjs` or the Sentry Project Check workflow.   |

Rotate immediately after any secret appears in a terminal transcript, chat, screenshot, issue, pull request, exported job definition, or smoke artifact.

### Troubleshooting

| Symptom                                | Fix                                                                                                  |
| :------------------------------------- | :--------------------------------------------------------------------------------------------------- |
| SDK always returns fallback            | Check `ADAPTIVE_ROUTING_ENABLED`, Upstash connectivity, key shape, payload validity, and max age.    |
| SDK returns fewer providers than fallback | This is expected when cache ranking overlaps fallback; current version serves the ranked subset only.          |
| SDK throws before returning providers  | Ensure `fallback` contains at least one provider and cache age/socket timeout values are positive.   |
| Databricks pipeline has no Bronze rows | Confirm Lakehouse Federation catalog, `source_schema`, `source_table`, and source `id` projection.   |
| Gold has no ranking rows               | Confirm terminal outcomes are `used`, `failed`, `discarded`, or `cancelled` and timestamps are valid. |
| Export job writes no keys              | Confirm Gold rows exist and the Upstash URL secret scope/key resolve inside the job.                 |
| Real-stack smoke cannot reach Supabase | Use Supavisor pooler overrides documented in `examples/real-stack-smoke/`.                           |
| Sentry Project Check fails             | Confirm `SENTRY_ORG`, `SENTRY_PROJECT`, `SENTRY_AUTH_TOKEN`, platform, and ownership rules.          |

## 9. Version surface

Current version surface:

- [x] Supabase `provider_cost_log` source contract
- [x] Databricks Bronze/Silver/Gold Lakeflow pipeline on Delta Lake
- [x] Gold-to-Upstash export job
- [x] Cache-first TypeScript and Python SDKs
- [x] Adaptive-routing runtime toggle that can skip cache reads
- [x] Optional offline MLflow value-model training entry point
- [x] Databricks Asset Bundle deploy path
- [x] Real-stack smoke harness for Databricks, Supabase, and Upstash

New features stay out of the public contract until they are implemented, documented, and validated against this stack.

## 10. Community

### Who's using it

- **[BabySea](https://babysea.ai)**: the execution control plane for generative media. BabySea's production provider-ranking loop is the source pattern behind this cache-first Databricks + Supabase + Upstash primitive.

*Using `adaptive-island`? Open a PR to add yourself.*

### Related projects

- [BabySea SDK](https://github.com/babysea-community/babysea): Production TypeScript SDK for the BabySea execution control plane for generative media.
- [Ledger Fortress](https://github.com/babysea-community/ledger-fortress): Atomic credit settlement engine for async inference workloads.
- [Rosetta Bridge](https://github.com/babysea-community/rosetta-bridge): Request normalization engine for multi-provider inference workloads.

### Contributing

We welcome PRs, issues, and design discussion. See [`CONTRIBUTING.md`](CONTRIBUTING.md), [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md), and [`SECURITY.md`](SECURITY.md).

## 11. License

[Apache License 2.0](LICENSE). Use it, fork it, ship it. Just keep the notice.
