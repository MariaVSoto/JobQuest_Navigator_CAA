import pymysql
import requests
import os

# MySQL connection config
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'jobuser')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'jobpass')
MYSQL_DB = os.getenv('MYSQL_DB', 'jobquest')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))

# Adzuna API config
APP_ID = os.getenv('ADZUNA_APP_ID', '3aea9429')
APP_KEY = os.getenv('ADZUNA_APP_KEY', '47c6c2410fe3c75a1a1e7e90eb21fa95')

# Table schema
CREATE_TABLE_SQL = '''
CREATE TABLE IF NOT EXISTS jobs (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255),
    company VARCHAR(255),
    location VARCHAR(255),
    created DATETIME,
    description TEXT,
    redirect_url TEXT,
    salary_min DECIMAL(12,2),
    salary_max DECIMAL(12,2),
    latitude DOUBLE,
    longitude DOUBLE,
    distance_km DOUBLE,
    company_address VARCHAR(255),
    company_latitude DOUBLE,
    company_longitude DOUBLE
);
'''

INSERT_SQL = '''
REPLACE INTO jobs (
    id, title, company, location, created, description, redirect_url,
    salary_min, salary_max, latitude, longitude, distance_km,
    company_address, company_latitude, company_longitude
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
'''

def parse_float(val):
    try:
        return float(val) if val else None
    except Exception:
        return None

def parse_datetime(val):
    if val:
        return val[:19].replace('T', ' ')
    return None

def main():
    # Fetch Adzuna API (Canada, first 3 pages, 50 per page)
    all_jobs = []
    for page in range(1, 8):
        API_URL = f"https://api.adzuna.com/v1/api/jobs/ca/search/{page}?app_id={APP_ID}&app_key={APP_KEY}"
        PARAMS = {
            'results_per_page': 50,
            'content-type': 'application/json',
        }
        response = requests.get(API_URL, params=PARAMS)
        response.raise_for_status()
        jobs = response.json().get('results', [])
        all_jobs.extend(jobs)
        print(f"Fetched {len(jobs)} jobs from page {page}")

    # Connect to MySQL
    conn = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT,
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute(CREATE_TABLE_SQL)
    conn.commit()
    cursor.execute("TRUNCATE TABLE jobs")
    conn.commit()

    count = 0
    for job in all_jobs:
        location_str = job.get('location', {}).get('display_name', '')
        company = job.get('company', {}).get('display_name', '')
        lat = job.get('latitude')
        lon = job.get('longitude')
        cursor.execute(INSERT_SQL, (
            job.get('id', ''),
            job.get('title', ''),
            company,
            location_str,
            parse_datetime(job.get('created', '')),
            job.get('description', ''),
            job.get('redirect_url', ''),
            parse_float(job.get('salary_min', '')),
            parse_float(job.get('salary_max', '')),
            lat,
            lon,
            None,  # distance_km
            None,  # company_address
            None,  # company_latitude
            None   # company_longitude
        ))
        count += 1
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Inserted {count} jobs into MySQL table 'jobs'.")

if __name__ == '__main__':
    main() 