"""
adaptive-island/training/train.py

Train the optional MLflow value-prediction model from Silver and register the
latest version in Models in Unity Catalog for offline analysis/promotion review.

This follows BabySea's documented production pattern: the customer request path
uses Upstash-cached Gold rankings when adaptive routing is enabled, and falls
back to the static provider order when disabled or unavailable. The request path
does not call Databricks Model Serving.
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime, timedelta

import mlflow
import mlflow.sklearn
from mlflow.models.signature import infer_signature
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# How far back to look for training and evaluation rows.
TRAIN_WINDOW_DAYS = 28
COST_PENALTY = 0.5
LATENCY_PENALTY = 0.3


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--catalog", required=True)
    p.add_argument("--region", required=True)
    p.add_argument(
        "--min-train-rows",
        type=int,
        default=100,
        help="Skip training if Silver has fewer rows than this. Raise in production.",
    )
    return p.parse_args()


def _load_silver(spark, catalog: str, since: datetime):
    return (
        spark.read.table(f"`{catalog}`.medallion.silver_provider_attempts")
        .where(f"submitted_at >= TIMESTAMP'{since.isoformat()}'")
        .where("outcome IN ('used', 'failed', 'discarded', 'cancelled')")
        .toPandas()
    )


def _build_feature_frame(df):
    """Pull the compact documented feature set out of Silver."""
    df = df.copy()
    df["hour_of_day"] = df["submitted_at"].dt.hour
    # Spark dayofweek uses 1 = Sunday ... 7 = Saturday. Keep the same convention.
    df["day_of_week"] = df["submitted_at"].dt.dayofweek + 1
    return df[["provider", "model", "hour_of_day", "day_of_week"]].copy()


def _build_target(df):
    latency = df["latency_ms"].dropna()
    latency_p95 = latency.quantile(0.95) if not latency.empty else 1.0
    latency_p95 = max(float(latency_p95), 1.0)
    latency_norm = (df["latency_ms"].fillna(latency_p95) / latency_p95).clip(0, 1)
    return (
        df["is_success"].astype(float) * 1.0
        - df["is_wasted"].astype(float) * COST_PENALTY
        - latency_norm * LATENCY_PENALTY
    )


def main() -> int:
    args = _parse_args()
    catalog = args.catalog
    region = args.region
    model_name = f"{catalog}.ml.predictive_routing"
    experiment = f"/Shared/adaptive-island/{region}"

    from pyspark.sql import SparkSession

    spark = SparkSession.builder.getOrCreate()
    mlflow.set_registry_uri("databricks-uc")
    mlflow.set_experiment(experiment)

    now = datetime.now(UTC)
    train_since = now - timedelta(days=TRAIN_WINDOW_DAYS)

    train_df = _load_silver(spark, catalog, train_since)

    if len(train_df) < args.min_train_rows:
        print(
            f"adaptive-island: not enough training rows "
            f"({len(train_df)} < {args.min_train_rows}); skipping."
        )
        return 0

    with mlflow.start_run(run_name=f"adaptive-island-{region}-{now.isoformat()}") as run:
        mlflow.log_param("region", region)
        mlflow.log_param("train_window_days", TRAIN_WINDOW_DAYS)
        mlflow.log_param("cost_penalty", COST_PENALTY)
        mlflow.log_param("latency_penalty", LATENCY_PENALTY)
        mlflow.log_metric("train_rows", len(train_df))

        X_train = _build_feature_frame(train_df)
        y_train = _build_target(train_df)

        preproc = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore"), ["provider", "model"]),
                ("num", "passthrough", ["hour_of_day", "day_of_week"]),
            ]
        )
        model = Pipeline(
            [
                ("preproc", preproc),
                (
                    "model",
                    GradientBoostingRegressor(
                        n_estimators=200,
                        max_depth=4,
                        learning_rate=0.05,
                        random_state=42,
                    ),
                ),
            ]
        )
        model.fit(X_train, y_train)

        preds = model.predict(X_train)
        mlflow.log_metric("train_mse", mean_squared_error(y_train, preds))
        mlflow.log_metric("train_r2", r2_score(y_train, preds))
        mlflow.log_param(
            "seen_providers",
            ",".join(sorted(train_df["provider"].dropna().unique().tolist()))[:500],
        )
        mlflow.log_param("seen_models_count", len(train_df["model"].dropna().unique()))

        signature = infer_signature(X_train.head(20), model.predict(X_train.head(20)))
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name=model_name,
            signature=signature,
        )

        client = mlflow.MlflowClient()
        latest = max(
            client.search_model_versions(f"name='{model_name}'"),
            key=lambda v: int(v.version),
        )
        client.set_registered_model_alias(model_name, "production", latest.version)
        mlflow.set_tag("registered_alias", "production")
        print(
            f"adaptive-island: training run {run.info.run_id} registered "
            f"{model_name} v{latest.version} -> alias 'production'"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
