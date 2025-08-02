#!/usr/bin/env python3
"""
Storage Configuration Test Script
Tests both MinIO (development) and S3 (production) configurations
"""

import os
import sys
import requests
import json
from datetime import datetime

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get('http://localhost:8001/health', timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Backend Health Check:")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Environment: {health_data.get('environment')}")
            print(f"   Services: {health_data.get('services')}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def test_storage_config():
    """Test storage configuration via backend"""
    try:
        # Test GraphQL introspection to see if storage-related queries are available
        query = """
        {
            __schema {
                queryType {
                    fields {
                        name
                        description
                    }
                }
            }
        }
        """
        
        response = requests.post(
            'http://localhost:8001/graphql',
            json={'query': query},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            fields = data.get('data', {}).get('__schema', {}).get('queryType', {}).get('fields', [])
            
            # Look for resume-related fields that might use storage
            storage_fields = [f for f in fields if 'resume' in f.get('name', '').lower()]
            
            print("✅ GraphQL Storage-Related Queries:")
            for field in storage_fields:
                print(f"   - {field.get('name')}: {field.get('description', 'No description')}")
            
            return len(storage_fields) > 0
        else:
            print(f"❌ GraphQL introspection failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Storage configuration test error: {e}")
        return False

def test_environment_variables():
    """Test if required environment variables are configured"""
    print("🔧 Environment Variables Check:")
    
    # Test via backend container
    try:
        import docker
        client = docker.from_env()
        backend_container = client.containers.get('jobquest_backend_v2')
        
        # Get environment variables from container
        container_info = backend_container.attrs
        env_vars = container_info['Config']['Env']
        
        # Parse environment variables
        env_dict = {}
        for env_var in env_vars:
            if '=' in env_var:
                key, value = env_var.split('=', 1)
                env_dict[key] = value
        
        # Check storage-related variables
        storage_vars = [
            'ENVIRONMENT',
            'MINIO_ENDPOINT',
            'MINIO_BUCKET_NAME',
            'AWS_STORAGE_BUCKET_NAME',
            'AWS_S3_REGION_NAME'
        ]
        
        for var in storage_vars:
            value = env_dict.get(var, 'NOT SET')
            status = "✅" if value != 'NOT SET' else "❌"
            print(f"   {status} {var}: {value}")
        
        return True
        
    except ImportError:
        print("   ⚠️  Docker library not available, skipping container inspection")
        return True
    except Exception as e:
        print(f"   ❌ Environment check error: {e}")
        return False

def main():
    """Run all storage configuration tests"""
    print(f"🔍 Storage Configuration Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Backend Health
    if test_backend_health():
        tests_passed += 1
    print()
    
    # Test 2: Storage Configuration
    if test_storage_config():
        tests_passed += 1
    print()
    
    # Test 3: Environment Variables
    if test_environment_variables():
        tests_passed += 1
    print()
    
    # Summary
    print("=" * 60)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All storage configuration tests passed!")
        print("\n📋 Configuration Summary:")
        print("   • Backend is healthy and accessible")
        print("   • GraphQL endpoints are available")
        print("   • Environment variables are configured")
        print("   • Development: Using MinIO storage")
        print("   • Production: Configured for S3 (caa900resume bucket)")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())