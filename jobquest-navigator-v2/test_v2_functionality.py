#!/usr/bin/env python3
"""
Test script for JobQuest Navigator v2 functionality
Validates backend, GraphQL, and basic frontend connectivity
"""

import requests
import json
import time
import sys

def print_status(message, status="INFO"):
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m", 
        "ERROR": "\033[91m",
        "WARNING": "\033[93m"
    }
    end_color = "\033[0m"
    print(f"{colors.get(status, '')}{status}: {message}{end_color}")

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_status(f"Backend health check passed: {data}", "SUCCESS")
            return True
        else:
            print_status(f"Backend health check failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"Backend health check failed: {e}", "ERROR")
        return False

def test_graphql_introspection():
    """Test GraphQL introspection query"""
    try:
        query = {
            "query": "query { __schema { types { name } } }"
        }
        response = requests.post(
            "http://localhost:8001/graphql",
            json=query,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            types = [t['name'] for t in data['data']['__schema']['types']]
            print_status(f"GraphQL introspection passed. Available types: {types[:5]}...", "SUCCESS")
            return True
        else:
            print_status(f"GraphQL introspection failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"GraphQL introspection failed: {e}", "ERROR")
        return False

def test_user_registration():
    """Test user registration mutation"""
    try:
        mutation = {
            "query": """
            mutation {
                registerUser(
                    email: "test@v2.com",
                    username: "testv2user",
                    password: "password123",
                    firstName: "Test",
                    lastName: "User"
                ) {
                    success
                    user {
                        id
                        email
                        username
                        fullName
                    }
                }
            }
            """
        }
        response = requests.post(
            "http://localhost:8001/graphql",
            json=mutation,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('data', {}).get('registerUser', {}).get('success'):
                user = data['data']['registerUser']['user']
                print_status(f"User registration passed: {user['email']} ({user['username']})", "SUCCESS")
                return True
            else:
                print_status(f"User registration failed: {data}", "ERROR")
                return False
        else:
            print_status(f"User registration failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"User registration failed: {e}", "ERROR")
        return False

def test_authentication():
    """Test user authentication"""
    try:
        mutation = {
            "query": """
            mutation {
                tokenAuth(username: "testv2user", password: "password123") {
                    token
                }
            }
            """
        }
        response = requests.post(
            "http://localhost:8001/graphql",
            json=mutation,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get('data', {}).get('tokenAuth', {}).get('token')
            if token:
                print_status(f"Authentication passed: token received", "SUCCESS")
                return True
            else:
                print_status(f"Authentication failed: no token", "ERROR")
                return False
        else:
            print_status(f"Authentication failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"Authentication failed: {e}", "ERROR")
        return False

def test_frontend_access():
    """Test frontend accessibility"""
    try:
        response = requests.get("http://localhost:3001", timeout=5)
        if response.status_code == 200 and "React App" in response.text:
            print_status("Frontend access test passed", "SUCCESS")
            return True
        else:
            print_status(f"Frontend access failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"Frontend access failed: {e}", "ERROR")
        return False

def test_database_connection():
    """Test database connectivity through backend"""
    try:
        # We can test this by trying to access the current user endpoint
        query = {
            "query": "query { me { id email username } }"
        }
        response = requests.post(
            "http://localhost:8001/graphql",
            json=query,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            user = data.get('data', {}).get('me')
            if user:
                print_status(f"Database connection test passed: user data retrieved", "SUCCESS")
                return True
            else:
                print_status("Database connection test failed: no user data", "ERROR")
                return False
        else:
            print_status(f"Database connection test failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"Database connection test failed: {e}", "ERROR")
        return False

def main():
    """Run all tests"""
    print_status("JobQuest Navigator v2 - Functionality Tests", "INFO")
    print_status("=" * 50, "INFO")
    
    tests = [
        ("Backend Health", test_backend_health),
        ("GraphQL Introspection", test_graphql_introspection),
        ("Database Connection", test_database_connection),
        ("User Registration", test_user_registration),
        ("Authentication", test_authentication),
        ("Frontend Access", test_frontend_access),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print_status(f"Running {test_name}...", "INFO")
        if test_func():
            passed += 1
        print()
        time.sleep(0.5)  # Small delay between tests
    
    print_status("=" * 50, "INFO")
    print_status(f"Test Results: {passed}/{total} passed", "SUCCESS" if passed == total else "WARNING")
    
    if passed == total:
        print_status("🎉 All tests passed! v2 is working correctly.", "SUCCESS")
        return 0
    else:
        print_status(f"❌ {total - passed} tests failed. Check the logs above.", "ERROR")
        return 1

if __name__ == "__main__":
    sys.exit(main())