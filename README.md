# Aadhaar Sentinel: Intelligence-Driven Capacity Planning & Integrity Review

**Team:** Team Sentinel
**Event:** UIDAI Hackathon 2026
**Domain:** Capacity Planning & Database Integrity

![Project Status](https://img.shields.io/badge/Status-Completed-success)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Focus](https://img.shields.io/badge/Focus-Geospatial_Analytics-orange)

---

## Executive Summary
As UIDAI scales to support **221 crore monthly authentications** and prepares for the mandatory biometric update (MBU) of **6 crore children** by September 2026, operational efficiency and database integrity are paramount.

**Aadhaar Sentinel** is a geospatial analytics framework designed to secure this mission. By analyzing **4.9 million pincode-level transactions** across **32,898 locations**, we have developed a dual-metric risk engine that distinguishes between **Capacity Stress** (operational bottlenecks) and **Integrity Risks** (suspicious demographic updates).

Our system transitions audit mechanisms from reactive "Complaint-Based" selection to predictive **"Severity-Based" prioritization**.

---

## Key Innovations

### 1. Dual-Metric Risk Engine
We moved beyond simple volume metrics to measure *pressure* and *anomaly*:
* **Capacity Engine (PNA):** Uses **Population-Normalized Activity** to identify districts where infrastructure is overwhelmed (e.g., West Delhi operating at 610% capacity).
* **Integrity Engine (DPR):** Uses the **Demographic Pressure Ratio** to detect "Silent Fraud"—centers processing thousands of name/address changes without corresponding biometric scans.

### 2. Severity-Weighted Prioritization
Traditional audits focus on "Top 10 by Complaint Volume." This misses hidden risks in smaller towns.
* **Our Solution:** A weighted scoring algorithm (`Score = Count + 2*DPR + 50*PNA`) that successfully surfaced **Mahabubabad** (Hidden Integrity Risk) and **West Delhi** (Dual Crisis) as top national priorities.

---

## Key Findings

| Risk Type | District | Metric | Insight |
| :--- | :--- | :--- | :--- |
| **Dual Crisis** | **West Delhi** | **610% Load** | Overcrowding is likely masking bulk demographic fraud. |
| **Silent Fraud** | **Ahilyanagar** | **DPR 193.0** | 193 demographic updates per 1 biometric scan. Highly suspicious. |
| **Capacity Collapse** | **Moradabad** | **PNA 6.31** | Highest infrastructure deficit in India. Needs urgent kit allocation. |
| **Border Risk** | **Sribhumi** | **DPR 77.0** | Abnormal demographic churn in a sensitive border corridor. |

---

## Quick Start Guide

# Prerequisites

* Python 3.8+
* Jupyter Notebook or VS Code
* Libraries: pandas, folium, numpy

# 1. Installation

Clone the repository:

```
git clone [https://github.com/saad-research/Aadhaar-Sentinel.git](https://github.com/saad-research/Aadhaar-Sentinel.git)
cd Aadhaar-Sentinel
```
# 2. Install dependencies:

```
pip install -r 01_Code/requirements.txt
```

# 3. Run the Analysis:

* Open 01_Code/aadhaar_sentinel_analysis.ipynb
* Run all cells to regenerate the datasets and maps

# 4. View the Maps:

* Navigate to 02_Outputs/ and open audit_targets_map.html in your web browser to interact with the findings.

---

## Strategic Alignment with UIDAI Goals

* Database Integrity: Directly supports the Deceased Aadhaar Deactivation drive by flagging high-DPR centers (potential death evasion/identity fraud).
* MBU Campaign: Supports the 6 Crore Biometric Update goal by identifying capacity bottlenecks (High PNA) for targeted kit deployment.
* Operational Intelligence: Provides a Geospatial Dashboard for District Magistrates to view real-time risk heatmaps.

----

## Contributors

**Team Sentinel**

- Mohammed Saad Shareef - Lead Data Scientist & Architect
- Syed Ahsan Ahmed – Security Lead & Integrity Intelligence
