import os
import sys
import subprocess
import sqlite3
from pathlib import  Path 

# Define canonical directory paths relative to this orchestrator file
PROJECT_ROOT = Path(__file__).parent.resolve()
DB_PATH = PROJECT_ROOT / "railpulse.db"
SQL_DIR = PROJECT_ROOT / "sql_queries"
APP_PATH = PROJECT_ROOT / "app.py"

def check_environment():
    """Validates core files and operational database existence before booting up."""
    print("[1/3] Auditing project environment structures...")
    
    # 1. Check if database exists and has active tables
    if not DB_PATH.exists():
        print(f"❌ Error: Database not found at {DB_PATH}")
        print("Please ensure your GTFS database generation pipeline run successfully first.")
        sys.exit(1)
        
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [t[0] for t in cursor.fetchall()]
            if 'trips' not in tables or 'stop_times' not in tables:
                print(f"⚠️ Warning: Database file '{DB_PATH.name}' appears empty or unpopulated.")
    except Exception as e:
        print(f"❌ Database health check failed: {str(e)}")
        sys.exit(1)

    # 2. Check for UI entry-point app
    if not APP_PATH.exists():
        print(f"❌ Error: Streamlit user interface module missing at {APP_PATH}")
        sys.exit(1)
        
    # 3. Check for foundational SQL text scripts
    if not SQL_DIR.exists():
        print(f"❌ Error: Repository directory '{SQL_DIR}' not found.")
        sys.exit(1)
        
    required_queries = [
        "1_peak_hour.sql", 
        "2_platform_bottlenecks.sql", 
        "3_busiest_morning_destination.sql", 
        "4_service_frequency.sql", 
        "5_accessibility_audit.sql"
    ]
    
    missing_files = [q for q in required_queries if not (SQL_DIR / q).exists()]
    if missing_files:
        print(f"⚠️ Notice: Missing {len(missing_files)} complementary query scripts.")
        for f in missing_files:
            print(f"   - {f}")
            
    print("✅ Environment verification check passed successfully.")

def run_background_pipeline():
    """Optional execution layer hook to run query validations or warm up data caches."""
    print("[2/3] Warming up database indexes and checking query configurations...")
    pipeline_script = PROJECT_ROOT / "run_query.py"
    if pipeline_script.exists():
        try:
            # Executes background tests silently without blocking standard console pipes
            subprocess.run([sys.executable, str(pipeline_script)], check=True, capture_output=True)
            print("✅ Pre-flight pipeline execution ran cleanly.")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Pre-flight notice: 'run_query.py' execution returned a non-zero exit code: {e.returncode}")
    else:
        print("ℹ️ Skipping pre-flight query script check (run_query.py not found).")

def start_dashboard():
    """Launches the Streamlit network server cleanly in your project environment context."""
    print("[3/3] Launching web visualization engine server via Streamlit context...")
    
    # Construct subprocess call utilizing the environment's specific python binary path
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(APP_PATH),
        "--server.port=8501",
        "--server.headless=false"
    ]
    
    try:
        # Hands control over directly to the active interactive browser instance
        subprocess.run(command, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard application server shut down cleanly by user request.")
    except Exception as e:
        print(f"❌ Failed to launch Streamlit application layer: {str(e)}")
        sys.exit(1)
        

if __name__ == "__main__":
    print("=====================================================================")
    print("🇧🇪  SNCB / NMBS TRANSIT NETWORK ANALYTICS ORCHESTRATOR ENTRYPOINT  🇧🇪")
    print("=====================================================================\n")
    check_environment()
    print("-" * 69)
    run_background_pipeline()
    print("-" * 69)
    start_dashboard()
