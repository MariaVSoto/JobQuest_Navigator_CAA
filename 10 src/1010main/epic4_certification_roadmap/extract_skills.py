import sys
import spacy
import json
import os

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Load known skills from skills-list.json
skills_path = os.path.join(os.path.dirname(__file__), 'skills-list.json')
with open(skills_path, 'r', encoding='utf-8') as f:
    skills_data = json.load(f)
    # skills_data is a dict with keys as numbers and values as skill names
    KNOWN_SKILLS = set([v.lower() for v in skills_data.values()])

def extract_skills(text):
    doc = nlp(text)
    found_skills = set()
    # Check for exact matches of tokens and noun chunks
    for token in doc:
        if token.text.lower() in KNOWN_SKILLS:
            found_skills.add(token.text)
    for chunk in doc.noun_chunks:
        if chunk.text.lower() in KNOWN_SKILLS:
            found_skills.add(chunk.text)
    return list(found_skills)

if __name__ == "__main__":
    resume_text = sys.stdin.read()
    skills = extract_skills(resume_text)
    print(json.dumps(skills)) 