SELECT 
    t.trip_headsign AS destination,
    COUNT(DISTINCT t.trip_id) AS morning_trip_count
FROM trips t
JOIN stop_times st ON t.trip_id = st.trip_id
WHERE st.stop_sequence = 1  -- Assures we look at the trip's starting origin segment
  AND st.departure_time < '12:00:00'
GROUP BY t.trip_headsign
ORDER BY morning_trip_count DESC
LIMIT 3;