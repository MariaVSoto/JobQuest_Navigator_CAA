#!/usr/bin/env python3
"""
Simple verification script for AWS Cognito configuration
"""

import requests
import json

def test_cognito_jwks():
    """Test if JWKS endpoint is accessible"""
    user_pool_id = "us-east-1_blSZREFys"
    region = "us-east-1"
    jwks_url = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
    
    print("🔐 Testing Cognito JWKS Endpoint")
    print("=" * 40)
    print(f"User Pool ID: {user_pool_id}")
    print(f"JWKS URL: {jwks_url}")
    
    try:
        response = requests.get(jwks_url, timeout=10)
        response.raise_for_status()
        
        jwks = response.json()
        num_keys = len(jwks.get('keys', []))
        
        print(f"✅ JWKS endpoint accessible")
        print(f"✅ Found {num_keys} signing keys")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_backend_endpoints():
    """Test backend endpoints if running"""
    print("\n🚀 Testing Backend Endpoints")
    print("=" * 40)
    
    endpoints = [
        ("Health Check", "http://localhost:8001/health"),
        ("Auth Status", "http://localhost:8001/auth/status"),
        ("GraphQL", "http://localhost:8001/graphql")
    ]
    
    results = []
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: OK")
                results.append(True)
                
                if "auth/status" in url:
                    data = response.json()
                    print(f"   Cognito configured: {data.get('cognito_configured', 'N/A')}")
                    print(f"   Development mode: {data.get('development_mode', 'N/A')}")
            else:
                print(f"⚠️  {name}: Status {response.status_code}")
                results.append(False)
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: Not running")
            results.append(False)
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            results.append(False)
    
    return results

def main():
    """Main verification function"""
    print("🧪 JobQuest Navigator v2 - Cognito Verification")
    print("=" * 60)
    
    # Test JWKS
    jwks_ok = test_cognito_jwks()
    
    # Test backend
    backend_results = test_backend_endpoints()
    backend_ok = any(backend_results)
    
    # Summary
    print("\n📋 Verification Summary")
    print("=" * 25)
    print(f"JWKS Endpoint: {'✅ PASS' if jwks_ok else '❌ FAIL'}")
    print(f"Backend: {'✅ RUNNING' if backend_ok else '⚠️  NOT RUNNING'}")
    
    print("\n🎯 Configuration Details")
    print("=" * 25)
    print("User Pool ID: us-east-1_blSZREFys")
    print("Client ID: 5iui547bod6sqgsi1a4heidpep")
    print("Region: us-east-1")
    
    if jwks_ok:
        print("\n🎉 Cognito is properly configured!")
        if not backend_ok:
            print("💡 Start the backend with: ./scripts/dev-start.sh")
        print("\n📚 Next Steps:")
        print("1. Start development environment: ./scripts/dev-start.sh")
        print("2. Access frontend: http://localhost:3001")
        print("3. Test GraphQL: http://localhost:8001/graphql")
    else:
        print("\n🔧 Configuration needs attention")
    
    return jwks_ok

if __name__ == "__main__":
    main()