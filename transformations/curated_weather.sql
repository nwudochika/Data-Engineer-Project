CREATE OR REPLACE VIEW curated_weather AS
SELECT 
    date,
    ROUND(meantemp, 2) AS mean_temp,
    ROUND(humidity, 2) AS humidity,
    ROUND(wind_speed, 2) AS wind_speed,
    ROUND(meanpressure, 2) AS mean_pressure,
    'public' AS source
FROM raw_public_data

UNION ALL

SELECT 
    date,
    ROUND(meantemp, 2),
    ROUND(humidity, 2),
    ROUND(wind_speed, 2),
    ROUND(meanpressure, 2),
    'fake' AS source
FROM raw_fake_data;
