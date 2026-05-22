"""Cache-hit branch returns the cached provider order deterministically."""

from __future__ import annotations

import json

from adaptive_island import Selector


class _StubCache:
    def __init__(self, payload: dict) -> None:
        self._payload = json.dumps(payload).encode("utf-8")
        self.keys: list[str] = []

    def get(self, key: str) -> bytes:
        self.keys.append(key)
        return self._payload


def _payload(**overrides: object) -> dict:
    payload = {
        "providers_ranked": ["b", "a", "c"],
        "scores": {"b": 0.9, "a": 0.4, "c": 0.1},
        "attempts_total": 240,
        "window_hours": 24,
        "computed_at": "2026-04-29T00:00:00Z",
    }
    payload.update(overrides)
    return payload


def test_cache_hit_prefers_top_provider() -> None:
    sel = Selector(cache_url=None)
    cache = _StubCache(_payload())
    sel._cache = cache  # type: ignore[attr-defined]

    ranked = sel.rank(model_id="demo/model", region="us", fallback=["a", "b", "c"])
    assert ranked == ["b", "a", "c"]
    assert cache.keys == ["predictive:ranking:us:demo/model"]
    assert sel.pick(model_id="demo/model", region="us", fallback=["a", "b", "c"]) == "b"
    assert sel.last_decision is not None
    assert sel.last_decision.source == "cached-ranking"


def test_cache_hit_serves_only_ranked_subset_of_fallback() -> None:
    """Match BabySea production: fallback providers absent from the ranking
    are not appended onto the served order. The ranking is the source of
    truth when a non-empty intersection exists."""
    sel = Selector(cache_url=None)
    sel._cache = _StubCache(  # type: ignore[attr-defined]
        _payload(providers_ranked=["b"], scores={"b": 0.9})
    )

    ranked = sel.rank(model_id="demo/model", region="us", fallback=["a", "b", "c"])

    assert ranked == ["b"]
    assert sel.last_decision is not None
    assert sel.last_decision.source == "cached-ranking"


def test_cache_with_no_allowed_providers_is_reported_as_fallback() -> None:
    sel = Selector(cache_url=None)
    sel._cache = _StubCache(_payload(providers_ranked=["x"], scores={"x": 1.0}))  # type: ignore[attr-defined]

    ranked = sel.rank(model_id="demo/model", region="us", fallback=["a", "b"])

    assert ranked == ["a", "b"]
    assert sel.last_decision is not None
    assert sel.last_decision.source == "fallback"


def test_malformed_cache_falls_back() -> None:
    sel = Selector(cache_url=None)
    sel._cache = _StubCache({"providers_ranked": ["b", "a"]})  # type: ignore[attr-defined]

    ranked = sel.rank(model_id="demo/model", region="us", fallback=["a", "b"])

    assert ranked == ["a", "b"]
    assert sel.last_decision is not None
    assert sel.last_decision.source == "fallback"


def test_invalid_computed_at_falls_back() -> None:
    sel = Selector(cache_url=None)
    sel._cache = _StubCache(_payload(computed_at="not-a-date"))  # type: ignore[attr-defined]

    ranked = sel.rank(model_id="demo/model", region="us", fallback=["a", "b"])

    assert ranked == ["a", "b"]
    assert sel.last_decision is not None
    assert sel.last_decision.source == "fallback"


def test_missing_score_key_falls_back() -> None:
    sel = Selector(cache_url=None)
    sel._cache = _StubCache(_payload(scores={"b": 0.9}))  # type: ignore[attr-defined]

    ranked = sel.rank(model_id="demo/model", region="us", fallback=["a", "b"])

    assert ranked == ["a", "b"]
    assert sel.last_decision is not None
    assert sel.last_decision.source == "fallback"


def test_boolean_score_falls_back() -> None:
    sel = Selector(cache_url=None)
    sel._cache = _StubCache(_payload(scores={"b": True, "a": 0.4, "c": 0.1}))  # type: ignore[attr-defined]

    ranked = sel.rank(model_id="demo/model", region="us", fallback=["a", "b"])

    assert ranked == ["a", "b"]
    assert sel.last_decision is not None
    assert sel.last_decision.source == "fallback"


def test_non_finite_score_falls_back() -> None:
    sel = Selector(cache_url=None)
    sel._cache = _StubCache(_payload(scores={"b": float("inf"), "a": 0.4, "c": 0.1}))  # type: ignore[attr-defined]

    ranked = sel.rank(model_id="demo/model", region="us", fallback=["a", "b"])

    assert ranked == ["a", "b"]
    assert sel.last_decision is not None
    assert sel.last_decision.source == "fallback"


def test_boolean_integer_fields_fall_back() -> None:
    sel = Selector(cache_url=None)
    sel._cache = _StubCache(_payload(attempts_total=True, window_hours=True))  # type: ignore[attr-defined]

    ranked = sel.rank(model_id="demo/model", region="us", fallback=["a", "b"])

    assert ranked == ["a", "b"]
    assert sel.last_decision is not None
    assert sel.last_decision.source == "fallback"


def test_expired_computed_at_falls_back_when_max_age_is_set() -> None:
    sel = Selector(cache_url=None, max_cache_age_seconds=1)
    sel._cache = _StubCache(_payload(computed_at="2020-01-01T00:00:00Z"))  # type: ignore[attr-defined]

    ranked = sel.rank(model_id="demo/model", region="us", fallback=["a", "b"])

    assert ranked == ["a", "b"]
    assert sel.last_decision is not None
    assert sel.last_decision.source == "fallback"
