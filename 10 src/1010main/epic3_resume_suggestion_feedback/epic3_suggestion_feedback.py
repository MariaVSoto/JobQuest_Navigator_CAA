import PyPDF2
import docx
import nltk
import requests
import spacy
import openai
import os
from bs4 import BeautifulSoup
from nltk.tokenize import wordpunct_tokenize
from nltk.corpus import stopwords

# Download necessary resources
nltk.download('punkt')
nltk.download('stopwords')

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

print(openai.__version__)

class ResumeAnalyzer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.nlp = nlp

    def extract_text_from_pdf(self, file_path):
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text

    def extract_text_from_doc(self, file_path):
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def extract_job_description(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Try to find a main job description div, fallback to all text
        job_description_div = soup.find('div', class_='job-description')
        if job_description_div:
            return job_description_div.text
        else:
            return soup.get_text()

    def analyze_resume(self, resume_text, job_description):
        # Process text with spaCy
        resume_doc = self.nlp(resume_text)
        job_doc = self.nlp(job_description)

        # Extract entities and keywords
        resume_entities = [ent.text for ent in resume_doc.ents]
        job_entities = [ent.text for ent in job_doc.ents]

        missing_entities = set(job_entities) - set(resume_entities)

        # Tokenize and remove stopwords
        resume_tokens = wordpunct_tokenize(resume_text.lower())
        resume_tokens = [word for word in resume_tokens if word.isalnum() and word not in self.stop_words]

        job_tokens = wordpunct_tokenize(job_description.lower())
        job_tokens = [word for word in job_tokens if word.isalnum() and word not in self.stop_words]

        missing_keywords = set(job_tokens) - set(resume_tokens)

        return list(missing_entities), list(missing_keywords)

    def generate_suggestions(self, resume_text, job_description):
        missing_entities, missing_keywords = self.analyze_resume(resume_text, job_description)
        suggestions = [
            f"Consider adding the following entities to your resume: {', '.join(missing_entities)}.",
            f"Consider adding the following keywords to your resume: {', '.join(missing_keywords)}.",
            "Ensure your resume highlights relevant experience and skills.",
            "Improve formatting for better readability."
        ]
        return suggestions

class UIReview:
    def __init__(self):
        pass

    def display_suggestions(self, suggestions):
        for suggestion in suggestions:
            print(f"Suggestion: {suggestion}")

    def accept_suggestion(self, suggestion):
        print(f"Accepted: {suggestion}")

    def reject_suggestion(self, suggestion):
        print(f"Rejected: {suggestion}")

class FeedbackLoop:
    def __init__(self):
        self.feedback_data = []

    def log_feedback(self, suggestion, action):
        self.feedback_data.append((suggestion, action))
        print(f"Logged: {suggestion} - {action}")

    def update_model(self):
        print("Model updated based on feedback.")

def get_ai_resume_review(resume_text, job_description, openai_api_key):
    client = openai.OpenAI(api_key=openai_api_key)
    prompt = f"""
You are an expert career coach and resume reviewer.
Here is a resume:
---
{resume_text}
---
And here is a job description:
---
{job_description}
---
Please provide a section-by-section review of the resume, with specific, actionable suggestions for improvement, tailored to the job description. Write your suggestions in clear, professional English.
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def main():
    # Get OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        openai_api_key = input("Enter your OpenAI API key: ").strip()

    analyzer = ResumeAnalyzer()
    ui = UIReview()
    feedback = FeedbackLoop()

    # Ask user for resume file
    file_path = input("Enter the path to your resume (PDF or DOCX): ")
    if file_path.endswith('.pdf'):
        resume_text = analyzer.extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        resume_text = analyzer.extract_text_from_doc(file_path)
    else:
        print("Unsupported file format. Please use PDF or DOCX.")
        return

    # Ask user for job URL
    job_url = input("Enter the URL of the job position: ")
    job_description = analyzer.extract_job_description(job_url)

    # Generate AI review
    print("\nGenerating AI-powered resume review...\n")
    review = get_ai_resume_review(resume_text, job_description, openai_api_key)
    print("AI Resume Review:\n")
    print(review)

    # Optionally, save the review to a file
    save = input("\nDo you want to save the review to a file? (yes/no): ").strip().lower()
    if save == 'yes':
        output_path = "ai_resume_review.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(review)
        print(f"Review saved to {output_path}")

if __name__ == "__main__":
    main()