from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ai_suggestions.models import AISuggestion, Feedback
from django.contrib.auth import get_user_model

User = get_user_model()

class FeedbackTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='feedbackuser@example.com', password='testpass123')
        self.client.login(email='feedbackuser@example.com', password='testpass123')
        self.suggestion = AISuggestion.objects.create(user=self.user, suggestion_type='resume_improvement', content='Add more skills')
        self.feedback = Feedback.objects.create(user=self.user, suggestion=self.suggestion, rating=5, comment='Very helpful!')

    def test_feedback_list(self):
        url = reverse('ai_suggestions:feedback_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(f['comment'] == 'Very helpful!' for f in response.data))

    def test_feedback_detail(self):
        url = reverse('ai_suggestions:feedback_detail', args=[self.feedback.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment'], 'Very helpful!')
