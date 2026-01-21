
import streamlit as st
import pandas as pd
import time
import db

st.set_page_config(page_title="Dcom", page_icon="", layout="wide")

# ─── STATE INITIALIZATION ──────────────────────────────────────────
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = None  # Variable to store Full Name
    st.session_state.user_role = None

def login_screen():
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.title("Dcom")
        st.caption("Secure Access Portal by UserEx")
        
        with st.form("login_form"):
            username = st.text_input("User ID", placeholder="e.g. MR_N1_3")
            password = st.text_input("Password", type="password")
            
            submit = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit:
                # 1. ADMIN CHECK
                if username == "ADMIN" and password == "ADMIN":
                    st.session_state.logged_in = True
                    st.session_state.user_id = "ADMIN"
                    st.session_state.user_name = "Administrator"
                    st.session_state.user_role = "admin"
                    st.rerun()
                
                # 2. DATABASE CHECK
                try:
                    users = db.load_data("User_Master")
                    
                    # Filter for the ID
                    user_match = users[users['mr_id'] == username]
                    
                    if not user_match.empty and password == username:
                        st.session_state.logged_in = True
                        st.session_state.user_id = username
                        st.session_state.user_role = "mr"
                        
                        # ─── NEW LOGIC: COMBINE FIRST & LAST NAME ───
                        try:
                            # distinct check to ensure columns exist
                            if 'first_name' in user_match.columns and 'last_name' in user_match.columns:
                                fname = str(user_match['first_name'].iloc[0])
                                lname = str(user_match['last_name'].iloc[0])
                                # Combine them
                                full_name = f"{fname} {lname}".strip()
                                st.session_state.user_name = full_name if full_name else username
                            else:
                                st.session_state.user_name = username
                        except:
                            st.session_state.user_name = username
                        # ─────────────────────────────────────────────
                        
                        st.success(f"Welcome, {st.session_state.user_name}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Invalid Credentials")
                except Exception as e:
                    st.error(f"System Error: {e}")

if not st.session_state.logged_in:
    login_screen()
else:
    # Landing Page
    st.title(f"Welcome, {st.session_state.user_name}") 
    st.info("Please select a module from the sidebar to begin.")
    
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.user_name = None
        st.rerun()