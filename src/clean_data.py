# Clean the Nigeria DRE Atlas data
# Run from the project folder: python src/clean_data.py

import pandas as pd
from pathlib import Path

# ---------- SETTINGS ----------
RAW_FILE = Path("data/raw/nigeria_dre_atlas_settlements.csv")
OUT_DIR = Path("data/processed")


# ---------- LOAD ----------
def load():
    cols = pd.read_csv(RAW_FILE, nrows=0).columns
    cols = [c for c in cols if c != "geometry"]   # skip the huge shape column
    return pd.read_csv(RAW_FILE, usecols=cols)


# ---------- CLEAN ----------
def clean(df):
    # rename columns
    df = df.rename(columns={
        "admin_cgaz_1": "state",
        "admin_cgaz_2": "lga",
        "distance_to_existing_transmission_lines": "dist_transmission_km",
        "distance_to_existing_hv_transmission_lines": "dist_hv_transmission_km",
        "distance_to_gridlight_targets": "dist_gridlight_target_km",
        "demand_connection": "demand_per_connection",
    })

    #drop columns that copy other columns
    df = df.drop(columns=["num_connections", "has_education_facility", "has_health_facility"])
    return df


# ---------- RUN ----------
def main():
    df = clean(load())
    print(df.shape)
    print(df.columns.tolist())


if __name__ == "__main__":
    main()