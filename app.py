import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

# Set dashboard configuration
st.set_page_config(
    page_title="NMBS/SNCB Rail Operational Dashboard",
    page_icon="🇧🇪",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = r"C:\Users\mahal\Desktop\MyWorkSpace\Projects\railpulse_sql_analysis\railpulse.db"
SQL_DIR = "sql_queries"

@st.cache_data(ttl=600)
def run_query_from_file(filename: str) -> pd.DataFrame:
    """Safely loads and executes an external SQL script file."""
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
        <!-- Precise Offline CSS Belgian Flag Graphic Wrapper -->
        <div style="display: flex; width: 54px; height: 36px; border-radius: 4px; overflow: hidden; flex-shrink: 0; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
            <div style="background-color: #000000; flex: 1;"></div>
            <div style="background-color: #FAE042; flex: 1;"></div>
            <div style="background-color: #ED2939; flex: 1;"></div>
        </div>
        <div>
            <h1 style="color: #FFFFFF; margin: 0; padding: 0; font-size: 2.3rem; font-weight: 700; font-family: 'Segoe UI', Helvetica, Arial, sans-serif; letter-spacing: -0.5px;">
                NMBS / SNCB Rail Network Dashboard
            </h1>
            <p style="color: #FFCC00; margin: 4px 0 0 0; padding: 0; font-size: 1.05rem; font-weight: 500; opacity: 0.95;">
                Automated Infrastructure Capacity, Vehicle Accessibility Audits & Corridor Analytics
            </p>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

# ----------------------------------------------------
# TAB LAYOUT INITIALIZATION
# ----------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📊 Service & Frequencies", "♿ Accessibility Audit", "⏳ Infrastructure Bottlenecks"])

# ----------------------------------------------------
# TAB 1: Network Frequencies & Corridors
# ----------------------------------------------------
with tab1:
    st.header("Operational Frequency Breakdown")
    col1, col2 = st.columns(2) # Fixed LayoutSpec positional argument parameter
    
    with col1:
        freq_df = run_query_from_file("4_service_frequency.sql")
        if not freq_df.empty:
            # Color Table 1: Soft blue density highlight on the numeric count column
            styled_freq = freq_df.style.background_gradient(cmap="Blues", subset=["corridor_count"])
            st.dataframe(
                styled_freq, 
                column_config={
                    "frequency_category": "Category",
                    "corridor_count": st.column_config.NumberColumn("Corridors Checked", format="%d"),
                    "percentage": st.column_config.ProgressColumn("Percentage Share", format="%.2f%%", min_value=0.0, max_value=100.0)
                },
                use_container_width=True,
                hide_index=True
            )
    with col2:
        if not freq_df.empty:
            fig_freq = px.pie(
                freq_df, 
                values='corridor_count', 
                names='frequency_category',
                title="Distribution of Network Traffic Volumes",
                color='frequency_category',
                color_discrete_map={
                    'High Frequency': '#003366',      # Brand Royal Blue
                    'Medium Frequency': '#FFCC00',    # Brand Canary Yellow
                    'Low Frequency/Special': '#ED2939' # Infrastructure Red
                },
                hole=0.4
            )
            fig_freq.update_layout(margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_freq, use_container_width=True)

# ----------------------------------------------------
# TAB 2: Accessibility Audit (Vehicle Features)
# ----------------------------------------------------
with tab2:
    st.header("Vehicle Feature Accessibility Audit")
    access_df = run_query_from_file("5_accessibility_audit.sql")
    
    if not access_df.empty:
        total_routes_audited = len(access_df)
        zero_amenity_routes = len(access_df[access_df['bike_percentage'] == 0.0])
        
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Total System Routes Audited", f"{total_routes_audited:,}")
        kpi2.metric("Zero-Amenity Routes (BUS Link)", f"{zero_amenity_routes:,}", delta=f"-{round((zero_amenity_routes/total_routes_audited)*100, 1)}% Options", delta_color="inverse")
        kpi3.metric("Perfect Score Routes (IC/S5)", f"{len(access_df[access_df['bike_percentage'] == 100.0]):,}")
        
        st.subheader("Granular Route Quality Overview")
        # Color Table 2: Soft mint yellow-to-green gradient tracking rolling stock storage compliance
        styled_access = access_df.style.background_gradient(cmap="YlGn", subset=["bike_percentage"])
        st.dataframe(
            styled_access,
            column_config={
                "route_id": "Route ID",
                "route_short_name": "Service Type",
                "route_long_name": "Route Name Description",
                "total_trips": st.column_config.NumberColumn("Total Trips", format="%d"),
                "bike_ratio": "Bikes Count/Trips",
                "bike_percentage": st.column_config.NumberColumn("Bicycle Storage Availability", format="%.1f%%"),
                "station_accessibility": "ADA Station Match Status"
            },
            use_container_width=True,
            hide_index=True
        )
 
# ----------------------------------------------------
# TAB 3: Operational Bottlenecks & Peak Demands
# ----------------------------------------------------
with tab3: 
    st.header("Temporal Infrastructure Capacity Analysis")
    b_col1, b_col2 = st.columns(2)

    
    with b_col1:
        st.subheader("Peak Operating Traffic Window")
        peak_df = run_query_from_file("1_peak_hour.sql")
        if not peak_df.empty:
            # Color Table 3: Shaded orange scale tracking absolute active hourly departures
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
            # Color Table 4: Targeted purple density shading for main terminal points
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
        # Color Table 5: Deep high-alert red color mapping tracking congestion triggers across specific platforms
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
