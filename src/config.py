# src/config.py
# All tunable parameters in one place.
# Change thresholds here, nowhere else.

OUTLIER_PERCENTILE = 0.98

# Scoring weights — justified by audit priority:
# Integrity anomalies (DPR) weighted highest because they indicate
# process non-compliance, which is harder to detect and higher risk.
WEIGHT_DPR = 0.50
WEIGHT_PNA = 0.35
WEIGHT_ACTIVITY = 0.15

# Census fallback: estimated population for pincodes with no district match
CENSUS_FALLBACK_POP = 30_000

# Population uncertainty band: Census 2011 data, adjusted for ~15 years growth
POP_GROWTH_FACTOR_MIN = 1.0   # Conservative (no growth assumed)
POP_GROWTH_FACTOR_MAX = 1.20  # Upper bound (20% urban growth estimate)

# Paths
RAW_DATA_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
OUTPUT_DIR = "outputs/maps"

CENSUS_PATH = "data/raw/Census_2011.csv"
POPULATION_COLUMN = "Population"

LATLON_PATH = "data/raw/india_district_latlon.csv"