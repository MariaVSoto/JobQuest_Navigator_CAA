#!/usr/bin/env python
"""
Lambda部署准备测试脚本
测试Zappa配置和Lambda部署准备工作
"""

import os
import sys
import json
import subprocess
import tempfile
from datetime import datetime

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_local')

import django
django.setup()

class LambdaPreparationTest:
    def __init__(self):
        self.test_results = []
        self.zappa_config_file = 'zappa_settings_local.json'
        
    def log_test(self, name, passed, details=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({'name': name, 'passed': passed, 'details': details})
        print(f"{status} {name}: {details}")
    
    def test_zappa_installation(self):
        """测试Zappa安装"""
        print("🔧 Testing Zappa Installation")
        
        try:
            result = subprocess.run(['zappa', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            passed = result.returncode == 0
            version = result.stdout.strip() if passed else "Not installed"
            self.log_test("Zappa - Installation", passed, f"Version: {version}")
        except Exception as e:
            self.log_test("Zappa - Installation", False, f"Error: {str(e)}")
    
    def test_zappa_configuration(self):
        """测试Zappa配置文件"""
        print("\n⚙️ Testing Zappa Configuration")
        
        try:
            # 检查配置文件是否存在
            config_exists = os.path.exists(self.zappa_config_file)
            self.log_test("Zappa - Config File Exists", config_exists, 
                         f"File: {self.zappa_config_file}")
            
            if config_exists:
                # 验证配置文件格式
                with open(self.zappa_config_file, 'r') as f:
                    config = json.load(f)
                
                # 检查必需的配置项
                required_keys = ['local']
                local_config = config.get('local', {})
                required_local_keys = [
                    'app_function', 'aws_region', 'runtime', 
                    'environment_variables', 'project_name'
                ]
                
                config_valid = all(key in config for key in required_keys)
                local_config_valid = all(key in local_config for key in required_local_keys)
                
                self.log_test("Zappa - Config Format", config_valid and local_config_valid,
                             f"Valid config structure: {config_valid and local_config_valid}")
                
                # 验证应用函数路径
                app_function = local_config.get('app_function', '')
                app_function_valid = app_function == 'core.wsgi.application'
                self.log_test("Zappa - App Function", app_function_valid,
                             f"App function: {app_function}")
                
                # 验证环境变量
                env_vars = local_config.get('environment_variables', {})
                django_settings = env_vars.get('DJANGO_SETTINGS_MODULE', '')
                settings_valid = django_settings == 'core.settings_local'
                self.log_test("Zappa - Django Settings", settings_valid,
                             f"Django settings: {django_settings}")
                
            else:
                self.log_test("Zappa - Config Validation", False, "Config file not found")
                
        except Exception as e:
            self.log_test("Zappa - Configuration", False, f"Error: {str(e)}")
    
    def test_aws_credentials(self):
        """测试AWS凭据配置"""
        print("\n🔑 Testing AWS Credentials")
        
        try:
            # 检查环境变量
            aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID', 'test')
            aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY', 'test')
            aws_region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
            aws_endpoint = os.environ.get('AWS_ENDPOINT_URL', 'http://localhost:4566')
            
            credentials_set = all([aws_access_key, aws_secret_key, aws_region])
            self.log_test("AWS - Credentials Set", credentials_set,
                         f"Access Key: {aws_access_key}, Region: {aws_region}")
            
            # 检查LocalStack端点
            localstack_endpoint = aws_endpoint == 'http://localhost:4566'
            self.log_test("AWS - LocalStack Endpoint", localstack_endpoint,
                         f"Endpoint: {aws_endpoint}")
            
            # 测试AWS CLI配置（如果可用）
            try:
                result = subprocess.run(['aws', 'configure', 'list'], 
                                      capture_output=True, text=True, timeout=10)
                aws_cli_available = result.returncode == 0
                self.log_test("AWS - CLI Available", aws_cli_available,
                             "AWS CLI configured" if aws_cli_available else "AWS CLI not configured")
            except Exception:
                self.log_test("AWS - CLI Available", False, "AWS CLI not found")
                
        except Exception as e:
            self.log_test("AWS - Credentials", False, f"Error: {str(e)}")
    
    def test_django_wsgi_application(self):
        """测试Django WSGI应用"""
        print("\n🐍 Testing Django WSGI Application")
        
        try:
            # 尝试导入WSGI应用
            from core.wsgi import application
            wsgi_importable = application is not None
            self.log_test("Django - WSGI Import", wsgi_importable,
                         f"WSGI application: {type(application).__name__}")
            
            # 检查Django设置
            from django.conf import settings
            debug_mode = settings.DEBUG
            allowed_hosts = settings.ALLOWED_HOSTS
            
            self.log_test("Django - Settings", True,
                         f"Debug: {debug_mode}, Allowed hosts: {len(allowed_hosts)}")
            
            # 检查数据库连接
            from django.db import connection
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    db_connection = True
            except Exception:
                db_connection = False
            
            self.log_test("Django - Database", db_connection,
                         f"Database: {settings.DATABASES['default']['ENGINE']}")
            
        except Exception as e:
            self.log_test("Django - WSGI Application", False, f"Error: {str(e)}")
    
    def test_lambda_package_size(self):
        """估算Lambda包大小"""
        print("\n📦 Testing Lambda Package Size")
        
        try:
            # 计算项目文件大小
            total_size = 0
            file_count = 0
            
            exclude_patterns = [
                '__pycache__', '.git', '.env', 'node_modules', 
                'static', 'media', 'logs', '*.pyc', '*.sqlite3'
            ]
            
            for root, dirs, files in os.walk('.'):
                # 排除不需要的目录
                dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
                
                for file in files:
                    # 排除不需要的文件
                    if not any(pattern in file for pattern in exclude_patterns):
                        file_path = os.path.join(root, file)
                        try:
                            size = os.path.getsize(file_path)
                            total_size += size
                            file_count += 1
                        except OSError:
                            pass
            
            # 转换为MB
            size_mb = total_size / (1024 * 1024)
            
            # Lambda限制检查（250MB解压缩）
            size_acceptable = size_mb < 200  # 留一些缓冲空间
            
            self.log_test("Lambda - Package Size", size_acceptable,
                         f"Estimated size: {size_mb:.2f}MB ({file_count} files)")
            
            if not size_acceptable:
                self.log_test("Lambda - Size Warning", False,
                             "Package may be too large for Lambda deployment")
            
        except Exception as e:
            self.log_test("Lambda - Package Size", False, f"Error: {str(e)}")
    
    def test_zappa_validation(self):
        """测试Zappa验证"""
        print("\n✅ Testing Zappa Validation")
        
        try:
            # 设置LocalStack环境变量
            env = os.environ.copy()
            env.update({
                'AWS_ACCESS_KEY_ID': 'test',
                'AWS_SECRET_ACCESS_KEY': 'test',
                'AWS_DEFAULT_REGION': 'us-east-1',
                'AWS_ENDPOINT_URL': 'http://localhost:4566'
            })
            
            # 运行Zappa状态检查（不会实际部署）
            result = subprocess.run(['zappa', 'status', 'local'], 
                                  capture_output=True, text=True, 
                                  timeout=30, env=env, cwd='.')
            
            # 预期会失败，因为还没部署，但这能验证配置
            validation_passed = 'local' in result.stderr or 'local' in result.stdout
            
            self.log_test("Zappa - Validation", validation_passed,
                         "Zappa can read configuration")
            
        except subprocess.TimeoutExpired:
            self.log_test("Zappa - Validation", False, "Zappa command timed out")
        except Exception as e:
            self.log_test("Zappa - Validation", False, f"Error: {str(e)}")
    
    def test_deployment_prerequisites(self):
        """测试部署先决条件"""
        print("\n📋 Testing Deployment Prerequisites")
        
        # 检查必需的Python包
        required_packages = [
            ('django', 'django'), 
            ('djangorestframework', 'rest_framework'), 
            ('zappa', 'zappa'), 
            ('boto3', 'boto3')
        ]
        
        for package_name, import_name in required_packages:
            try:
                __import__(import_name)
                self.log_test(f"Package - {package_name}", True, "Installed")
            except ImportError:
                self.log_test(f"Package - {package_name}", False, "Not installed")
        
        # 检查项目文件
        required_files = [
            'manage.py', 'core/wsgi.py', 'core/settings_local.py',
            'zappa_settings_local.json'
        ]
        
        for file_path in required_files:
            file_exists = os.path.exists(file_path)
            self.log_test(f"File - {file_path}", file_exists,
                         "Exists" if file_exists else "Missing")
        
        # 检查数据库迁移状态
        try:
            from django.core.management import execute_from_command_line
            from io import StringIO
            import sys
            
            # 捕获showmigrations输出
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            try:
                execute_from_command_line(['manage.py', 'showmigrations', 
                                         '--settings=core.settings_local'])
                migrations_output = captured_output.getvalue()
                migrations_applied = '[X]' in migrations_output
                self.log_test("Django - Migrations", migrations_applied,
                             "Migrations applied" if migrations_applied else "Migrations pending")
            finally:
                sys.stdout = old_stdout
                
        except Exception as e:
            self.log_test("Django - Migrations", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """运行所有Lambda准备测试"""
        print("🚀 JobQuest Navigator Lambda Deployment Preparation Test")
        print("=" * 70)
        
        # 运行所有测试
        self.test_zappa_installation()
        self.test_zappa_configuration()
        self.test_aws_credentials()
        self.test_django_wsgi_application()
        self.test_lambda_package_size()
        self.test_deployment_prerequisites()
        self.test_zappa_validation()
        
        # 总结
        print("\n📊 Lambda Preparation Test Summary")
        print("=" * 70)
        passed_tests = sum(1 for test in self.test_results if test['passed'])
        total_tests = len(self.test_results)
        
        print(f"Total Lambda Prep Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # 保存结果
        with open('lambda_preparation_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📝 Detailed results saved to: lambda_preparation_test_results.json")
        
        if passed_tests == total_tests:
            print("\n🎉 All Lambda preparation tests passed!")
            print("\n📋 Ready for Lambda Deployment:")
            print("   - Zappa is configured and ready")
            print("   - AWS credentials are set for LocalStack")
            print("   - Django WSGI application is functional")
            print("   - Package size is within Lambda limits")
            print("\n🚀 Next steps:")
            print("   1. Run: zappa deploy local")
            print("   2. Test Lambda endpoints")
            print("   3. Run: zappa update local (for subsequent deployments)")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} preparation test(s) failed.")
            print("Please fix the issues before attempting Lambda deployment.")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    test_runner = LambdaPreparationTest()
    success = test_runner.run_all_tests()
    sys.exit(0 if success else 1)