from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from jobs.models import Job
from django.contrib.auth import get_user_model

User = get_user_model()

class JobViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass123')
        self.client.login(email='testuser@example.com', password='testpass123')
        self.job = Job.objects.create(title='Software Engineer', company='TestCorp', location='Toronto', description='Test job', salary_min=60000, salary_max=90000)

    def test_job_list(self):
        url = reverse('jobs:job_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Software Engineer', str(response.data))

    def test_job_detail(self):
        url = reverse('jobs:job_detail', args=[self.job.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Software Engineer')

    def test_job_create_requires_auth(self):
        self.client.logout()
        url = reverse('jobs:job_create')
        data = {
            'title': 'Backend Developer',
            'company': 'NewCorp',
            'location': 'Vancouver',
            'description': 'Backend job',
            'salary_min': 70000,
            'salary_max': 100000
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_job_update(self):
        url = reverse('jobs:job_update', args=[self.job.id])
        data = {'title': 'Senior Software Engineer'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Senior Software Engineer')
