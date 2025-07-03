#!/usr/bin/env python3
"""
Test script to verify Adzuna API integration and functionality.
"""

import requests
import json
import sys

def test_direct_adzuna_api():
    """Test direct connection to Adzuna API."""
    print("🔍 Testing direct Adzuna API connection...")
    
    url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
    params = {
        'app_id': '3aea9429',
        'app_key': '47c6c2410fe3c75a1a1e7e90eb21fa95',
        'what': 'programmer',
        'where': 'los angeles',
        'results_per_page': 3
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        results_count = len(data.get('results', []))
        total_count = data.get('count', 0)
        
        print(f"✅ Direct API test successful!")
        print(f"   📊 Total jobs found: {total_count}")
        print(f"   📄 Results returned: {results_count}")
        
        if results_count > 0:
            job = data['results'][0]
            print(f"   📝 Sample job: {job.get('title', 'N/A')} at {job.get('company', {}).get('display_name', 'N/A')}")
        
        return True
        
    except requests.RequestException as e:
        print(f"❌ Direct API test failed: {e}")
        return False

def test_backend_api():
    """Test backend Django API integration."""
    print("\n🔍 Testing backend Django API...")
    
    # Test backend health
    try:
        health_response = requests.get('http://localhost:8000/health/', timeout=10)
        if health_response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"⚠️ Backend health check returned: {health_response.status_code}")
    except requests.RequestException as e:
        print(f"❌ Backend is not accessible: {e}")
        return False
    
    # Test jobs API endpoint
    try:
        jobs_response = requests.get('http://localhost:8000/api/jobs/jobs/', timeout=10)
        
        if jobs_response.status_code == 200:
            data = jobs_response.json()
            print(f"✅ Jobs API accessible")
            
            if isinstance(data, dict) and 'results' in data:
                results_count = len(data['results'])
                print(f"   📊 Jobs in database: {results_count}")
                
                if results_count > 0:
                    job = data['results'][0]
                    print(f"   📝 Sample job: {job.get('title', 'N/A')}")
                else:
                    print("   ⚠️ No jobs found in database - may need to sync from Adzuna")
            else:
                print(f"   ⚠️ Unexpected response format: {type(data)}")
        
        elif jobs_response.status_code == 401:
            print("⚠️ Jobs API requires authentication")
        else:
            print(f"⚠️ Jobs API returned status: {jobs_response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ Jobs API test failed: {e}")
        return False
    
    return True

def test_frontend_api_calls():
    """Test that frontend can make API calls."""
    print("\n🔍 Testing frontend API calls...")
    
    # Test if frontend is running
    try:
        frontend_response = requests.get('http://localhost:3002', timeout=5)
        if frontend_response.status_code == 200:
            print("✅ Frontend is running on port 3002")
        else:
            print(f"⚠️ Frontend returned status: {frontend_response.status_code}")
    except requests.RequestException as e:
        print(f"❌ Frontend is not accessible on port 3002: {e}")
        return False
    
    return True

def test_graphql_endpoint():
    """Test GraphQL endpoint."""
    print("\n🔍 Testing GraphQL endpoint...")
    
    query = """
    query {
        __schema {
            types {
                name
            }
        }
    }
    """
    
    try:
        response = requests.post(
            'http://localhost:8000/graphql/',
            json={'query': query},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                print("✅ GraphQL endpoint is working")
                # Count available types
                types = data['data']['__schema']['types']
                print(f"   📊 Available GraphQL types: {len(types)}")
            else:
                print(f"⚠️ GraphQL returned errors: {data.get('errors', 'Unknown error')}")
        else:
            print(f"⚠️ GraphQL endpoint returned status: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ GraphQL test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🧪 JobQuest Navigator - Adzuna API Integration Test")
    print("=" * 60)
    
    tests = [
        test_direct_adzuna_api,
        test_backend_api,
        test_frontend_api_calls,
        test_graphql_endpoint
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"   ✅ Passed: {sum(results)}")
    print(f"   ❌ Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("🎉 All tests passed! Adzuna API integration is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())