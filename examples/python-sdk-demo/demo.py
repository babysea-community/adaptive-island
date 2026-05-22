"""Minimal adaptive-island Python SDK demo.

Run a local Redis stand-in for Upstash (e.g. `docker run -p 6379:6379 redis:7-alpine`),
then:

    pip install -e ../../client/python redis
    python demo.py

You will see the Selector return the cached provider order and gracefully fall
back when the cache is empty.
"""

from __future__ import annotations

import json
import os

import redis
from adaptive_island import Selector

CACHE_URL = os.environ.get("CACHE_URL", "redis://localhost:6379")
MODEL_ID = "demo/model"
REGION = "us"


def seed_cache() -> None:
    """Write one ranking key so the SDK has something to read."""
    client = redis.from_url(CACHE_URL)
    payload = {
        "providers_ranked": ["fast", "mid", "slow"],
        "scores": {"fast": 0.95, "mid": 0.50, "slow": 0.10},
        "attempts_total": 450,
        "window_hours": 24,
        "computed_at": "2026-04-29T00:00:00Z",
    }
    key = f"predictive:ranking:{REGION}:{MODEL_ID}"
    client.set(key, json.dumps(payload), ex=48 * 3600)
    print(f"seeded {key}")


def main() -> None:
    seed_cache()

    sel = Selector(cache_url=CACHE_URL)
    providers = sel.rank(
        model_id=MODEL_ID,
        region=REGION,
        fallback=["fast", "mid", "slow"],
    )

    print("\nrank(...) result:")
    for i, provider in enumerate(providers, start=1):
        print(f"  {i}. {provider}")

    print(f"\nLast decision source: {sel.last_decision.source if sel.last_decision else 'none'}")

    # Log an outcome event (this is what your application would emit).
    event = sel.log_attempt(
        model_id=MODEL_ID,
        region=REGION,
        provider=providers[0],
        outcome="used",
        estimated_cost=0.0011,
    )
    print("\nExample attempt.v1 event:")
    print(json.dumps(event, indent=2))


if __name__ == "__main__":
    main()
