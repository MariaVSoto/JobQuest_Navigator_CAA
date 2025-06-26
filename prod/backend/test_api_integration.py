"""
JobQuest Navigator - API Integration Tests
Comprehensive test suite for validating API functionality before production deployment.
"""

import pytest
import requests
import json
from datetime import datetime, timedelta
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from core.models import User, Company, Location
from jobs.models import Job, JobApplication
from skills.models import Skill, SkillCategory
from resumes.models import Resume, ResumeVersion
from application_tracking.models import ApplicationTracker

User = get_user_model()


class BaseAPITestCase(APITestCase):
    """Base test case with common setup for API tests."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create test company and location
        self.location = Location.objects.create(
            city='Toronto',
            province='ON',
            country='Canada',
            latitude=43.6532,
            longitude=-79.3832
        )
        
        self.company = Company.objects.create(
            name='Test Company',
            location=self.location,
            industry='Technology',
            size='100-500',
            description='A test company'
        )
        
        # Authenticate user
        self.client.force_authenticate(user=self.user)


class HealthCheckTestCase(APITestCase):
    """Test health check endpoints."""
    
    def test_basic_health_check(self):
        """Test basic health check endpoint."""
        url = '/health/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'healthy')
    
    def test_detailed_health_check(self):
        """Test detailed health check endpoint."""
        url = '/health/detailed/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('database', response.data)
        self.assertIn('redis', response.data)


class AuthenticationTestCase(APITestCase):
    """Test authentication and user management."""
    
    def test_user_registration(self):
        """Test user registration endpoint."""
        url = '/api/auth/register/'
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
    
    def test_user_login(self):
        """Test user login endpoint."""
        # Create user first
        User.objects.create_user(
            email='logintest@example.com',
            password='loginpass123'
        )
        
        url = '/api/auth/login/'
        data = {
            'email': 'logintest@example.com',
            'password': 'loginpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class JobsAPITestCase(BaseAPITestCase):
    """Test Jobs API endpoints (Epic 1)."""
    
    def setUp(self):
        super().setUp()
        
        # Create test job
        self.job = Job.objects.create(
            title='Software Engineer',
            company=self.company,
            location=self.location,
            description='A test job posting',
            employment_type='full_time',
            salary_min=70000,
            salary_max=90000,
            external_id='test-job-001'
        )
    
    def test_job_list(self):
        """Test job listing endpoint."""
        url = '/api/jobs/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_job_detail(self):
        """Test job detail endpoint."""
        url = f'/api/jobs/{self.job.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.job.id))
    
    def test_job_application(self):
        """Test job application endpoint."""
        url = f'/api/jobs/{self.job.id}/apply/'
        data = {
            'cover_letter': 'I am interested in this position'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class SkillsAPITestCase(BaseAPITestCase):
    """Test Skills API endpoints (Epic 4) - ViewSets version."""
    
    def setUp(self):
        super().setUp()
        
        # Create test skill category
        self.category = SkillCategory.objects.create(
            name='Programming Languages',
            description='Various programming languages'
        )
        
        # Create test skill
        self.skill = Skill.objects.create(
            name='Python',
            category=self.category,
            description='Python programming language',
            skill_type='technical',
            difficulty_level=2
        )
    
    def test_skill_categories_list(self):
        """Test skill categories list endpoint."""
        url = '/api/skills/categories/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_skills_list(self):
        """Test skills list endpoint."""
        url = '/api/skills/skills/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_skill_detail(self):
        """Test skill detail endpoint."""
        url = f'/api/skills/skills/{self.skill.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.skill.id))
    
    def test_trending_skills(self):
        """Test trending skills custom action."""
        url = '/api/skills/skills/trending/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)


class ResumesAPITestCase(BaseAPITestCase):
    """Test Resumes API endpoints (Epic 2)."""
    
    def setUp(self):
        super().setUp()
        
        # Create test resume
        self.resume = Resume.objects.create(
            name='My Resume',
            user=self.user
        )
        
        # Create test resume version
        self.resume_version = ResumeVersion.objects.create(
            resume=self.resume,
            file_name='resume_v1.pdf',
            file_size=1024,
            file_type='pdf',
            comment='Initial version'
        )
    
    def test_resume_list(self):
        """Test resume listing endpoint."""
        url = '/api/resumes/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_resume_versions(self):
        """Test resume versions endpoint."""
        url = f'/api/resumes/{self.resume.id}/versions/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ApplicationTrackingAPITestCase(BaseAPITestCase):
    """Test Application Tracking API endpoints (Epic 5)."""
    
    def setUp(self):
        super().setUp()
        
        # Create test data
        self.job = Job.objects.create(
            title='Test Job',
            company=self.company,
            location=self.location,
            description='Test job description'
        )
        
        self.job_application = JobApplication.objects.create(
            user=self.user,
            job=self.job,
            cover_letter='Test cover letter'
        )
        
        self.resume = Resume.objects.create(
            name='Test Resume',
            user=self.user
        )
        
        self.resume_version = ResumeVersion.objects.create(
            resume=self.resume,
            file_name='test_resume.pdf',
            comment='Test version'
        )
    
    def test_application_tracker_list(self):
        """Test application tracker listing."""
        url = '/api/application-tracking/applications/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_create_application_tracker(self):
        """Test creating application tracker."""
        url = '/api/application-tracking/applications/'
        data = {
            'job_application': self.job_application.id,
            'resume_version': self.resume_version.id,
            'priority': 'high',
            'application_source': 'direct',
            'notes': 'Test application tracking'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_dashboard_endpoint(self):
        """Test application tracking dashboard."""
        url = '/api/application-tracking/applications/dashboard/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_applications', response.data)
    
    def test_analytics_endpoint(self):
        """Test application analytics."""
        url = '/api/application-tracking/applications/analytics/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AITestCase(BaseAPITestCase):
    """Test AI Suggestions API endpoints (Epic 3)."""
    
    def test_ai_suggestions_list(self):
        """Test AI suggestions listing."""
        url = '/api/ai-suggestions/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_generate_resume_suggestions(self):
        """Test resume suggestions generation."""
        # Create a test resume first
        resume = Resume.objects.create(
            name='Test Resume',
            user=self.user
        )
        
        url = '/api/ai-suggestions/generate-resume/'
        data = {
            'resume_id': str(resume.id)
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CompanyResearchAPITestCase(BaseAPITestCase):
    """Test Company Research API endpoints (Epic 6)."""
    
    def test_company_research_list(self):
        """Test company research listing."""
        url = '/api/company-research/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_generate_company_research(self):
        """Test company research generation."""
        url = '/api/company-research/generate/'
        data = {
            'company_id': str(self.company.id)
        }
        response = self.client.post(url, data)
        # This might return different status codes depending on implementation
        self.assertIn(response.status_code, [200, 201, 202])


class EndToEndTestCase(BaseAPITestCase):
    """End-to-end integration tests simulating real user workflows."""
    
    def test_complete_job_application_workflow(self):
        """Test complete workflow: job search → application → tracking."""
        
        # 1. Search for jobs
        url = '/api/jobs/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 2. Create a job for testing
        job = Job.objects.create(
            title='Full Stack Developer',
            company=self.company,
            location=self.location,
            description='Full stack development position'
        )
        
        # 3. Create resume and version
        resume = Resume.objects.create(
            name='Full Stack Resume',
            user=self.user
        )
        
        resume_version = ResumeVersion.objects.create(
            resume=resume,
            file_name='fullstack_resume.pdf',
            comment='Tailored for full stack positions'
        )
        
        # 4. Apply to job
        url = f'/api/jobs/{job.id}/apply/'
        data = {
            'cover_letter': 'I am very interested in this full stack position',
            'resume_version_id': str(resume_version.id)
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 5. Check application tracking was created
        url = '/api/application-tracking/applications/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 6. Get AI suggestions for resume
        url = '/api/ai-suggestions/generate-resume/'
        data = {'resume_id': str(resume.id)}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_skills_assessment_workflow(self):
        """Test skills management and assessment workflow."""
        
        # 1. Get skill categories
        url = '/api/skills/categories/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 2. Search for specific skills
        url = '/api/skills/skills/?search=python'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Get trending skills
        url = '/api/skills/skills/trending/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# Performance Tests
class PerformanceTestCase(BaseAPITestCase):
    """Basic performance tests for critical endpoints."""
    
    def test_job_list_performance(self):
        """Test job listing performance with pagination."""
        # Create multiple jobs for testing
        for i in range(50):
            Job.objects.create(
                title=f'Job {i}',
                company=self.company,
                location=self.location,
                description=f'Job description {i}'
            )
        
        url = '/api/jobs/?page_size=20'
        
        import time
        start_time = time.time()
        response = self.client.get(url)
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Response should be under 1 second for 50 jobs
        self.assertLess(end_time - start_time, 1.0)
        self.assertEqual(len(response.data['results']), 20)
    
    def test_concurrent_user_simulation(self):
        """Test API behavior with multiple concurrent requests."""
        from threading import Thread
        import time
        
        results = []
        
        def make_request():
            url = '/api/jobs/'
            response = self.client.get(url)
            results.append(response.status_code)
        
        # Create 10 concurrent threads
        threads = []
        for i in range(10):
            thread = Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # All requests should succeed
        self.assertEqual(len(results), 10)
        self.assertTrue(all(status_code == 200 for status_code in results))
        # All requests should complete within 5 seconds
        self.assertLess(end_time - start_time, 5.0)


if __name__ == '__main__':
    # Run tests
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    if not settings.configured:
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests([
        'test_api_integration.HealthCheckTestCase',
        'test_api_integration.AuthenticationTestCase',
        'test_api_integration.JobsAPITestCase',
        'test_api_integration.SkillsAPITestCase',
        'test_api_integration.ApplicationTrackingAPITestCase',
        'test_api_integration.EndToEndTestCase',
        'test_api_integration.PerformanceTestCase',
    ])
    
    if failures:
        print(f"\n❌ {failures} test(s) failed")
        exit(1)
    else:
        print("\n✅ All API integration tests passed!")
        exit(0)