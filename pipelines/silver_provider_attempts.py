"""
adaptive-island/pipelines/silver_provider_attempts.py

Silver layer: clean Bronze and derive routing-relevant fields.

Adds the same fields BabySea uses for provider-ranking and optional MLflow
training: latency, success/wasted semantics, failover flag, and time buckets.
"""

from __future__ import annotations

import dlt
from pyspark.sql import functions as F


@dlt.table(
    name="silver_provider_attempts",
    comment=(
        "Typed provider attempts with latency, success, wasted-attempt, "
        "failover, and time-bucket fields."
    ),
    table_properties={
        "delta.enableChangeDataFeed": "true",
        "adaptive_island.layer": "silver",
    },
)
@dlt.expect_or_drop("non_negative_latency", "latency_ms IS NULL OR latency_ms >= 0")
def silver_provider_attempts():
    bronze = dlt.read("bronze_provider_attempts")

    return (
        bronze
        .withColumn(
            "latency_ms",
            F.when(
                F.col("resolved_at").isNotNull() & F.col("submitted_at").isNotNull(),
                (
                    F.unix_millis("resolved_at")
                    - F.unix_millis("submitted_at")
                ).cast("long"),
            ).otherwise(F.lit(None).cast("long")),
        )
        .withColumn("is_success", F.col("outcome") == F.lit("used"))
        .withColumn(
            "is_wasted",
            F.col("outcome").isin("failed", "discarded", "cancelled"),
        )
        .withColumn("is_failover", F.coalesce(F.col("attempt_order"), F.lit(1)) > 1)
        .withColumn("submitted_date", F.col("submitted_at").cast("date"))
        .withColumn(
            "submitted_bucket_5min",
            (
                F.expr("unix_timestamp(submitted_at) - (unix_timestamp(submitted_at) % 300)")
                .cast("timestamp")
            ),
        )
    )
