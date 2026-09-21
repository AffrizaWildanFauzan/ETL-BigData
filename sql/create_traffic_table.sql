CREATE TABLE IF NOT EXISTS urban_traffic_congestion (
    record_id            INTEGER,
    date_time            TIMESTAMP,
    city_zone            VARCHAR(50),
    road_type            VARCHAR(50),
    traffic_volume       INTEGER,
    average_speed_kmph    DOUBLE PRECISION,
    weather_condition    VARCHAR(50),
    accident_reported    BOOLEAN,
    travel_time_minutes  DOUBLE PRECISION,
    congestion_level     VARCHAR(20),

    year                 INTEGER,
    month                INTEGER,
    day                  INTEGER,
    hour                 INTEGER,
    day_of_week          INTEGER,
    is_weekend           BOOLEAN
);
