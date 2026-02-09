select
    date,
    round(meantemp::numeric, 2) as mean_temp,
    round(humidity::numeric, 2) as humidity,
    round(wind_speed::numeric, 2) as wind_speed,
    round(meanpressure::numeric, 2) as mean_pressure,
    'public' as source
from {{ source('public', 'raw_public_data') }}
