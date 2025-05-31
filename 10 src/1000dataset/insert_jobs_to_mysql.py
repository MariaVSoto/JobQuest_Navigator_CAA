import pymysql
import csv
import os

# MySQL connection config
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'jobuser')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'jobpass')
MYSQL_DB = os.getenv('MYSQL_DB', 'jobquest')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))

CSV_FILE = os.getenv('CSV_FILE', 'adzuna_jobs_sample.csv')

# Table schema (only fields from CSV)
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
    salary_max DECIMAL(12,2)
);
'''

INSERT_SQL = '''
REPLACE INTO jobs (
    id, title, company, location, created, description, redirect_url,
    salary_min, salary_max
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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

    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        for row in rows:
            cursor.execute(INSERT_SQL, (
                row['id'],
                row['title'],
                row['company'],
                row['location'],
                parse_datetime(row['created']),
                row['description'],
                row['redirect_url'],
                parse_float(row['salary_min']),
                parse_float(row['salary_max'])
            ))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Inserted {len(rows)} jobs into MySQL table 'jobs'.")

if __name__ == '__main__':
    main()
