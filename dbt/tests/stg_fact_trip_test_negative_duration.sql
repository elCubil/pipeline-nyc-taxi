{{ config (severity = 'warn') }}


WITH t1 AS(
SELECT (tpep_dropoff_datetime-tpep_pickup_datetime) AS duracion
FROM {{ref ('stg_fact_trip')}}
WHERE (tpep_dropoff_datetime-tpep_pickup_datetime)<= INTERVAL '0'
)

SELECT COUNT(*)
FROM t1

--Se encontro que solo 749 registros presentan una duracion de viaje
--igual o menor a 0. De este total 618 tienen valor 0 y son del tipo 2 (cash)
-- y 95 tambien tienen valor 0 pero son del tipo 1 (credit card)