import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# ---------------------------------------------------------
# DATABASE MANAGER (Google Sheets)
# ---------------------------------------------------------

def load_data(worksheet_name):
    """
    Reads a worksheet from Google Sheets and returns a DataFrame.
    """
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # ttl=0 ensures we get fresh data every time (no caching)
        df = conn.read(worksheet=worksheet_name, ttl=0)
        
        # Clean up: Drop completely empty rows if any
        if not df.empty:
            df = df.dropna(how='all')
            
        return df
    except Exception as e:
        # If the sheet is empty or not found, return an empty DF
        return pd.DataFrame()

def save_data(df, worksheet_name):
    """
    Overwrites the specific worksheet with new data.
    """
    conn = st.connection("gsheets", type=GSheetsConnection)
    conn.update(worksheet=worksheet_name, data=df)