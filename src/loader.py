import pandas as pd
import os
import warnings

warnings.filterwarnings('ignore')

def load_and_concat_csvs(folder_path: str) -> pd.DataFrame:

    """Load all CSV files from a folder and concatenate them."""
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    csv_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    if not csv_files:
        return pd.DataFrame()
    return pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)

def preprocess_and_aggregate(demo_df, bio_df, enr_df):
    """Standardizes text, computes row totals, and aggregates to PINCODE level."""
    # 1. Standardize Strings
    for df in [demo_df, bio_df, enr_df]:
        if "district" in df.columns:
            df["district"] = df["district"].astype(str).str.upper().str.strip()
        if "state" in df.columns:
            df["state"] = df["state"].astype(str).str.upper().str.strip()

    # 2. Compute Totals per Row
    demo_df["demo_total"] = demo_df["demo_age_5_17"].astype(int) + demo_df["demo_age_17_"].astype(int)
    bio_df["bio_total"] = bio_df["bio_age_5_17"].astype(int) + bio_df["bio_age_17_"].astype(int)
    enr_df["enrol_total"] = enr_df["age_0_5"].astype(int) + enr_df["age_5_17"].astype(int) + enr_df["age_18_greater"].astype(int)

    # 3. Aggregate to PINCODE level
    demo_pin = demo_df.groupby(["pincode", "district", "state"], as_index=False)["demo_total"].sum()
    bio_pin = bio_df.groupby(["pincode", "district", "state"], as_index=False)["bio_total"].sum()
    enr_pin = enr_df.groupby(["pincode", "district", "state"], as_index=False)["enrol_total"].sum()

    return demo_pin, bio_pin, enr_pin