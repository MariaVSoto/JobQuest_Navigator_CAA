from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from jobs.models import Job, SavedJob
from django.contrib.auth import get_user_model

User = get_user_model()

class JobSaveTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='saveuser@example.com', password='testpass123')
        self.client.login(email='saveuser@example.com', password='testpass123')
        self.job = Job.objects.create(title='Frontend Developer', company='WebCorp', location='Calgary', description='Frontend job', salary_min=70000, salary_max=110000)

    def test_save_job(self):
        url = reverse('jobs:save_job', args=[self.job.id])
        response = self.client.post(url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertTrue(SavedJob.objects.filter(job=self.job, user=self.user).exists())

    def test_unsave_job(self):
        SavedJob.objects.create(job=self.job, user=self.user)
        url = reverse('jobs:unsave_job', args=[self.job.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(SavedJob.objects.filter(job=self.job, user=self.user).exists())

    def test_saved_jobs_list(self):
        SavedJob.objects.create(job=self.job, user=self.user)
        url = reverse('jobs:saved_jobs')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(job['title'] == 'Frontend Developer' for job in response.data))
