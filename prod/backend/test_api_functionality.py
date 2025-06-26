#!/usr/bin/env python
"""
API功能完整测试脚本
测试所有ViewSets的CRUD操作和自定义actions
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

BASE_URL = 'http://localhost:8000'

class APIFunctionalityTest:
    def __init__(self):
        self.token = None
        self.headers = {}
        self.test_results = []
        
    def log_test(self, name, passed, details=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({'name': name, 'passed': passed, 'details': details})
        print(f"{status} {name}: {details}")
    
    def setup_authentication(self):
        """设置测试用户和认证"""
        try:
            User = get_user_model()
            user, created = User.objects.get_or_create(
                username='apitester',
                defaults={
                    'email': 'apitester@jobquest.com',
                    'first_name': 'API',
                    'last_name': 'Tester'
                }
            )
            if created:
                user.set_password('apitest123')
                user.save()
            
            token, _ = Token.objects.get_or_create(user=user)
            self.token = token.key
            self.headers = {'Authorization': f'Token {self.token}', 'Content-Type': 'application/json'}
            
            self.log_test("Authentication Setup", True, f"Token: {self.token[:10]}...")
            return True
        except Exception as e:
            self.log_test("Authentication Setup", False, f"Error: {str(e)}")
            return False
    
    def test_jobs_api(self):
        """测试Jobs API的CRUD操作"""
        print("\n📋 Testing Jobs API")
        
        # 1. 获取jobs列表
        try:
            response = requests.get(f"{BASE_URL}/api/jobs/", headers=self.headers)
            passed = response.status_code == 200
            data = response.json() if passed else {}
            count = len(data.get('results', [])) if 'results' in data else len(data) if isinstance(data, list) else 0
            self.log_test("Jobs - List", passed, f"Status: {response.status_code}, Count: {count}")
        except Exception as e:
            self.log_test("Jobs - List", False, f"Error: {str(e)}")
        
        # 2. 测试搜索功能
        try:
            response = requests.get(f"{BASE_URL}/api/jobs/search/", 
                                  headers=self.headers, 
                                  params={'q': 'developer'})
            passed = response.status_code == 200
            self.log_test("Jobs - Search", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Jobs - Search", False, f"Error: {str(e)}")
        
        # 3. 测试过滤
        try:
            response = requests.get(f"{BASE_URL}/api/jobs/", 
                                  headers=self.headers,
                                  params={'job_type': 'full_time'})
            passed = response.status_code == 200
            self.log_test("Jobs - Filter", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Jobs - Filter", False, f"Error: {str(e)}")
    
    def test_resumes_api(self):
        """测试Resumes API的ViewSets功能"""
        print("\n📄 Testing Resumes API")
        
        # 1. 获取resumes列表
        try:
            response = requests.get(f"{BASE_URL}/api/resumes/resumes/", headers=self.headers)
            passed = response.status_code == 200
            data = response.json() if passed else {}
            count = len(data.get('results', [])) if 'results' in data else len(data) if isinstance(data, list) else 0
            self.log_test("Resumes - List", passed, f"Status: {response.status_code}, Count: {count}")
        except Exception as e:
            self.log_test("Resumes - List", False, f"Error: {str(e)}")
        
        # 2. 测试模板列表
        try:
            response = requests.get(f"{BASE_URL}/api/resumes/resume-templates/", headers=self.headers)
            passed = response.status_code == 200
            self.log_test("Resumes - Templates", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Resumes - Templates", False, f"Error: {str(e)}")
        
        # 3. 测试分析功能
        try:
            response = requests.get(f"{BASE_URL}/api/resumes/resumes/analytics/", headers=self.headers)
            passed = response.status_code == 200
            self.log_test("Resumes - Analytics", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Resumes - Analytics", False, f"Error: {str(e)}")
    
    def test_skills_api(self):
        """测试Skills API功能"""
        print("\n🎯 Testing Skills API")
        
        # 1. 获取技能列表
        try:
            response = requests.get(f"{BASE_URL}/api/skills/", headers=self.headers)
            passed = response.status_code == 200
            data = response.json() if passed else {}
            count = len(data.get('results', [])) if 'results' in data else len(data) if isinstance(data, list) else 0
            self.log_test("Skills - List", passed, f"Status: {response.status_code}, Count: {count}")
        except Exception as e:
            self.log_test("Skills - List", False, f"Error: {str(e)}")
        
        # 2. 测试用户技能
        try:
            response = requests.get(f"{BASE_URL}/api/skills/user-skills/", headers=self.headers)
            passed = response.status_code == 200
            self.log_test("Skills - User Skills", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Skills - User Skills", False, f"Error: {str(e)}")
        
        # 3. 测试认证路线图
        try:
            response = requests.get(f"{BASE_URL}/api/skills/certification-roadmaps/", headers=self.headers)
            passed = response.status_code == 200
            self.log_test("Skills - Certification Roadmaps", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Skills - Certification Roadmaps", False, f"Error: {str(e)}")
    
    def test_ai_suggestions_api(self):
        """测试AI Suggestions API功能"""
        print("\n🤖 Testing AI Suggestions API")
        
        # 1. 获取建议列表
        try:
            response = requests.get(f"{BASE_URL}/api/ai-suggestions/", headers=self.headers)
            passed = response.status_code == 200
            data = response.json() if passed else {}
            count = len(data.get('results', [])) if 'results' in data else len(data) if isinstance(data, list) else 0
            self.log_test("AI Suggestions - List", passed, f"Status: {response.status_code}, Count: {count}")
        except Exception as e:
            self.log_test("AI Suggestions - List", False, f"Error: {str(e)}")
        
        # 2. 测试反馈功能
        try:
            response = requests.get(f"{BASE_URL}/api/ai-suggestions/feedback/", headers=self.headers)
            passed = response.status_code == 200
            self.log_test("AI Suggestions - Feedback", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("AI Suggestions - Feedback", False, f"Error: {str(e)}")
    
    def test_company_research_api(self):
        """测试Company Research API功能"""
        print("\n🏢 Testing Company Research API")
        
        # 1. 获取公司研究列表
        try:
            response = requests.get(f"{BASE_URL}/api/company-research/", headers=self.headers)
            passed = response.status_code == 200
            data = response.json() if passed else {}
            count = len(data.get('results', [])) if 'results' in data else len(data) if isinstance(data, list) else 0
            self.log_test("Company Research - List", passed, f"Status: {response.status_code}, Count: {count}")
        except Exception as e:
            self.log_test("Company Research - List", False, f"Error: {str(e)}")
        
        # 2. 测试面试准备
        try:
            response = requests.get(f"{BASE_URL}/api/company-research/interview-prep/", headers=self.headers)
            passed = response.status_code == 200
            self.log_test("Company Research - Interview Prep", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Company Research - Interview Prep", False, f"Error: {str(e)}")
    
    def test_user_profile_api(self):
        """测试用户资料API"""
        print("\n👤 Testing User Profile API")
        
        # 1. 获取用户资料
        try:
            response = requests.get(f"{BASE_URL}/api/user/profile/", headers=self.headers)
            passed = response.status_code == 200
            data = response.json() if passed else {}
            self.log_test("User - Profile", passed, f"Status: {response.status_code}, Username: {data.get('username', 'N/A')}")
        except Exception as e:
            self.log_test("User - Profile", False, f"Error: {str(e)}")
        
        # 2. 获取用户偏好
        try:
            response = requests.get(f"{BASE_URL}/api/user/preferences/", headers=self.headers)
            passed = response.status_code == 200
            self.log_test("User - Preferences", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("User - Preferences", False, f"Error: {str(e)}")
    
    def test_create_operations(self):
        """测试创建操作"""
        print("\n➕ Testing Create Operations")
        
        # 创建简历测试数据
        resume_data = {
            "title": "API Test Resume",
            "full_name": "API Tester",
            "email": "apitester@jobquest.com",
            "phone": "+1234567890",
            "professional_summary": "Test resume for API validation",
            "resume_data": {
                "personalInfo": {
                    "fullName": "API Tester",
                    "email": "apitester@jobquest.com"
                },
                "experience": [],
                "education": [],
                "skills": []
            }
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/resumes/resumes/", 
                                   headers=self.headers, 
                                   json=resume_data)
            passed = response.status_code in [200, 201]
            if passed:
                created_resume = response.json()
                resume_id = created_resume.get('id')
                self.log_test("Create - Resume", passed, f"Status: {response.status_code}, ID: {resume_id}")
                
                # 测试更新操作
                update_data = {"title": "Updated API Test Resume"}
                update_response = requests.patch(f"{BASE_URL}/api/resumes/resumes/{resume_id}/",
                                               headers=self.headers,
                                               json=update_data)
                update_passed = update_response.status_code == 200
                self.log_test("Update - Resume", update_passed, f"Status: {update_response.status_code}")
                
                # 清理 - 删除测试简历
                delete_response = requests.delete(f"{BASE_URL}/api/resumes/resumes/{resume_id}/",
                                                headers=self.headers)
                delete_passed = delete_response.status_code == 204
                self.log_test("Delete - Resume", delete_passed, f"Status: {delete_response.status_code}")
            else:
                self.log_test("Create - Resume", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Create - Resume", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """运行所有API功能测试"""
        print("🚀 JobQuest Navigator API Functionality Test")
        print("=" * 60)
        
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Stopping tests.")
            return False
        
        # 运行所有测试
        self.test_jobs_api()
        self.test_resumes_api()
        self.test_skills_api()
        self.test_ai_suggestions_api()
        self.test_company_research_api()
        self.test_user_profile_api()
        self.test_create_operations()
        
        # 总结
        print("\n📊 API Test Summary")
        print("=" * 60)
        passed_tests = sum(1 for test in self.test_results if test['passed'])
        total_tests = len(self.test_results)
        
        print(f"Total API Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # 保存结果
        with open('api_functionality_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📝 Detailed results saved to: api_functionality_test_results.json")
        
        if passed_tests == total_tests:
            print("\n🎉 All API tests passed! API functionality is working correctly.")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} API test(s) failed.")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    test_runner = APIFunctionalityTest()
    success = test_runner.run_all_tests()
    sys.exit(0 if success else 1)