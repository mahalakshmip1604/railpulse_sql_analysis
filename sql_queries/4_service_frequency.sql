WITH TripEnds AS (
    SELECT 
        trip_id,
        MIN(stop_sequence) AS min_seq,
        MAX(stop_sequence) AS max_seq
    FROM stop_times
    GROUP BY trip_id
),
TripCorridors AS (
    SELECT 
        t.trip_id,
        st_start.stop_id AS origin_stop,
        st_end.stop_id AS destination_stop
    FROM trips t
    JOIN TripEnds te ON t.trip_id = te.trip_id
    JOIN stop_times st_start ON t.trip_id = st_start.trip_id AND st_start.stop_sequence = te.min_seq
    JOIN stop_times st_end ON t.trip_id = st_end.trip_id AND st_end.stop_sequence = te.max_seq
),
CorridorVolumes AS (
    SELECT 
        origin_stop,
        destination_stop,
        COUNT(*) AS total_trips
    FROM TripCorridors
    GROUP BY origin_stop, destination_stop
),
CorridorClassified AS (
    SELECT 
        origin_stop,
        destination_stop,
        CASE 
            WHEN total_trips >= 50 THEN 'High Frequency'
            WHEN total_trips BETWEEN 10 AND 49 THEN 'Medium Frequency'
            ELSE 'Low Frequency/Special'
        END AS frequency_category
    FROM CorridorVolumes
)
SELECT 
    frequency_category,
    COUNT(*) AS corridor_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM CorridorClassified), 2) AS percentage
FROM CorridorClassified
GROUP BY frequency_category
ORDER BY COUNT(*) DESC;