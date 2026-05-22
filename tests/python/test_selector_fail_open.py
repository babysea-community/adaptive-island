"""Smoke tests for the Python SDK fail-open path."""

from __future__ import annotations

from adaptive_island import Selector
from pytest import MonkeyPatch


class _ExplodingCache:
    def get(self, key: str) -> bytes:  # pragma: no cover - should not be called
        raise AssertionError(f"cache should not be read for key {key}")


def test_pick_falls_back_when_no_cache():
    sel = Selector(cache_url=None)
    chosen = sel.pick(
        model_id="demo/model",
        region="us",
        fallback=["a", "b", "c"],
    )
    assert chosen == "a"
    assert sel.last_decision is not None
    assert sel.last_decision.source == "fallback"
    assert sel.last_decision.providers == ("a", "b", "c")


def test_adaptive_routing_disabled_skips_cache():
    sel = Selector(cache_url=None, adaptive_routing_enabled=False)
    sel._cache = _ExplodingCache()  # type: ignore[attr-defined]

    ranked = sel.rank(
        model_id="demo/model",
        region="us",
        fallback=["a", "b", "c"],
    )

    assert ranked == ["a", "b", "c"]
    assert sel.last_decision is not None
    assert sel.last_decision.source == "adaptive-disabled"


def test_adaptive_routing_disabled_from_env(monkeypatch: MonkeyPatch):
    for value in ("false", "FALSE", "0", "off", " disabled "):
        monkeypatch.setenv("ADAPTIVE_ROUTING_ENABLED", value)
        sel = Selector(cache_url=None)
        sel._cache = _ExplodingCache()  # type: ignore[attr-defined]

        ranked = sel.rank(
            model_id="demo/model",
            region="us",
            fallback=["a", "b"],
        )

        assert ranked == ["a", "b"]
        assert sel.last_decision is not None
        assert sel.last_decision.source == "adaptive-disabled"


def test_adaptive_routing_enabled_by_default_reads_cache(monkeypatch: MonkeyPatch):
    monkeypatch.delenv("ADAPTIVE_ROUTING_ENABLED", raising=False)

    class Cache:
        def __init__(self) -> None:
            self.keys: list[str] = []

        def get(self, key: str) -> bytes:
            self.keys.append(key)
            return b'{"providers_ranked":["b","a"],"scores":{"b":0.9,"a":0.1},"attempts_total":2,"window_hours":24,"computed_at":"2026-04-29T00:00:00Z"}'

    cache = Cache()
    sel = Selector(cache_url=None)
    sel._cache = cache  # type: ignore[attr-defined]

    ranked = sel.rank(
        model_id="demo/model",
        region="us",
        fallback=["a", "b"],
    )

    assert ranked == ["b", "a"]
    assert cache.keys == ["predictive:ranking:us:demo/model"]
    assert sel.last_decision is not None
    assert sel.last_decision.source == "cached-ranking"


def test_cache_timeout_must_be_positive():
    try:
        Selector(cache_url=None, cache_socket_timeout_seconds=0)
    except ValueError as exc:
        assert "cache_socket_timeout_seconds" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected ValueError")


def test_log_attempt_returns_event():
    sel = Selector(cache_url=None)
    sel.pick(
        model_id="demo/model",
        region="us",
        fallback=["a", "b"],
    )
    event = sel.log_attempt(
        model_id="demo/model",
        region="us",
        provider="a",
        outcome="used",
        estimated_cost=0.001,
    )
    assert event["schema_version"] == "attempt.v1"
    assert event["provider"] == "a"
    assert event["model"] == "demo/model"
    assert event["outcome"] == "used"
