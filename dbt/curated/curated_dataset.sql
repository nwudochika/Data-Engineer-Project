select * from {{ ref('stg_public_weather') }}
union all
select * from {{ ref('stg_fake_weather') }}
