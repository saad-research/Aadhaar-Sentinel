import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.config import OUTLIER_PERCENTILE

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="Aadhaar Sentinel",
    layout="wide"
)

st.title("🛡️ Aadhaar Sentinel")
st.caption("Decision-Support Analytics for Capacity Planning & Integrity Review")

# ----------------------------
# Load Data
# FIX: paths now match pipeline.py output locations
# ----------------------------
@st.cache_data
def load_data():
    sentinel = pd.read_csv("data/processed/sentinel_final.csv")
    outliers = pd.read_csv("data/processed/outliers_ml.csv")
    return sentinel, outliers

sentinel_df, outliers_df = load_data()

# ----------------------------
# Sidebar Filters
# ----------------------------
st.sidebar.header("Filters")

states = ["All"] + sorted(sentinel_df["state"].dropna().unique().tolist())
selected_state = st.sidebar.selectbox("Select State", states)

# District filter cascades from state selection
if selected_state != "All":
    district_pool = sentinel_df[sentinel_df["state"] == selected_state]
else:
    district_pool = sentinel_df

districts = ["All"] + sorted(district_pool["district"].dropna().unique().tolist())
selected_district = st.sidebar.selectbox("Select District", districts)

# Apply filters
filtered_df = sentinel_df.copy()

if selected_state != "All":
    filtered_df = filtered_df[filtered_df["state"] == selected_state]

if selected_district != "All":
    filtered_df = filtered_df[filtered_df["district"] == selected_district]

# ----------------------------
# Global thresholds — always computed on FULL dataset, not filtered
# FIX: use OUTLIER_PERCENTILE from config instead of hardcoded 0.98
# ----------------------------
pna_thresh = sentinel_df["PNA"].quantile(OUTLIER_PERCENTILE)
dpr_thresh = sentinel_df["DPR"].quantile(OUTLIER_PERCENTILE)

# ----------------------------
# Top Metrics
# ----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Activity (Filtered)",
    f"{int(filtered_df['TAI'].sum()):,}"
)

col2.metric(
    "ML-Flagged Anomalies (National)",
    int(outliers_df.shape[0])
)

col3.metric(
    "High-DPR Pincodes (Filtered)",
    int(filtered_df[filtered_df["DPR"] >= dpr_thresh].shape[0])
)

col4.metric(
    "High-PNA Pincodes (Filtered)",
    int(filtered_df[filtered_df["PNA"] >= pna_thresh].shape[0])
)

st.divider()

# ----------------------------
# Tabs
# ----------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📍 Capacity Planning", "⚠️ Integrity Review", "📊 Risk Composition", "📖 Methodology"]
)

# ----------------------------
# TAB 1 — Capacity Planning
# ----------------------------
with tab1:
    st.subheader("High-Activity Regions (Population-Normalised)")
    st.caption("PNA > 1.0 indicates total enrollment activity exceeds estimated resident population.")

    top_pna = (
        filtered_df
        .sort_values("PNA", ascending=False)
        [["pincode", "district", "state", "TAI", "PNA"]]
        .head(20)
    )

    st.dataframe(top_pna, use_container_width=True)
    st.divider()

    st.subheader("Top 10 Districts by Average PNA")

    top_pna_chart = (
        filtered_df
        .groupby("district", as_index=False)["PNA"]
        .mean()
        .sort_values("PNA", ascending=False)
        .head(10)
        .set_index("district")
    )

    st.bar_chart(top_pna_chart)

# ----------------------------
# TAB 2 — Integrity Review
# ----------------------------
with tab2:
    st.subheader("Pincodes Requiring Audit Review (High DPR)")
    st.caption(
        "High DPR indicates demographic attribute updates occurring without corresponding "
        "biometric re-verification. This is a process anomaly flag, not a fraud determination."
    )

    high_dpr = (
        filtered_df
        .sort_values("DPR", ascending=False)
        [["pincode", "district", "state", "demo_total", "bio_total", "DPR"]]
        .head(20)
    )

    st.dataframe(high_dpr, use_container_width=True)
    st.divider()

    st.subheader("Top 10 Districts by Average DPR")

    top_dpr_chart = (
        filtered_df
        .groupby("district", as_index=False)["DPR"]
        .mean()
        .sort_values("DPR", ascending=False)
        .head(10)
        .set_index("district")
    )

    st.bar_chart(top_dpr_chart)

# ----------------------------
# TAB 3 — Risk Composition
# ----------------------------
with tab3:
    st.subheader("Risk Type Composition of Flagged Pincodes")
    st.caption(f"Thresholds: PNA ≥ {pna_thresh:.4f} (98th percentile), DPR ≥ {dpr_thresh:.4f} (98th percentile)")

    risk_df = filtered_df.copy()
    risk_df["risk_type"] = "Normal"

    risk_df.loc[
        (risk_df["PNA"] >= pna_thresh) & (risk_df["DPR"] >= dpr_thresh),
        "risk_type"
    ] = "Dual Risk (Critical)"

    risk_df.loc[
        (risk_df["PNA"] >= pna_thresh) & (risk_df["DPR"] < dpr_thresh),
        "risk_type"
    ] = "Capacity Risk"

    risk_df.loc[
        (risk_df["PNA"] < pna_thresh) & (risk_df["DPR"] >= dpr_thresh),
        "risk_type"
    ] = "Integrity Anomaly"

    risk_counts = (
        risk_df[risk_df["risk_type"] != "Normal"]["risk_type"]
        .value_counts()
    )

    col_left, col_right = st.columns(2)

    with col_left:
        fig, ax = plt.subplots(figsize=(5, 5))
        colors = ["#800080", "#003366", "#8B0000"]
        ax.pie(
            risk_counts,
            labels=risk_counts.index,
            autopct="%1.1f%%",
            startangle=90,
            colors=colors[:len(risk_counts)]
        )
        ax.set_title("Capacity vs Integrity Anomaly Split")
        st.pyplot(fig)

    with col_right:
        st.dataframe(
            risk_counts.reset_index().rename(
                columns={"index": "Risk Type", "risk_type": "Count"}
            ),
            use_container_width=True
        )

        # FIX: show ML vs statistical comparison
        st.divider()
        st.markdown("**Detection Method Comparison (National)**")
        stat_count = sentinel_df[
            (sentinel_df["TAI"] >= sentinel_df["TAI"].quantile(OUTLIER_PERCENTILE)) |
            (sentinel_df["DPR"] >= dpr_thresh) |
            (sentinel_df["PNA"] >= pna_thresh)
        ].shape[0]

        ml_count = outliers_df.shape[0]

        if "pincode" in outliers_df.columns:
            stat_flags = set(
                sentinel_df[
                    (sentinel_df["TAI"] >= sentinel_df["TAI"].quantile(OUTLIER_PERCENTILE)) |
                    (sentinel_df["DPR"] >= dpr_thresh) |
                    (sentinel_df["PNA"] >= pna_thresh)
                ]["pincode"].astype(str)
            )
            ml_flags = set(outliers_df["pincode"].astype(str))
            overlap = len(stat_flags & ml_flags)
        else:
            overlap = "N/A"

        st.markdown(f"""
        | Method | Flagged |
        |---|---|
        | Statistical (98th pct) | {stat_count:,} |
        | Isolation Forest (ML) | {ml_count:,} |
        | Overlap (high-confidence) | {overlap} |
        """)

# ----------------------------
# TAB 4 — Methodology
# ----------------------------
with tab4:
    st.markdown("""
    ### Core Metrics

    **TAI — Total Activity Index**
    ```
    TAI = Enrolments + Demographic Updates + Biometric Updates
    ```
    Measures overall operational throughput per PINCODE.

    **DPR — Demographic Pressure Ratio**
    ```
    DPR = Demographic Updates / (Biometric Updates + 1)
    ```
    Process integrity proxy. The +1 prevents division by zero.
    A high DPR indicates demographic attribute changes occurring without
    corresponding biometric re-verification.

    **PNA — Population-Normalised Activity**
    ```
    PNA = TAI / Estimated PINCODE Population
    ```
    Capacity stress indicator. PNA > 1.0 indicates activity exceeding
    estimated resident population.

    **Population Estimation**

    Estimated PINCODE population = District Population (Census 2011) ÷
    number of PINKCODEs in district. PNA is reported with uncertainty
    bounds (±20% growth factor) to account for the age of this estimate.

    ---

    ### Anomaly Detection

    **Method 1 — Statistical Baseline**
    PINKCODEs exceeding the 98th percentile on TAI, DPR, or PNA (union).

    **Method 2 — Isolation Forest (Primary)**
    `sklearn IsolationForest` trained on joint feature space (TAI, DPR, PNA)
    with contamination=0.02. Identifies multivariate anomalies.
    The raw isolation score is retained for continuous ranking within
    the flagged set.

    ---

    ### Composite Risk Score

    ```
    audit_priority_score = (dpr_z × 0.50) + (pna_z × 0.35) + (activity_z × 0.15)
    ```

    Z-score normalised. Weights reflect audit priority: integrity anomalies
    (DPR) are weighted highest as they indicate process non-compliance.

    ---

    ### Limitations

    - Population estimates use Census 2011 data; PNA carries ~20% uncertainty
      in high-growth urban districts
    - DPR anomalies indicate statistical deviation, not confirmed irregularity
    - Ground-truth audit outcomes required to formally evaluate precision/recall
    - Analysis is cross-sectional; temporal trends are not yet modelled

    ---

    ### Privacy

    All analysis is performed on aggregated PINCODE or district-level data.
    No Aadhaar numbers, biometric templates, or individual records are
    processed at any stage.
    """)

# ----------------------------
# Footer
# ----------------------------
st.caption("Aadhaar Sentinel | Geospatial Risk Analytics Engine")