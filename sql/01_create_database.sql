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

-- QUESTION 1 - HOW BIG IS THE ACCESS GAP?

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

-- QUESTION 2 - WHICH STATES AND LGAS OFFER THE BEST OPPORTUNITY?

-- 2a: top 10 states by unserved demand (target places only)
SELECT state,
       COUNT(*) AS target_places,
       SUM(population) AS people,
       ROUND(SUM(demand)) AS unserved_demand,
       ROUND(100 * SUM(demand) / (SELECT SUM(demand) FROM settlements WHERE is_target = 1), 1) AS pct_of_demand,
       ROUND(AVG(opportunity_score), 1) AS avg_score,
       ROUND(AVG(opportunity_score_adj), 1) AS avg_score_adj
FROM settlements
WHERE is_target = 1
GROUP BY state
ORDER BY unserved_demand DESC
LIMIT 10;

-- 2b: top 20 LGAs by unserved demand (target places only)
SELECT state,
       lga,
       COUNT(*) AS target_places,
       SUM(population) AS people,
       ROUND(SUM(demand)) AS unserved_demand,
       ROUND(SUM(demand) / COUNT(*), 1) AS demand_per_place,
       ROUND(AVG(opportunity_score_adj), 1) AS avg_score_adj
FROM settlements
WHERE is_target = 1
GROUP BY state, lga
ORDER BY unserved_demand DESC
LIMIT 20;

-- QUESTION 3 - GRID OR OFF-GRID?

SELECT grid_band,
       COUNT(*) AS target_places,
       SUM(population) AS people,
       ROUND(100 * SUM(population) / (SELECT SUM(population) FROM settlements WHERE is_target = 1), 1) AS pct_people,
       ROUND(SUM(demand)) AS unserved_demand,
       ROUND(AVG(dist_transmission_km), 1) AS avg_dist_line_km,
       ROUND(AVG(dist_nearest_hub_km), 1) AS avg_dist_hub_km,
       ROUND(AVG(pv_value)) AS avg_solar
FROM settlements
WHERE is_target = 1
GROUP BY grid_band
ORDER BY FIELD(grid_band, 'Under 5 km', '5-10 km', 'Over 10 km');

-- QUESTION 4 - CAN CUSTOMERS PAY, AND IS THERE PRODUCTIVE DEMAND?
SELECT state,
       COUNT(*) AS target_places,
       ROUND(AVG(mean_rwi), 2) AS avg_wealth,
       ROUND(100 * AVG(num_education_facilities > 0 OR num_health_facilities > 0), 1) AS pct_with_school_or_clinic,
       ROUND(100 * AVG(main_road_access), 1) AS pct_with_road,
       ROUND(AVG(ag_value_area)) AS avg_farm_value_per_area,
       ROUND(100 * AVG(rwi_missing), 1) AS pct_wealth_missing
FROM settlements
WHERE is_target = 1
GROUP BY state
ORDER BY SUM(demand) DESC
LIMIT 10;


-- QUESTION 5 - HOW MUCH DOES SECURITY RISK MATTER?

SELECT security_risk,
       COUNT(*) AS target_places,
       SUM(population) AS people,
       ROUND(SUM(demand)) AS unserved_demand,
       ROUND(100 * SUM(demand) / (SELECT SUM(demand) FROM settlements WHERE is_target = 1), 1) AS pct_of_demand,
       ROUND(AVG(opportunity_score), 1) AS avg_score,
       ROUND(AVG(opportunity_score_adj), 1) AS avg_score_adj,
       ROUND(AVG(total_incidents_50km)) AS avg_incidents_50km,
       ROUND(AVG(fatal50_total)) AS avg_fatalities_50km
FROM settlements
WHERE is_target = 1
GROUP BY security_risk
ORDER BY FIELD(security_risk, 'low', 'medium', 'high');