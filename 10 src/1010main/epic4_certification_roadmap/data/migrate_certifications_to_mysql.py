import pymysql
import json
import uuid
import os

MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'jobuser')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'jobpass')
MYSQL_DB = os.getenv('MYSQL_DB', 'jobquest')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))

CREATE_TABLE_SQL = '''
CREATE TABLE IF NOT EXISTS Certifications (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    link VARCHAR(2048),
    relevant_skills JSON
);
'''

INSERT_SQL = '''
REPLACE INTO Certifications (
    id, name, description, link, relevant_skills
) VALUES (%s, %s, %s, %s, %s)
'''

json_path = os.path.join(os.path.dirname(__file__), 'certificationMap.json')
with open(json_path, 'r', encoding='utf-8') as f:
    cert_map = json.load(f)

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

for key, cert in cert_map.items():
    cert_id = str(uuid.uuid4())
    name = cert.get('name', '')
    description = cert.get('description', '')
    link = cert.get('link', '')
    relevant_skills = json.dumps(cert.get('relevant_skills', []))
    cursor.execute(INSERT_SQL, (cert_id, name, description, link, relevant_skills))

conn.commit()
cursor.close()
conn.close()
print('Certifications migrated successfully!') 