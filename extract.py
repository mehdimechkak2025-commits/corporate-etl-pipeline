import requests
import pandas as pd

print("Connecting to the Global Talent API...")

# --- 1. EXTRACT PHASE ---
url = "https://www.arbeitnow.com/api/job-board-api"
response = requests.get(url)
raw_data = response.json()
jobs = raw_data['data']

print(f"Success! Extracted {len(jobs)} live job postings.")
print("-" * 30)


print("Transforming raw data into a structured Data Table...")


df = pd.DataFrame(jobs)


df_clean = df[['title', 'company_name', 'location', 'remote']]


remote_jobs = df_clean[df_clean['remote'] == True]


print(f"Analysis complete: Out of {len(jobs)} jobs, {len(remote_jobs)} are fully remote.")
print("-" * 30)
print("Here is a preview of your cleaned, structured database:")
print(df_clean.head())

print("Loading data into a local file...")


df_clean.to_csv('market_intel_jobs.csv', index=False, encoding='utf-8')

print("Pipeline Complete! Your data has been securely saved to 'market_intel_jobs.csv'.")