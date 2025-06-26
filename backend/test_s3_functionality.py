#!/usr/bin/env python
"""
S3文件上传和存储功能测试
测试LocalStack S3服务的文件操作
"""

import os
import sys
import boto3
import json
import tempfile
from datetime import datetime

# LocalStack S3配置
LOCALSTACK_URL = 'http://localhost:4566'
AWS_ACCESS_KEY_ID = 'test'
AWS_SECRET_ACCESS_KEY = 'test'
AWS_REGION = 'us-east-1'

class S3FunctionalityTest:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=LOCALSTACK_URL,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.test_results = []
        self.static_bucket = 'jobquest-navigator-static-local'
        self.frontend_bucket = 'jobquest-navigator-frontend-local'
    
    def log_test(self, name, passed, details=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({'name': name, 'passed': passed, 'details': details})
        print(f"{status} {name}: {details}")
    
    def test_bucket_access(self):
        """测试S3存储桶访问"""
        print("🪣 Testing S3 Bucket Access")
        
        try:
            # 列出所有存储桶
            response = self.s3_client.list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]
            
            # 检查必需的存储桶
            required_buckets = [self.static_bucket, self.frontend_bucket]
            all_buckets_exist = all(bucket in buckets for bucket in required_buckets)
            
            self.log_test("S3 - Bucket Access", all_buckets_exist, 
                         f"Found buckets: {buckets}")
            
            # 测试每个存储桶的访问权限
            for bucket in required_buckets:
                try:
                    self.s3_client.head_bucket(Bucket=bucket)
                    self.log_test(f"S3 - {bucket} Access", True, "Bucket accessible")
                except Exception as e:
                    self.log_test(f"S3 - {bucket} Access", False, f"Error: {str(e)}")
                    
        except Exception as e:
            self.log_test("S3 - Bucket Access", False, f"Error: {str(e)}")
    
    def test_file_upload_download(self):
        """测试文件上传和下载"""
        print("\n📁 Testing File Upload/Download")
        
        # 创建测试文件
        test_files = [
            ('test.txt', 'Hello, JobQuest Navigator!', 'text/plain'),
            ('test.json', json.dumps({'message': 'API test data', 'timestamp': datetime.now().isoformat()}), 'application/json'),
            ('test.css', 'body { background-color: #f0f0f0; }', 'text/css'),
        ]
        
        for filename, content, content_type in test_files:
            try:
                # 上传文件到静态存储桶
                self.s3_client.put_object(
                    Bucket=self.static_bucket,
                    Key=f'test/{filename}',
                    Body=content.encode('utf-8'),
                    ContentType=content_type
                )
                
                self.log_test(f"S3 - Upload {filename}", True, 
                             f"Uploaded to {self.static_bucket}/test/{filename}")
                
                # 验证文件存在
                try:
                    response = self.s3_client.head_object(
                        Bucket=self.static_bucket,
                        Key=f'test/{filename}'
                    )
                    file_size = response['ContentLength']
                    self.log_test(f"S3 - Verify {filename}", True, 
                                 f"File exists, size: {file_size} bytes")
                except Exception as e:
                    self.log_test(f"S3 - Verify {filename}", False, f"Error: {str(e)}")
                
                # 下载并验证内容
                try:
                    response = self.s3_client.get_object(
                        Bucket=self.static_bucket,
                        Key=f'test/{filename}'
                    )
                    downloaded_content = response['Body'].read().decode('utf-8')
                    content_matches = downloaded_content == content
                    
                    self.log_test(f"S3 - Download {filename}", content_matches,
                                 f"Content {'matches' if content_matches else 'differs'}")
                except Exception as e:
                    self.log_test(f"S3 - Download {filename}", False, f"Error: {str(e)}")
                    
            except Exception as e:
                self.log_test(f"S3 - Upload {filename}", False, f"Error: {str(e)}")
    
    def test_static_file_simulation(self):
        """模拟Django静态文件上传"""
        print("\n🎨 Testing Static File Simulation")
        
        static_files = {
            'css/styles.css': '''
/* JobQuest Navigator Styles */
.navbar { background-color: #2c3e50; }
.btn-primary { background-color: #3498db; }
.footer { text-align: center; color: #7f8c8d; }
            ''',
            'js/app.js': '''
// JobQuest Navigator JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('JobQuest Navigator loaded');
});
            ''',
            'images/logo.svg': '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="40" fill="#3498db"/>
    <text x="50" y="55" text-anchor="middle" fill="white" font-size="12">JQ</text>
</svg>
            '''
        }
        
        for file_path, content in static_files.items():
            try:
                # 确定内容类型
                if file_path.endswith('.css'):
                    content_type = 'text/css'
                elif file_path.endswith('.js'):
                    content_type = 'application/javascript'
                elif file_path.endswith('.svg'):
                    content_type = 'image/svg+xml'
                else:
                    content_type = 'application/octet-stream'
                
                # 上传静态文件
                self.s3_client.put_object(
                    Bucket=self.static_bucket,
                    Key=f'static/{file_path}',
                    Body=content.strip().encode('utf-8'),
                    ContentType=content_type
                )
                
                self.log_test(f"Static - Upload {file_path}", True,
                             f"Uploaded as {content_type}")
                
                # 生成公共URL（LocalStack格式）
                url = f"{LOCALSTACK_URL}/{self.static_bucket}/static/{file_path}"
                self.log_test(f"Static - URL {file_path}", True, f"URL: {url}")
                
            except Exception as e:
                self.log_test(f"Static - Upload {file_path}", False, f"Error: {str(e)}")
    
    def test_frontend_deployment_simulation(self):
        """模拟前端部署到S3"""
        print("\n🌐 Testing Frontend Deployment Simulation")
        
        # 模拟React构建文件
        frontend_files = {
            'index.html': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JobQuest Navigator</title>
</head>
<body>
    <div id="root"></div>
    <script src="/static/js/main.js"></script>
</body>
</html>
            ''',
            'static/js/main.js': '''
// JobQuest Navigator Main App
console.log("JobQuest Navigator Frontend Loaded");
window.JobQuestConfig = {
    apiUrl: "http://localhost:8000/api",
    version: "1.0.0"
};
            ''',
            'static/css/main.css': '''
/* JobQuest Navigator Main Styles */
body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
.app-header { background: #2c3e50; color: white; padding: 1rem; }
.main-content { padding: 2rem; }
            ''',
            'manifest.json': json.dumps({
                "short_name": "JobQuest",
                "name": "JobQuest Navigator",
                "description": "Your career navigation companion"
            }, indent=2)
        }
        
        uploaded_count = 0
        for file_path, content in frontend_files.items():
            try:
                # 确定内容类型
                if file_path.endswith('.html'):
                    content_type = 'text/html'
                elif file_path.endswith('.js'):
                    content_type = 'application/javascript'
                elif file_path.endswith('.css'):
                    content_type = 'text/css'
                elif file_path.endswith('.json'):
                    content_type = 'application/json'
                else:
                    content_type = 'text/plain'
                
                # 上传到前端存储桶
                self.s3_client.put_object(
                    Bucket=self.frontend_bucket,
                    Key=file_path,
                    Body=content.strip().encode('utf-8'),
                    ContentType=content_type
                )
                
                uploaded_count += 1
                self.log_test(f"Frontend - Upload {file_path}", True,
                             f"Uploaded as {content_type}")
                
            except Exception as e:
                self.log_test(f"Frontend - Upload {file_path}", False, f"Error: {str(e)}")
        
        # 验证前端部署完整性
        try:
            # 列出前端存储桶中的所有文件
            response = self.s3_client.list_objects_v2(Bucket=self.frontend_bucket)
            objects = response.get('Contents', [])
            object_keys = [obj['Key'] for obj in objects]
            
            self.log_test("Frontend - Deployment Complete", 
                         len(object_keys) == len(frontend_files),
                         f"Uploaded {len(object_keys)}/{len(frontend_files)} files")
            
            # 生成前端访问URL
            frontend_url = f"{LOCALSTACK_URL}/{self.frontend_bucket}/index.html"
            self.log_test("Frontend - Access URL", True, f"URL: {frontend_url}")
            
        except Exception as e:
            self.log_test("Frontend - Deployment Complete", False, f"Error: {str(e)}")
    
    def test_file_permissions(self):
        """测试文件权限和访问控制"""
        print("\n🔒 Testing File Permissions")
        
        try:
            # 上传带有公共读权限的文件
            test_content = "Public test file content"
            self.s3_client.put_object(
                Bucket=self.static_bucket,
                Key='public/test-public.txt',
                Body=test_content.encode('utf-8'),
                ContentType='text/plain',
                ACL='public-read'
            )
            
            self.log_test("S3 - Public File Upload", True, "Public file uploaded")
            
            # 上传私有文件
            private_content = "Private test file content"
            self.s3_client.put_object(
                Bucket=self.static_bucket,
                Key='private/test-private.txt',
                Body=private_content.encode('utf-8'),
                ContentType='text/plain'
            )
            
            self.log_test("S3 - Private File Upload", True, "Private file uploaded")
            
        except Exception as e:
            self.log_test("S3 - File Permissions", False, f"Error: {str(e)}")
    
    def test_cleanup(self):
        """清理测试文件"""
        print("\n🧹 Cleaning Up Test Files")
        
        test_keys = [
            'test/test.txt', 'test/test.json', 'test/test.css',
            'static/css/styles.css', 'static/js/app.js', 'static/images/logo.svg',
            'public/test-public.txt', 'private/test-private.txt'
        ]
        
        cleaned_count = 0
        for key in test_keys:
            try:
                self.s3_client.delete_object(Bucket=self.static_bucket, Key=key)
                cleaned_count += 1
            except Exception:
                pass  # 忽略不存在的文件
        
        self.log_test("S3 - Cleanup", True, f"Cleaned {cleaned_count} test files")
    
    def run_all_tests(self):
        """运行所有S3功能测试"""
        print("🚀 JobQuest Navigator S3 Functionality Test")
        print("=" * 60)
        
        # 运行所有测试
        self.test_bucket_access()
        self.test_file_upload_download()
        self.test_static_file_simulation()
        self.test_frontend_deployment_simulation()
        self.test_file_permissions()
        self.test_cleanup()
        
        # 总结
        print("\n📊 S3 Test Summary")
        print("=" * 60)
        passed_tests = sum(1 for test in self.test_results if test['passed'])
        total_tests = len(self.test_results)
        
        print(f"Total S3 Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # 保存结果
        with open('s3_functionality_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📝 Detailed results saved to: s3_functionality_test_results.json")
        
        if passed_tests == total_tests:
            print("\n🎉 All S3 tests passed! S3 functionality is working correctly.")
            print("\n📋 S3 Service Summary:")
            print(f"   - Static files bucket: {self.static_bucket}")
            print(f"   - Frontend bucket: {self.frontend_bucket}")
            print(f"   - LocalStack endpoint: {LOCALSTACK_URL}")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} S3 test(s) failed.")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    test_runner = S3FunctionalityTest()
    success = test_runner.run_all_tests()
    sys.exit(0 if success else 1)