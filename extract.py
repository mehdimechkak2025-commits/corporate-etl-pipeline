import os
import requests
import pandas as pd
from dotenv import load_dotenv

print("Initializing Secure Pipeline...")

# --- 1. SECURITY PHASE ---
load_dotenv()
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

# --- 2. EXTRACT PHASE ---
print("Extracting live market data...")
api_url = "https://www.arbeitnow.com/api/job-board-api"
response = requests.get(api_url)
jobs = response.json()['data']

# --- 3. TRANSFORM PHASE ---
print("Structuring data...")
df = pd.DataFrame(jobs)
df_clean = df[['title', 'company_name', 'location', 'remote']]

# Convert to a list of dictionaries for the database
db_data = df_clean.to_dict(orient='records')

# --- 4. LOAD PHASE (REST API BYPASS) ---
print("Loading data directly into Cloud PostgreSQL via REST...")

# Bulletproof URL formatting: strip hidden spaces and trailing slashes
clean_url = supabase_url.strip().rstrip('/')
clean_key = supabase_key.strip()

table_url = f"{clean_url}/rest/v1/job_postings"

# Create the security badges (Headers) to prove we have permission
headers = {
    "apikey": clean_key,
    "Authorization": f"Bearer {clean_key}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# POST the data directly to the database
db_response = requests.post(table_url, headers=headers, json=db_data)

# Check if we bypassed the system successfully
if db_response.status_code == 201:
    print(f"Massive Success! Bypassed C++ and inserted {len(db_data)} live jobs into Supabase.")
else:
    print(f"Server Error {db_response.status_code}: {db_response.text}")