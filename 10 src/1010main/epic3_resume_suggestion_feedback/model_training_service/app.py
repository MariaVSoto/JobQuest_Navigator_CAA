from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from services.model_service import ModelService
from services.training_service import TrainingService
from services.metrics_service import MetricsService

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize services
model_service = ModelService()
training_service = TrainingService()
metrics_service = MetricsService()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/model/train', methods=['POST'])
def train_model():
    try:
        # Start model training
        training_id = training_service.start_training()
        
        return jsonify({
            "trainingId": training_id,
            "status": "started"
        }), 202

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/model/performance', methods=['GET'])
def get_model_performance():
    try:
        # Get latest model performance metrics
        metrics = metrics_service.get_latest_metrics()
        
        return jsonify(metrics), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/model/status/<training_id>', methods=['GET'])
def get_training_status(training_id):
    try:
        status = training_service.get_training_status(training_id)
        return jsonify(status), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port) 