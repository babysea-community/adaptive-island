"""
adaptive-island Selector.

Reads an adaptive-island provider ranking, shaped after BabySea's documented
Upstash cache contract, and returns an ordered provider list. The Python client
uses Upstash's Redis protocol under the hood. It falls back to the
caller-provided order when the cache is unavailable or malformed. Selection is
deterministic by default so the SDK matches the production
`generation_provider_order: "fastest"` semantics.
"""

from __future__ import annotations

import json
import logging
import math
import os
import urllib.parse
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

logger = logging.getLogger(__name__)


def redis_url_for_tls(url: str, use_tls: bool) -> str:
    """Return a redis-py URL that enables TLS without passing unsupported kwargs."""
    if use_tls and url.startswith("redis://"):
        return "redis://" + url[len("redis://") :]
    return url


def should_use_tls_for_cache_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    hostname = (parsed.hostname or "").casefold().rstrip(".")
    return parsed.scheme == "redis" or hostname == "upstash.io" or hostname.endswith(
        ".upstash.io"
    )


@dataclass(frozen=True)
class Decision:
    provider: str
    providers: tuple[str, ...]
    source: str  # "cached-ranking" | "fallback" | "adaptive-disabled"


_DISABLED_VALUES = {"false", "0", "off", "disabled"}


def _resolve_adaptive_routing_enabled(explicit: bool | None) -> bool:
    if explicit is not None:
        return explicit

    raw = os.environ.get("ADAPTIVE_ROUTING_ENABLED")
    if raw is None or not raw.strip():
        return True

    return raw.strip().lower() not in _DISABLED_VALUES


class Selector:
    """Rank providers for a (model, region), fail-open."""

    def __init__(
        self,
        cache_url: str | None = None,
        *,
        key_prefix: str = "predictive:ranking",
        max_cache_age_seconds: int | None = None,
        cache_socket_timeout_seconds: float = 0.5,
        adaptive_routing_enabled: bool | None = None,
    ) -> None:
        if max_cache_age_seconds is not None and max_cache_age_seconds <= 0:
            raise ValueError("adaptive-island: max_cache_age_seconds must be positive.")
        if cache_socket_timeout_seconds <= 0:
            raise ValueError(
                "adaptive-island: cache_socket_timeout_seconds must be positive."
            )
        self._key_prefix = key_prefix
        self._max_cache_age_seconds = max_cache_age_seconds
        self._adaptive_routing_enabled = _resolve_adaptive_routing_enabled(
            adaptive_routing_enabled
        )
        self._last_decision: Decision | None = None
        self._cache = self._build_cache(
            cache_url or os.environ.get("ADAPTIVE_ISLAND_CACHE_URL"),
            cache_socket_timeout_seconds=cache_socket_timeout_seconds,
        )

    @staticmethod
    def _build_cache(url: str | None, *, cache_socket_timeout_seconds: float):
        if not url:
            return None
        try:
            import redis

            use_tls = should_use_tls_for_cache_url(url)
            return redis.from_url(
                redis_url_for_tls(url, use_tls),
                socket_connect_timeout=cache_socket_timeout_seconds,
                socket_timeout=cache_socket_timeout_seconds,
            )
        except Exception:  # noqa: BLE001
            logger.warning("adaptive-island: cache disabled, will use fallback only.")
            return None

    @property
    def last_decision(self) -> Decision | None:
        return self._last_decision

    def rank(
        self,
        *,
        model_id: str,
        region: str,
        fallback: Sequence[str],
    ) -> list[str]:
        """Return providers ordered best-first. Never raises when fallback is present."""
        if not fallback:
            raise ValueError("adaptive-island: fallback must contain at least one provider.")

        allowed = list(dict.fromkeys(fallback))

        if not self._adaptive_routing_enabled:
            self._last_decision = Decision(
                allowed[0], tuple(allowed), "adaptive-disabled"
            )
            return allowed

        ranking = self._read_ranking(model_id=model_id, region=region)
        allowed_set = set(allowed)

        if ranking:
            # Match BabySea production semantics: trust the ranking and serve
            # only its intersection with the configured providers. Configured
            # providers not present in the ranking are intentionally excluded
            # so adaptive routing reflects observed performance, not
            # configuration order.
            ordered = [provider for provider in ranking if provider in allowed_set]
            if not ordered:
                self._last_decision = Decision(allowed[0], tuple(allowed), "fallback")
                return allowed
            self._last_decision = Decision(ordered[0], tuple(ordered), "cached-ranking")
            return ordered

        self._last_decision = Decision(allowed[0], tuple(allowed), "fallback")
        return allowed

    def pick(
        self,
        *,
        model_id: str,
        region: str,
        fallback: Sequence[str],
    ) -> str:
        """Return the first provider from `rank(...)` for simple integrations."""
        return self.rank(model_id=model_id, region=region, fallback=fallback)[0]

    def build_attempt(
        self,
        *,
        generation_id: str | None = None,
        model_id: str,
        provider: str,
        outcome: str,
        attempt_order: int = 1,
        account_id: str | None = None,
        provider_model_id: str | None = None,
        prediction_id: str | None = None,
        estimated_cost: float | None = None,
        was_cancelled: bool = False,
        cancel_available: bool = False,
        submitted_at: str | None = None,
        resolved_at: str | None = None,
        error_message: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        """Build an `attempt.v1` event compatible with the Supabase source table."""
        now = datetime.now(timezone.utc).isoformat()
        return {
            "schema_version": "attempt.v1",
            "generation_id": generation_id or uuid4().hex,
            "account_id": account_id,
            "provider": provider,
            "provider_model_id": provider_model_id,
            "prediction_id": prediction_id,
            "model": model_id,
            "estimated_cost": float(estimated_cost) if estimated_cost is not None else None,
            "outcome": outcome,
            "attempt_order": int(attempt_order),
            "was_cancelled": bool(was_cancelled),
            "cancel_available": bool(cancel_available),
            "submitted_at": submitted_at or now,
            "resolved_at": resolved_at,
            "error_message": error_message,
            "metadata": metadata or {},
        }

    def log_attempt(
        self,
        *,
        model_id: str,
        region: str,
        provider: str,
        outcome: str,
        attempt_order: int = 1,
        account_id: str | None = None,
        estimated_cost: float | None = None,
        error_message: str | None = None,
        features: dict | None = None,
        sink=None,
    ) -> dict:
        """Build an attempt event and optionally write it to a caller-provided sink."""
        event = self.build_attempt(
            model_id=model_id,
            provider=provider,
            outcome=outcome,
            attempt_order=attempt_order,
            account_id=account_id,
            estimated_cost=estimated_cost,
            error_message=error_message,
            metadata={"region": region, **(features or {})},
        )
        if sink is not None:
            sink(event)
        return event

    def _read_ranking(self, *, model_id: str, region: str) -> list[str] | None:
        if self._cache is None:
            return None
        key = f"{self._key_prefix}:{region}:{model_id}"
        try:
            raw = self._cache.get(key)
        except Exception:  # noqa: BLE001
            return None
        if raw is None:
            return None
        if not isinstance(raw, (str, bytes, bytearray)):
            return None
        try:
            payload = json.loads(raw)
            if not _valid_ranking_payload(
                payload,
                max_cache_age_seconds=self._max_cache_age_seconds,
            ):
                return None
            providers = payload.get("providers_ranked")
            return [p for p in providers if isinstance(p, str) and p]
        except (ValueError, TypeError):
            return None


def _valid_ranking_payload(
    payload: object,
    *,
    max_cache_age_seconds: int | None = None,
) -> bool:
    if not isinstance(payload, dict):
        return False
    providers = payload.get("providers_ranked")
    scores = payload.get("scores")
    attempts_total = payload.get("attempts_total")
    window_hours = payload.get("window_hours")
    computed_at = payload.get("computed_at")

    if not isinstance(providers, list) or not providers:
        return False
    if not all(isinstance(p, str) and p for p in providers):
        return False
    if not isinstance(scores, dict):
        return False
    if not set(providers).issubset(set(scores.keys())):
        return False
    if not all(
        isinstance(k, str)
        and isinstance(v, (int, float))
        and not isinstance(v, bool)
        and math.isfinite(float(v))
        for k, v in scores.items()
    ):
        return False
    if isinstance(attempts_total, bool) or not isinstance(attempts_total, int) or attempts_total < 0:
        return False
    if isinstance(window_hours, bool) or not isinstance(window_hours, int) or window_hours <= 0:
        return False
    computed_at_dt = _parse_rfc3339_datetime(computed_at)
    if computed_at_dt is None:
        return False
    if max_cache_age_seconds is not None:
        age = datetime.now(timezone.utc) - computed_at_dt.astimezone(timezone.utc)
        if age.total_seconds() > max_cache_age_seconds:
            return False
    return True


def _parse_rfc3339_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed
