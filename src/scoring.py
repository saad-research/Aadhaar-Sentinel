# src/scoring.py
import pandas as pd
from scipy.stats import zscore
from sklearn.ensemble import IsolationForest
from src.config import (
    OUTLIER_PERCENTILE, WEIGHT_DPR, WEIGHT_PNA,
    WEIGHT_ACTIVITY, POP_GROWTH_FACTOR_MAX
)


def compute_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replaces ad-hoc scoring with Z-score normalized composite.
    Weights are documented in config.py.
    """
    df = df.copy()
    df["dpr_z"] = zscore(df["DPR"].fillna(0))
    df["pna_z"] = zscore(df["PNA"].fillna(0))
    df["activity_z"] = zscore(df["TAI"].fillna(0))

    df["audit_priority_score"] = (
        df["dpr_z"] * WEIGHT_DPR
        + df["pna_z"] * WEIGHT_PNA
        + df["activity_z"] * WEIGHT_ACTIVITY
    )
    # Shift to positive range for readability
    df["audit_priority_score"] -= df["audit_priority_score"].min()
    return df


def flag_anomalies_statistical(df: pd.DataFrame) -> pd.DataFrame:
    """Percentile-based baseline. Kept for comparison against ML method."""
    tai_t = df["TAI"].quantile(OUTLIER_PERCENTILE)
    dpr_t = df["DPR"].quantile(OUTLIER_PERCENTILE)
    pna_t = df["PNA"].quantile(OUTLIER_PERCENTILE)

    mask = (df["TAI"] >= tai_t) | (df["DPR"] >= dpr_t) | (df["PNA"] >= pna_t)
    outliers = df[mask].copy()
    outliers["detection_method"] = "statistical_percentile"
    return outliers


def flag_anomalies_isolation_forest(df: pd.DataFrame) -> pd.DataFrame:
    """
    Isolation Forest anomaly detection.
    contamination=0.02 mirrors the 98th percentile baseline for comparison.
    """
    features = ["DPR", "PNA", "TAI"]
    X = df[features].fillna(0)

    model = IsolationForest(
        n_estimators=200,
        contamination=1 - OUTLIER_PERCENTILE,
        random_state=42
    )
    df = df.copy()
    df["anomaly_score"] = model.fit_predict(X)
    df["iso_score"] = model.decision_function(X)  # Raw score, useful for ranking

    outliers = df[df["anomaly_score"] == -1].copy()
    outliers["detection_method"] = "isolation_forest"
    return outliers


def add_population_uncertainty(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds PNA uncertainty bounds to account for outdated Census 2011 data.
    Addresses the limitation that urban populations have grown since 2011.
    """
    df = df.copy()
    df["PNA_conservative"] = df["TAI"] / df["est_pincode_pop"]
    df["PNA_upper_bound"] = df["TAI"] / (
        df["est_pincode_pop"] * POP_GROWTH_FACTOR_MAX
    )
    return df