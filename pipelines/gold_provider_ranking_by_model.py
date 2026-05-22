"""
adaptive-island/pipelines/gold_provider_ranking_by_model.py

Gold layer: per (model, region) provider ranking.

This follows BabySea's documented runtime contract. The export job writes each
row to Upstash as `predictive:ranking:<region>:<model>` and SDKs consume the
ranked provider list without calling Databricks on the request path.
"""

from __future__ import annotations

import dlt
from pyspark.sql import functions as F

# Same default shape as the documented BabySea implementation.
COST_PENALTY = float(
    spark.conf.get("spark.adaptive_island.cost_penalty", "0.5")  # noqa: F821
)
LATENCY_PENALTY = float(
    spark.conf.get("spark.adaptive_island.latency_penalty", "0.3")  # noqa: F821
)
RANKING_WINDOW_HOURS = int(
    spark.conf.get("spark.adaptive_island.ranking_window_hours", "24")  # noqa: F821
)


@dlt.table(
    name="gold_provider_ranking_by_model",
    comment=(
        "Per-model regional provider ranking. Refreshed by Lakeflow and "
        "exported to Upstash for cache-first serving."
    ),
    table_properties={
        "delta.enableChangeDataFeed": "true",
        "adaptive_island.layer": "gold",
    },
)
def gold_provider_ranking_by_model():
    silver = dlt.read("silver_provider_attempts")

    per_pair = (
        silver.where(F.col("outcome").isin("used", "failed", "discarded", "cancelled"))
        .where(F.col("resolved_at").isNotNull())
        .where(
            F.col("submitted_at")
            >= F.expr(f"current_timestamp() - INTERVAL {RANKING_WINDOW_HOURS} HOURS")
        )
        .where(F.col("model").isNotNull() & F.col("provider").isNotNull())
        .groupBy("model", "region", "provider")
        .agg(
            F.count("*").alias("attempts"),
            F.sum(F.col("is_success").cast("int")).alias("succeeded"),
            F.sum(F.col("is_wasted").cast("int")).alias("wasted"),
            F.expr("percentile_approx(latency_ms, 0.95)").alias("latency_p95_ms"),
        )
        .withColumn(
            "success_rate",
            F.when(F.col("attempts") > 0, F.col("succeeded") / F.col("attempts"))
            .otherwise(F.lit(0.0)),
        )
        .withColumn(
            "wasted_rate",
            F.when(F.col("attempts") > 0, F.col("wasted") / F.col("attempts"))
            .otherwise(F.lit(0.0)),
        )
    )

    model_max = per_pair.groupBy("model", "region").agg(
        F.expr("max(coalesce(latency_p95_ms, 0))").alias("max_p95_ms"),
    )

    scored = (
        per_pair.join(model_max, on=["model", "region"], how="left")
        .withColumn(
            "latency_p95_norm",
            F.when(
                F.col("max_p95_ms") > 0,
                F.col("latency_p95_ms") / F.col("max_p95_ms"),
            ).otherwise(F.lit(0.0)),
        )
        .withColumn(
            "score",
            F.col("success_rate") * F.lit(1.0)
            - F.col("wasted_rate") * F.lit(COST_PENALTY)
            - F.col("latency_p95_norm") * F.lit(LATENCY_PENALTY),
        )
    )

    return (
        scored.groupBy("model", "region")
        .agg(
            F.collect_list(
                F.struct(
                    (-F.col("score")).alias("neg_score"),
                    F.col("latency_p95_ms").alias("latency_p95_ms"),
                    F.col("provider").alias("provider"),
                    F.col("score").alias("score"),
                    F.col("attempts").alias("attempts"),
                )
            ).alias("rows"),
        )
        .withColumn("sorted_rows", F.sort_array(F.col("rows")))
        .withColumn(
            "providers_ranked",
            F.transform(F.col("sorted_rows"), lambda x: x["provider"]),
        )
        .withColumn(
            "scores",
            F.map_from_entries(
                F.transform(
                    F.col("sorted_rows"),
                    lambda x: F.struct(x["provider"].alias("k"), x["score"].alias("v")),
                )
            ),
        )
        .withColumn(
            "attempts_total",
            F.expr("aggregate(sorted_rows, 0L, (acc, x) -> acc + x.attempts)"),
        )
        .withColumn("window_hours", F.lit(RANKING_WINDOW_HOURS))
        .withColumn("computed_at", F.current_timestamp())
        .select(
            "model",
            "region",
            "providers_ranked",
            "scores",
            "attempts_total",
            "window_hours",
            "computed_at",
        )
    )
