SELECT 
    s.platform_code,
    s.parent_station AS stop_id,
    s.stop_name,
    COUNT(*) AS scheduled_departures
FROM stop_times st
JOIN stops s ON st.stop_id = s.stop_id
WHERE s.parent_station = 'gs:nmbssncb:S8813003' 
  AND s.platform_code IS NOT NULL
GROUP BY s.platform_code, s.parent_station, s.stop_name
ORDER BY scheduled_departures DESC
LIMIT 3;