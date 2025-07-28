#!/usr/bin/env python3
"""
Test script for User GraphQL queries and mutations
"""

import asyncio
from app.graphql.schema import schema

async def test_me_query():
    """Test the me query"""
    try:
        # Test me query
        me_query = '''
        query GetMe {
            me {
                id
                email
                username
                fullName
                bio
                currentJobTitle
                yearsOfExperience
                industry
                careerLevel
                jobSearchStatus
                preferredWorkType
            }
        }
        '''
        
        print('Testing me query...')
        result = await schema.execute(me_query)
        
        if result.errors:
            print('❌ GraphQL Errors:', result.errors)
        else:
            print('✅ Me query successful!')
            user = result.data['me']
            print(f'User: {user["fullName"]} ({user["email"]})')
            print(f'Job Title: {user["currentJobTitle"]}')
            print(f'Experience: {user["yearsOfExperience"]} years in {user["industry"]}')
            print(f'Career Level: {user["careerLevel"]}')
            print(f'Job Search Status: {user["jobSearchStatus"]}')
            print(f'Preferred Work Type: {user["preferredWorkType"]}')
            return True
            
    except Exception as e:
        print('❌ Test error:', str(e))
        import traceback
        traceback.print_exc()
        return False

async def test_user_query():
    """Test user query by ID"""
    try:
        # Test user query
        user_query = '''
        query GetUser {
            user(id: "test-user-123") {
                id
                email
                username
                fullName
                currentJobTitle
                industry
                careerLevel
            }
        }
        '''
        
        print('Testing user query by ID...')
        result = await schema.execute(user_query)
        
        if result.errors:
            print('❌ GraphQL Errors:', result.errors)
        else:
            print('✅ User query successful!')
            user = result.data['user']
            print(f'User: {user["fullName"]} ({user["email"]})')
            print(f'Job Title: {user["currentJobTitle"]}')
            print(f'Industry: {user["industry"]}')
            return True
            
    except Exception as e:
        print('❌ Test error:', str(e))
        return False

async def test_register_mutation():
    """Test user registration mutation"""
    try:
        # Test registration mutation
        register_mutation = '''
        mutation RegisterUser {
            registerUser(
                email: "newuser@example.com"
                username: "newuser123"
                password: "securepassword"
                firstName: "John"
                lastName: "Doe"
            ) {
                success
                user {
                    id
                    email
                    username
                    fullName
                }
                errors
            }
        }
        '''
        
        print('Testing user registration mutation...')
        result = await schema.execute(register_mutation)
        
        if result.errors:
            print('❌ GraphQL Errors:', result.errors)
        else:
            print('✅ Registration mutation successful!')
            registration = result.data['registerUser']
            if registration['success']:
                user = registration['user']
                print(f'Registered user: {user["fullName"]} ({user["email"]})')
                print(f'Username: {user["username"]}')
            else:
                print('❌ Registration failed:', registration['errors'])
            return registration['success']
            
    except Exception as e:
        print('❌ Test error:', str(e))
        return False

async def test_update_profile_mutation():
    """Test user profile update mutation"""
    try:
        # Test profile update mutation
        update_mutation = '''
        mutation UpdateProfile {
            updateUserProfile(input: {
                fullName: "John Smith"
                bio: "Senior software engineer with 8+ years of experience"
                currentJobTitle: "Senior Software Engineer"
                yearsOfExperience: 8
                industry: "Technology"
                careerLevel: "senior"
                jobSearchStatus: "passively_looking"
                preferredWorkType: "hybrid"
            }) {
                success
                user {
                    id
                    fullName
                    bio
                    currentJobTitle
                    yearsOfExperience
                    industry
                    careerLevel
                    jobSearchStatus
                    preferredWorkType
                }
                errors
            }
        }
        '''
        
        print('Testing profile update mutation...')
        result = await schema.execute(update_mutation)
        
        if result.errors:
            print('❌ GraphQL Errors:', result.errors)
        else:
            print('✅ Profile update mutation successful!')
            update_result = result.data['updateUserProfile']
            if update_result['success']:
                user = update_result['user']
                print(f'Updated user: {user["fullName"]}')
                print(f'Bio: {user["bio"]}')
                print(f'Job Title: {user["currentJobTitle"]}')
                print(f'Experience: {user["yearsOfExperience"]} years')
                print(f'Career Level: {user["careerLevel"]}')
                print(f'Job Search Status: {user["jobSearchStatus"]}')
            else:
                print('❌ Profile update failed:', update_result['errors'])
            return update_result['success']
            
    except Exception as e:
        print('❌ Test error:', str(e))
        return False

async def test_auth_mutations():
    """Test authentication mutations"""
    try:
        # Test login mutation
        login_mutation = '''
        mutation Login {
            tokenAuth(username: "testuser", password: "testpass") {
                token
            }
        }
        '''
        
        print('Testing login mutation...')
        result = await schema.execute(login_mutation)
        
        if result.errors:
            print('❌ GraphQL Errors:', result.errors)
        else:
            print('✅ Login mutation successful!')
            auth_result = result.data['tokenAuth']
            print(f'Token received: {auth_result["token"][:20]}...')
            
            # Test token verification
            verify_mutation = '''
            mutation VerifyToken {
                verifyToken(token: "mock-jwt-token-for-demo")
            }
            '''
            
            print('Testing token verification...')
            verify_result = await schema.execute(verify_mutation)
            
            if verify_result.errors:
                print('❌ Token verification errors:', verify_result.errors)
            else:
                is_valid = verify_result.data['verifyToken']
                print(f'✅ Token verification: {"valid" if is_valid else "invalid"}')
            
            return True
            
    except Exception as e:
        print('❌ Test error:', str(e))
        return False

async def main():
    """Run all tests"""
    print("🧪 Testing User GraphQL Queries and Mutations\n")
    
    # Test queries
    me_success = await test_me_query()
    print()
    
    user_success = await test_user_query()
    print()
    
    # Test mutations
    register_success = await test_register_mutation()
    print()
    
    update_success = await test_update_profile_mutation()
    print()
    
    auth_success = await test_auth_mutations()
    print()
    
    if all([me_success, user_success, register_success, update_success, auth_success]):
        print("🎉 All User GraphQL tests passed!")
    else:
        print("❌ Some tests failed.")

if __name__ == "__main__":
    asyncio.run(main())