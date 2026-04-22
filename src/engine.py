import pandas as pd
from src.config import POPULATION_COLUMN, CENSUS_FALLBACK_POP

def calculate_base_metrics(demo_pin, bio_pin, enr_pin, district_pop_df):
    # Merge datasets
    df = demo_pin.merge(bio_pin, on=["pincode", "district", "state"], how="outer") \
                 .merge(enr_pin, on=["pincode", "district", "state"], how="outer") \
                 .fillna(0)
    
    # Ensure 6-digit pincode strings
    df["pincode"] = df["pincode"].astype(str).str.split('.').str[0].str.zfill(6)
    
    # Calculate TAI and DPR
    df["TAI"] = df["demo_total"] + df["bio_total"] + df["enrol_total"]
    df["DPR"] = df["demo_total"] / (df["bio_total"] + 1)
    
    # Estimate Population and calculate PNA
    district_pop_df = district_pop_df.rename(columns={"District name": "district", "State name": "state"})
    district_pop_df["district"] = district_pop_df["district"].astype(str).str.upper().str.strip()
    
    pin_counts = df.groupby("district")["pincode"].nunique().reset_index(name="pin_count")
    district_stats = pin_counts.merge(district_pop_df, on="district", how="left")
    district_stats["est_pincode_pop"] = district_stats[POPULATION_COLUMN] / district_stats["pin_count"]
    district_stats["est_pincode_pop"] = district_stats["est_pincode_pop"].fillna(CENSUS_FALLBACK_POP)
    
    df = df.merge(district_stats[["district", "est_pincode_pop"]], on="district", how="left")
    district_stats["est_pincode_pop"] = district_stats["est_pincode_pop"].fillna(CENSUS_FALLBACK_POP)
    
    df["PNA"] = df["TAI"] / df["est_pincode_pop"]
    
    return df