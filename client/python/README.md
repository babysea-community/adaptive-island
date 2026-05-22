# adaptive-island Python SDK

The official Python SDK for [`adaptive-island`](https://github.com/babysea-community/adaptive-island), a cache-first provider-ranking pattern for multi-vendor AI workloads built with Databricks, Supabase, and Upstash.

## Install

Until PyPI publication, the supported install path is source install or a pinned commit SHA:

```bash
# from this directory
pip install -e .

# or pin via pip
# pip install "adaptive-island @ git+https://github.com/babysea-community/adaptive-island.git@<commit-sha>#subdirectory=client/python"
```

## Usage

```python
from adaptive_island import Selector

sel = Selector(cache_url="redis://default:<token>@<host>:6379")

# Optional defense-in-depth freshness guard in addition to Upstash TTL:
# sel = Selector(cache_url="redis://...", max_cache_age_seconds=48 * 60 * 60)
# Optional network guard for community Upstash deployments; failures are fail-open:
# sel = Selector(cache_url="redis://...", cache_socket_timeout_seconds=1.0)
# Optional production toggle; False skips cache reads and returns fallback directly:
# ADAPTIVE_ROUTING_ENABLED=false/0/off/disabled also disables cache reads by default.
# sel = Selector(cache_url="redis://...", adaptive_routing_enabled=False)

providers = sel.rank(
    model_id="black-forest-labs/flux-schnell",
    region="us",
    fallback=["replicate", "fal", "cloudflare"],
)

# Try providers[0], then fail over through the rest in order.

sel.log_attempt(
    model_id="black-forest-labs/flux-schnell",
    region="us",
    provider=providers[0],
    outcome="used",
    estimated_cost=0.0023,
)
```

The SDK is **fail-open**: if adaptive routing is disabled, or if Upstash is unavailable, empty, malformed, TTL-expired, or older than `max_cache_age_seconds`, `rank()` returns the caller-provided `fallback=` order after removing duplicate providers.

See the [main README](https://github.com/babysea-community/adaptive-island) for the full architecture.

Apache 2.0.
