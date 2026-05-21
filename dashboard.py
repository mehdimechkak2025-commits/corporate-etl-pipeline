import streamlit as st
import os
import requests
import pandas as pd
from dotenv import load_dotenv

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Market Intel", page_icon="🌍", layout="wide")
st.title("📊 Autonomous Lead Generation Dashboard")
st.markdown("Live data securely pulled from Cloud PostgreSQL.")

# --- 2. SECURE DATABASE CONNECTION ---
load_dotenv()
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

clean_url = supabase_url.strip().rstrip('/')
clean_key = supabase_key.strip()
table_url = f"{clean_url}/rest/v1/job_postings"

headers = {
    "apikey": clean_key,
    "Authorization": f"Bearer {clean_key}"
}

# --- 3. DATA FETCHING (WITH CACHING) ---
# We use @st.cache_data so the web page doesn't crash the database by asking for data every single second.
@st.cache_data(ttl=600) # Caches the data for 10 minutes
def fetch_data():
    # Adding '?select=*' tells the database to give us everything
    response = requests.get(f"{table_url}?select=*", headers=headers)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error(f"Failed to connect to database: {response.text}")
        return pd.DataFrame()

df = fetch_data()

# --- 4. BUILD THE USER INTERFACE ---
if not df.empty:
    # 🎛️ Add Interactive Sidebar Filters
    st.sidebar.header("🔍 Filter Intelligence")
    search_term = st.sidebar.text_input("Search Job Title or Company:")
    remote_only = st.sidebar.checkbox("Remote Opportunities Only")

    # 🧠 Apply the Filters Dynamically
    filtered_df = df.copy()
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(search_term, case=False, na=False) |
            filtered_df['company_name'].str.contains(search_term, case=False, na=False)
        ]
        
    if remote_only:
        filtered_df = filtered_df[filtered_df['remote'] == True]

    # 📊 Calculate metrics based on the FILTERED data
    total_jobs = len(filtered_df)
    remote_jobs = len(filtered_df[filtered_df['remote'] == True])
    
    # Display the top metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Matching Results", value=total_jobs)
    with col2:
        st.metric(label="Remote Matches", value=remote_jobs)
    with col3:
        st.metric(label="Database Status", value="Connected 🟢")

    st.divider()

    # Create the interactive table for the client
    st.subheader("Interactive Intelligence Feed")
    display_df = filtered_df[['title', 'company_name', 'location', 'remote', 'created_at']]
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
else:
    st.warning("The database is currently empty or unreachable.")