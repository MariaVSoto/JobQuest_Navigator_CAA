from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from jobs.models import Job, JobApplication
from django.contrib.auth import get_user_model

User = get_user_model()

class JobApplicationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='applicant@example.com', password='testpass123')
        self.client.login(email='applicant@example.com', password='testpass123')
        self.job = Job.objects.create(title='QA Engineer', company='TestQA', location='Montreal', description='QA job', salary_min=50000, salary_max=80000)

    def test_apply_job(self):
        url = reverse('jobs:apply_job', args=[self.job.id])
        response = self.client.post(url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertTrue(JobApplication.objects.filter(job=self.job, user=self.user).exists())

    def test_job_application_list(self):
        JobApplication.objects.create(job=self.job, user=self.user)
        url = reverse('jobs:job_applications')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
