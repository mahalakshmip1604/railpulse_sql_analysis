WITH TrueTripCounts AS (
    -- Calculate bike metrics strictly at the trip level first to prevent duplication
    SELECT 
        route_id,
        COUNT(*) AS total_trips,
        SUM(CASE WHEN bikes_allowed = 1 THEN 1 ELSE 0 END) AS bike_allowed_trips
    FROM trips
    GROUP BY route_id
),
RouteStationAccessibility AS (
    -- Group station infrastructure assets independently
    SELECT 
        t.route_id,
        MAX(CASE WHEN s.location_type = 1 OR s.platform_code IS NOT NULL THEN 1 ELSE 0 END) AS route_has_accessible_stations
    FROM trips t
    LEFT JOIN stop_times st ON t.trip_id = st.trip_id
    LEFT JOIN stops s ON st.stop_id = s.stop_id
    GROUP BY t.route_id
)
SELECT 
    r.route_id,
    r.route_short_name,
    r.route_long_name,
    ttc.total_trips,
    
    -- Precise bike storage ratios & percentages
    ttc.bike_allowed_trips || '/' || ttc.total_trips AS bike_ratio,
    ROUND((ttc.bike_allowed_trips * 100.0) / ttc.total_trips, 2) AS bike_percentage,
    
    -- Station accessibility tracking
    CASE 
        WHEN rsa.route_has_accessible_stations = 1 THEN 'Yes (Station Audited)'
        ELSE 'No Verified Station Infrastructure' 
    END AS station_accessibility
FROM TrueTripCounts ttc
JOIN routes r ON ttc.route_id = r.route_id
JOIN RouteStationAccessibility rsa ON ttc.route_id = rsa.route_id
ORDER BY bike_percentage ASC, ttc.total_trips DESC;