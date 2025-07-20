#!/usr/bin/env python3
"""
Test script for Secure Authentication GraphQL queries and mutations
"""

import asyncio
from app.graphql.schema import schema

async def test_secure_login():
    """Test secure login mutation"""
    try:
        # Test secure login mutation
        login_mutation = '''
        mutation SecureLogin {
            secureLogin(username: "testuser", password: "securepassword") {
                success
                user {
                    id
                    email
                    username
                    fullName
                    currentJobTitle
                    industry
                }
                message
                errors
            }
        }
        '''
        
        print('Testing secure login mutation...')
        result = await schema.execute(login_mutation)
        
        if result.errors:
            print('❌ GraphQL Errors:', result.errors)
        else:
            print('✅ Secure login mutation successful!')
            login_result = result.data['secureLogin']
            if login_result['success']:
                user = login_result['user']
                print(f'Logged in user: {user["fullName"]} ({user["email"]})')
                print(f'Job Title: {user["currentJobTitle"]}')
                print(f'Industry: {user["industry"]}')
                print(f'Message: {login_result["message"]}')
            else:
                print('❌ Login failed:', login_result['errors'])
            return login_result['success']
            
    except Exception as e:
        print('❌ Test error:', str(e))
        return False

async def test_session_validation():
    """Test session validation query"""
    try:
        # Test session validation query
        validation_query = '''
        query ValidateSession {
            validateSession {
                valid
                user {
                    id
                    email
                    username
                    fullName
                    currentJobTitle
                }
                message
            }
        }
        '''
        
        print('Testing session validation query...')
        result = await schema.execute(validation_query)
        
        if result.errors:
            print('❌ GraphQL Errors:', result.errors)
        else:
            print('✅ Session validation query successful!')
            validation_result = result.data['validateSession']
            if validation_result['valid']:
                user = validation_result['user']
                print(f'Valid session for: {user["fullName"]} ({user["email"]})')
                print(f'Job Title: {user["currentJobTitle"]}')
                print(f'Message: {validation_result["message"]}')
            else:
                print('❌ Session is invalid')
            return validation_result['valid']
            
    except Exception as e:
        print('❌ Test error:', str(e))
        return False

async def test_token_refresh():
    """Test token refresh mutation"""
    try:
        # Test token refresh mutation
        refresh_mutation = '''
        mutation RefreshToken {
            refreshToken {
                success
                user {
                    id
                    email
                    username
                    fullName
                    bio
                    currentJobTitle
                }
                message
                errors
            }
        }
        '''
        
        print('Testing token refresh mutation...')
        result = await schema.execute(refresh_mutation)
        
        if result.errors:
            print('❌ GraphQL Errors:', result.errors)
        else:
            print('✅ Token refresh mutation successful!')
            refresh_result = result.data['refreshToken']
            if refresh_result['success']:
                user = refresh_result['user']
                print(f'Token refreshed for: {user["fullName"]} ({user["email"]})')
                print(f'Bio: {user["bio"]}')
                print(f'Message: {refresh_result["message"]}')
            else:
                print('❌ Token refresh failed:', refresh_result['errors'])
            return refresh_result['success']
            
    except Exception as e:
        print('❌ Test error:', str(e))
        return False

async def test_secure_logout():
    """Test secure logout mutation"""
    try:
        # Test secure logout mutation
        logout_mutation = '''
        mutation SecureLogout {
            secureLogout {
                success
                message
                errors
            }
        }
        '''
        
        print('Testing secure logout mutation...')
        result = await schema.execute(logout_mutation)
        
        if result.errors:
            print('❌ GraphQL Errors:', result.errors)
        else:
            print('✅ Secure logout mutation successful!')
            logout_result = result.data['secureLogout']
            if logout_result['success']:
                print(f'Logout successful: {logout_result["message"]}')
            else:
                print('❌ Logout failed:', logout_result['errors'])
            return logout_result['success']
            
    except Exception as e:
        print('❌ Test error:', str(e))
        return False

async def test_invalid_login():
    """Test secure login with invalid credentials"""
    try:
        # Test secure login with empty credentials
        invalid_login_mutation = '''
        mutation InvalidLogin {
            secureLogin(username: "", password: "") {
                success
                message
                errors
            }
        }
        '''
        
        print('Testing secure login with invalid credentials...')
        result = await schema.execute(invalid_login_mutation)
        
        if result.errors:
            print('❌ GraphQL Errors:', result.errors)
        else:
            print('✅ Invalid login test successful!')
            login_result = result.data['secureLogin']
            if not login_result['success']:
                print(f'Expected failure: {login_result["errors"]}')
                return True
            else:
                print('❌ Login should have failed but succeeded')
                return False
            
    except Exception as e:
        print('❌ Test error:', str(e))
        return False

async def main():
    """Run all tests"""
    print("🧪 Testing Secure Authentication GraphQL Operations\n")
    
    # Test secure login
    login_success = await test_secure_login()
    print()
    
    # Test session validation
    validation_success = await test_session_validation()
    print()
    
    # Test token refresh
    refresh_success = await test_token_refresh()
    print()
    
    # Test logout
    logout_success = await test_secure_logout()
    print()
    
    # Test invalid login
    invalid_login_success = await test_invalid_login()
    print()
    
    if all([login_success, validation_success, refresh_success, logout_success, invalid_login_success]):
        print("🎉 All Secure Authentication GraphQL tests passed!")
        print("\n🔒 Security Features Implemented:")
        print("  ✅ HttpOnly cookie authentication support")
        print("  ✅ Secure login with validation")
        print("  ✅ Session validation")
        print("  ✅ Automatic token refresh")
        print("  ✅ Secure logout with cleanup")
        print("  ✅ Input validation and error handling")
    else:
        print("❌ Some tests failed.")

if __name__ == "__main__":
    asyncio.run(main())