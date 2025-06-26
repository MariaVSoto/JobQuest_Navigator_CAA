#!/usr/bin/env python
"""
Local deployment test script for JobQuest Navigator
Tests API endpoints and LocalStack services
"""

import os
import sys
import requests
import json
from datetime import datetime

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_local')

import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

# Test configuration
BASE_URL = 'http://localhost:8000'
LOCALSTACK_URL = 'http://localhost:4566'

class LocalDeploymentTest:
    def __init__(self):
        self.test_results = []
        self.token = None
        
    def log_test(self, name, passed, details=""):
        """Log test results"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            'name': name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status} {name}: {details}")
    
    def test_health_check(self):
        """Test Django health endpoint"""
        try:
            response = requests.get(f"{BASE_URL}/health/", timeout=5)
            data = response.json()
            passed = response.status_code == 200 and data.get('status') == 'healthy'
            self.log_test("Django Health Check", passed, f"Status: {response.status_code}, Response: {data.get('message', 'No message')}")
        except Exception as e:
            self.log_test("Django Health Check", False, f"Error: {str(e)}")
    
    def test_admin_access(self):
        """Test Django admin access"""
        try:
            response = requests.get(f"{BASE_URL}/admin/", timeout=5)
            passed = response.status_code in [200, 302]  # 302 is redirect to login
            self.log_test("Django Admin Access", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Django Admin Access", False, f"Error: {str(e)}")
    
    def create_test_user(self):
        """Create or get test user and token"""
        try:
            User = get_user_model()
            user, created = User.objects.get_or_create(
                username='testuser',
                defaults={
                    'email': 'test@jobquest.com',
                    'first_name': 'Test',
                    'last_name': 'User'
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
            
            token, created = Token.objects.get_or_create(user=user)
            self.token = token.key
            self.log_test("Test User Creation", True, f"User: {user.username}, Token created: {created}")
            return True
        except Exception as e:
            self.log_test("Test User Creation", False, f"Error: {str(e)}")
            return False
    
    def test_authentication(self):
        """Test user authentication"""
        try:
            auth_data = {
                'username': 'testuser',
                'password': 'testpass123'
            }
            response = requests.post(f"{BASE_URL}/api/auth/login/", json=auth_data, timeout=5)
            passed = response.status_code in [200, 201]
            self.log_test("User Authentication", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
    
    def test_api_endpoints(self):
        """Test main API endpoints"""
        if not self.token:
            self.log_test("API Endpoints Test", False, "No authentication token available")
            return
        
        headers = {'Authorization': f'Token {self.token}'}
        endpoints = [
            '/api/jobs/',
            '/api/resumes/',
            '/api/skills/',
            '/api/ai-suggestions/',
            '/api/company-research/',
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
                passed = response.status_code in [200, 201]
                details = f"Status: {response.status_code}"
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, dict) and 'results' in data:
                            details += f", Results: {len(data['results'])} items"
                        elif isinstance(data, list):
                            details += f", Items: {len(data)}"
                    except:
                        pass
                self.log_test(f"API Endpoint {endpoint}", passed, details)
            except Exception as e:
                self.log_test(f"API Endpoint {endpoint}", False, f"Error: {str(e)}")
    
    def test_localstack_s3(self):
        """Test LocalStack S3 service"""
        try:
            # Test S3 health
            response = requests.get(f"{LOCALSTACK_URL}/_localstack/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                s3_status = health_data.get('services', {}).get('s3', 'unknown')
                passed = s3_status in ['running', 'available']
                self.log_test("LocalStack S3 Health", passed, f"S3 Status: {s3_status}")
            else:
                self.log_test("LocalStack S3 Health", False, f"Health check failed: {response.status_code}")
            
            # Test S3 buckets
            import boto3
            s3_client = boto3.client(
                's3',
                endpoint_url=LOCALSTACK_URL,
                aws_access_key_id='test',
                aws_secret_access_key='test',
                region_name='us-east-1'
            )
            
            buckets = s3_client.list_buckets()
            bucket_names = [b['Name'] for b in buckets['Buckets']]
            expected_buckets = ['jobquest-navigator-static-local', 'jobquest-navigator-frontend-local']
            
            all_buckets_exist = all(bucket in bucket_names for bucket in expected_buckets)
            self.log_test("LocalStack S3 Buckets", all_buckets_exist, f"Buckets: {bucket_names}")
            
        except Exception as e:
            self.log_test("LocalStack S3 Test", False, f"Error: {str(e)}")
    
    def test_database_operations(self):
        """Test database operations"""
        try:
            User = get_user_model()
            user_count = User.objects.count()
            
            # Create a test object
            from jobs.models import Job, Category
            from core.models import Company, Location
            
            # Create required related objects
            company, _ = Company.objects.get_or_create(
                name="Test Company",
                defaults={'description': 'Test company description'}
            )
            location, _ = Location.objects.get_or_create(
                city="Test City",
                defaults={'country': 'TC', 'latitude': 0.0, 'longitude': 0.0}
            )
            category, _ = Category.objects.get_or_create(
                name="Technology",
                defaults={'adzuna_tag': 'technology'}
            )
            
            test_job = Job.objects.create(
                title="Test Developer Position",
                description="A test job for deployment verification",
                company=company,
                location=location,
                category=category,
                salary_min=50000,
                salary_max=80000,
                job_type='full_time',
                contract_type='permanent',
                remote_type='hybrid'
            )
            
            job_count = Job.objects.count()
            test_job.delete()  # Clean up
            
            passed = user_count > 0 and job_count > 0
            self.log_test("Database Operations", passed, f"Users: {user_count}, Jobs created/deleted successfully")
            
        except Exception as e:
            self.log_test("Database Operations", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all deployment tests"""
        print("🚀 JobQuest Navigator Local Deployment Test")
        print("=" * 50)
        
        # Core Django tests
        self.test_health_check()
        self.test_admin_access()
        self.test_database_operations()
        
        # Authentication tests
        if self.create_test_user():
            self.test_authentication()
            self.test_api_endpoints()
        
        # LocalStack tests
        self.test_localstack_s3()
        
        # Summary
        print("\n📊 Test Summary")
        print("=" * 50)
        passed_tests = sum(1 for test in self.test_results if test['passed'])
        total_tests = len(self.test_results)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! Local deployment is working correctly.")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Check the details above.")
        
        # Save detailed results
        with open('local_deployment_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📝 Detailed results saved to: local_deployment_test_results.json")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    test_runner = LocalDeploymentTest()
    success = test_runner.run_all_tests()
    sys.exit(0 if success else 1)