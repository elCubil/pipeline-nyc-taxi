{{ config(severity = 'warn') }}


WITH tabla1 AS(

    SELECT(fare_amount+extra+mta_tax+tip_amount
+tolls_amount+improvement_surcharge+congestion_surcharge+airport_fee) AS suma
    FROM {{ref ('stg_fact_trip')}}
)

SELECT COUNT(*)
FROM tabla1
WHERE suma<=0

--Se encontro que 35,836 registros que representan 1.27% de los registros totales
-- presentan una suma de ingresos menor o igual a cero
--se hallo que de los 35,836 registros el 60% son del tipo de pago en disputa
-- 24% son de pagos en efectivo, es decir pueden ser correcciones del conductor
--16% son del tipo sin cargo; podrian deverse a costesias o viajes cancelados
-- y 0.4% son del tipo credit card