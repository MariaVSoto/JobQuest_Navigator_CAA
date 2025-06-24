from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from certifications.models import Certification
from django.contrib.auth import get_user_model

User = get_user_model()

class CertificationViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='certuser@example.com', password='testpass123')
        self.client.login(email='certuser@example.com', password='testpass123')
        self.cert = Certification.objects.create(name='AWS Certified Solutions Architect', provider='Amazon')

    def test_certification_list(self):
        url = reverse('certifications:certification_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(cert['name'] == 'AWS Certified Solutions Architect' for cert in response.data))

    def test_certification_detail(self):
        url = reverse('certifications:certification_detail', args=[self.cert.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'AWS Certified Solutions Architect')
