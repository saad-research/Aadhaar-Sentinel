# Aadhaar Sentinel
### Geospatial Risk Analytics for National Identity Infrastructure

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat-square&logo=streamlit)](https://streamlit.io)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-IsolationForest-F7931E?style=flat-square&logo=scikit-learn)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)]()

---

> **Aadhaar Sentinel** is a dual-metric geospatial analytics framework that distinguishes between *infrastructure capacity stress* and *demographic update anomalies* across India's national identity enrollment network — transitioning audit mechanisms from reactive complaint-based selection to ML-augmented severity-based prioritization.


## The Problem

India's Aadhaar network processes over **221 crore monthly authentication transactions** across 32,898 PINCODE-level enrollment centers. Traditional audit governance relies on complaint volume to prioritize inspections — a method that structurally fails in two ways:

1. **It misses Silent Anomalies** — low-volume centers processing thousands of demographic updates without corresponding biometric verification, invisible to volume-based scanners.
2. **It cannot separate causes** — a district showing high update activity may be experiencing infrastructure overload, process irregularity, or both simultaneously. These require completely different operational responses.

No existing public analytics framework applies multivariate anomaly detection to distinguish between these failure modes at PINCODE resolution.


## What Sentinel Does Differently

Most government data analytics pipelines aggregate to state or district level and rank by raw volume. Sentinel introduces three changes:

| Conventional Approach | Sentinel Approach |
|---|---|
| Volume-based ranking | Severity-weighted composite scoring (Z-normalized) |
| Single-metric flagging | Dual-metric separation (Capacity vs. Integrity) |
| Percentile thresholds | Isolation Forest multivariate anomaly detection |
| Static district maps | Interactive PINCODE-resolution geospatial dashboard |
| Point estimates | Population uncertainty bounds (Census 2011 ± growth factor) |


## Architecture

```
aadhaar-sentinel/
├── src/
│   ├── config.py          # Centralised thresholds, weights, paths
│   ├── loader.py          # Raw CSV ingestion and normalisation
│   ├── engine.py          # Metric computation (TAI, DPR, PNA)
│   ├── scoring.py         # Anomaly detection (statistical + Isolation Forest)
│   └── maps.py            # Folium map generation
├── data/
│   ├── raw/               # UIDAI source datasets (gitignored)
│   └── processed/         # Generated CSVs
├── outputs/maps/          # Interactive HTML maps
├── notebooks/             # Exploratory analysis only
├── tests/                 # Unit tests for core pipeline
├── app.py                 # Streamlit dashboard
├── pipeline.py            # End-to-end pipeline runner
└── requirements.txt
```


## Core Metrics

Sentinel derives three risk indicators at the PINCODE level:

**1. Total Activity Index (TAI)**
```
TAI = Enrolments + Demographic Updates + Biometric Updates
```
Measures overall operational throughput. Used to weight anomaly scores.

**2. Demographic Pressure Ratio (DPR)**
```
DPR = Demographic Updates / (Biometric Updates + 1)
```
Process integrity proxy. A high DPR indicates demographic attribute changes (name, address, date of birth) occurring without corresponding biometric re-verification — a pattern requiring audit investigation.

**3. Population-Normalised Activity (PNA)**
```
PNA = TAI / Estimated PINCODE Population
```
Capacity stress indicator. Values above 1.0 indicate total enrollment activity exceeding the estimated resident population — signaling extreme infrastructure demand or cross-boundary footfall.

**Population Estimation:**
Estimated PINCODE population is derived as District Population (Census 2011) ÷ number of PINKCODEs in district. To account for the age of this estimate, PNA is reported with uncertainty bounds assuming 0–20% population growth, producing `PNA_conservative` and `PNA_upper_bound` columns.


## Anomaly Detection

Sentinel implements and compares two detection methodologies:

### Method 1 — Statistical Baseline (Percentile Thresholding)
PINKCODEs exceeding the **98th percentile** on any of TAI, DPR, or PNA are flagged. This is interpretable and reproducible but treats each metric independently and cannot capture multivariate anomaly structure.

### Method 2 — Isolation Forest (Primary)
An `IsolationForest` model (scikit-learn) is trained on the joint feature space `(TAI, DPR, PNA)` with `contamination=0.02`, mirroring the 98th percentile baseline for direct comparison. Isolation Forest identifies anomalies by measuring how quickly a point can be *isolated* via random feature splits — points that require fewer splits are structural outliers in the multivariate space.

```python
model = IsolationForest(n_estimators=200, contamination=0.02, random_state=42)
df["anomaly_score"] = model.fit_predict(X)   # -1 = anomaly
df["iso_score"]     = model.decision_function(X)  # Raw isolation score
```

The raw `iso_score` is retained for continuous ranking — a point with iso_score = -0.3 is a stronger anomaly than one at -0.05, enabling prioritization within the flagged set.

### Composite Risk Scoring
Final audit priority is determined by a Z-score normalised weighted composite:

```python
audit_priority_score = (dpr_z × 0.50) + (pna_z × 0.35) + (activity_z × 0.15)
```

Weights are documented in `src/config.py` and justified by audit logic: DPR anomalies represent process non-compliance (highest audit urgency), PNA anomalies represent infrastructure stress (operational response), and TAI represents overall load context.


## Key Findings

Analysis of **4.9 million PINCODE-level transactions** across **33,304 PINCODE locations** identified five risk patterns:

| Risk Category | Location | Key Metric | Finding |
|---|---|---|---|
| **Critical Dual Risk** | West Delhi | PNA: 6.1, DPR: 12.2 | Operating at ~610% estimated capacity; elevated demographic anomaly rate masks irregular update patterns |
| **Critical Dual Risk** | North East Delhi | PNA: 5.4, DPR: 1.6 | 537% capacity overload; requires structural kit reallocation |
| **High-DPR Anomaly Cluster** | Ahilyanagar | DPR: 193.0, PNA: 0.006 | 193 demographic updates per biometric scan; negligible load suggests targeted process irregularity |
| **Capacity Deficit** | Moradabad | PNA: 6.3, DPR: 1.3 | Highest capacity deficit nationally; near-normal DPR isolates this as infrastructure, not integrity |
| **Border Corridor Anomaly** | Sribhumi (Assam) | DPR: 77.0 | High demographic churn in northeastern border corridor; consistent with elevated residency-status adjustments |

> **Methodological Note:** High DPR is classified as a *process anomaly requiring audit investigation*, not as evidence of fraud. Ground-truth labeling is required to distinguish between operator error, data entry patterns, and intentional irregularity.

**Detection method validation:** Isolation Forest flagged 667 multivariate anomalies; 647 (97%) were independently confirmed by the statistical baseline, forming a high-confidence audit target set. Statistical thresholding flagged 1,702 univariate outliers — the 1,055 unique to the statistical method represent single-metric extremes without multivariate anomaly structure.

**Severity-weighted scoring surfaced findings invisible to volume-based auditing:** Ahilyanagar (DPR: 193) would not appear in a top-20 complaint-volume audit. Mahabubabad showed extreme deviation despite negligible total volume. Tier-2/3 cities are systematically underweighted by conventional methods.

## Dashboard

An interactive Streamlit dashboard provides four decision-support views:

- **Capacity Planning** — district-level PNA rankings, top-10 bar chart
- **Integrity Review** — high-DPR PINCODE drill-down with update breakdown
- **Risk Composition** — classification of flagged PINKCODEs by risk type,
  plus detection method comparison (Statistical vs Isolation Forest)
- **Methodology** — full metric definitions, limitations, and epistemic caveats

Geospatial outputs (national surveillance map and top-20 audit targets map)
are generated as interactive HTML files in `outputs/maps/` by `pipeline.py`.

**Run locally:**
```bash
# 1. Generate processed data
python pipeline.py

# 2. Launch dashboard
streamlit run app.py
```


## Quick Start

**Requirements:** Python 3.9+, Jupyter (optional, for notebooks)

```bash
# Clone the repository
git clone https://github.com/saad-research/aadhaar-sentinel.git
cd aadhaar-sentinel

# Install dependencies
pip install -r requirements.txt

# Place UIDAI CSV folders in data/raw/
# Place district population CSV in data/raw/Census_2011.csv
# (Source: india-districts-census-2011 dataset, columns: 'District name', 'State name', 'Population')

# Run the full pipeline
python pipeline.py

# Launch dashboard
streamlit run app.py

# Run tests
python -m pytest tests/ -v
```


## Data Sources

| Dataset | Source | Granularity |
|---|---|---|
| Aadhaar Enrolment Data | UIDAI Open Data Portal | PINCODE × Quarter |
| Demographic Update Data | UIDAI Open Data Portal | PINCODE × Quarter |
| Biometric Update Data | UIDAI Open Data Portal | PINCODE × Quarter |
| District Population | Census of India 2011 | District |
| District Coordinates | Public GitHub (Saravanan Suriya) | District centroid |

All analysis is performed on aggregated, non-personal data. No Aadhaar numbers, biometric templates, or individual records are processed at any stage.


## Privacy & Ethical Considerations

This project processes only **publicly available, aggregated government data** at PINCODE or district level. No Personally Identifiable Information is used or derivable from the outputs.

**Epistemic constraints acknowledged:**
- Population estimates use 2011 Census data; PNA values for high-growth urban districts carry ~20% uncertainty
- DPR anomalies indicate statistical deviation from regional norms, not confirmed irregularity
- Ground-truth audit outcomes would be required to validate detection precision


## Limitations & Future Work

**Current limitations:**
- Temporal data not yet available; all analysis is cross-sectional (single snapshot)
- Census 2011 population estimates introduce systematic PNA uncertainty in high-growth urban areas
- Isolation Forest operates without labeled anomaly data; precision/recall cannot be formally evaluated without audit ground truth

**Planned extensions:**
- Time-series anomaly detection on quarterly transaction data (Prophet / LSTM)
- DBSCAN geographic clustering to detect coordinated multi-PINCODE anomaly patterns
- Sensitivity analysis: ablation study comparing Isolation Forest vs. Local Outlier Factor vs. DBSCAN
- Integration with UIDAI's official population registry APIs to replace Census proxy

## Tech Stack

| Component | Technology |
|---|---|
| Data Engineering | Python, Pandas, NumPy |
| Anomaly Detection | scikit-learn (Isolation Forest) |
| Statistical Analysis | SciPy (Z-score normalisation) |
| Geospatial Visualisation | Folium, HeatMap plugin |
| Interactive Dashboard | Streamlit |
| Testing | pytest |
| Version Control | Git |


## Project Structure Rationale

The codebase is organised around separation of concerns:

- **`src/config.py`** — all tunable parameters (thresholds, weights, paths) in one place; no magic numbers in pipeline code
- **`src/engine.py`** — pure metric calculation with no scoring logic
- **`src/scoring.py`** — anomaly detection and composite scoring as a separate, testable module
- **`pipeline.py`** — single entry point to regenerate all processed data; `app.py` only reads, never transforms


## Acknowledgements

Population estimation methodology uses Census of India 2011 district statistics as a scalable proxy for PINCODE-level population. This approach is appropriate for policy-level prototyping and capacity simulation; production deployment would require official UIDAI or state civil registry data.


## License

MIT License. See [LICENSE](LICENSE) for details.

---

*Built as part of applied research in privacy-preserving analytics and AI security.*