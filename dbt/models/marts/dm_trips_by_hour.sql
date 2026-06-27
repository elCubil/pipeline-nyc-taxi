SELECT pickup_hour,
       COUNT(*) AS total_viajes,
       ROUND(AVG(total_amount)::NUMERIC,2) AS ingreso_promedio,
       ROUND(AVG(passenger_count)::NUMERIC,2) AS pasajeros_promedio,
       ROUND(AVG(trip_distance)::NUMERIC,2) AS distancia_promedio
FROM {{ ref('fct_trips') }}
GROUP BY pickup_hour
ORDER BY pickup_hour