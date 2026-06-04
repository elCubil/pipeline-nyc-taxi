SELECT vendor_id,vendor_name
FROM {{source ('fuente_principal','dim_vendor')}}