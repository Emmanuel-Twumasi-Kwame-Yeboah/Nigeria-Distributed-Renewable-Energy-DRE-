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



        #change True/False into 1/0 (night light)
    df["has_nightlight"] = df["has_nightlight"].astype(int)


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

        #power status (from how much of the place is lit at night)
    df["power_status"] = "No power"
    df.loc[df["overlap_percentage"] > 0, "power_status"] = "Some power"
    df.loc[df["overlap_percentage"] >= 50, "power_status"] = "Has power"

        #place type (from population)
    df["place_type"] = "Village"
    df.loc[df["population"] >= 1000, "place_type"] = "Small town"
    df.loc[df["population"] >= 5000, "place_type"] = "Town"
    df.loc[df["population"] >= 20000, "place_type"] = "City"

        #grid band (distance to the nearest power line)
    df["grid_band"] = "Under 5 km"
    df.loc[df["dist_transmission_km"] > 5, "grid_band"] = "5-10 km"
    df.loc[df["dist_transmission_km"] > 10, "grid_band"] = "Over 10 km"

        #target places (rural AND no power)
    df["is_rural"] = (df["population"] < 5000).astype(int)
    df["is_target"] = ((df["is_rural"] == 1) & (df["power_status"] == "No power")).astype(int)

        #rank demand from 0 to 1 (target places only)
    target = df["is_target"] == 1
    df["rank_demand"] = df.loc[target, "demand"].rank(pct=True)

        #rank sunshine from 0 to 1 (target places only)
    df["rank_solar"] = df.loc[target, "pv_value"].rank(pct=True)

        #rank wealth from 0 to 1 (target places only); blank wealth gets a neutral 0.5
    df["rank_wealth"] = df.loc[target, "mean_rwi"].rank(pct=True)
    df.loc[target, "rank_wealth"] = df.loc[target, "rank_wealth"].fillna(0.5)

    #rank distance from the power line from 0 to 1 (target places only)
    df["rank_distance"] = df.loc[target, "dist_transmission_km"].rank(pct=True)

        #extra users score (school or clinic, plus road access), target places only
    has_facility = ((df["num_education_facilities"] > 0) | (df["num_health_facilities"] > 0)).astype(int)
    df["rank_productive"] = (0.5 * has_facility + 0.5 * df["main_road_access"]).where(target)

        #opportunity score out of 100 (target places only)
    df["opportunity_score"] = (
        0.30 * df["rank_demand"]
        + 0.20 * df["rank_solar"]
        + 0.20 * df["rank_wealth"]
        + 0.15 * df["rank_distance"]
        + 0.15 * df["rank_productive"]
    ) * 100
    df["opportunity_score"] = df["opportunity_score"].round(2)

        #lower the score in risky areas (low = 1.0, medium = 0.9, high = 0.8)
    risk_factor = df["security_risk"].map({"low": 1.0, "medium": 0.9, "high": 0.8})
    df["opportunity_score_adj"] = (df["opportunity_score"] * risk_factor).round(2)

    return df


# ---------- RUN ----------
def main():
    df = clean(load())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_DIR / "settlements_clean.csv", index=False)
    print("Saved:", df.shape)
    print(df[["opportunity_score", "opportunity_score_adj"]].describe())
    print(df["has_nightlight"].value_counts())

if __name__ == "__main__":
    main()