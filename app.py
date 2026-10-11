import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
from dotenv import load_dotenv

# Initialize backend environments
load_dotenv()

from chatbox_assistant.api_engine import CloudSQLRouter
from chatbox_assistant.guardrails import verify_user_input_safety, verify_generated_sql_safety
from chatbox_assistant.consultant import RailPulseConsultant

# Set unified app window configuration
st.set_page_config(
    page_title="NMBS/SNCB Rail Operational Dashboard Suite",
    page_icon="🇧🇪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration Constants
DB_PATH = r"C:\Users\mahal\Desktop\MyWorkSpace\Projects\railpulse_sql_analysis\railpulse.db"
SQL_DIR = "sql_queries"

# Maintain continuous AI message sessions in memory caching arrays
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------------------------------
# DATABASE READ WRAPPERS FOR STATIC SCRIPTS
# ----------------------------------------------------
@st.cache_data(ttl=600)
def run_query_from_file(filename: str) -> pd.DataFrame:
    """Safely loads and executes an external SQL script file from the workspace."""
    file_path = os.path.join(SQL_DIR, filename)
    if not os.path.exists(file_path):
        st.error(f"Missing SQL file: {filename}")
        return pd.DataFrame()
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            query = f.read()
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"SQL execution failed for {filename}: {str(e)}")
        return pd.DataFrame()

# ----------------------------------------------------
# VISUAL BRANDING: OFF-LINE CSS HEADER CARD
# ----------------------------------------------------
st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 18px; background-color: #003366; padding: 20px; border-radius: 8px; margin-bottom: 25px; border-left: 8px solid #FFCC00; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="display: flex; width: 54px; height: 36px; border-radius: 4px; overflow: hidden; flex-shrink: 0; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
            <div style="background-color: #000000; flex: 1;"></div>
            <div style="background-color: #FAE042; flex: 1;"></div>
            <div style="background-color: #ED2939; flex: 1;"></div>
        </div>
        <div>
            <h1 style="color: #FFFFFF; margin: 0; padding: 0; font-size: 2.3rem; font-weight: 700; font-family: 'Segoe UI', Helvetica, Arial, sans-serif; letter-spacing: -0.5px;">
                NMBS / SNCB Rail Network Dashboard Suite
            </h1>
            <p style="color: #FFCC00; margin: 4px 0 0 0; padding: 0; font-size: 1.05rem; font-weight: 500; opacity: 0.95;">
                Unified Portal: Static Analytical Infrastructure Matrices & Real-Time AI Conversational Engines
            </p>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

# ----------------------------------------------------
# UNIFIED TAB LAYOUT WORKSPACES
# ----------------------------------------------------
tab_ai, tab1, tab2, tab3 = st.tabs([
    "💬 AI Text-to-SQL Assistant", 
    "📊 Service & Frequencies", 
    "♿ Accessibility Audit", 
    "⏳ Infrastructure Bottlenecks"
])

# ====================================================
# TAB MASTER: REAL-TIME CONVERSATIONAL AGENT INTERFACE
# ====================================================
with tab_ai:
    st.header("Context-Aware Transit Network Interface")
    st.write("Interact with raw network telemetry logs using natural language commands.")
    st.divider()
    
    # Display previous conversations from continuous sessions
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sql"):
                with st.expander("🔍 View Executed SQL Query Block"):
                    st.code(message["sql"], language="sql")
            if "dataframe" in message and message["dataframe"] is not None:
                st.markdown("#### Database Record Output:")
                df_info = message["dataframe"]
                history_df = pd.DataFrame(df_info["data"], columns=df_info["columns"])
                
                # Dynamic terminal column color profiling for historical blocks
                hist_numeric_cols = history_df.select_dtypes(include=['number']).columns.tolist()
                if hist_numeric_cols:
                    styled_history = history_df.style.background_gradient(cmap="Oranges", subset=hist_numeric_cols)
                else:
                    styled_history = history_df
                    
                st.dataframe(styled_history, use_container_width=True)

    # Capture interactive user inputs
    if user_prompt := st.chat_input("Ask about schedules, platforms, delays, or transit network bottlenecks..."):
        
        st.session_state.messages.append({"role": "user", "content": user_prompt, "dataframe": None})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
            # Layer 1 Security Processing Check
            if not verify_user_input_safety(user_prompt):
                error_msg = "🚨 SYSTEM ALERT: Prohibited entry token caught by Pre-Inference Guardrails."
                response_placeholder.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg, "dataframe": None})
            else:
                response_placeholder.markdown("*Formulating context schema patterns...*")
                
                router = CloudSQLRouter()
                generated_sql = router.generate_sql_query(user_prompt)
                
                # Terminal Logger Hook: Prints the generated statement directly to your terminal environment
                print(f"\n[AI TERMINAL LOG] Generated SQL Query:\n{generated_sql}\n" + "-"*50)
                
                if "ERROR:" in generated_sql:
                    response_placeholder.markdown(f"❌ **Translation Interrupted:** {generated_sql}")
                    st.session_state.messages.append({"role": "assistant", "content": generated_sql, "dataframe": None})
                
                # Layer 2 Structural Verification Validation
                elif not verify_generated_sql_safety(generated_sql):
                    error_msg = "🚨 SYSTEM ALERT: Dangerous modification operation caught by Post-Inference Guardrails."
                    response_placeholder.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg, "dataframe": None})
                    
                else:
                    response_placeholder.markdown("*Executing read operation on disk cluster metrics...*")
                    
                    try:
                        with sqlite3.connect(DB_PATH) as conn:
                            cursor = conn.cursor()
                            cursor.execute(generated_sql)
                            raw_data = cursor.fetchall()
                            
                            # Clean Header Patch: Extracts string name from index 0 of description metadata fields
                            columns = [str(desc[0]) for desc in cursor.description] if cursor.description else []
                        
                        if not raw_data:
                            msg = "ℹ️ Query compiled successfully but found zero matching records inside this database context."
                            response_placeholder.markdown(msg)
                            
                            with st.expander("🔍 View Executed SQL Query Block"):
                                st.code(generated_sql, language="sql")
                                
                            st.session_state.messages.append({"role": "assistant", "content": msg, "dataframe": None, "sql": generated_sql})
                        else:
                            response_placeholder.markdown("*Synthesizing professional consulting brief...*")
                            
                            advisor = RailPulseConsultant()
                            processed_rows = advisor.format_seconds_to_minutes(raw_data, columns)
                            
                            tactical_brief = advisor.generate_tactical_recommendation(
                                user_prompt, columns, processed_rows
                            )
                            
                            response_placeholder.markdown(tactical_brief)
                            
                            with st.expander("🔍 View Executed SQL Query Block"):
                                st.code(generated_sql, language="sql")
                            
                            st.markdown("#### Database Record Output:")
                            
                            display_df = pd.DataFrame(processed_rows, columns=columns)
                            
                            # Dynamic Gradient Coloring Engine: Auto-shades density columns like 'trip_count' or 'departure_volume'
                            ai_numeric_cols = display_df.select_dtypes(include=['number']).columns.tolist()
                            if ai_numeric_cols:
                                styled_display = display_df.style.background_gradient(cmap="Blues", subset=ai_numeric_cols)
                            else:
                                styled_display = display_df
                                
                            st.dataframe(styled_display, use_container_width=True)
                            
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": tactical_brief,
                                "dataframe": {
                                    "data": processed_rows,
                                    "columns": columns
                                },
                                "sql": generated_sql
                            })
                            st.rerun()
                            
                    except Exception as db_err:
                        err_msg = f"❌ **Database Fault:** Failed to compute statement parameters. Details: {str(db_err)}"
                        response_placeholder.markdown(err_msg)
                        st.session_state.messages.append({"role": "assistant", "content": err_msg, "dataframe": None, "sql": generated_sql})
# ----------------------------------------------------
# TAB 1: Network Frequencies & num_services (Static)
# ----------------------------------------------------
with tab1:
    st.header("Operational Frequency Breakdown")
    col1, col2 = st.columns(2)
    
    with col1:
        freq_df = run_query_from_file("4_service_frequency.sql")
        if not freq_df.empty:
            styled_freq = freq_df.style.background_gradient(cmap="Blues", subset=["num_services"])
            st.dataframe(
                styled_freq, 
                column_config={
                    "frequency_category": "Category",
                    "num_services": st.column_config.NumberColumn("number of services Checked", format="%d"),
                    "percentage": st.column_config.ProgressColumn("Percentage Share", format="%.2f%%", min_value=0.0, max_value=100.0)
                }, 
                use_container_width=True, 
                hide_index=True
            )
            
    with col2:
        if not freq_df.empty:
            fig_freq = px.pie(
                freq_df, 
                values='num_services', 
                names='frequency_category', 
                title="Distribution of Network Traffic Volumes",
                color='frequency_category', 
                color_discrete_map={
                    'High Frequency': '#003366', 
                    'Medium Frequency': '#FFCC00',
                    'Low Frequency/Special': '#ED2939'
                }, 
                hole=0.4
            )
            fig_freq.update_layout(margin=dict(t=40, b=0, l=0, r=0))
            
            # MOVED INSIDE COL2: This places the chart directly next to the table
            st.plotly_chart(fig_freq, use_container_width=True)

# ----------------------------------------------------
# TAB 2: Accessibility Audit (Vehicle Features - Static)
# ----------------------------------------------------
with tab2:
    st.header("Vehicle Feature Accessibility Audit")
    access_df = run_query_from_file("5_accessibility_audit.sql")
    
    if not access_df.empty:
        # Define accurate target column keys based explicitly on the SQL query
        target_pct_col = "bike_percentage"
        total_trips_col = "total_trips"
        
        # Calculate summary metrics safely from DataFrame columns
        total_routes_audited = len(access_df)
        zero_amenity_routes = int((access_df[target_pct_col] == 0.0).sum())
        perfect_score_routes = int((access_df[target_pct_col] == 100.0).sum())
            
        # Render clean system KPI metric cards
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Total System Routes Audited", f"{total_routes_audited:,}")
        
        # Calculate delta percentage representing unequipped route shares
        if total_routes_audited > 0:
            pct_delta = f"-{round((zero_amenity_routes / total_routes_audited) * 100, 1)}% Options"
        else:
            pct_delta = "0.0% Options"
            
        kpi2.metric("Zero-Amenity Routes (BUS Link)", f"{zero_amenity_routes:,}", delta=pct_delta, delta_color="inverse")
        kpi3.metric("Perfect Score Routes (IC/S5)", f"{perfect_score_routes:,}")
        
        st.subheader("Granular Route Quality Overview")
        
        # Style row percentage elements using a clean color gradient map
        styled_access = access_df.style.background_gradient(cmap="YlGn", subset=[target_pct_col])
            
        # Bind explicit visual mappings aligning perfectly with the updated SELECT variables
        base_configs = {
            "route_id": "Route ID",
            "route_short_name": "Service Type",
            "route_long_name": "Route Name Description",
            total_trips_col: st.column_config.NumberColumn("Total Trips", format="%d"),
            "bike_ratio": "Bikes Count/Trips",
            target_pct_col: st.column_config.NumberColumn("Bicycle Storage Availability", format="%.2f%%")
        }
            
        # Display polished, interactive dashboard table matrix
        st.dataframe(
            styled_access,
            column_config=base_configs,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No active compliance logs or accessibility audit records were found inside the current dataset view.")

# ----------------------------------------------------
# TAB 3: Operational Bottlenecks & Peak Demands (Static)
# ----------------------------------------------------
with tab3:
    st.header("Temporal Infrastructure Capacity Analysis")
    b_col1, b_col2 = st.columns(2)
    
    with b_col1:
        st.subheader("Peak Operating Traffic Window")
        peak_df = run_query_from_file("1_peak_hour.sql")
        if not peak_df.empty:
            styled_peak = peak_df.style.background_gradient(cmap="Oranges", subset=["scheduled_departures"])
            st.dataframe(
                styled_peak,
                column_config={
                    "peak_hour": "Hour of Day (24h)",
                    "scheduled_departures": st.column_config.NumberColumn("Active Departures", format="%d")
                },
                use_container_width=True, 
                hide_index=True
            )
            
    with b_col2:
        st.subheader("Busiest Station Morning Terminals")
        dest_df = run_query_from_file("3_busiest_morning_destination.sql")
        if not dest_df.empty:
            styled_dest = dest_df.style.background_gradient(cmap="Purples", subset=["morning_trip_count"])
            st.dataframe(
                styled_dest,
                column_config={
                    "destination": "Terminal Hub Station",
                    "morning_trip_count": st.column_config.NumberColumn("Inbound Morning Trips", format="%d")
                },
                use_container_width=True, 
                hide_index=True
            )
            
    st.divider()
    st.subheader("Platform Network Bottlenecks Detected")
    
    bottleneck_df = run_query_from_file("2_platform_bottlenecks.sql")
    if not bottleneck_df.empty:
        styled_bottleneck = bottleneck_df.style.background_gradient(cmap="Reds", subset=["scheduled_departures"])
        st.dataframe(
            styled_bottleneck,
            column_config={
                "platform_code": "Track/Voie",
                "stop_id": "Station ID Reference",
                "stop_name": "Station Location",
                "scheduled_departures": st.column_config.NumberColumn("Total Dispatches Passing", format="%d")
            },
            use_container_width=True, 
            hide_index=True
        )
