"""
adaptive-island/pipelines/bronze_provider_attempts.py

Bronze layer: ingest provider-attempt rows from Supabase via
Databricks Lakehouse Federation.

This follows the documented BabySea source shape: one operational row per
provider submission, later resolved to an outcome such as used, failed,
discarded, cancelled, or pending. Bronze preserves the operational record and
adds only lineage columns.

Required Lakeflow Spark Declarative Pipelines settings:
    spark.adaptive_island.federation_catalog -> e.g. "adaptive_island_supabase_catalog"
    spark.adaptive_island.source_schema      -> defaults to "public"
    spark.adaptive_island.source_table       -> defaults to "provider_cost_log"
    spark.adaptive_island.region             -> e.g. "us"
"""

from __future__ import annotations

import dlt
from pyspark.sql import functions as F


def _conf(key: str) -> str:
    """Read a pipeline-level conf with a clear error message."""
    value = spark.conf.get(key, None)  # noqa: F821 (Spark global in DLT)
    if value is None or value == "":
        raise ValueError(f"adaptive-island: missing required conf {key!r}")
    return value


FEDERATION_CATALOG = _conf("spark.adaptive_island.federation_catalog")
SOURCE_SCHEMA = spark.conf.get("spark.adaptive_island.source_schema", "public")  # noqa: F821
SOURCE_TABLE_NAME = spark.conf.get(  # noqa: F821
    "spark.adaptive_island.source_table",
    "provider_cost_log",
)
REGION = _conf("spark.adaptive_island.region")

# Catalog names may contain hyphens (Lakehouse Federation appends `_catalog`
# to the connection name). Always backtick on read.
SOURCE_TABLE = f"`{FEDERATION_CATALOG}`.`{SOURCE_SCHEMA}`.`{SOURCE_TABLE_NAME}`"


@dlt.table(
    name="bronze_provider_attempts",
    comment=(
        "Raw provider attempts federated from Supabase. Follows the "
        "operational provider_cost_log contract and adds lineage only."
    ),
    table_properties={
        "delta.enableChangeDataFeed": "true",
        "adaptive_island.layer": "bronze",
        "adaptive_island.region": REGION,
    },
)
@dlt.expect_or_drop("attempt_id_present", "attempt_id IS NOT NULL")
@dlt.expect_or_drop("generation_id_present", "generation_id IS NOT NULL")
@dlt.expect_or_drop("model_present", "model IS NOT NULL")
@dlt.expect_or_drop("provider_present", "provider IS NOT NULL")
@dlt.expect_or_drop(
    "valid_outcome",
    "outcome IN ('used','cancelled','discarded','failed','pending')",
)
def bronze_provider_attempts():
    """Read directly from the federated operational source."""
    return (
        spark.read.table(SOURCE_TABLE)  # noqa: F821
        .select(
            F.col("id").cast("long").alias("attempt_id"),
            F.col("account_id").cast("string").alias("account_id"),
            F.col("generation_id").cast("string").alias("generation_id"),
            F.col("provider").cast("string"),
            F.col("provider_model_id").cast("string").alias("provider_model_id"),
            F.col("prediction_id").cast("string").alias("prediction_id"),
            F.col("model").cast("string").alias("model"),
            F.col("estimated_cost").cast("double").alias("estimated_cost"),
            F.col("outcome").cast("string").alias("outcome"),
            F.col("attempt_order").cast("int").alias("attempt_order"),
            F.col("was_cancelled").cast("boolean").alias("was_cancelled"),
            F.col("cancel_available").cast("boolean").alias("cancel_available"),
            F.col("submitted_at").cast("timestamp").alias("submitted_at"),
            F.col("resolved_at").cast("timestamp").alias("resolved_at"),
            F.col("error_message").cast("string").alias("error_message"),
            F.col("metadata").cast("string").alias("metadata_json"),
            F.lit(REGION).alias("region"),
            F.current_timestamp().alias("ingested_at"),
        )
    )
