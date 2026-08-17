# seed_delays.py
import sqlite3
import random
from datetime import datetime, timedelta

def create_and_seed_operational_metrics():
    print("Connecting to railpulse.db...")
    conn = sqlite3.connect("railpulse.db")
    cursor = conn.cursor()

    # 1. Create the stop_times_updates operational tracking table
    print("Creating table: 'stop_times_updates'...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stop_times_updates (
        update_id INTEGER PRIMARY KEY AUTOINCREMENT,
        trip_id TEXT,
        stop_id TEXT,
        platform_code TEXT,
        arrival_delay_seconds INTEGER,
        departure_delay_seconds INTEGER,
        date_timestamp TEXT
    );
    """)

    # 2. Fetch valid trip and stop relations out of your real database data
    cursor.execute("""
    SELECT DISTINCT t.trip_id, st.stop_id 
    FROM trips t 
    INNER JOIN stop_times st ON t.trip_id = st.trip_id 
    LIMIT 100;
    """)
    valid_pairs = cursor.fetchall()

    if not valid_pairs:
        print("Error: Could not extract existing schedules from trips/stop_times.")
        conn.close()
        return

    # 3. Generate randomized, realistic tracking data rows
    print(f"Injecting {len(valid_pairs)} live telemetry rows...")
    base_time = datetime.now() - timedelta(hours=4) # Simulating this morning
    
    insert_data = []
    platforms = ["1", "2", "3", "4", "5", "6A", "11"]

    for idx, (trip_id, stop_id) in enumerate(valid_pairs):
        # Emulate a severe tracking bottleneck on Platform 4 at Brussels-Central (stop_id setup check)
        # If your stops data uses precise ID strings, we inject realistic delay metrics
        if idx % 10 == 0:
            platform = "4"
            arrival_delay = random.randint(1200, 2400)   # 20 to 40 minutes severe delay
            departure_delay = random.randint(1200, 2600)
        else:
            platform = random.choice(platforms)
            arrival_delay = random.randint(0, 300)       # 0 to 5 minutes normal operations
            departure_delay = random.randint(0, 350)

        timestamp = (base_time + timedelta(minutes=idx)).strftime("%Y-%m-%d %H:%M:%S")
        insert_data.append((trip_id, stop_id, platform, arrival_delay, departure_delay, timestamp))

    cursor.executemany("""
    INSERT INTO stop_times_updates (trip_id, stop_id, platform_code, arrival_delay_seconds, departure_delay_seconds, date_timestamp)
    VALUES (?, ?, ?, ?, ?, ?);
    """, insert_data)

    conn.commit()
    print("Database seeding completed successfully.")
    conn.close()

if __name__ == "__main__":
    create_and_seed_operational_metrics()
