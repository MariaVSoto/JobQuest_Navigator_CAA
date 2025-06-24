from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from jobs.models import JobAlert
from django.contrib.auth import get_user_model

User = get_user_model()

class JobAlertTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='alertuser@example.com', password='testpass123')
        self.client.login(email='alertuser@example.com', password='testpass123')
        self.alert = JobAlert.objects.create(user=self.user, keyword='Python', location='Toronto')

    def test_job_alert_list(self):
        url = reverse('jobs:job_alerts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(alert['keyword'] == 'Python' for alert in response.data))

    def test_job_alert_detail(self):
        url = reverse('jobs:job_alert_detail', args=[self.alert.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['keyword'], 'Python')
