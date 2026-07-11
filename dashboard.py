import streamlit as st
import requests
import pandas as pd

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Market Intel", page_icon="🌍", layout="wide")
st.title("📊 Autonomous Lead Generation Dashboard")
st.markdown("Live data securely pulled from Cloud PostgreSQL.")

# --- 2. SECURE DATABASE CONNECTION (CLOUD READY) ---
# We bypass dotenv entirely and use Streamlit's native secrets manager
try:
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
except KeyError:
    st.error("⚠️ Connection Error: Secrets are missing from the Streamlit Cloud dashboard.")
    st.stop()

clean_url = supabase_url.strip().rstrip('/')
clean_key = supabase_key.strip()

# Make sure this matches your actual database table name! 
# (You previously used market_intel_jobs, update this if needed)
table_url = f"{clean_url}/rest/v1/market_intel_jobs"

headers = {
    "apikey": clean_key,
    "Authorization": f"Bearer {clean_key}"
}

# --- 3. DATA FETCHING (WITH CACHING) ---
@st.cache_data(ttl=600)
def fetch_data():
    try:
        response = requests.get(f"{table_url}?select=*", headers=headers)
        response.raise_for_status() # This acts as a security guard to catch bad URLs/Keys
        return pd.DataFrame(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to pull data from Supabase. Error details: {e}")
        return pd.DataFrame()

df = fetch_data()

# --- 4. BUILD THE USER INTERFACE ---
if not df.empty:
    st.sidebar.header("🔍 Filter Intelligence")
    search_term = st.sidebar.text_input("Search Job Title or Company:")
    remote_only = st.sidebar.checkbox("Remote Opportunities Only")

    filtered_df = df.copy()
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(search_term, case=False, na=False) |
            filtered_df['company_name'].str.contains(search_term, case=False, na=False)
        ]
        
    if remote_only:
        filtered_df = filtered_df[filtered_df['remote'] == True]

    total_jobs = len(filtered_df)
    remote_jobs = len(filtered_df[filtered_df['remote'] == True])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Matching Results", value=total_jobs)
    with col2:
        st.metric(label="Remote Matches", value=remote_jobs)
    with col3:
        st.metric(label="Database Status", value="Connected 🟢")

    st.divider()

    st.subheader("Interactive Intelligence Feed")
    # Verify these columns match exactly what is inside your Supabase table
    display_df = filtered_df[['title', 'company_name', 'location', 'remote', 'created_at']]
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
else:
    st.warning("The database is currently empty or unreachable.")