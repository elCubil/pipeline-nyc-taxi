SELECT partida,pu_borough,COUNT(*) AS total_viajes,ROUND(SUM(total_amount)::NUMERIC,2) AS ingreso_total,ROUND(AVG(total_amount)::NUMERIC,2) AS ingreso_promedio,
ROUND(AVG(trip_distance)::NUMERIC,2) AS  distancia_promedio
FROM {{ ref('fct_trips') }}
GROUP BY (partida,pu_borough)
ORDER BY total_viajes DESC