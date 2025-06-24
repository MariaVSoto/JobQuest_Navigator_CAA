from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from resumes.models import Resume
from django.contrib.auth import get_user_model

User = get_user_model()

class ResumeViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='resumeuser@example.com', password='testpass123')
        self.client.login(email='resumeuser@example.com', password='testpass123')
        self.resume = Resume.objects.create(user=self.user, title='My Resume', summary='Experienced developer')

    def test_resume_list(self):
        url = reverse('resumes:resume_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(resume['title'] == 'My Resume' for resume in response.data))

    def test_resume_detail(self):
        url = reverse('resumes:resume_detail', args=[self.resume.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'My Resume')

    def test_resume_create_requires_auth(self):
        self.client.logout()
        url = reverse('resumes:resume_create')
        data = {'title': 'New Resume', 'summary': 'Test summary'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_resume_update(self):
        url = reverse('resumes:resume_update', args=[self.resume.id])
        data = {'title': 'Updated Resume'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Resume')
