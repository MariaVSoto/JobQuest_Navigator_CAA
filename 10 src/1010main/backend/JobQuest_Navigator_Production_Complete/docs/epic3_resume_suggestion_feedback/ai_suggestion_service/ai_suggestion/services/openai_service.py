import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_resume_suggestions(resume_text):
    prompt = f"Provide suggestions to improve the following resume:\n\n{resume_text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def generate_job_match_suggestions(resume_text):
    prompt = f"Suggest suitable job roles based on the following resume:\n\n{resume_text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
