import os
import requests
import pandas as pd
from dotenv import load_dotenv
from groq import Groq

print("Initializing AI-Powered Autonomous Pipeline...")

# --- 1. SECURITY PHASE ---
load_dotenv()
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
discord_webhook = os.environ.get("DISCORD_WEBHOOK_URL")
groq_key = os.environ.get("GROQ_API_KEY")

clean_url = supabase_url.strip().rstrip('/')
clean_key = supabase_key.strip()
clean_discord = discord_webhook.strip() if discord_webhook else None

# Wake up the AI Engine
ai_client = Groq(api_key=groq_key.strip())

# --- 2. EXTRACT & TRANSFORM PHASE ---
print("Extracting and structuring live market data...")
api_url = "https://www.arbeitnow.com/api/job-board-api"
response = requests.get(api_url)
jobs = response.json()['data']

df = pd.DataFrame(jobs)
df_clean = df[['title', 'company_name', 'location', 'remote']]
db_data = df_clean.to_dict(orient='records')

# --- 3. DATABASE LOAD PHASE ---
print("Syncing with Cloud PostgreSQL...")
table_url = f"{clean_url}/rest/v1/market_intel_jobs"
headers = {
    "apikey": clean_key,
    "Authorization": f"Bearer {clean_key}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}
requests.post(table_url, headers=headers, json=db_data)

# --- 4. AI ANALYSIS & ALERT PHASE ---
print("Scanning for High-Value Targets...")
high_value_jobs = df_clean[
    (df_clean['remote'] == True) & 
    (df_clean['title'].str.contains('Data|Engineer|Python|Software', case=False, na=False))
]

if not high_value_jobs.empty and clean_discord:
    top_job = high_value_jobs.iloc[0]
    print(f"Target Acquired: {top_job['title']} at {top_job['company_name']}. Sending to AI for analysis...")
    
    # 🧠 Give the AI its identity and instructions
    system_prompt = "You are a ruthless, highly analytical Senior Tech Recruiter. I will give you a job title and company. Give me a 2-sentence summary of why this is a good opportunity for an automation engineer, and give it a 'Relevance Score' out of 10. Be concise and professional."
    user_prompt = f"Job Title: {top_job['title']}\nCompany: {top_job['company_name']}\nLocation: {top_job['location']}"
    
    # Send the data to Groq's Llama 3 model
    ai_response = ai_client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
      model="llama-3.3-70b-versatile",
        temperature=0.7
    )
    
    # Extract the AI's actual text answer
    ai_analysis = ai_response.choices[0].message.content
    
    # Build the intelligent Discord payload
    discord_payload = {
        "content": f"🚨 **AI INTELLIGENCE REPORT** 🚨\n**Target:** {top_job['title']} at {top_job['company_name']}\n\n**🤖 Llama-3 Analysis:**\n{ai_analysis}"
    }
    
    # Fire the webhook
    webhook_response = requests.post(clean_discord, json=discord_payload)
    
    if webhook_response.status_code == 204:
        print("Mission Complete. AI Intelligence delivered to Discord.")
    else:
        print(f"Webhook failed. Code: {webhook_response.status_code}")
else:
    print("No high-value targets found today. AI remains asleep.")