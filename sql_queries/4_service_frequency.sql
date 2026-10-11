WITH ServiceFrequency AS (
        SELECT
            t.route_id,
            COUNT(t.trip_id) AS operating_days
        FROM trips t
        GROUP BY t.route_id
    ),
    CategorizedServices AS (
        SELECT
            route_id,
            CASE
                WHEN operating_days >= 50 THEN 'High Frequency'
                WHEN operating_days >= 10 THEN 'Medium Frequency'
                ELSE 'Low Frequency/Special'
            END AS frequency_category
        FROM ServiceFrequency
    )
    SELECT
        frequency_category,
        COUNT(*) AS num_services,
        ROUND(
            COUNT(*) * 100.0 /
            (SELECT COUNT(*) FROM CategorizedServices),
            2
        ) AS percentage
    FROM CategorizedServices
    GROUP BY frequency_category
    ORDER BY CASE frequency_category
        WHEN 'High Frequency' THEN 1
        WHEN 'Medium Frequency' THEN 2
        WHEN 'Low Frequency/Special' THEN 3
    END;
