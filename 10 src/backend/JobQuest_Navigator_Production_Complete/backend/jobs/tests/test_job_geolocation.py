from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from jobs.models import Job
from django.contrib.auth import get_user_model

User = get_user_model()

class JobGeolocationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='geo@example.com', password='testpass123')
        self.client.login(email='geo@example.com', password='testpass123')
        self.job = Job.objects.create(title='GIS Analyst', company='GeoCorp', location='Ottawa', description='GIS job', salary_min=65000, salary_max=95000, latitude=45.4215, longitude=-75.6997)

    def test_nearby_jobs(self):
        url = reverse('jobs:nearby_jobs')
        response = self.client.get(url, {'latitude': 45.4215, 'longitude': -75.6997, 'radius': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(job['title'] == 'GIS Analyst' for job in response.data))

    def test_job_map(self):
        url = reverse('jobs:job_map')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
