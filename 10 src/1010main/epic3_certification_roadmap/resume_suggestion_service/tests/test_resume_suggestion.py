import unittest
from app import app
import json

class TestResumeSuggestionService(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')

    def test_analyze_resume(self):
        test_data = {
            'resumeId': 'test123',
            'jobId': 'job456'
        }
        response = self.app.post('/api/suggestions/analyze',
                               data=json.dumps(test_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('suggestions', data)

    def test_get_suggestions(self):
        response = self.app.get('/api/suggestions/test123')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('suggestions', data)

if __name__ == '__main__':
    unittest.main() 