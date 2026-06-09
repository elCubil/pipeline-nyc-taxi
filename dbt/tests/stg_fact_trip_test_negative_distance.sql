{{ config(severity='warn')}}

SELECT COUNT(*)
FROM {{ref('stg_fact_trip')}}
WHERE trip_distance<=0

--Se encontró que solo 36,967 registros presentan distancia recorrida igual a 0.
-- De esta cantidad 20234 son del tipo payment type 1 (tarjeta de credito) y 8512 son
-- del tipo 2 (cash)