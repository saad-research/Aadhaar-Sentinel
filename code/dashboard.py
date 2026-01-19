# dashboard.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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
# ----------------------------
@st.cache_data
def load_data():
    sentinel = pd.read_csv("outputs/sentinel_df.csv")
    outliers = pd.read_csv("outputs/outliers_v2.csv")
    return sentinel, outliers

sentinel_df, outliers_df = load_data()

# ----------------------------
# Sidebar Filters
# ----------------------------
st.sidebar.header("Filters")

states = ["All"] + sorted(sentinel_df["state"].dropna().unique().tolist())
selected_state = st.sidebar.selectbox("Select State", states)

districts = ["All"] + sorted(sentinel_df["district"].dropna().unique().tolist())
selected_district = st.sidebar.selectbox("Select District", districts)

# Apply filters
filtered_df = sentinel_df.copy()

if selected_state != "All":
    filtered_df = filtered_df[filtered_df["state"] == selected_state]

if selected_district != "All":
    filtered_df = filtered_df[filtered_df["district"] == selected_district]

# ----------------------------
# Global thresholds (DO NOT filter these)
# ----------------------------
pna_thresh = sentinel_df["PNA"].quantile(0.98)
dpr_thresh = sentinel_df["DPR"].quantile(0.98)

# ----------------------------
# Top Metrics
# ----------------------------
col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Activity",
    f"{int(filtered_df['TAI'].sum()):,}"
)

col2.metric(
    "Outlier Pincodes",
    int(outliers_df.shape[0])
)

col3.metric(
    "High-DPR Pincodes",
    int(filtered_df[filtered_df["DPR"] > 1.5].shape[0])
)

# ----------------------------
# Tabs
# ----------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📍 Capacity Planning", "⚠️ Integrity Review", "📊 Visual Representation", "📖 Methodology"]
)

# ----------------------------
# TAB 1 — Capacity Planning
# ----------------------------
with tab1:
    st.subheader("High-Activity Regions (Population-Normalized)")

    top_pna = (
        filtered_df
        .sort_values("PNA", ascending=False)
        [["pincode", "district", "state", "TAI", "PNA"]]
        .head(20)
    )

    st.dataframe(top_pna, use_container_width=True)

    st.divider()

    st.subheader("Capacity Risk — Top Districts by PNA")

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
    st.subheader("Pincodes Requiring Review (High DPR)")

    high_dpr = (
        filtered_df
        .sort_values("DPR", ascending=False)
        [["pincode", "district", "state", "demo_total", "bio_total", "DPR"]]
        .head(20)
    )

    st.dataframe(high_dpr, use_container_width=True)

    st.divider()

    st.subheader("Integrity Risk — Top Districts by DPR")

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
# TAB 3 — Visual Representation
# ----------------------------
with tab3:
    st.subheader("Risk Composition of Flagged Pincodes")

    # Classify risk types
    risk_df = filtered_df.copy()
    risk_df["risk_type"] = "Normal"

    risk_df.loc[
        (risk_df["PNA"] >= pna_thresh) &
        (risk_df["DPR"] >= dpr_thresh),
        "risk_type"
    ] = "Dual Risk"

    risk_df.loc[
        (risk_df["PNA"] >= pna_thresh) &
        (risk_df["DPR"] < dpr_thresh),
        "risk_type"
    ] = "Capacity Risk"

    risk_df.loc[
        (risk_df["PNA"] < pna_thresh) &
        (risk_df["DPR"] >= dpr_thresh),
        "risk_type"
    ] = "Integrity Risk"

    # Keep only non-normal risks
    risk_counts = (
        risk_df[risk_df["risk_type"] != "Normal"]["risk_type"]
        .value_counts()
    )

    # Plot pie chart
    fig, ax = plt.subplots()
    ax.pie(
        risk_counts,
        labels=risk_counts.index,
        autopct="%1.1f%%",
        startangle=90
    )
    ax.set_title("Capacity vs Integrity")

    st.pyplot(fig)

# ----------------------------
# TAB 4 — Methodology
# ----------------------------
with tab4:
    st.markdown("""
    ### Metrics Used

    **TAI — Total Activity Index**  
    Enrolments + Demographic Updates + Biometric Updates

    **PNA — Population-Normalized Activity**  
    TAI / Estimated Pincode Population  
    (Population estimated using Census 2011 district proxy)

    **DPR — Demographic Pressure Ratio**  
    Demographic Updates / Biometric Updates

    ### Outlier Detection
    - Top 2% statistical outliers based on:
      - Population-normalized activity (PNA)
      - Demographic Pressure Ratio (DPR)

    ### Privacy
    - Analysis performed at pincode level  
    - No individual-level data used  
    """)

# ----------------------------
# Footer
# ----------------------------
st.caption("Aadhaar Sentinel | UIDAI Hackathon Prototype")
