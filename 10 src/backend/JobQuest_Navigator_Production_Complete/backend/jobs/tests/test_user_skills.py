from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from jobs.models import Skill, UserSkill
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSkillTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='userskill@example.com', password='testpass123')
        self.client.login(email='userskill@example.com', password='testpass123')
        self.skill = Skill.objects.create(name='Django', category='Programming')
        self.user_skill = UserSkill.objects.create(user=self.user, skill=self.skill, proficiency='advanced')

    def test_user_skill_list(self):
        url = reverse('jobs:user_skills')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(us['skill']['name'] == 'Django' for us in response.data))

    def test_user_skill_detail(self):
        url = reverse('jobs:user_skill_detail', args=[self.user_skill.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['skill']['name'], 'Django')
