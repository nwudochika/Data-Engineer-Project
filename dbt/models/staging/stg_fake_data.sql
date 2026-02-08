select
    date,
    meantemp as mean_temp,
    humidity,
    wind_speed,
    meanpressure as mean_pressure
from {{ source('public', 'raw_fake_data') }}
