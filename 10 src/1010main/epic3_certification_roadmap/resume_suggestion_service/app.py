from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import openai
from models.suggestion import Suggestion
from services.ai_service import AIService
from services.job_service import JobService
from services.resume_service import ResumeService

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize services
ai_service = AIService()
job_service = JobService()
resume_service = ResumeService()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/suggestions/analyze', methods=['POST'])
def analyze_resume():
    try:
        data = request.get_json()
        resume_id = data.get('resumeId')
        job_id = data.get('jobId')

        if not resume_id or not job_id:
            return jsonify({"error": "resumeId and jobId are required"}), 400

        # Get resume and job data
        resume = resume_service.get_resume(resume_id)
        job = job_service.get_job(job_id)

        # Generate suggestions using AI
        suggestions = ai_service.generate_suggestions(resume, job)

        return jsonify(suggestions), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/suggestions/<resume_id>', methods=['GET'])
def get_suggestions(resume_id):
    try:
        suggestions = resume_service.get_suggestions(resume_id)
        return jsonify(suggestions), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port) 