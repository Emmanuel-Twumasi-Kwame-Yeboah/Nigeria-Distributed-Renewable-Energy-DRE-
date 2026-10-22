CREATE DATABASE ngn_dre;
USE ngn_dre;
SELECT DATABASE();
USE ngn_dre;

CREATE TABLE settlements (
    geohash VARCHAR(12) PRIMARY KEY,
    lat DOUBLE,
    lon DOUBLE,
    village_name VARCHAR(255),
    state VARCHAR(50),
    lga VARCHAR(100),
    hull_area DOUBLE,
    building_density_percent DOUBLE,
    num_buildings INT,
    large_buildings INT,
    medium_buildings INT,
    small_buildings INT,
    very_small_structures INT,
    population INT,
    closest_distance_water DOUBLE,
    main_road_access TINYINT,
    dist_main_road_km DOUBLE,
    nearest_hub_name VARCHAR(255),
    dist_nearest_hub_km DOUBLE,
    num_education_facilities INT,
    num_health_facilities INT,
    mean_rwi DOUBLE,
    dist_transmission_km DOUBLE,
    dist_hv_transmission_km DOUBLE,
    has_nightlight TINYINT,
    overlap_percentage DOUBLE,
    dist_gridlight_target_km DOUBLE,
    pv_value DOUBLE,
    crop_types VARCHAR(500),
    ag_area DOUBLE,
    ag_value BIGINT,
    ag_yield DOUBLE,
    ag_value_area INT,
    total_incidents_50km INT,
    security_risk VARCHAR(10),
    demand DOUBLE,
    demand_per_connection DOUBLE,
    rwi_missing TINYINT,
    hub_missing TINYINT,
    fatal25_p1 INT, fatal25_p2 INT, fatal25_p3 INT, fatal25_p4 INT, fatal25_total INT,
    fatal50_p1 INT, fatal50_p2 INT, fatal50_p3 INT, fatal50_p4 INT, fatal50_total INT,
    power_status VARCHAR(15),
    place_type VARCHAR(15),
    grid_band VARCHAR(15),
    is_rural TINYINT,
    is_target TINYINT,
    rank_demand DOUBLE,
    rank_solar DOUBLE,
    rank_wealth DOUBLE,
    rank_distance DOUBLE,
    rank_productive DOUBLE,
    opportunity_score DOUBLE,
    opportunity_score_adj DOUBLE
);

DESCRIBE settlements;

-- ========== QUESTION 1 - HOW BIG IS THE ACCESS GAP? ==========

-- 1a: places, people and demand by power status
SELECT power_status,
       COUNT(*) AS places,
       SUM(population) AS people,
       ROUND(100 * SUM(population) / (SELECT SUM(population) FROM settlements), 1) AS pct_people,
       ROUND(SUM(demand)) AS demand
FROM settlements
GROUP BY power_status;

-- 1b: top 10 states by people living with no power
SELECT state,
       COUNT(*) AS places_no_power,
       SUM(population) AS people_no_power,
       ROUND(100 * SUM(population) / (SELECT SUM(population) FROM settlements WHERE power_status = 'No power'), 1) AS pct_of_gap
FROM settlements
WHERE power_status = 'No power'
GROUP BY state
ORDER BY people_no_power DESC
LIMIT 10;

-- 1c: people with no power, by place type
SELECT place_type,
       COUNT(*) AS places_no_power,
       SUM(population) AS people_no_power,
       ROUND(100 * SUM(population) / (SELECT SUM(population) FROM settlements WHERE power_status = 'No power'), 1) AS pct_of_gap
FROM settlements
WHERE power_status = 'No power'
GROUP BY place_type
ORDER BY people_no_power DESC;