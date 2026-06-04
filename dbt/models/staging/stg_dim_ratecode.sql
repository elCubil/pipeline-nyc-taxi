SELECT ratecode_id,ratecode_desc
FROM {{source('fuente_principal','dim_ratecode')}}