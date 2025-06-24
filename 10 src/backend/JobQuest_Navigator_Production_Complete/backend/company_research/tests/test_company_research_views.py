from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from company_research.models import CompanyResearch
from django.contrib.auth import get_user_model

User = get_user_model()

class CompanyResearchViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='companyuser@example.com', password='testpass123')
        self.client.login(email='companyuser@example.com', password='testpass123')
        self.research = CompanyResearch.objects.create(user=self.user, company_name='TechCorp', insights='Innovative company')

    def test_company_research_list(self):
        url = reverse('company_research:company_research_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(r['company_name'] == 'TechCorp' for r in response.data))

    def test_company_research_detail(self):
        url = reverse('company_research:company_research_detail', args=[self.research.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], 'TechCorp')
