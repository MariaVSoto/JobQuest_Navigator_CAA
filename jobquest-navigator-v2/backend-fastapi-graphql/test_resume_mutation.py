#!/usr/bin/env python3
"""
Test script for resume GraphQL mutations
"""

import asyncio
from app.graphql.schema import schema

async def test_create_resume():
    """Test the create resume mutation"""
    try:
        # Test create resume mutation
        create_resume_query = """
        mutation CreateResume($input: CreateResumeInput!) {
            createResume(input: $input) {
                success
                resumeId
                message
                errors
            }
        }
        """
        
        variables = {
            'input': {
                'title': 'Kevin Software Developer Resume',
                'personalInfo': {
                    'fullName': 'Kevin Wang',
                    'email': 'kevin@example.com',
                    'phone': '+1-555-0123',
                    'location': 'Los Angeles, CA'
                },
                'summary': 'Experienced software developer with 5+ years in web development.',
                'experience': [
                    {
                        'company': 'Tech Corp',
                        'position': 'Senior Developer',
                        'startDate': '2020-01-01',
                        'endDate': '2024-01-01',
                        'current': False,
                        'description': 'Led development of web applications using React and Node.js'
                    }
                ],
                'skills': ['JavaScript', 'React', 'Node.js', 'Python'],
                'targetRole': 'Full Stack Developer'
            }
        }
        
        print("Testing create resume mutation...")
        result = await schema.execute(create_resume_query, variable_values=variables)
        
        if result.errors:
            print('❌ GraphQL Errors:', result.errors)
            return False
        else:
            print('✅ Resume creation test successful!')
            print('Response:', result.data['createResume'])
            return True
            
    except Exception as e:
        print('❌ Test error:', str(e))
        import traceback
        traceback.print_exc()
        return False

async def test_simple_mutation():
    """Test a simple mutation first"""
    try:
        simple_query = """
        mutation TestMutation {
            testMutation(message: "Hello GraphQL!")
        }
        """
        
        print("Testing simple mutation...")
        result = await schema.execute(simple_query)
        
        if result.errors:
            print('❌ Simple mutation errors:', result.errors)
            return False
        else:
            print('✅ Simple mutation successful!')
            print('Response:', result.data)
            return True
            
    except Exception as e:
        print('❌ Simple test error:', str(e))
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🧪 Testing GraphQL Resume Mutations\n")
    
    # Test simple mutation first
    simple_success = await test_simple_mutation()
    print()
    
    if simple_success:
        # Test complex resume mutation
        resume_success = await test_create_resume()
        print()
        
        if resume_success:
            print("🎉 All tests passed! Resume GraphQL mutation is working.")
        else:
            print("❌ Resume mutation test failed.")
    else:
        print("❌ Basic GraphQL functionality not working.")

if __name__ == "__main__":
    asyncio.run(main())