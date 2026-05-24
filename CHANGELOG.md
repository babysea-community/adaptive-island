# Changelog

All notable changes will be documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## [0.3.6] - 2026-05-24

### Changed

- Reordered Python CI steps in GitHub Actions (`publish-check.yml`) and CircleCI (`config.yml`) to run `ruff check` before `pytest`, matching the lint-before-test convention followed by the TypeScript jobs.

## [0.3.5] - 2026-05-23

### Fixed

- Hardened Upstash cache URL host checks to parse hostnames before enabling trusted-host TLS behavior, resolving CodeQL URL substring alerts.
- Replaced Sentry URL trailing-slash regex normalization with a bounded string scan to avoid CodeQL ReDoS noise.

## [0.3.4] - 2026-05-23

### Changed

- Expanded Dependabot version updates to check TypeScript dependencies daily, Python dependencies weekly, and GitHub Actions weekly.

## [0.3.3] - 2026-05-22

### Changed

- Adjusted advisory Snyk Code and IaC scans to avoid GitHub failure annotations while preserving SARIF upload, IaC reporting, and the enforced Open Source test.
- Constrained GitHub Actions Codecov uploads to the explicit TypeScript LCOV report to avoid irrelevant uploader search warnings.

## [0.3.2] - 2026-05-22

### Added

- Added a Snyk Security workflow for Snyk Code SARIF upload, Open Source scanning and monitoring, and IaC reporting with `SNYK_TOKEN`.

### Changed

- Replaced the native CircleCI README badge with a Shields.io badge that matches the project badge style.
- Replaced the static Snyk README badge with a realtime Snyk Security workflow status badge.

## [0.3.1] - 2026-05-22

### Added

- Added a CircleCI native badge.

## [0.3.0] - 2026-05-22

### Added

- Added a CircleCI package-check workflow for adaptive-island TypeScript lint/coverage/build/package validation, Python pytest/ruff validation, and trusted `main` Codecov CLI upload when `CODECOV_TOKEN` is configured in CircleCI.

## [0.2.9] - 2026-05-22

### Added

- Added repository `codecov.yml` with GitHub Actions and CircleCI provider recognition, CI-gated Codecov status, pull request comment configuration, and TypeScript client path fixes.

### Changed

- Updated trusted Package Check Codecov uploads to pass `CODECOV_TOKEN` through the action environment and fail CI when coverage upload fails.

## [0.2.8] - 2026-05-22

### Changed

- Updated primitive deploy automation to sync GitHub repository description, homepage, and topics from TypeScript package metadata.

## [0.2.7] - 2026-05-22

### Changed

- Standardized contributing and code-of-conduct guidance with the shared BabySea OSS documentation standard.
- Upgraded Package Check, Sentry Project Check, and CodeQL workflows to Node 24-compatible GitHub Action majors, including Codecov upload via `codecov/codecov-action@v6`.

### Fixed

- Made the Sentry project check skip cleanly when all Sentry repository secrets are absent, fail partial secret configuration, and treat permission-limited Sentry API responses as advisory when explicitly enabled by CI.

## [0.2.6] - 2026-05-22

### Added

- Added TypeScript coverage generation and Package Check Codecov upload using `client/typescript/coverage/lcov.info`.

## [0.2.5] - 2026-05-21

### Changed

- Update badge icon.

## [0.2.4] - 2026-05-20

### Added

- Added icon packs for button and hero, and provide link for buttons.

## [0.2.3] - 2026-05-19

### Changed

- Updated `adaptive-island` icon and banner in README.

## [0.2.2] - 2026-05-19

### Changed

- Expanded README production-readiness guidance with operator posture, configuration surface, deployment gates, monitoring, backup and disaster recovery, secret rotation, and troubleshooting sections for the validated Databricks + Supabase + Upstash stack.
- Expanded security, contribution, and conduct docs with ownership boundaries, operational guardrails, incident-response guidance, documentation-review standards, and private handling for sensitive deployment information.
- Corrected the Docker Compose local guide to document the current version ranked-subset behavior: cached rankings do not append unranked fallback providers when a non-empty intersection exists.
- Cleaned formatting in the existing-event-log adoption example without changing its deployment flow.

## [0.2.1] - 2026-05-17

### Security

- Hardened `scripts/sentry-project-check.mjs` with normalized config parsing, HTTPS-only Sentry URL validation except localhost, bounded retry handling, strict Sentry API response-shape checks, stronger secret redaction, and stackless failure output. No runtime Sentry SDK, DSN, or telemetry is added.

### Changed

- Bumped TypeScript and Python SDK packages from `0.2.0` to `0.2.1`.

## [0.2.0] - 2026-05-11

### Added

- Added a production-aligned adaptive-routing toggle to both SDKs:
  - TypeScript: `adaptiveRoutingEnabled` selector option plus `resolveAdaptiveRoutingEnabled()` for production-compatible environment value parsing.
  - Python: `adaptive_routing_enabled` selector option, with `ADAPTIVE_ROUTING_ENABLED` environment fallback.
- Added `adaptive-disabled` decision metadata so callers can distinguish an intentional static fallback from a cache miss/malformed-cache fallback.
- Added Python and TypeScript tests proving disabled adaptive routing skips cache reads entirely and returns the caller fallback order after deduplication.
- Added Python and TypeScript regression tests proving the cached ranking is the source of truth when its intersection with the configured providers is non-empty (no append of unranked fallback providers).

### Changed

- Bumped TypeScript and Python SDK packages from `0.1.0` to `0.2.0`.
- Aligned the public runtime contract with BabySea's current production approach: Databricks remains offline/internal, Upstash ranking is the only adaptive serving artifact, and SDKs never call Databricks on the request path.
- Aligned `Selector.rank()` semantics with BabySea production: when the cached ranking has a non-empty intersection with the configured providers, the SDK returns only the ranked subset instead of appending unranked fallback providers. Adaptive routing now reflects observed provider performance rather than configuration order. Cache miss, empty intersection, and disabled adaptive routing paths are unchanged.
- Updated the failure-mode documentation to match the new ranked-subset behavior.
- Updated README, architecture, failure-mode, security, and SDK docs to describe `adaptiveRoutingEnabled=true` / `adaptive_routing_enabled=True` as cache-backed adaptive routing and `false`/`0`/`off`/`disabled` as static fallback-only routing.
- Reframed MLflow training as optional offline analysis/promotion review rather than a request-path serving refinement.

### Removed

- Removed the Mosaic AI Model Serving entry point and Databricks Asset Bundle serving-endpoint scaffold from the current public surface.
- Removed request-path Model Serving guidance from the production-readiness checklist and fail-open matrix.

## [0.1.0] - 2026-05-08

### Added

- Added the upcoming `execution-arrow` primitive to the shared README architecture map with its temporary `/#` launch link and `/v1/generate/image` + `/v1/generate/video` scope.
- Added `BabySea OSS taxonomy` in `README.md`.
- Fix table formatting in `README.md`.
- Added shared BabySea OSS architecture framing, 30-second summary, request-path guarantee, routing lifecycle, data contract, scoring configuration, evaluation metrics, and testing/failure-mode documentation.
- Added a credentials-free local synthetic demo that ranks providers from CSV attempts and a self-verifying TypeScript SDK cache demo proving cached-ranking, malformed-cache fallback, and missing-key fallback behavior without Upstash credentials.
- Added a cross-repo OSS architecture document under `apps/babysea-oss/ARCHITECTURE.md` explaining how the SDK, request normalization, provider ranking, and credit settlement fit together.
- Added stronger security-policy guidance for Databricks tokens, Upstash URLs, Supabase credentials, data minimization, request-path fail-open behavior, region/model normalization, and retention boundaries.
- Added standalone external-repo workflows under `.github/workflows/` for CodeQL, TypeScript package checks, Python package checks, local SDK demo validation, and package dry-runs.
- Added an explicit README status note explaining that this is a production-grade OSS primitive with a stable v0.1 runtime contract.
- Added README workflow badges for the standalone CodeQL and Package Check workflows.
- Added `scripts/sentry-project-check.mjs`, a README badge, ignored local `.sentryclirc` support, and a scheduled `Sentry Project Check` workflow. The workflow reads Sentry org/project configuration from GitHub Actions secrets, verifies the configured project slug, active status, `other` platform, ownership, and Code Guard rules, and does not add runtime tracking.
- Real-stack smoke harness under `examples/real-stack-smoke/` for Databricks API access, Databricks Asset Bundle shape, disposable Supabase `provider_cost_log` scoring, safe smoke-scoped Upstash ranking writes, and Python SDK cache reads.
- Sentry code-guard for the `babysea-community/adaptive-island` OSS project.
- Standalone OSS security policy and Dependabot dependency-security configuration for the public `babysea-community/adaptive-island` repository.
- Lakeflow Spark Declarative Pipelines for Bronze, Silver, and Gold layers on Delta Lake.
- MLflow value-model training entry point for optional Mosaic AI Model Serving re-score.
- Mosaic AI Model Serving entry point (`serving/score.py`).
- Lakeflow Job that exports the Gold ranking to Upstash with a 48 h TTL.
- Python SDK (`adaptive_island.Selector`) with cache-first deterministic ranking and fail-open fallback.
- TypeScript SDK with the same ranking contract (preview, no published build yet).
- JSON Schemas: `attempt.v1.json`, `ranking.v1.json`.
- Databricks Asset Bundle for one-command deploy.
- Documentation: architecture, deployment guide, adoption-on-existing-event-log guide.
- Examples: Asset Bundle, local docker-compose stack, Python SDK demo, adapter-view template.
- GitHub Actions CI running ruff + pytest + bundle validate on every PR.

### Changed

- Added a bullet-point table of contents after the BabySea OSS architecture section for quick navigation.
- Numbered all H2 sections after BabySea OSS architecture for consistent cross-primitive README structure.
- Promoted "Terms used in this repo" from a subsection to a top-level `## Terms` table matching the format used by rosetta-bridge and ledger-fortress.
- Added a `## Why it's different` problem/solution table matching the structure of sibling primitives.
- Renamed "Production-grade v0.1 surface" to "Current v0.1 surface" for cross-primitive consistency.
- Added `## Who's using the pattern` section matching sibling primitives.
- Reorder the badge.
- Re-validated the public OSS contract against BabySea's Databricks-backed provider-routing implementation and tightened wording around the production-grade Databricks + Supabase + Upstash contract.
- Clarified that Databricks improves later requests, not the active request, and that the Python SDK source-install path is the supported path until PyPI publication.
- Replaced unsupported public README language with stable v0.1 runtime-contract language for Supabase attempt rows, Databricks Bronze/Silver/Gold, Upstash `predictive:ranking:<region>:<model>`, and SDK fail-open fallback.
- Removed unimplemented `min_attempts` scoring guidance and promotion-gate wording from evaluation docs so the public surface only documents shipped ranking behavior.
- Normalized region examples to `us`, `eu`, and `apac`, matching the production-inspired regional stack model.
- Neutralized Databricks Asset Bundle example federation catalog names for community deployments while preserving the Supabase Lakehouse Federation shape.
- Marked the Python SDK package classifier as production/stable for the current v0.1 runtime contract.
- Replaced the public status badge, security-policy wording, and Python development classifier with production-grade/stable wording, matching the validated production-derived implementation.
- Changed the status badge label to production-grade for OSS primitive status consistency.
- Clarified that public production-inspired claims are grounded in BabySea's internal production implementation and limited to features implemented in this repo.
- Tightened README, architecture, deployment, contribution, and code-comment terminology around the supported Databricks + Supabase + Upstash stack contract.
- Documented that Upstash is the production cache and that Redis appears only for the Upstash protocol/client path or local developer stand-ins.
- Clarified the deploy guide's source-table requirement as the Databricks `provider_cost_log` projection, not a literal SDK insert payload with `schema_version`.
- Normalized the Apache 2.0 `LICENSE` wording to the canonical BabySea OSS format used across public packages.
- Expanded the Databricks deployment guide with a real-stack smoke validation step and Supavisor pooler guidance for environments where direct Supabase database hosts are IPv6-only.
- Typed the local synthetic SDK demo's in-memory cache helper so editor `checkJs` diagnostics stay clean while preserving the credentials-free behavior proof.
- Cache contract now matches the BabySea production shape: `predictive:ranking:<region>:<model>` with `providers_ranked`, `scores`, `attempts_total`, `window_hours`, and `computed_at`.
- TypeScript SDK dev toolchain updated to TypeScript 6 and Vitest 4 with clean build/test output, clearing the public Dependabot dependency PR set from the OSS repo source of truth.
- TypeScript SDK contributing docs now distinguish the Node.js 18+ runtime target from the Node.js 20.19+/22.12+ local development toolchain requirement.
- SDKs now return deterministic provider order, fail open to the caller-provided fallback list, validate finite provider scores, parse `computed_at`, and optionally reject cache values older than an SDK max-age guard.
- SDK decision metadata now reports `fallback` when a cached ranking has no provider overlap with the caller's allowed fallback list.
- Databricks bundle now writes all medallion tables under `<catalog>.medallion`, supports Upstash TLS, and resolves the Upstash URL from a Databricks secret scope instead of a secret-bearing bundle/job parameter.
- Silver now drops negative-latency rows before they can influence Gold ranking scores.
- Optional Mosaic AI serving now requires an explicit `MODEL_URI` instead of defaulting to a hard-coded `main` catalog model.
- Source contract now mirrors the Supabase `provider_cost_log` attempt-log shape.
- README and architecture docs now define the Databricks + Supabase + Upstash stack contract, OSS terminology, and current v0.1 surface without unimplemented roadmap claims.
- Python SDK cache connections now support configurable `cache_socket_timeout_seconds` and default to a community-friendlier 500 ms fail-open network guard.
- Python and TypeScript package metadata now explicitly names Databricks, Supabase, and Upstash and aligns with the package release version.
- Root workspace packaging now supports `pip install -e '.[dev]'` from the OSS root by discovering the SDK under `client/python` and installing the SDK's Upstash client runtime dependency (`redis`).
- `attempt.v1` now documents optional database-generated `id` so the schema matches the Supabase source projection used by Bronze.
- Real-stack smoke validation now defaults to smoke-scoped cache keys, refuses to overwrite existing Upstash keys unless explicitly allowed, restores existing values/TTL after intentional overwrite tests, and validates that `DATABRICKS_HOST` is an HTTPS Databricks URL.
- Added a scoped `pyrightconfig.json` for local SDK typechecking; Databricks DLT/job files remain syntax-validated locally because they rely on Databricks runtime modules/globals.

### Removed

- GitHub Actions CI workflow and README CI badge from the standalone OSS repo surface.
- Propensity/SNIPS/off-policy promotion-gate claims that were not part of BabySea's verified production path.

### Validated

- Ran the real-stack smoke harness against Databricks, Supabase, and Upstash on 2026-05-06. Result: Databricks API authenticated, 1 SQL warehouse visible, bundle shape parsed, 9 disposable Supabase attempt rows scored, a smoke-scoped Upstash key was written/read/deleted, the SDK returned `cached-ranking`, and temporary resources were cleaned up.
- Ran Python tests, Ruff, TypeScript lint, Vitest, build, package dry-run, and the self-verifying local SDK cache demo.
- Bronze/Silver/Gold pipeline design is grounded in BabySea's checked-in production Databricks medallion implementation.
- Adapter-view pattern is documented for teams whose existing attempt logs use different column names.
- Ran the real-stack smoke harness against Databricks, Supabase, and Upstash on 2026-05-02. Result: Databricks API authenticated, 1 SQL warehouse visible, Databricks bundle shape parsed, 9 disposable Supabase attempt rows scored into `cloudflare ➜ replicate ➜ fal`, a smoke-scoped Upstash key was written with short TTL, Python SDK returned `cached-ranking`, and the temporary schema/key were cleaned up. Sanitized artifact: `/tmp/adaptive-island-real-stack-result.json`.
- Confirmed Supabase direct database access from this container was IPv6-only; validation used the project's IPv4-compatible Supavisor pooler settings instead.
- Compared the OSS control loop against BabySea's verified production references: Supabase `provider_cost_log`, Databricks Bronze/Silver/Gold medallion pipeline, `gold_provider_ranking_by_model`, Upstash key shape `predictive:ranking:<region>:<model>`, and cache-first fail-open SDK behavior.
- Ran local temp end-to-end simulation from Supabase-shaped provider attempts through the Gold scoring formula, cache payload generation, Python SDK cache hit, and deterministic fallback path. Latest result artifact: `/tmp/adaptive-island-validation.AaNOJP/adaptive-island-validation-result.json`.
- Ran Python validation: `py_compile` for SDK/jobs/training/serving/pipeline files, `python -m pytest -q` (`13 passed`), JSON schema parsing, and YAML parsing for the Databricks Asset Bundle and Docker Compose example.
- Ran Python static checks: `python -m ruff check .` and scoped `python -m pyright` (`0 errors`).
- Ran TypeScript validation: `npm test -- --run` (`12 passed`) and `npm run lint` (`tsc --noEmit`).
- Checked Databricks CLI availability; it is not installed in this container, so local validation is limited to YAML parsing rather than `databricks bundle validate`.
- Re-attempted disposable local PostgreSQL validation for the Supabase source-table SQL, but the developer stand-in setup did not complete reliably in this container; no external credentials were written or echoed.
