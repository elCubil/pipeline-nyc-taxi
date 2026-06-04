SELECT location_id,borough,zone,service_zone
FROM {{source('fuente_principal','dim_location')}}