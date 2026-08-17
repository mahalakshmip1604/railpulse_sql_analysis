import sqlite3 
import pandas as pd
from pathlib import Path 

# 1. Dynamic root resolution - makes project instantly portable across machines
PROJECT_ROOT = Path(__file__).parent.resolve()
DATABASE_PATH = PROJECT_ROOT / "railpulse.db"
QUERY_DIR = PROJECT_ROOT / "sql_queries"


# Ensure foundational database environment asset exists
if not DATABASE_PATH.is_file():
    raise FileNotFoundError(f"Database file missing: {DATABASE_PATH}")

if not QUERY_DIR.is_dir(): 
    raise FileNotFoundError(f"SQL queries directory missing: {QUERY_DIR}")

# Define all 5 production queries to execute in sequential order
sql_files = [
    "1_peak_hour.sql",
    "2_platform_bottlenecks.sql",
    "3_busiest_morning_destination.sql",
    "4_service_frequency.sql",
    "5_accessibility_audit.sql"
]

print("=========================================================================")
# Print heading matching the official NMBS/SNCB network blue and yellow theme styling
print("🇧🇪  NMBS / SNCB DATA CONSOLE PIPELINE RUNNER  🇧🇪")
print("=========================================================================\n")

# Connect to database once and iterate through the batch list processing pipeline
with sqlite3.connect(DATABASE_PATH) as conn:
    for filename in sql_files:
        file_path = QUERY_DIR / filename
        
        print(f"🔄 Processing Query Script: {filename}")
        print("-" * 75)
        
        if not file_path.is_file():
            print(f"❌ Error: Script file '{filename}' was not found in directory folder.\n")
            continue
            
        try:
            # Load text file content cleanly into memory
            query_text = file_path.read_text(encoding="utf-8")
            
            # Execute query and parse straight into a data matrix grid
            df = pd.read_sql_query(query_text, conn)
            
            print("📈 OUTPUT LOG:")
            if df.empty:
                print("⚠️ Query execution returned an empty data dataset grid frame structure.")
            else:
                # Pretty print without row index numbering cluttering console views
                print(df.to_string(index=False))
                
        except Exception as e:
            print(f"❌ Execution standard engine crash report: {str(e)}")
            
        print("\n" + "="*75 + "\n")

print("✅ Complete background sequence batch execution run finished successfully.")
