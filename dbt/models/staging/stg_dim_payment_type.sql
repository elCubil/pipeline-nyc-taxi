SELECT payment_type_id,payment_desc
FROM {{source('fuente_principal','dim_payment_type')}}