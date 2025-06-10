from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from models.feedback import Feedback
from services.feedback_service import FeedbackService
from services.model_service import ModelService

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize services
feedback_service = FeedbackService()
model_service = ModelService()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/suggestions/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json()
        suggestion_id = data.get('suggestionId')
        action = data.get('action')
        feedback_text = data.get('feedbackText')

        if not suggestion_id or not action:
            return jsonify({"error": "suggestionId and action are required"}), 400

        # Create feedback entry
        feedback = Feedback(
            suggestion_id=suggestion_id,
            action=action,
            feedback_text=feedback_text
        )

        # Save feedback
        saved_feedback = feedback_service.save_feedback(feedback)

        # Trigger model retraining if needed
        if feedback_service.should_retrain_model():
            model_service.schedule_retraining()

        return jsonify(saved_feedback), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/feedback/history', methods=['GET'])
def get_feedback_history():
    try:
        user_id = request.args.get('userId')
        if not user_id:
            return jsonify({"error": "userId is required"}), 400

        feedback_history = feedback_service.get_feedback_history(user_id)
        return jsonify(feedback_history), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port) 