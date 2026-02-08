select
    date,
    round(meantemp, 2) as mean_temp,
    round(humidity, 2) as humidity,
    round(wind_speed, 2) as wind_speed,
    round(meanpressure, 2) as mean_pressure
from {{ source('public', 'raw_public_data') }}
