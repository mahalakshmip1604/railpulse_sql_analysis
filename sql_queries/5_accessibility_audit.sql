SELECT
    r.route_id,
    r.route_short_name,
    r.route_long_name,
    COUNT(t.trip_id) AS total_trips,
    SUM(CASE WHEN t.bikes_allowed = 1 THEN 1 ELSE 0 END) || '/' || COUNT(t.trip_id) AS bike_ratio,
    ROUND(
        SUM(CASE WHEN t.bikes_allowed = 1 THEN 1 ELSE 0 END) * 100.0
        / NULLIF(COUNT(t.trip_id), 0),
        2
    ) AS bike_percentage
FROM routes r
LEFT JOIN trips t ON r.route_id = t.route_id
GROUP BY r.route_id, r.route_short_name, r.route_long_name
ORDER BY bike_percentage ASC, total_trips DESC;