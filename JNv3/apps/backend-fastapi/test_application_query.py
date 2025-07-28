#!/usr/bin/env python3
"""
Test script for Application GraphQL queries and mutations
"""

import asyncio
from app.graphql.schema import schema

async def test_applications_query():
    """Test the applications query"""
    try:
        # Test applications query
        applications_query = '''
        query GetApplications {
            applications(limit: 3) {
                id
                userId
                jobId
                status
                appliedDate
                lastUpdated
                coverLetter
                notes
                aiSuggestions
                skillsAnalysis
                job {
                    id
                    title
                    company {
                        name
                    }
                }
            }
        }
        '''
        
        print('Testing applications query...')
        result = await schema.execute(applications_query)
        
        if result.errors:
            print('❌ GraphQL Errors:', result.errors)
        else:
            print('✅ Applications query successful!')
            applications = result.data['applications']
            print(f'Found {len(applications)} applications:')
            for app in applications:
                print(f'  - {app["status"]} for {app["job"]["title"]} at {app["job"]["company"]["name"]}')
                print(f'    Applied: {app["appliedDate"][:10]}')
                print(f'    Cover Letter: {len(app["coverLetter"] or "")} chars')
                if app["aiSuggestions"]:
                    print(f'    AI Suggestions: Available')
                print()
            return True
            
    except Exception as e:
        print('❌ Test error:', str(e))
        import traceback
        traceback.print_exc()
        return False

async def test_application_filtering():
    """Test application filtering by status"""
    try:
        # Test filtering by status
        filter_query = '''
        query GetApplicationsByStatus {
            applications(status: "interview") {
                id
                status
                job {
                    title
                }
            }
        }
        '''
        
        print('Testing application filtering by status...')
        result = await schema.execute(filter_query)
        
        if result.errors:
            print('❌ Filter query errors:', result.errors)
        else:
            print('✅ Application filtering successful!')
            applications = result.data['applications']
            print(f'Found {len(applications)} interview applications:')
            for app in applications:
                print(f'  - {app["status"]}: {app["job"]["title"]}')
            return True
            
    except Exception as e:
        print('❌ Filter test error:', str(e))
        return False

async def test_saved_jobs_query():
    """Test saved jobs query"""
    try:
        # Test saved jobs query
        saved_jobs_query = '''
        query GetSavedJobs {
            savedJobs(limit: 2) {
                id
                userId
                jobId
                savedDate
                notes
                job {
                    id
                    title
                    company {
                        name
                    }
                    locationText
                }
            }
        }
        '''
        
        print('Testing saved jobs query...')
        result = await schema.execute(saved_jobs_query)
        
        if result.errors:
            print('❌ GraphQL Errors:', result.errors)
        else:
            print('✅ Saved jobs query successful!')
            saved_jobs = result.data['savedJobs']
            print(f'Found {len(saved_jobs)} saved jobs:')
            for saved in saved_jobs:
                print(f'  - {saved["job"]["title"]} at {saved["job"]["company"]["name"]}')
                print(f'    Location: {saved["job"]["locationText"]}')
                print(f'    Saved: {saved["savedDate"][:10]}')
                print(f'    Notes: {saved["notes"]}')
                print()
            return True
            
    except Exception as e:
        print('❌ Test error:', str(e))
        return False

async def test_create_application_mutation():
    """Test create application mutation"""
    try:
        # First get a job ID to apply to
        jobs_query = '''
        query GetJobs {
            jobs(limit: 1) {
                id
                title
            }
        }
        '''
        
        jobs_result = await schema.execute(jobs_query)
        if jobs_result.errors or not jobs_result.data['jobs']:
            print('❌ Could not get job for application test')
            return False
        
        job_id = jobs_result.data['jobs'][0]['id']
        
        # Test create application mutation
        create_application_mutation = f'''
        mutation CreateApplication {{
            createApplication(input: {{
                jobId: "{job_id}"
                coverLetter: "I am very excited about this opportunity and believe my skills would be a great fit for your team."
                notes: "Applied through GraphQL test"
            }}) {{
                success
                applicationId
                application {{
                    id
                    status
                    coverLetter
                    notes
                    job {{
                        title
                    }}
                }}
                errors
            }}
        }}
        '''
        
        print('Testing create application mutation...')
        result = await schema.execute(create_application_mutation)
        
        if result.errors:
            print('❌ GraphQL Errors:', result.errors)
        else:
            print('✅ Create application mutation successful!')
            create_result = result.data['createApplication']
            if create_result['success']:
                app = create_result['application']
                print(f'Created application: {app["id"]}')
                print(f'Job: {app["job"]["title"]}')
                print(f'Status: {app["status"]}')
                print(f'Cover Letter: {len(app["coverLetter"])} chars')
            else:
                print('❌ Application creation failed:', create_result['errors'])
            return create_result['success']
            
    except Exception as e:
        print('❌ Test error:', str(e))
        return False

async def test_save_job_mutation():
    """Test save job mutation"""
    try:
        # First get a job ID to save
        jobs_query = '''
        query GetJobs {
            jobs(limit: 1) {
                id
                title
            }
        }
        '''
        
        jobs_result = await schema.execute(jobs_query)
        if jobs_result.errors or not jobs_result.data['jobs']:
            print('❌ Could not get job for save test')
            return False
        
        job_id = jobs_result.data['jobs'][0]['id']
        
        # Test save job mutation
        save_job_mutation = f'''
        mutation SaveJob {{
            saveJob(input: {{
                jobId: "{job_id}"
                notes: "Interesting position, want to research more"
            }}) {{
                success
                savedJobId
                savedJob {{
                    id
                    notes
                    job {{
                        title
                    }}
                }}
                errors
            }}
        }}
        '''
        
        print('Testing save job mutation...')
        result = await schema.execute(save_job_mutation)
        
        if result.errors:
            print('❌ GraphQL Errors:', result.errors)
        else:
            print('✅ Save job mutation successful!')
            save_result = result.data['saveJob']
            if save_result['success']:
                saved = save_result['savedJob']
                print(f'Saved job: {saved["id"]}')
                print(f'Job: {saved["job"]["title"]}')
                print(f'Notes: {saved["notes"]}')
            else:
                print('❌ Job save failed:', save_result['errors'])
            return save_result['success']
            
    except Exception as e:
        print('❌ Test error:', str(e))
        return False

async def main():
    """Run all tests"""
    print("🧪 Testing Application GraphQL Queries and Mutations\n")
    
    # Test queries
    applications_success = await test_applications_query()
    print()
    
    filter_success = await test_application_filtering()
    print()
    
    saved_jobs_success = await test_saved_jobs_query()
    print()
    
    # Test mutations
    create_app_success = await test_create_application_mutation()
    print()
    
    save_job_success = await test_save_job_mutation()
    print()
    
    if all([applications_success, filter_success, saved_jobs_success, create_app_success, save_job_success]):
        print("🎉 All Application GraphQL tests passed!")
    else:
        print("❌ Some tests failed.")

if __name__ == "__main__":
    asyncio.run(main())