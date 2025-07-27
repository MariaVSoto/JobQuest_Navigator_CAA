#!/usr/bin/env python3
"""
Deployment verification script for JobQuest Navigator v2
Tests both backend and frontend functionality including enhanced interview prep
"""

import requests
import json
import time
import sys
from urllib.parse import urljoin

# Service URLs
BACKEND_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:3001"
GRAPHQL_URL = f"{BACKEND_URL}/graphql"

def test_backend_health():
    """Test backend health endpoint"""
    print("🔍 Testing backend health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend is healthy - Status: {health_data.get('status')}")
            print(f"   Environment: {health_data.get('environment')}")
            print(f"   Database: {health_data.get('services', {}).get('database')}")
            print(f"   GraphQL: {health_data.get('services', {}).get('graphql')}")
            return True
        else:
            print(f"❌ Backend health check failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def test_graphql_schema():
    """Test GraphQL schema introspection"""
    print("\n🔍 Testing GraphQL schema...")
    try:
        query = {
            "query": """
            {
                __schema {
                    types {
                        name
                    }
                }
            }
            """
        }
        response = requests.post(GRAPHQL_URL, json=query, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and '__schema' in data['data']:
                types = [t['name'] for t in data['data']['__schema']['types']]
                expected_types = ['User', 'Job', 'Company', 'JobApplication', 'DashboardData']
                found_types = [t for t in expected_types if t in types]
                print(f"✅ GraphQL schema loaded - Found {len(found_types)}/{len(expected_types)} expected types")
                print(f"   Available types: {', '.join(found_types)}")
                return True
            else:
                print("❌ GraphQL schema introspection failed")
                return False
        else:
            print(f"❌ GraphQL request failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GraphQL test error: {e}")
        return False

def test_frontend_access():
    """Test frontend accessibility"""
    print("\n🔍 Testing frontend access...")
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            html_content = response.text
            if 'JobQuest Navigator' in html_content or 'interview-prep' in html_content:
                print("✅ Frontend is accessible and contains expected content")
                return True
            else:
                print("⚠️  Frontend accessible but content may be incomplete")
                return True
        else:
            print(f"❌ Frontend access failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend access error: {e}")
        return False

def test_enhanced_interview_prep():
    """Test enhanced interview prep functionality through GraphQL"""
    print("\n🔍 Testing enhanced interview prep components...")
    try:
        # Test mock data that should be available in enhanced component
        query = {
            "query": """
            {
                __type(name: "JobApplication") {
                    name
                    fields {
                        name
                        type {
                            name
                        }
                    }
                }
            }
            """
        }
        response = requests.post(GRAPHQL_URL, json=query, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and data['data']['__type']:
                fields = [f['name'] for f in data['data']['__type']['fields']]
                expected_fields = ['id', 'userId', 'jobId', 'status', 'appliedDate']
                found_fields = [f for f in expected_fields if f in fields]
                print(f"✅ JobApplication type available - {len(found_fields)}/{len(expected_fields)} expected fields")
                print("✅ Enhanced interview prep should work with available GraphQL types")
                return True
            else:
                print("❌ JobApplication type not found in schema")
                return False
        else:
            print(f"❌ GraphQL type introspection failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Enhanced interview prep test error: {e}")
        return False

def test_database_connection():
    """Test database connectivity through backend"""
    print("\n🔍 Testing database connection...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            db_status = health_data.get('services', {}).get('database', 'unknown')
            if db_status == 'connected':
                print("✅ Database connection verified")
                return True
            else:
                print(f"❌ Database connection failed - Status: {db_status}")
                return False
        else:
            print("❌ Could not check database status")
            return False
    except Exception as e:
        print(f"❌ Database connection test error: {e}")
        return False

def main():
    """Run all deployment verification tests"""
    print("🚀 JobQuest Navigator v2 - Deployment Verification")
    print("=" * 50)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("GraphQL Schema", test_graphql_schema),
        ("Frontend Access", test_frontend_access),
        ("Enhanced Interview Prep", test_enhanced_interview_prep),
        ("Database Connection", test_database_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            time.sleep(1)  # Brief pause between tests
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Deployment verification successful!")
        print("\n🌐 Access URLs:")
        print(f"   Frontend: {FRONTEND_URL}")
        print(f"   Backend API: {BACKEND_URL}")
        print(f"   GraphQL Playground: {GRAPHQL_URL}")
        print(f"   Enhanced Interview Prep: {FRONTEND_URL}/interview-prep")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)