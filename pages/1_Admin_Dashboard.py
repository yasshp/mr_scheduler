
import streamlit as st
import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logic
import db

st.set_page_config(page_title="Admin Console", page_icon="🛡️", layout="wide")

# ─── NO CUSTOM CSS ─────────────────────────────────────────────────

if 'logged_in' not in st.session_state or st.session_state.user_role != 'admin':
    st.error("Access Denied: Admin rights required.")
    st.stop()

st.title("🛡️ Admin Console")

tab1, tab2 = st.tabs(["Schedule Generator", "Database View"])

with tab1:
    st.header("Schedule Generator")
    st.write("Run optimization algorithm for all MRs.")
    
    if st.button("Run Generator", type="primary"):
        with st.status("Running Generator...", expanded=True):
            try:
                users = db.load_data("User_Master")
                contacts = db.load_data("Contacts")
                acts = db.load_data("Activities")
                if 'date' in acts.columns: acts['date'] = pd.to_datetime(acts['date'], errors='coerce')
                
                scheds = []
                for idx, row in users.iterrows():
                    st.write(f"Processing: {row['mr_id']}...")
                    df = logic.run_schedule_logic_for_single_mr(row['mr_id'], users, contacts, acts, pd.to_datetime('2025-12-31'))
                    if not df.empty: scheds.append(df)
                
                if scheds:
                    final = pd.concat(scheds)
                    final['date'] = final['date'].astype(str)
                    db.save_data(final, "Master_Schedule")
                    st.success("Schedule Updated Successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

with tab2:
    st.header("Data Inspector")
    opt = st.selectbox("Select Table", ["User_Master", "Contacts", "Activities", "Master_Schedule"])
    
    if st.button("Refresh"):
        st.cache_data.clear()
        st.rerun()
    
    try:
        st.dataframe(db.load_data(opt), use_container_width=True)
    except:
        st.error("Error loading table.")