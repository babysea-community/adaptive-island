#!/usr/bin/env python3
"""Compute a local adaptive-island ranking from synthetic attempt rows."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict


class Attempt(TypedDict):
    provider: str
    outcome: str
    latency_ms: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--model", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--window-hours", type=int, default=24)
    return parser.parse_args()


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, math.ceil((p / 100.0) * len(ordered)) - 1)
    return ordered[index]


def load_attempts(path: Path, model: str, region: str) -> list[Attempt]:
    attempts: list[Attempt] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row["model"] != model or row["region"] != region:
                continue
            attempts.append(
                {
                    "provider": row["provider"],
                    "outcome": row["outcome"],
                    "latency_ms": float(row["latency_ms"]),
                }
            )
    return attempts


def score_attempts(attempts: list[Attempt], window_hours: int) -> dict[str, object]:
    grouped: dict[str, list[Attempt]] = defaultdict(list)
    for attempt in attempts:
        grouped[attempt["provider"]].append(attempt)

    p95_by_provider = {
        provider: percentile([attempt["latency_ms"] for attempt in rows], 95)
        for provider, rows in grouped.items()
    }
    max_p95 = max(p95_by_provider.values(), default=1.0) or 1.0

    scores: dict[str, float] = {}
    for provider, rows in grouped.items():
        total = len(rows)
        success_rate = sum(1 for row in rows if row["outcome"] == "used") / total
        wasted_rate = (
            sum(1 for row in rows if row["outcome"] in {"cancelled", "discarded", "failed"}) / total
        )
        latency_p95_norm = p95_by_provider[provider] / max_p95
        scores[provider] = round(
            success_rate * 1.0 - wasted_rate * 0.5 - latency_p95_norm * 0.3,
            6,
        )

    providers_ranked = sorted(
        scores,
        key=lambda provider: (-scores[provider], p95_by_provider[provider], provider),
    )

    return {
        "providers_ranked": providers_ranked,
        "scores": scores,
        "attempts_total": len(attempts),
        "window_hours": window_hours,
        "computed_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }


def main() -> int:
    args = parse_args()
    attempts = load_attempts(args.csv_path, args.model, args.region)
    payload = score_attempts(attempts, args.window_hours)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
