WITH t1 AS(

    SELECT trip_id,ft.vendor_id,dv.vendor_name,tpep_pickup_datetime,tpep_dropoff_datetime,
EXTRACT(EPOCH FROM (tpep_dropoff_datetime-tpep_pickup_datetime))/60 AS trip_duration,passenger_count,
trip_distance,ft.ratecode_id,dr.ratecode_desc,store_and_fwd_flag,pu_location_id,dl1.zone AS partida,dl1.borough AS pu_borough,
do_location_id,dl2.zone AS llegada,dl2.borough AS do_borough,
payment_type,dp.payment_desc,
fare_amount,extra,mta_tax,tip_amount,tolls_amount,improvement_surcharge,congestion_surcharge,airport_fee,
(fare_amount + extra+mta_tax+tip_amount+tolls_amount+improvement_surcharge+congestion_surcharge+airport_fee)AS total_amount

    FROM {{ref('stg_fact_trip')}} ft
        JOIN {{ref('stg_dim_vendor')}} dv ON ft.vendor_id=dv.vendor_id
            JOIN {{ref('stg_dim_ratecode')}} dr ON ft.ratecode_id=dr.ratecode_id
            JOIN {{ref('stg_dim_location')}} dl1 ON ft.pu_location_id=dl1.location_id
            JOIN {{ref('stg_dim_location')}} dl2 ON ft.do_location_id=dl2.location_id
            JOIN {{ref('stg_dim_payment_type')}} dp ON ft.payment_type=dp.payment_type_id

    WHERE
    (trip_distance>0)
    AND
    (tpep_dropoff_datetime-tpep_pickup_datetime)>INTERVAL '0'
    AND
    (fare_amount + extra+mta_tax+tip_amount+tolls_amount+improvement_surcharge+congestion_surcharge+airport_fee)>0
)


SELECT*
FROM t1