{{ config(severity = 'warn') }}


WITH tabla1 AS(

    SELECT(fare_amount+extra+mta_tax+tip_amount
+tolls_amount+improvement_surcharge+congestion_surcharge+airport_fee) AS suma
    FROM {{ref ('stg_fact_trip')}}
)

SELECT COUNT(*)
FROM tabla1
WHERE suma<=0