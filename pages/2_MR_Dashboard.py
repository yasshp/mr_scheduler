
# import streamlit as st
# import pandas as pd
# import datetime
# import time
# import os
# import sys
# import folium
# from streamlit_folium import st_folium

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# import db

# st.set_page_config(page_title="MR Workflow", page_icon="⚡", layout="wide")

# if 'logged_in' not in st.session_state or not st.session_state.logged_in:
#     st.warning("Please login first.")
#     st.stop()

# mr_id = st.session_state.user_id
# mr_name = st.session_state.get('user_name', mr_id)

# # ─── HEADER ────────────────────────────────────────────────────────
# st.title(f"Hello, {mr_name}") 
# d = st.date_input("Select Date", datetime.date.today() + datetime.timedelta(days=1))

# # ─── LOAD DATA ─────────────────────────────────────────────────────
# df = db.load_data("Master_Schedule")
# if df.empty:
#     st.info("No schedule data available.")
#     st.stop()

# daily = df[(df['mr_id'] == mr_id) & (pd.to_datetime(df['date']).dt.date == d)].copy()
# daily = daily.sort_values('start_time')

# # ─── HELPER FUNCTIONS ──────────────────────────────────────────────
# def get_col(row, candidates, default="N/A"):
#     for col in candidates:
#         if col in row.index and pd.notna(row[col]) and str(row[col]).strip() != "":
#             return row[col]
#     return default

# # ─── METRICS ───────────────────────────────────────────────────────
# total = len(daily)
# done = len(daily[daily['status'] == 'Done'])
# rem = total - done

# c1, c2, c3 = st.columns(3)
# c1.metric("Total Visits", total)
# c2.metric("Completed", done)
# c3.metric("Pending", rem)

# st.divider()

# # ─── 🗺️ ROUTE MAP VISUALIZATION ──────────────────────────────────
# # Only show map if we have data points
# if not daily.empty:
#     with st.expander("🗺️ View Daily Route Map", expanded=True):
#         # 1. Calculate Center of Map (Average of all points)
#         # Check if lat/long exist and are numeric
#         if 'latitude' in daily.columns and 'longitude' in daily.columns:
#              valid_points = daily[
#                 (pd.to_numeric(daily['latitude'], errors='coerce') != 0) & 
#                 (pd.to_numeric(daily['latitude'], errors='coerce').notna())
#             ]
             
#              if not valid_points.empty:
#                 avg_lat = valid_points['latitude'].mean()
#                 avg_lon = valid_points['longitude'].mean()
                
#                 # Create Base Map
#                 m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
                
#                 # List to hold coordinates for the connecting line
#                 route_coords = []
                
#                 # 2. Add Markers
#                 for idx, row in valid_points.iterrows():
#                     lat = row['latitude']
#                     lon = row['longitude']
#                     doc_name = get_col(row, ['contact_person', 'doctor_name', 'customer_name'])
                    
#                     # Color logic: Green if Done, Blue if Pending
#                     icon_color = 'green' if row['status'] == 'Done' else 'blue'
                    
#                     folium.Marker(
#                         [lat, lon],
#                         popup=f"<b>{doc_name}</b><br>{row['start_time']}",
#                         tooltip=f"{row['customer_name']}",
#                         icon=folium.Icon(color=icon_color, icon="user-md", prefix='fa')
#                     ).add_to(m)
                    
#                     route_coords.append([lat, lon])
                
#                 # 3. Add PolyLine (Connect the dots)
#                 if len(route_coords) > 1:
#                     folium.PolyLine(
#                         route_coords,
#                         color="blue",
#                         weight=2.5,
#                         opacity=1
#                     ).add_to(m)

#                 # Render map
#                 st_folium(m, width=None, height=400)
#              else:
#                  st.caption("No valid GPS coordinates found for this route.")
#         else:
#             st.caption("Latitude/Longitude data missing.")

# st.divider()

# # ─── KANBAN BOARD ──────────────────────────────────────────────────
# c_todo, c_done = st.columns(2)

# with c_todo:
#     st.subheader("🚀 Upcoming")
#     pending = daily[daily['status'] != 'Done']
    
#     if pending.empty:
#         st.success("No pending tasks!")
        
#     for idx, row in pending.iterrows():
#         dist = get_col(row, ['distance_km', 'Distance'], '0')
#         dur = get_col(row, ['travel_duration_min', 'Duration'], '0')
#         dr_name = get_col(row, ['contact_person', 'doctor_name'], None)
        
#         with st.container(border=True):
#             c_time, c_type = st.columns([1, 2])
#             c_time.markdown(f"** {row['start_time']}**")
#             c_type.caption(f"{row['activity_type']}")
            
#             st.markdown(f"### {row['customer_name']}")
#             if dr_name: st.markdown(f"** {dr_name}**")
            
#             st.caption(f"📍 {row['locality']}")
            
#             with st.expander(f"🔻 Trip: {dist} km ({dur} min)"):
#                 st.markdown("**🚗 Logistics**")
#                 t1, t2 = st.columns(2)
#                 t1.info(f" **{dist} km**")
#                 t2.info(f" **{dur} min**")
#                 st.divider()
#                 st.markdown("**💡 Talking Strategy**")
#                 st.write(row.get('suggested_talking_points', 'No strategy provided.'))
                
#             if st.button("Mark Complete", key=f"btn_{row['activity_id']}", use_container_width=True, type="primary"):
#                 f = db.load_data("Master_Schedule")
#                 f.loc[f['activity_id'] == row['activity_id'], 'status'] = 'Done'
#                 db.save_data(f, "Master_Schedule")
#                 st.rerun()

# with c_done:
#     st.subheader("✅ Completed")
#     completed = daily[daily['status'] == 'Done']
    
#     for idx, row in completed.iterrows():
#         with st.container(border=True):
#             st.markdown(f"~~{row['customer_name']}~~")

#             st.caption(f"Finished at {row['end_time']}")

import streamlit as st
import pandas as pd
import datetime
import time
import os
import sys
import folium
from streamlit_folium import st_folium

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

st.set_page_config(page_title="MR Workflow", page_icon="⚡", layout="wide")

# ─── 1. HIDE DEFAULT SIDEBAR ───────────────────────────────────────
st.markdown("""<style>[data-testid="stSidebarNav"] {display: none;}</style>""", unsafe_allow_html=True)

# ─── 2. CUSTOM NAVIGATION ──────────────────────────────────────────
st.sidebar.title("Navigation")
# Note: Ensure your main file is named Login.py or app.py and update this line:
st.sidebar.page_link("Login.py", label="Home", icon="🏠")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login first.")
    st.stop()
    
# Menu Logic
if st.session_state.user_role == 'mr':
    # ✅ FIX: This link MUST match the filename "2_MR_Dashboard.py"
    st.sidebar.page_link("pages/2_MR_Dashboard.py", label="Daily Schedule", icon="⚡")
    st.sidebar.page_link("pages/3_Reports.py", label="My Reports", icon="📊")
elif st.session_state.user_role == 'admin':
    st.sidebar.page_link("pages/1_Admin_Dashboard.py", label="Admin Console", icon="🛡️")

# ─── PAGE CONTENT ──────────────────────────────────────────────────
mr_id = st.session_state.user_id
mr_name = st.session_state.get('user_name', mr_id)

st.title(f"Hello, {mr_name}") 
d = st.date_input("Select Date", datetime.date.today() + datetime.timedelta(days=1))

df = db.load_data("Master_Schedule")
if df.empty:
    st.info("No schedule data available.")
    st.stop()

daily = df[(df['mr_id'] == mr_id) & (pd.to_datetime(df['date']).dt.date == d)].copy()
daily = daily.sort_values('start_time')

# Helper
def get_col(row, candidates, default="N/A"):
    for col in candidates:
        if col in row.index and pd.notna(row[col]) and str(row[col]).strip() != "":
            return row[col]
    return default

# Metrics
total = len(daily)
done = len(daily[daily['status'] == 'Done'])
rem = total - done
c1, c2, c3 = st.columns(3)
c1.metric("Total Visits", total)
c2.metric("Completed", done)
c3.metric("Pending", rem)

st.divider()

# Map
if not daily.empty:
    with st.expander("🗺️ View Daily Route Map", expanded=True):
        if 'latitude' in daily.columns and 'longitude' in daily.columns:
             valid_points = daily[
                (pd.to_numeric(daily['latitude'], errors='coerce') != 0) & 
                (pd.to_numeric(daily['latitude'], errors='coerce').notna())
            ]
             if not valid_points.empty:
                avg_lat = valid_points['latitude'].mean()
                avg_lon = valid_points['longitude'].mean()
                m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
                
                route_coords = []
                for idx, row in valid_points.iterrows():
                    lat = row['latitude']
                    lon = row['longitude']
                    doc_name = get_col(row, ['contact_person', 'doctor_name', 'customer_name'])
                    icon_color = 'green' if row['status'] == 'Done' else 'blue'
                    
                    folium.Marker([lat, lon], popup=f"{doc_name}", icon=folium.Icon(color=icon_color, icon="user-md", prefix='fa')).add_to(m)
                    route_coords.append([lat, lon])
                
                if len(route_coords) > 1:
                    folium.PolyLine(route_coords, color="blue", weight=2.5, opacity=1).add_to(m)
                
                # ✅ FIX: returned_objects=[] stops the infinite reload glitch
                st_folium(m, width=None, height=400, returned_objects=[]) 
             else: st.caption("No valid GPS coordinates found.")

st.divider()

# Kanban
c_todo, c_done = st.columns(2)
with c_todo:
    st.subheader("🚀 Upcoming")
    pending = daily[daily['status'] != 'Done']
    if pending.empty: st.success("No pending tasks!")
    for idx, row in pending.iterrows():
        dist = get_col(row, ['distance_km', 'Distance'], '0')
        dur = get_col(row, ['travel_duration_min', 'Duration'], '0')
        dr_name = get_col(row, ['contact_person', 'doctor_name'], None)
        with st.container(border=True):
            st.markdown(f"** {row['start_time']}**")
            st.markdown(f"### {row['customer_name']}")
            if dr_name: st.markdown(f"** {dr_name}**")
            st.caption(f"📍 {row['locality']}")
            with st.expander(f"🔻 Trip: {dist} km ({dur} min)"):
                st.markdown("**🚗 Logistics**")
                t1, t2 = st.columns(2)
                t1.info(f" **{dist} km**")
                t2.info(f" **{dur} min**")
                st.divider()
                st.markdown("**💡 Talking Strategy**")
                st.write(row.get('suggested_talking_points', 'No strategy provided.'))
                
            if st.button("Mark Complete", key=f"btn_{row['activity_id']}", use_container_width=True, type="primary"):
                f = db.load_data("Master_Schedule")
                f.loc[f['activity_id'] == row['activity_id'], 'status'] = 'Done'
                db.save_data(f, "Master_Schedule")
                st.rerun()

with c_done:
    st.subheader("✅ Completed")
    completed = daily[daily['status'] == 'Done']
    for idx, row in completed.iterrows():
        with st.container(border=True):
            st.markdown(f"~~{row['customer_name']}~~")
            st.caption(f"Finished at {row['end_time']}")
