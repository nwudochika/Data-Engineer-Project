{{
  config(
    materialized='view',
    schema='public'
  )
}}
select * from {{ ref('stg_public_data') }}
union all
select * from {{ ref('stg_fake_data') }}
