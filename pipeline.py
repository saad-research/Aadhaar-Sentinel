import os
import pandas as pd
from src import config
from src.loader import load_and_concat_csvs, preprocess_and_aggregate
from src.engine import calculate_base_metrics
from src.scoring import compute_risk_score, flag_anomalies_isolation_forest, flag_anomalies_statistical, add_population_uncertainty

def run():
    print("Loading data...")
    demo_df = load_and_concat_csvs(os.path.join(config.RAW_DATA_DIR, "aadhaar_demographic_updates"))
    bio_df = load_and_concat_csvs(os.path.join(config.RAW_DATA_DIR, "aadhaar_biometric_update_pincode"))
    enr_df = load_and_concat_csvs(os.path.join(config.RAW_DATA_DIR, "aadhaar_enrolment_pincode"))
    district_pop = pd.read_csv(config.CENSUS_PATH)

    print("Processing...")
    demo_pin, bio_pin, enr_pin = preprocess_and_aggregate(demo_df, bio_df, enr_df)
    base_df = calculate_base_metrics(demo_pin, bio_pin, enr_pin, district_pop)
    
    print("Scoring and Anomaly Detection...")
    scored_df = compute_risk_score(base_df)
    scored_df = add_population_uncertainty(scored_df)
    
    outliers_stat = flag_anomalies_statistical(scored_df)
    outliers_ml = flag_anomalies_isolation_forest(scored_df)
    
    os.makedirs(config.PROCESSED_DIR, exist_ok=True)
    scored_df.to_csv(os.path.join(config.PROCESSED_DIR, "sentinel_final.csv"), index=False)
    outliers_ml.to_csv(os.path.join(config.PROCESSED_DIR, "outliers_ml.csv"), index=False)
    
    print("Pipeline complete.")

if __name__ == "__main__":
    run()