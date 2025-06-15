import pymysql
import json
import os
from pathlib import Path
from 10_src.1010main.epic4_certification_roadmap.skill_analysis.skill_extractor import SkillExtractor

MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'jobuser')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'jobpass')
MYSQL_DB = os.getenv('MYSQL_DB', 'jobquest')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))

# --- CONFIG ---
JOB_ID = input('Enter Job ID: ')
RESUME_PATH = input('Enter path to resume text file: ')

# --- LOAD RESUME ---
with open(RESUME_PATH, 'r', encoding='utf-8') as f:
    resume_text = f.read()

# --- INIT SKILL EXTRACTOR ---
skill_extractor = SkillExtractor()
resume_skills = skill_extractor.extract_skills(resume_text)

# --- CONNECT TO MYSQL ---
conn = pymysql.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB,
    port=MYSQL_PORT,
    charset='utf8mb4'
)
cursor = conn.cursor()

# --- FETCH JOB ---
cursor.execute('SELECT description, skills FROM jobs WHERE id=%s', (JOB_ID,))
row = cursor.fetchone()
if not row:
    print('Job not found!')
    exit(1)
description, skills_json = row
if skills_json:
    job_skills = json.loads(skills_json)
else:
    job_skills = skill_extractor.extract_skills(description)

print(f'Job Skills: {job_skills}')
print(f'Resume Skills: {resume_skills}')

# --- FETCH CERTIFICATIONS ---
cursor.execute('SELECT name, description, link, relevant_skills FROM Certifications')
certs = cursor.fetchall()
cert_list = []
for name, desc, link, rel_skills_json in certs:
    rel_skills = json.loads(rel_skills_json)
    # Simple match: at least one job or resume skill in relevant_skills
    if any(s in rel_skills for s in job_skills + resume_skills):
        cert_list.append({'name': name, 'description': desc, 'link': link, 'matched_skills': [s for s in job_skills + resume_skills if s in rel_skills]})

# --- OUTPUT ROADMAP ---
print('\nRecommended Certifications:')
for cert in cert_list:
    print(f"- {cert['name']} (Matched Skills: {', '.join(cert['matched_skills'])})")
    print(f"  {cert['description']}")
    print(f"  Link: {cert['link']}\n")

cursor.close()
conn.close() 