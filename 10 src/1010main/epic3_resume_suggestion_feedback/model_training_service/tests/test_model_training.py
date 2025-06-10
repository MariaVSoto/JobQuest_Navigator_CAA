import unittest
from app import app
import json

class TestModelTrainingService(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')

    def test_start_training(self):
        response = self.app.post('/api/model/train')
        self.assertEqual(response.status_code, 202)
        data = json.loads(response.data)
        self.assertIn('trainingId', data)
        self.assertEqual(data['status'], 'started')

    def test_get_training_status(self):
        # First start a training
        response = self.app.post('/api/model/train')
        training_id = json.loads(response.data)['trainingId']
        
        # Then check its status
        response = self.app.get(f'/api/model/status/{training_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_get_model_performance(self):
        response = self.app.get('/api/model/performance')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('metrics', data)

if __name__ == '__main__':
    unittest.main() 