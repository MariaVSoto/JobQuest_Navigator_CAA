from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from skills.models import Skill
from django.contrib.auth import get_user_model

User = get_user_model()

class SkillViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='skilluser@example.com', password='testpass123')
        self.client.login(email='skilluser@example.com', password='testpass123')
        self.skill = Skill.objects.create(name='Python', category='Programming')

    def test_skill_list(self):
        url = reverse('skills:skill_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(skill['name'] == 'Python' for skill in response.data))

    def test_skill_detail(self):
        url = reverse('skills:skill_detail', args=[self.skill.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Python')
