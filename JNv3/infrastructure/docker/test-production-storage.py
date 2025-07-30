#!/usr/bin/env python3
"""
Production Storage Switching Test
Tests the ability to switch from MinIO (dev) to S3 (production) storage
"""

import os
import sys
import subprocess
import time
import requests
import json

def run_with_production_config():
    """Test running with production configuration"""
    print("🔄 Testing Production Storage Configuration...")
    
    try:
        # Create a temporary production environment override
        prod_env = {
            'ENVIRONMENT': 'production',
            'AWS_STORAGE_BUCKET_NAME': 'caa900resume',
            'AWS_S3_REGION_NAME': 'us-east-1',
            'DEBUG': 'false'
        }
        
        # Start a test backend container with production environment
        print("   📦 Starting backend with production environment...")
        
        # Use docker run to test production config without affecting current setup
        cmd = [
            'docker', 'run', '--rm', '-d',
            '--name', 'test_backend_prod',
            '--network', 'docker_jobquest_network',
            '-p', '8002:8000',  # Use different port to avoid conflicts
        ]
        
        # Add environment variables
        for key, value in prod_env.items():
            cmd.extend(['-e', f'{key}={value}'])
        
        # Add required database and redis connections
        cmd.extend([
            '-e', 'DATABASE_URL=postgresql+asyncpg://jobquest_user:jobquest_password_2024@jobquest_db_v2:5432/jobquest_navigator_v2',
            '-e', 'REDIS_URL=redis://:jobquest_redis_2024@jobquest_redis_v2:6379/0',
            '-e', 'SECRET_KEY=test-secret-key',
            '-e', 'COGNITO_USER_POOL_ID=us-east-1_blSZREFys',
            '-e', 'COGNITO_CLIENT_ID=5iui547bod6sqgsi1a4heidpep',
            'docker-backend',  # Use the existing backend image
            'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000'
        ])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"   ❌ Failed to start production backend: {result.stderr}")
            return False
        
        container_id = result.stdout.strip()
        print(f"   ✅ Started production test container: {container_id[:12]}")
        
        # Wait for the container to start
        print("   ⏳ Waiting for backend to start...")
        time.sleep(10)
        
        # Test the production backend
        try:
            response = requests.get('http://localhost:8002/health', timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"   ✅ Production backend health: {health_data.get('status')}")
                print(f"   🌍 Environment: {health_data.get('environment')}")
                
                # Check if it's using production environment
                if health_data.get('environment') == 'production':
                    print("   ✅ Successfully switched to production environment")
                    success = True
                else:
                    print("   ❌ Environment did not switch to production")
                    success = False
            else:
                print(f"   ❌ Production backend health check failed: {response.status_code}")
                success = False
                
        except Exception as e:
            print(f"   ❌ Production backend test error: {e}")
            success = False
        
        # Clean up the test container
        print("   🧹 Cleaning up test container...")
        subprocess.run(['docker', 'stop', container_id], capture_output=True)
        
        return success
        
    except Exception as e:
        print(f"   ❌ Production test error: {e}")
        return False

def test_terraform_configuration():
    """Test Terraform configuration for S3"""
    print("🏗️  Testing Terraform S3 Configuration...")
    
    try:
        terraform_dir = "../terraform"
        
        # Check if Terraform files exist
        main_tf = os.path.join(terraform_dir, "main.tf")
        prod_tfvars = os.path.join(terraform_dir, "environments/production.tfvars")
        
        if not os.path.exists(main_tf):
            print("   ❌ Terraform main.tf not found")
            return False
        
        if not os.path.exists(prod_tfvars):
            print("   ❌ Production tfvars not found")
            return False
        
        # Check if S3 configuration is present
        with open(main_tf, 'r') as f:
            main_content = f.read()
            
        with open(prod_tfvars, 'r') as f:
            prod_content = f.read()
        
        # Check for S3-related configurations
        s3_checks = [
            ('S3 module in main.tf', 'module "s3"' in main_content),
            ('S3 bucket name variable', 's3_bucket_name' in main_content),
            ('Production bucket name', 'caa900resume' in prod_content),
        ]
        
        all_passed = True
        for check_name, check_result in s3_checks:
            status = "✅" if check_result else "❌"
            print(f"   {status} {check_name}")
            if not check_result:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"   ❌ Terraform configuration test error: {e}")
        return False

def test_environment_switching():
    """Test the storage service environment switching logic"""
    print("🔀 Testing Environment Switching Logic...")
    
    # Test the current development environment
    try:
        response = requests.get('http://localhost:8001/health')
        if response.status_code == 200:
            health_data = response.json()
            current_env = health_data.get('environment', 'unknown')
            print(f"   ✅ Current environment: {current_env}")
        else:
            print("   ❌ Could not determine current environment")
            return False
    except Exception as e:
        print(f"   ❌ Environment check error: {e}")
        return False
    
    # Check environment variables
    try:
        env_check = subprocess.run([
            'docker', 'exec', 'jobquest_backend_v2', 'env'
        ], capture_output=True, text=True)
        
        if env_check.returncode == 0:
            env_vars = env_check.stdout
            
            checks = [
                ('MinIO endpoint configured', 'MINIO_ENDPOINT=' in env_vars),
                ('MinIO bucket configured', 'MINIO_BUCKET_NAME=' in env_vars),
                ('AWS S3 bucket configured', 'AWS_STORAGE_BUCKET_NAME=caa900resume' in env_vars),
                ('AWS region configured', 'AWS_S3_REGION_NAME=us-east-1' in env_vars),
            ]
            
            all_passed = True
            for check_name, check_result in checks:
                status = "✅" if check_result else "❌"
                print(f"   {status} {check_name}")
                if not check_result:
                    all_passed = False
            
            return all_passed
        else:
            print("   ❌ Could not check environment variables")
            return False
            
    except Exception as e:
        print(f"   ❌ Environment switching test error: {e}")
        return False

def main():
    """Run production storage tests"""
    print("🧪 Production Storage Configuration Test")
    print("=" * 50)
    
    tests = [
        ("Terraform Configuration", test_terraform_configuration),
        ("Environment Switching", test_environment_switching),
        ("Production Config Test", run_with_production_config),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
        print()
    
    # Summary
    print("=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All production storage tests passed!")
        print("\n📋 Ready for Production Deployment:")
        print("   • S3 bucket 'caa900resume' is configured")
        print("   • Environment switching logic is working")
        print("   • Terraform configuration is ready")
        print("   • Storage service supports both MinIO and S3")
        return 0
    else:
        print("\n⚠️  Some tests failed. Review the configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())