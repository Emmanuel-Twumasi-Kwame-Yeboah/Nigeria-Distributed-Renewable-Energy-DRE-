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
        
        #mark which values were empty (1 = empty, 0 = filled)
    df["rwi_missing"] = df["mean_rwi"].isna().astype(int)
    df["hub_missing"] = df["nearest_hub_name"].isna().astype(int)

        #fill the one empty solar value with the middle value of its LGA
    lga_middle = df.groupby(["state", "lga"])["pv_value"].transform("median")
    df["pv_value"] = df["pv_value"].fillna(lga_middle)

        #change True/False into 1/0
    df["main_road_access"] = df["main_road_access"].astype(int)

        #split the text "11;0;3;0" into 4 number columns (25 km)
    parts = df["fatalities_within_25km"].str.split(";", expand=True).astype(int)




    parts.columns = ["fatal25_p1", "fatal25_p2", "fatal25_p3", "fatal25_p4"]




    df = pd.concat([df, parts], axis=1)




    df["fatal25_total"] = parts.sum(axis=1)



    
    df = df.drop(columns=["fatalities_within_25km"])

        #split the text into 4 number columns (50 km)
    parts = df["fatalities_within_50km"].str.split(";", expand=True).astype(int)
    parts.columns = ["fatal50_p1", "fatal50_p2", "fatal50_p3", "fatal50_p4"]
    df = pd.concat([df, parts], axis=1)
    df["fatal50_total"] = parts.sum(axis=1)
    df = df.drop(columns=["fatalities_within_50km"])
    return df


# ---------- RUN ----------
def main():
    df = clean(load())
    print(df.shape)
    print(df.loc[0, ["fatal25_p1", "fatal25_p2", "fatal25_p3", "fatal25_p4", "fatal25_total"]])
    print(df["rwi_missing"].sum(), df["hub_missing"].sum())
    print(df["pv_value"].isna().sum())
    print(df["main_road_access"].value_counts())
    print(df.loc[0, ["fatal50_p1", "fatal50_p2", "fatal50_p3", "fatal50_p4", "fatal50_total"]])
if __name__ == "__main__":
    main()