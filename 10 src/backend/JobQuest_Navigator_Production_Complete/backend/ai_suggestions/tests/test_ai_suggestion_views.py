from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ai_suggestions.models import AISuggestion
from django.contrib.auth import get_user_model

User = get_user_model()

class AISuggestionViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='aiuser@example.com', password='testpass123')
        self.client.login(email='aiuser@example.com', password='testpass123')
        self.suggestion = AISuggestion.objects.create(user=self.user, suggestion_type='resume_improvement', content='Improve your summary')

    def test_ai_suggestion_list(self):
        url = reverse('ai_suggestions:ai_suggestion_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(s['content'] == 'Improve your summary' for s in response.data))

    def test_ai_suggestion_detail(self):
        url = reverse('ai_suggestions:ai_suggestion_detail', args=[self.suggestion.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Improve your summary')
