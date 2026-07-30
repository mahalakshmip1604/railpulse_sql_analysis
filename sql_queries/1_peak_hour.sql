SELECT 
    STRFTIME('%H', departure_time) AS peak_hour,
    COUNT(DISTINCT trip_id) AS scheduled_departures
FROM stop_times
WHERE departure_time IS NOT NULL
GROUP BY peak_hour
ORDER BY scheduled_departures DESC
LIMIT 5;