#!/usr/bin/env python
"""
前端集成测试脚本
测试React前端与Django后端的连接和数据交互
"""

import os
import sys
import requests
import json
import subprocess
import time
import threading
from datetime import datetime

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_local')

import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

BACKEND_URL = 'http://localhost:8000'
FRONTEND_URL = 'http://localhost:3000'
FRONTEND_PATH = '/Users/kevinwang/Documents/Project/20-Project/JobQuest_Navigator_CAA/10 src/front-end'

class FrontendIntegrationTest:
    def __init__(self):
        self.test_results = []
        self.token = None
        self.headers = {}
        self.frontend_process = None
        
    def log_test(self, name, passed, details=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({'name': name, 'passed': passed, 'details': details})
        print(f"{status} {name}: {details}")
    
    def setup_test_environment(self):
        """设置测试环境"""
        print("🔧 Setting Up Test Environment")
        
        try:
            # 创建测试用户和token
            User = get_user_model()
            user, created = User.objects.get_or_create(
                username='frontendtest',
                defaults={
                    'email': 'frontendtest@jobquest.com',
                    'first_name': 'Frontend',
                    'last_name': 'Tester'
                }
            )
            if created:
                user.set_password('frontend123')
                user.save()
            
            token, _ = Token.objects.get_or_create(user=user)
            self.token = token.key
            self.headers = {'Authorization': f'Token {self.token}', 'Content-Type': 'application/json'}
            
            self.log_test("Test Environment Setup", True, f"User: {user.username}, Token ready")
            return True
        except Exception as e:
            self.log_test("Test Environment Setup", False, f"Error: {str(e)}")
            return False
    
    def test_backend_availability(self):
        """测试后端服务可用性"""
        print("\n🔌 Testing Backend Availability")
        
        try:
            # 测试健康检查
            response = requests.get(f"{BACKEND_URL}/health/", timeout=5)
            health_ok = response.status_code == 200
            self.log_test("Backend - Health Check", health_ok, f"Status: {response.status_code}")
            
            # 测试API根端点
            response = requests.get(f"{BACKEND_URL}/api/jobs/", headers=self.headers, timeout=5)
            api_ok = response.status_code == 200
            self.log_test("Backend - API Access", api_ok, f"Status: {response.status_code}")
            
            # 测试CORS响应头
            if api_ok:
                cors_headers = response.headers.get('Access-Control-Allow-Origin', '')
                cors_configured = cors_headers == '*' or 'localhost:3000' in cors_headers
                self.log_test("Backend - CORS Headers", cors_configured, f"CORS: {cors_headers}")
            
            return health_ok and api_ok
            
        except Exception as e:
            self.log_test("Backend - Availability", False, f"Error: {str(e)}")
            return False
    
    def test_frontend_structure(self):
        """测试前端项目结构"""
        print("\n📁 Testing Frontend Structure")
        
        try:
            # 检查前端目录存在
            frontend_exists = os.path.exists(FRONTEND_PATH)
            self.log_test("Frontend - Directory Exists", frontend_exists, f"Path: {FRONTEND_PATH}")
            
            if not frontend_exists:
                return False
            
            # 检查关键文件
            key_files = [
                'package.json', 'public/index.html', 'src/App.js', 
                'src/index.js', 'src/services/resumeService.js'
            ]
            
            for file_path in key_files:
                full_path = os.path.join(FRONTEND_PATH, file_path)
                file_exists = os.path.exists(full_path)
                self.log_test(f"Frontend - {file_path}", file_exists, 
                             "Exists" if file_exists else "Missing")
            
            # 检查node_modules
            node_modules_exists = os.path.exists(os.path.join(FRONTEND_PATH, 'node_modules'))
            self.log_test("Frontend - Dependencies", node_modules_exists,
                         "node_modules found" if node_modules_exists else "Dependencies not installed")
            
            return True
            
        except Exception as e:
            self.log_test("Frontend - Structure", False, f"Error: {str(e)}")
            return False
    
    def install_frontend_dependencies(self):
        """安装前端依赖"""
        print("\n📦 Installing Frontend Dependencies")
        
        try:
            os.chdir(FRONTEND_PATH)
            
            # 检查是否需要安装依赖
            if not os.path.exists('node_modules'):
                result = subprocess.run(['npm', 'install'], 
                                      capture_output=True, text=True, timeout=120)
                install_success = result.returncode == 0
                self.log_test("Frontend - Install Dependencies", install_success,
                             "npm install completed" if install_success else f"Error: {result.stderr[:100]}")
                return install_success
            else:
                self.log_test("Frontend - Install Dependencies", True, "Dependencies already installed")
                return True
                
        except Exception as e:
            self.log_test("Frontend - Install Dependencies", False, f"Error: {str(e)}")
            return False
    
    def start_frontend_server(self):
        """启动前端开发服务器"""
        print("\n🚀 Starting Frontend Server")
        
        try:
            os.chdir(FRONTEND_PATH)
            
            # 设置环境变量
            env = os.environ.copy()
            env['REACT_APP_API_URL'] = BACKEND_URL
            env['PORT'] = '3000'
            
            # 启动前端服务器（后台运行）
            self.frontend_process = subprocess.Popen(
                ['npm', 'start'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务器启动
            print("   Waiting for frontend server to start...")
            for i in range(30):  # 等待最多30秒
                try:
                    response = requests.get(FRONTEND_URL, timeout=2)
                    if response.status_code == 200:
                        self.log_test("Frontend - Server Start", True, f"Server running on {FRONTEND_URL}")
                        return True
                except:
                    pass
                time.sleep(1)
                print(f"   Waiting... ({i+1}/30)")
            
            self.log_test("Frontend - Server Start", False, "Server failed to start within 30 seconds")
            return False
            
        except Exception as e:
            self.log_test("Frontend - Server Start", False, f"Error: {str(e)}")
            return False
    
    def test_frontend_backend_communication(self):
        """测试前端与后端的通信"""
        print("\n💬 Testing Frontend-Backend Communication")
        
        try:
            # 创建测试数据
            test_resume_data = {
                "title": "Frontend Integration Test Resume",
                "full_name": "Frontend Tester",
                "email": "frontendtest@jobquest.com",
                "professional_summary": "Test resume for frontend integration",
                "resume_data": {
                    "personalInfo": {
                        "fullName": "Frontend Tester",
                        "email": "frontendtest@jobquest.com"
                    },
                    "experience": [],
                    "education": [],
                    "skills": []
                }
            }
            
            # 通过API创建简历
            response = requests.post(f"{BACKEND_URL}/api/resumes/resumes/", 
                                   headers=self.headers, 
                                   json=test_resume_data)
            
            create_success = response.status_code in [200, 201]
            if create_success:
                resume_data = response.json()
                resume_id = resume_data.get('id')
                self.log_test("API - Create Resume", True, f"Resume ID: {resume_id}")
                
                # 测试获取数据
                get_response = requests.get(f"{BACKEND_URL}/api/resumes/resumes/{resume_id}/",
                                          headers=self.headers)
                get_success = get_response.status_code == 200
                self.log_test("API - Get Resume", get_success, f"Status: {get_response.status_code}")
                
                # 清理测试数据
                delete_response = requests.delete(f"{BACKEND_URL}/api/resumes/resumes/{resume_id}/",
                                                headers=self.headers)
                delete_success = delete_response.status_code == 204
                self.log_test("API - Delete Resume", delete_success, f"Status: {delete_response.status_code}")
                
                return create_success and get_success and delete_success
            else:
                self.log_test("API - Create Resume", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Frontend-Backend Communication", False, f"Error: {str(e)}")
            return False
    
    def test_service_layer_integration(self):
        """测试前端服务层与API的集成"""
        print("\n🔄 Testing Service Layer Integration")
        
        try:
            # 读取resumeService.js文件
            service_file_path = os.path.join(FRONTEND_PATH, 'src/services/resumeService.js')
            if os.path.exists(service_file_path):
                with open(service_file_path, 'r') as f:
                    service_content = f.read()
                
                # 检查服务配置
                api_url_configured = 'REACT_APP_API_URL' in service_content or 'localhost:8000' in service_content
                self.log_test("Service - API URL Config", api_url_configured, "API URL configuration found")
                
                # 检查认证配置
                auth_configured = 'Authorization' in service_content and 'Bearer' in service_content
                self.log_test("Service - Auth Config", auth_configured, "Authentication configuration found")
                
                # 检查ViewSets端点
                viewsets_endpoints = [
                    '/resumes/', '/resume-templates/', '/resume-versions/',
                    '/resume-shares/', '/resume-comments/', '/resume-exports/'
                ]
                
                endpoints_configured = all(endpoint in service_content for endpoint in viewsets_endpoints)
                self.log_test("Service - ViewSets Endpoints", endpoints_configured,
                             f"ViewSets endpoints configured: {endpoints_configured}")
                
                return api_url_configured and auth_configured
            else:
                self.log_test("Service - File Exists", False, "resumeService.js not found")
                return False
                
        except Exception as e:
            self.log_test("Service Layer Integration", False, f"Error: {str(e)}")
            return False
    
    def test_cors_configuration(self):
        """测试CORS配置"""
        print("\n🌐 Testing CORS Configuration")
        
        try:
            # 发送CORS预检请求
            headers = {
                'Origin': FRONTEND_URL,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type,Authorization'
            }
            
            response = requests.options(f"{BACKEND_URL}/api/jobs/", headers=headers)
            
            # 检查CORS响应头
            cors_origin = response.headers.get('Access-Control-Allow-Origin', '')
            cors_methods = response.headers.get('Access-Control-Allow-Methods', '')
            cors_headers = response.headers.get('Access-Control-Allow-Headers', '')
            
            origin_allowed = cors_origin == '*' or FRONTEND_URL in cors_origin
            methods_allowed = 'POST' in cors_methods
            headers_allowed = 'Content-Type' in cors_headers and 'Authorization' in cors_headers
            
            self.log_test("CORS - Origin", origin_allowed, f"Origin: {cors_origin}")
            self.log_test("CORS - Methods", methods_allowed, f"Methods: {cors_methods}")
            self.log_test("CORS - Headers", headers_allowed, f"Headers: {cors_headers}")
            
            return origin_allowed and methods_allowed and headers_allowed
            
        except Exception as e:
            self.log_test("CORS Configuration", False, f"Error: {str(e)}")
            return False
    
    def test_authentication_flow(self):
        """测试认证流程"""
        print("\n🔐 Testing Authentication Flow")
        
        try:
            # 测试登录端点
            login_data = {
                'username': 'frontendtest',
                'password': 'frontend123'
            }
            
            response = requests.post(f"{BACKEND_URL}/api/auth/login/", json=login_data)
            login_success = response.status_code in [200, 201]
            
            if login_success:
                auth_data = response.json()
                token_received = 'token' in auth_data or 'access' in auth_data
                self.log_test("Auth - Login", login_success and token_received,
                             f"Login successful, token received: {token_received}")
                
                # 测试受保护的端点
                if token_received:
                    test_headers = {'Authorization': f"Token {self.token}"}
                    protected_response = requests.get(f"{BACKEND_URL}/api/user/profile/", 
                                                    headers=test_headers)
                    protected_access = protected_response.status_code == 200
                    self.log_test("Auth - Protected Access", protected_access,
                                 f"Protected endpoint access: {protected_response.status_code}")
                    
                    return login_success and token_received and protected_access
            else:
                self.log_test("Auth - Login", False, f"Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Authentication Flow", False, f"Error: {str(e)}")
            return False
    
    def cleanup(self):
        """清理资源"""
        print("\n🧹 Cleaning Up")
        
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
                self.log_test("Cleanup - Frontend Server", True, "Server stopped")
            except:
                try:
                    self.frontend_process.kill()
                    self.log_test("Cleanup - Frontend Server", True, "Server killed")
                except:
                    self.log_test("Cleanup - Frontend Server", False, "Failed to stop server")
    
    def run_all_tests(self):
        """运行所有前端集成测试"""
        print("🚀 JobQuest Navigator Frontend Integration Test")
        print("=" * 70)
        
        try:
            # 设置测试环境
            if not self.setup_test_environment():
                print("❌ Test environment setup failed. Aborting tests.")
                return False
            
            # 测试后端可用性
            if not self.test_backend_availability():
                print("❌ Backend not available. Aborting frontend tests.")
                return False
            
            # 测试前端结构
            if not self.test_frontend_structure():
                print("❌ Frontend structure issues. Aborting tests.")
                return False
            
            # 安装前端依赖
            if not self.install_frontend_dependencies():
                print("❌ Frontend dependencies installation failed.")
                return False
            
            # 运行其他测试（不启动前端服务器）
            self.test_service_layer_integration()
            self.test_cors_configuration()
            self.test_authentication_flow()
            self.test_frontend_backend_communication()
            
            # 总结
            print("\n📊 Frontend Integration Test Summary")
            print("=" * 70)
            passed_tests = sum(1 for test in self.test_results if test['passed'])
            total_tests = len(self.test_results)
            
            print(f"Total Integration Tests: {total_tests}")
            print(f"Passed: {passed_tests}")
            print(f"Failed: {total_tests - passed_tests}")
            print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
            
            # 保存结果
            with open('frontend_integration_test_results.json', 'w') as f:
                json.dump(self.test_results, f, indent=2)
            
            print(f"\n📝 Detailed results saved to: frontend_integration_test_results.json")
            
            if passed_tests == total_tests:
                print("\n🎉 All frontend integration tests passed!")
                print("\n📋 Integration Summary:")
                print(f"   - Backend API: {BACKEND_URL}")
                print(f"   - Frontend Path: {FRONTEND_PATH}")
                print("   - CORS: Configured")
                print("   - Authentication: Working")
                print("   - Service Layer: Ready")
                print("\n🚀 Ready for full-stack testing!")
                print("   1. Start frontend: cd front-end && npm start")
                print("   2. Visit: http://localhost:3000")
                print("   3. Test user credentials: frontendtest / frontend123")
            else:
                print(f"\n⚠️  {total_tests - passed_tests} integration test(s) failed.")
            
            return passed_tests == total_tests
            
        finally:
            self.cleanup()

if __name__ == "__main__":
    test_runner = FrontendIntegrationTest()
    success = test_runner.run_all_tests()
    sys.exit(0 if success else 1)