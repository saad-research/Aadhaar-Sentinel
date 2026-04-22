# tests/test_engine.py
import pandas as pd
import pytest
from src.scoring import compute_risk_score, flag_anomalies_statistical


def make_dummy_df():
    return pd.DataFrame({
        "pincode": ["110001", "110002", "110003"],
        "district": ["WEST DELHI", "EAST DELHI", "NORTH DELHI"],
        "state": ["DELHI", "DELHI", "DELHI"],
        "demo_total": [5000, 100, 200],
        "bio_total": [10, 90, 180],
        "enrol_total": [500, 300, 400],
        "TAI": [5510, 490, 780],
        "DPR": [500.0, 1.1, 1.1],
        "PNA": [6.1, 0.05, 0.08],
        "est_pincode_pop": [1000, 1000, 1000],
    })


def test_risk_score_column_exists():
    df = compute_risk_score(make_dummy_df())
    assert "audit_priority_score" in df.columns


def test_high_dpr_ranks_high():
    df = compute_risk_score(make_dummy_df())
    top = df.sort_values("audit_priority_score", ascending=False).iloc[0]
    assert top["district"] == "WEST DELHI"


def test_statistical_outliers_not_empty():
    df = flag_anomalies_statistical(make_dummy_df())
    assert len(df) > 0