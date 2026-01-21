import streamlit as st
import pandas as pd
import datetime
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

st.set_page_config(page_title="Analytics Reports", page_icon="📊", layout="wide")

# ─── AUTH CHECK ────────────────────────────────────────────────────
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login to view reports.")
    st.stop()

# Get User Info
user_role = st.session_state.user_role
user_id = st.session_state.user_id

# ─── HEADER ────────────────────────────────────────────────────────
st.title("📊 Performance & Activity Reports")
st.markdown("Analyze visits, coverage, and travel metrics.")

# ─── LOAD DATA ─────────────────────────────────────────────────────
df = db.load_data("Master_Schedule")

if df.empty:
    st.info("No data available to generate reports.")
    st.stop()

# Clean & Convert Data Types
df['date'] = pd.to_datetime(df['date'])
# Ensure numeric columns are actually numbers (handle "N/A" or strings)
df['distance_km'] = pd.to_numeric(df['distance_km'], errors='coerce').fillna(0)
df['duration_min'] = pd.to_numeric(df['duration_min'], errors='coerce').fillna(0)

# ─── FILTERS (SIDEBAR) ─────────────────────────────────────────────
st.sidebar.header("Filter Reports")

# 1. Date Range Filter
min_date = df['date'].min().date()
max_date = df['date'].max().date()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

if len(date_range) == 2:
    start_date, end_date = date_range
    mask_date = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
    df_filtered = df.loc[mask_date]
else:
    df_filtered = df.copy()

# 2. MR Filter (Only visible to Admin)
if user_role == 'admin':
    all_mrs = ['All'] + list(df_filtered['mr_id'].unique())
    selected_mr = st.sidebar.selectbox("Select MR", all_mrs)
    if selected_mr != 'All':
        df_filtered = df_filtered[df_filtered['mr_id'] == selected_mr]
else:
    # If standard user, force filter to their own ID
    df_filtered = df_filtered[df_filtered['mr_id'] == user_id]

# ─── KPI METRICS ───────────────────────────────────────────────────
st.divider()

# Calculate Metrics
total_visits = len(df_filtered)
completed_visits = len(df_filtered[df_filtered['status'] == 'Done'])
pending_visits = total_visits - completed_visits
completion_rate = int((completed_visits / total_visits * 100) if total_visits > 0 else 0)

# Travel Metrics
total_distance = df_filtered['distance_km'].sum()
total_time = df_filtered['travel_duration_min'].astype(float).sum() if 'travel_duration_min' in df_filtered.columns else 0

# Display KPIs
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Visits", total_visits, border=True)
k2.metric("Completion Rate", f"{completion_rate}%", border=True)
k3.metric("Distance Traveled", f"{total_distance:.1f} km", border=True)
k4.metric("Doctors Covered", df_filtered['customer_id'].nunique(), border=True)

# ─── CHARTS AREA ───────────────────────────────────────────────────
st.subheader("📈 Activity Trends")

tab1, tab2 = st.tabs(["Daily Activity", "Zone Analysis"])

with tab1:
    # Bar Chart: Visits per Day
    daily_counts = df_filtered.groupby(df_filtered['date'].dt.date).size()
    st.bar_chart(daily_counts)
    st.caption("Number of scheduled visits per day.")

with tab2:
    # Bar Chart: Visits by Zone (or Locality if Zone is missing)
    if 'zone' in df_filtered.columns:
        zone_counts = df_filtered['zone'].value_counts()
        st.bar_chart(zone_counts)
        st.caption("Distribution of visits across different zones.")
    else:
        loc_counts = df_filtered['locality'].value_counts().head(10)
        st.bar_chart(loc_counts)
        st.caption("Top 10 Localities visited.")

# ─── DETAILED DATA TABLE ───────────────────────────────────────────
st.divider()
st.subheader("📋 Detailed Report")

# Columns to show
cols_to_show = ['date', 'mr_id', 'customer_name', 'locality', 'status', 'distance_km']
# Filter columns that actually exist
available_cols = [c for c in cols_to_show if c in df_filtered.columns]

st.dataframe(
    df_filtered[available_cols].sort_values('date', ascending=False),
    use_container_width=True,
    hide_index=True
)

# ─── DOWNLOAD BUTTON ──────────────────────────────────────────────
csv = df_filtered.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📥 Download Report as CSV",
    data=csv,
    file_name=f"MR_Report_{datetime.date.today()}.csv",
    mime='text/csv',
    type='primary'
)