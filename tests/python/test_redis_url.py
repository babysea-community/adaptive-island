from __future__ import annotations

import sys

from adaptive_island.selector import Selector, redis_url_for_tls


def test_upstash_redis_url_is_normalized_to_redis() -> None:
    url = "redis://default:token@wired-hyena-112998.upstash.io:6379"
    assert redis_url_for_tls(url, use_tls=True).startswith("redis://")


def test_redis_from_url_does_not_receive_ssl_kwarg(monkeypatch) -> None:
    calls: list[tuple[str, dict]] = []

    class FakeRedisModule:
        @staticmethod
        def from_url(url: str, **kwargs):
            calls.append((url, kwargs))
            return object()

    monkeypatch.setitem(sys.modules, "redis", FakeRedisModule)

    assert (
        Selector._build_cache(
            "redis://default:token@example.upstash.io:6379",
            cache_socket_timeout_seconds=0.5,
        )
        is not None
    )
    assert calls == [
        (
            "redis://default:token@example.upstash.io:6379",
            {"socket_connect_timeout": 0.5, "socket_timeout": 0.5},
        )
    ]
