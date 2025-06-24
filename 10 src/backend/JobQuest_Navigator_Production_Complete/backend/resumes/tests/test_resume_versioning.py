from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from resumes.models import Resume, ResumeVersion
from django.contrib.auth import get_user_model

User = get_user_model()

class ResumeVersioningTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='versionuser@example.com', password='testpass123')
        self.client.login(email='versionuser@example.com', password='testpass123')
        self.resume = Resume.objects.create(user=self.user, title='Versioned Resume', summary='v1')
        self.version = ResumeVersion.objects.create(resume=self.resume, content='v1 content')

    def test_resume_version_list(self):
        url = reverse('resumes:resume_versions', args=[self.resume.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(v['content'] == 'v1 content' for v in response.data))

    def test_resume_version_detail(self):
        url = reverse('resumes:resume_version_detail', args=[self.resume.id, self.version.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'v1 content')
