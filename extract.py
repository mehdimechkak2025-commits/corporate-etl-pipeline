import os
import requests
import pandas as pd
from dotenv import load_dotenv

print("Initializing Secure Pipeline with Alert System...")

# --- 1. SECURITY PHASE ---
load_dotenv()
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
discord_webhook = os.environ.get("DISCORD_WEBHOOK_URL") # Access the new Discord key

clean_url = supabase_url.strip().rstrip('/')
clean_key = supabase_key.strip()
clean_discord = discord_webhook.strip() if discord_webhook else None

# --- 2. EXTRACT PHASE ---
print("Extracting live market data...")
api_url = "https://www.arbeitnow.com/api/job-board-api"
response = requests.get(api_url)
jobs = response.json()['data']

# --- 3. TRANSFORM PHASE ---
print("Structuring data...")
df = pd.DataFrame(jobs)
df_clean = df[['title', 'company_name', 'location', 'remote']]
db_data = df_clean.to_dict(orient='records')

# --- 4. LOAD PHASE (DATABASE) ---
print("Loading data directly into Cloud PostgreSQL via REST...")
table_url = f"{clean_url}/rest/v1/job_postings"
headers = {
    "apikey": clean_key,
    "Authorization": f"Bearer {clean_key}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}
db_response = requests.post(table_url, headers=headers, json=db_data)

if db_response.status_code == 201:
    print(f"Success! Inserted {len(db_data)} live jobs into Supabase.")
else:
    print(f"Server Error {db_response.status_code}: {db_response.text}")

# --- 5. EVENT-DRIVEN ALERT PHASE ---
print("Scanning for High-Value Targets...")

# Filter: Must be remote AND contain our specific tech keywords
high_value_jobs = df_clean[
    (df_clean['remote'] == True) & 
    (df_clean['title'].str.contains('Data|Engineer|Python|Software', case=False, na=False))
]

if not high_value_jobs.empty and clean_discord:
    print(f"🚨 ALERT: Found {len(high_value_jobs)} high-value jobs. Firing Webhook!")
    
    # Grab the absolute best match (the very first one on the list)
    top_job = high_value_jobs.iloc[0]
    
    # Build the Discord message payload
    discord_payload = {
        "content": f"🚨 **NEW HIGH-VALUE JOB ALERT** 🚨\n**Title:** {top_job['title']}\n**Company:** {top_job['company_name']}\n**Location:** {top_job['location']}\n**Remote:** Yes 🌍"
    }
    
    # Shoot the payload to Discord
    webhook_response = requests.post(clean_discord, json=discord_payload)
    
    if webhook_response.status_code == 204:
        print("Target neutralized. Message successfully delivered to Discord.")
    else:
        print(f"Webhook failed to deliver. Code: {webhook_response.status_code}")
else:
    print("No high-value targets found in this batch. Staying quiet.")