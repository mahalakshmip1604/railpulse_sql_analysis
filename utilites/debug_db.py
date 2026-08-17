import os
import sqlite3
import pandas as pd

# Define the connection parameters (Update path to your actual local DB file)
DB_PATH = "railpulse.db"

# 1. Configure Pandas global formatting settings for clean terminal output
pd.set_option("display.max_columns", None)  # Force show every single column
pd.set_option("display.max_rows", None)  # Force show every single row matching
pd.set_option("display.max_colwidth", None)  # Prevent internal cell truncation
pd.set_option("display.width", 1000)  # Stop visual horizontal table wrapping

# 2. SQL query targeting routes scoring lowest in bike storage metrics
# Note: wheelchair metrics are omitted due to missing wheelchair_accessible in schema
query = """
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


SELECT
    r.route_id,
    r.route_short_name,
    r.route_long_name,
    COUNT(t.trip_id) AS total_trips,
    SUM(CASE WHEN t.bikes_allowed = 1 THEN 1 ELSE 0 END) || '/' || COUNT(t.trip_id) AS bike_storage_ratio,
    ROUND(
        SUM(CASE WHEN t.bikes_allowed = 1 THEN 1 ELSE 0 END) * 100.0
        / NULLIF(COUNT(t.trip_id), 0),
        2
    ) AS bike_storage_percentage
FROM routes r
LEFT JOIN trips t ON r.route_id = t.route_id
GROUP BY r.route_id, r.route_short_name, r.route_long_name
ORDER BY bike_storage_percentage ASC, total_trips DESC
"""

if not os.path.exists(DB_PATH):
    print(
        f"Initialization Error: Database file '{DB_PATH}' not found in runtime directory."
    )
else:
    conn = sqlite3.connect(DB_PATH)
    try:
        # 3. Read data from connection straight into a Pandas DataFrame
        df = pd.read_sql_query(query, conn)

        # 4. Neatly print full output to console using .to_string()
        print("\n--- Route Amenity Performance Metrics ---")
        print(df)

        # 5. Export to Excel spreadsheet utilizing automatic width formatting
        excel_filename = "route_amenity_scores.xlsx"
        with pd.ExcelWriter(excel_filename, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Amenity Metrics")

            # Iterate worksheets to auto-fit cell content structural dimensions
            worksheet = writer.sheets["Amenity Metrics"]
            for col in worksheet.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                col_letter = col.column_letter
                worksheet.column_dimensions[col_letter].width = max(
                    max_len + 3, 11
                )

        print(
            f"\n[SUCCESS] Matrix saved directly to spreadsheet file: '{excel_filename}'"
        )

    except sqlite3.OperationalError as database_exception:
        print(
            f"\n[DATABASE CRITICAL ERROR]: Operational structural failure.\nDetails: {database_exception}"
        )
    except ModuleNotFoundError:
        print(
            "\n[DEPENDENCY ERROR]: Missing library dependencies. Execute: pip install openpyxl"
        )
    finally:
        # Close standard active connection hooks cleanly
        conn.close()
