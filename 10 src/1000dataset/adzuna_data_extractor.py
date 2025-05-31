import requests
import csv
import os

# Set your Adzuna app_id and app_key here or use environment variables
APP_ID = os.getenv('ADZUNA_APP_ID', '3aea9429')
APP_KEY = os.getenv('ADZUNA_APP_KEY', '47c6c2410fe3c75a1a1e7e90eb21fa95')

# API endpoint for job search (example: UK)
BASE_URL = "https://api.adzuna.com/v1/api/jobs/gb/search/{}?app_id={}&app_key={}"  # page, app_id, app_key

# Optional: add more query parameters as needed
PARAMS = {
    'results_per_page': 50,  # 50 per page
    'content-type': 'application/json',
}

# Fields to extract from each job ad
FIELDS = [
    'id', 'title', 'company', 'location', 'created', 'description', 'redirect_url', 'salary_min', 'salary_max'
]

all_jobs = []
for page in range(1, 4):  # Pages 1, 2, 3
    API_URL = BASE_URL.format(page, APP_ID, APP_KEY)
    response = requests.get(API_URL, params=PARAMS)
    response.raise_for_status()
    data = response.json()
    jobs = data.get('results', [])
    all_jobs.extend(jobs)
    print(f"Fetched {len(jobs)} jobs from page {page}")

# Prepare CSV file
csv_file = 'adzuna_jobs_sample.csv'
with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    # Write header
    writer.writerow(FIELDS)
    # Write job data
    for job in all_jobs:
        row = [
            job.get('id', ''),
            job.get('title', ''),
            job.get('company', {}).get('display_name', ''),
            job.get('location', {}).get('display_name', ''),
            job.get('created', ''),
            job.get('description', ''),
            job.get('redirect_url', ''),
            job.get('salary_min', ''),
            job.get('salary_max', ''),
        ]
        writer.writerow(row)

print(f"Extracted {len(all_jobs)} jobs to {csv_file}") 