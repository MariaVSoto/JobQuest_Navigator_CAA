import unittest
from app import app
import json

class TestFeedbackService(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')

    def test_submit_feedback(self):
        test_data = {
            'suggestionId': 'sugg123',
            'action': 'accepted',
            'feedbackText': 'Great suggestion!'
        }
        response = self.app.post('/api/suggestions/feedback',
                               data=json.dumps(test_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('feedbackId', data)

    def test_get_feedback_history(self):
        response = self.app.get('/api/feedback/history?userId=user123')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('feedback', data)

if __name__ == '__main__':
    unittest.main() 