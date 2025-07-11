#!/usr/bin/env python3
"""
Test script for AWS Cognito configuration
Verifies that the User Pool and App Client are properly configured
"""

import os
import sys
import asyncio
import requests
from pathlib import Path

# Add the backend app to Python path
backend_path = Path(__file__).parent.parent / "backend-fastapi-graphql"
sys.path.insert(0, str(backend_path))

from app.core.config import settings
from app.auth.cognito import CognitoAuth


def test_cognito_config():
    """Test Cognito configuration"""
    print("🔐 Testing AWS Cognito Configuration")
    print("=" * 50)
    
    # Check environment variables
    print(f"User Pool ID: {settings.cognito_user_pool_id}")
    print(f"Client ID: {settings.cognito_client_id}")
    print(f"Region: {settings.cognito_region}")
    
    if not settings.cognito_user_pool_id:
        print("❌ COGNITO_USER_POOL_ID not configured")
        return False
    
    if not settings.cognito_client_id:
        print("⚠️  COGNITO_CLIENT_ID not configured - run ./scripts/setup-cognito.sh")
        print("   Will use development mode for authentication")
        return True
    
    # Test JWKS endpoint
    try:
        cognito_auth = CognitoAuth()
        jwks_url = cognito_auth.jwks_url
        print(f"JWKS URL: {jwks_url}")
        
        response = requests.get(jwks_url, timeout=10)
        response.raise_for_status()
        
        jwks = response.json()
        print(f"✅ JWKS endpoint accessible - {len(jwks.get('keys', []))} keys found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error accessing JWKS endpoint: {e}")
        return False


def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is running - {data.get('status')}")
            return True
        else:
            print(f"❌ Backend health check failed - Status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️  Backend is not running - start with ./scripts/dev-start.sh")
        return False
    except Exception as e:
        print(f"❌ Error checking backend: {e}")
        return False


def test_auth_endpoint():
    """Test authentication status endpoint"""
    try:
        response = requests.get("http://localhost:8001/auth/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Auth endpoint accessible")
            print(f"   Cognito configured: {data.get('cognito_configured')}")
            print(f"   Development mode: {data.get('development_mode')}")
            return True
        else:
            print(f"❌ Auth endpoint failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking auth endpoint: {e}")
        return False


def main():
    """Main test function"""
    print("🧪 JobQuest Navigator v2 - Cognito Configuration Test")
    print("=" * 60)
    
    # Test configuration
    config_ok = test_cognito_config()
    print()
    
    # Test backend
    backend_ok = test_backend_health()
    print()
    
    # Test auth endpoint if backend is running
    auth_ok = True
    if backend_ok:
        auth_ok = test_auth_endpoint()
        print()
    
    # Summary
    print("📋 Test Summary")
    print("-" * 20)
    print(f"Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Backend: {'✅ PASS' if backend_ok else '⚠️  NOT RUNNING'}")
    print(f"Authentication: {'✅ PASS' if auth_ok else '❌ FAIL'}")
    
    if config_ok and (not backend_ok or auth_ok):
        print("\n🎉 Cognito configuration is ready!")
        if not backend_ok:
            print("💡 Start the backend with: ./scripts/dev-start.sh")
    else:
        print("\n🔧 Configuration needs attention:")
        if not config_ok:
            print("   - Run ./scripts/setup-cognito.sh to configure App Client")
        if backend_ok and not auth_ok:
            print("   - Check backend logs for authentication issues")
    
    return config_ok and auth_ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)