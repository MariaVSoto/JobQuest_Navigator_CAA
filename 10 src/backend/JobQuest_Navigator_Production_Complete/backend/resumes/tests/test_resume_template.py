from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from resumes.models import ResumeTemplate
from django.contrib.auth import get_user_model

User = get_user_model()

class ResumeTemplateTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='templateuser@example.com', password='testpass123')
        self.client.login(email='templateuser@example.com', password='testpass123')
        self.template = ResumeTemplate.objects.create(title='Modern', content='Template content')

    def test_resume_template_list(self):
        url = reverse('resumes:resume_template_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(t['title'] == 'Modern' for t in response.data))

    def test_resume_template_detail(self):
        url = reverse('resumes:resume_template_detail', args=[self.template.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Modern')
