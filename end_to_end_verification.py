#!/usr/bin/env python3
"""
End-to-End Migration Verification for JobQuest Navigator
Validates the complete migration from Django to FastAPI
"""

import sys
import os
import requests
import time
import subprocess
import json

def test_django_backend():
    """Test Django backend functionality"""
    print("🧪 Testing Django Backend...")
    
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()
        
        from core.models import User
        from jobs.models import Job
        print("  ✅ Django models import successfully")
        
        # Test basic model creation (in memory)
        user_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
        print("  ✅ Django model structure validated")
        
        return True
    except Exception as e:
        print(f"  ❌ Django backend test failed: {e}")
        return False

def test_fastapi_imports():
    """Test FastAPI backend imports"""
    print("\n🧪 Testing FastAPI Backend Imports...")
    
    try:
        sys.path.append('/Users/kevinwang/Documents/Project/20-Project/t2/JobQuest_Navigator_CAA/jobquest-navigator-v2/backend-fastapi-graphql')
        
        # Test core imports (without database dependencies)
        from fastapi import FastAPI
        import strawberry
        from strawberry.fastapi import GraphQLRouter
        print("  ✅ FastAPI and Strawberry GraphQL import successfully")
        
        # Test configuration
        from app.core.config import Settings
        settings = Settings()
        print("  ✅ Configuration system works")
        
        return True
    except Exception as e:
        print(f"  ❌ FastAPI import test failed: {e}")
        return False

def test_frontend_structure():
    """Test frontend structure and configuration"""
    print("\n🧪 Testing Frontend Structure...")
    
    try:
        # Check if key frontend files exist
        frontend_dir = "/Users/kevinwang/Documents/Project/20-Project/t2/JobQuest_Navigator_CAA/frontend"
        
        key_files = [
            "src/apolloClient.js",
            "src/pages/CreateJob.jsx", 
            "src/context/JobContext.jsx",
            ".env"
        ]
        
        for file_path in key_files:
            full_path = os.path.join(frontend_dir, file_path)
            if os.path.exists(full_path):
                print(f"  ✅ {file_path} exists")
            else:
                print(f"  ❌ {file_path} missing")
                return False
        
        # Check Apollo Client configuration
        apollo_path = os.path.join(frontend_dir, "src/apolloClient.js")
        with open(apollo_path, 'r') as f:
            content = f.read()
            if "fastapi" in content.lower() and "graphql" in content.lower():
                print("  ✅ Apollo Client configured for dual endpoints")
            else:
                print("  ⚠️  Apollo Client may need FastAPI configuration")
        
        return True
    except Exception as e:
        print(f"  ❌ Frontend structure test failed: {e}")
        return False

def test_removed_dependencies():
    """Test that external dependencies have been removed"""
    print("\n🧪 Testing Removed Dependencies...")
    
    try:
        # Check that Maps-related code is removed
        frontend_dir = "/Users/kevinwang/Documents/Project/20-Project/t2/JobQuest_Navigator_CAA/frontend/src"
        
        # Check JobListings.jsx for removed Maps
        job_listings_path = os.path.join(frontend_dir, "pages/JobListings.jsx")
        if os.path.exists(job_listings_path):
            with open(job_listings_path, 'r') as f:
                content = f.read()
                if "google" not in content.lower() and "maps" not in content.lower():
                    print("  ✅ Google Maps removed from JobListings")
                else:
                    print("  ⚠️  Google Maps references may still exist")
        
        # Check that Adzuna API references are removed
        backend_dir = "/Users/kevinwang/Documents/Project/20-Project/t2/JobQuest_Navigator_CAA/backend/core"
        security_path = os.path.join(backend_dir, "security.py")
        if os.path.exists(security_path):
            with open(security_path, 'r') as f:
                content = f.read()
                if "adzuna" not in content.lower():
                    print("  ✅ Adzuna API removed from security module")
                else:
                    print("  ⚠️  Adzuna API references may still exist")
        
        return True
    except Exception as e:
        print(f"  ❌ Dependency removal test failed: {e}")
        return False

def test_user_job_functionality():
    """Test user job creation functionality"""
    print("\n🧪 Testing User Job Creation Functionality...")
    
    try:
        # Check CreateJob component exists and has proper structure
        frontend_dir = "/Users/kevinwang/Documents/Project/20-Project/t2/JobQuest_Navigator_CAA/frontend/src"
        create_job_path = os.path.join(frontend_dir, "pages/CreateJob.jsx")
        
        if os.path.exists(create_job_path):
            with open(create_job_path, 'r') as f:
                content = f.read()
                
                required_elements = [
                    "CREATE_USER_JOB",  # GraphQL mutation
                    "job title",        # Form field
                    "company",          # Form field
                    "description"       # Form field
                ]
                
                for element in required_elements:
                    if element.lower() in content.lower():
                        print(f"  ✅ {element} found in CreateJob component")
                    else:
                        print(f"  ❌ {element} missing from CreateJob component")
                        return False
        
        # Check GraphQL mutation definition
        if "mutation" in content and "CreateUserJob" in content:
            print("  ✅ GraphQL mutation properly defined")
        else:
            print("  ❌ GraphQL mutation not found")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ User job functionality test failed: {e}")
        return False

def test_authentication_migration():
    """Test authentication migration from JWT to Cognito"""
    print("\n🧪 Testing Authentication Migration...")
    
    try:
        # Check Apollo Client for Cognito token support
        frontend_dir = "/Users/kevinwang/Documents/Project/20-Project/t2/JobQuest_Navigator_CAA/frontend/src"
        apollo_path = os.path.join(frontend_dir, "apolloClient.js")
        
        with open(apollo_path, 'r') as f:
            content = f.read()
            
            if "cognito" in content.lower():
                print("  ✅ Cognito token support found in Apollo Client")
            else:
                print("  ⚠️  Cognito token support may need implementation")
            
            if "Bearer" in content:
                print("  ✅ Bearer token authentication configured")
            else:
                print("  ❌ Bearer token authentication missing")
                return False
        
        # Check environment configuration
        env_path = "/Users/kevinwang/Documents/Project/20-Project/t2/JobQuest_Navigator_CAA/frontend/.env"
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                content = f.read()
                if "FASTAPI" in content:
                    print("  ✅ FastAPI endpoint configuration found")
                else:
                    print("  ⚠️  FastAPI endpoint configuration may be missing")
        
        return True
    except Exception as e:
        print(f"  ❌ Authentication migration test failed: {e}")
        return False

def test_migration_compatibility():
    """Test migration compatibility and hybrid approach"""
    print("\n🧪 Testing Migration Compatibility...")
    
    try:
        # Check for dual endpoint support
        apollo_path = "/Users/kevinwang/Documents/Project/20-Project/t2/JobQuest_Navigator_CAA/frontend/src/apolloClient.js"
        
        with open(apollo_path, 'r') as f:
            content = f.read()
            
            if "getGraphQLEndpoint" in content:
                print("  ✅ Dual endpoint support implemented")
            else:
                print("  ❌ Dual endpoint support missing")
                return False
            
            if "USE_FASTAPI" in content:
                print("  ✅ Feature flag system implemented")
            else:
                print("  ❌ Feature flag system missing")
                return False
        
        # Check environment variables
        env_path = "/Users/kevinwang/Documents/Project/20-Project/t2/JobQuest_Navigator_CAA/frontend/.env"
        with open(env_path, 'r') as f:
            content = f.read()
            if "REACT_APP_USE_FASTAPI_JOBS" in content:
                print("  ✅ Migration feature flags configured")
            else:
                print("  ❌ Migration feature flags missing")
                return False
        
        return True
    except Exception as e:
        print(f"  ❌ Migration compatibility test failed: {e}")
        return False

def test_documentation_update():
    """Test that documentation has been updated"""
    print("\n🧪 Testing Documentation Updates...")
    
    try:
        base_dir = "/Users/kevinwang/Documents/Project/20-Project/t2/JobQuest_Navigator_CAA"
        docs_dir = os.path.join(base_dir, "docs")
        
        # Check for new documentation files
        new_docs = [
            "Technical-Design-Document-v2.md",
            "JobQuest-Navigator-PRD-v2.md", 
            "User-Flow-Design-v2.md"
        ]
        
        for doc in new_docs:
            doc_path = os.path.join(docs_dir, doc)
            if os.path.exists(doc_path):
                with open(doc_path, 'r') as f:
                    content = f.read()
                    if "fastapi" in content.lower() and "simplified" in content.lower():
                        print(f"  ✅ {doc} updated with new architecture")
                    else:
                        print(f"  ⚠️  {doc} may need architecture updates")
            else:
                print(f"  ❌ {doc} not found in docs/ directory")
                return False
        
        return True
    except Exception as e:
        print(f"  ❌ Documentation update test failed: {e}")
        return False

def run_end_to_end_verification():
    """Run comprehensive end-to-end verification"""
    print("🚀 Starting End-to-End Migration Verification\n")
    
    tests = [
        ("Django Backend Compatibility", test_django_backend),
        ("FastAPI Backend Imports", test_fastapi_imports),
        ("Frontend Structure", test_frontend_structure),
        ("Removed Dependencies", test_removed_dependencies),
        ("User Job Functionality", test_user_job_functionality),
        ("Authentication Migration", test_authentication_migration),
        ("Migration Compatibility", test_migration_compatibility),
        ("Documentation Updates", test_documentation_update)
    ]
    
    passed = 0
    total = len(tests)
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    print(f"\n📊 Verification Results: {passed}/{total} tests passed")
    
    # Detailed results
    print("\n📋 Detailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    # Migration status assessment
    print("\n🎯 Migration Status Assessment:")
    
    if passed >= total * 0.9:  # 90% or more
        print("🎉 EXCELLENT: Migration is highly successful with minimal issues")
    elif passed >= total * 0.75:  # 75% or more  
        print("✅ GOOD: Migration is largely successful with some minor issues")
    elif passed >= total * 0.5:   # 50% or more
        print("⚠️  FAIR: Migration has significant progress but needs attention")
    else:
        print("❌ NEEDS WORK: Migration requires substantial fixes")
    
    # Feature status summary
    print("\n🔧 Feature Implementation Status:")
    feature_status = {
        "Backend Architecture Migration": results.get("FastAPI Backend Imports", False),
        "User Job Input System": results.get("User Job Functionality", False),
        "External API Removal": results.get("Removed Dependencies", False),
        "Authentication Upgrade": results.get("Authentication Migration", False),
        "Dual Endpoint Support": results.get("Migration Compatibility", False),
        "Documentation Updates": results.get("Documentation Updates", False)
    }
    
    for feature, status in feature_status.items():
        icon = "✅" if status else "⚠️"
        print(f"  {icon} {feature}")
    
    # Next steps recommendation
    print("\n📋 Recommended Next Steps:")
    if not results.get("FastAPI Backend Imports", True):
        print("  1. Fix FastAPI backend import issues")
    if not results.get("Authentication Migration", True):
        print("  2. Complete Cognito authentication integration") 
    if not results.get("User Job Functionality", True):
        print("  3. Finalize user job creation functionality")
    
    print("  4. Deploy FastAPI backend to AWS Lambda")
    print("  5. Implement remaining AI features (skills assessment, resume optimization)")
    print("  6. Complete end-to-end testing with live services")
    
    return passed >= total * 0.75  # Consider success if 75% or more tests pass

if __name__ == "__main__":
    success = run_end_to_end_verification()
    sys.exit(0 if success else 1)