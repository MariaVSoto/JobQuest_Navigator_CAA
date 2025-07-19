#!/usr/bin/env python3
"""
Test script for Jobs GraphQL queries
"""

import asyncio
from app.graphql.schema import schema

async def test_jobs_query():
    """Test the jobs query"""
    try:
        # Test jobs query
        jobs_query = '''
        query GetJobs {
            jobs(limit: 2) {
                id
                title
                description
                locationText
                salaryMin
                salaryMax
                jobType
                experienceLevel
                remoteType
                company {
                    id
                    name
                    industry
                }
                isSaved
                isApplied
            }
        }
        '''
        
        print('Testing jobs query...')
        result = await schema.execute(jobs_query)
        
        if result.errors:
            print('❌ GraphQL Errors:', result.errors)
        else:
            print('✅ Jobs query successful!')
            jobs = result.data['jobs']
            print(f'Found {len(jobs)} jobs:')
            for job in jobs:
                print(f'  - {job["title"]} at {job["company"]["name"]} ({job["locationText"]})')
                print(f'    Salary: ${job["salaryMin"]:,.0f} - ${job["salaryMax"]:,.0f}')
                print(f'    Type: {job["jobType"]}, Experience: {job["experienceLevel"]}, Remote: {job["remoteType"]}')
                print(f'    Saved: {job["isSaved"]}, Applied: {job["isApplied"]}')
                print()
            return True
            
    except Exception as e:
        print('❌ Test error:', str(e))
        import traceback
        traceback.print_exc()
        return False

async def test_job_filtering():
    """Test job filtering capabilities"""
    try:
        # Test filtering by location
        filter_query = '''
        query GetJobsByLocation {
            jobs(location: "remote") {
                id
                title
                locationText
                remoteType
            }
        }
        '''
        
        print('Testing job filtering by location...')
        result = await schema.execute(filter_query)
        
        if result.errors:
            print('❌ Filter query errors:', result.errors)
        else:
            print('✅ Job filtering successful!')
            jobs = result.data['jobs']
            print(f'Found {len(jobs)} remote jobs:')
            for job in jobs:
                print(f'  - {job["title"]} ({job["locationText"]}) - {job["remoteType"]}')
            return True
            
    except Exception as e:
        print('❌ Filter test error:', str(e))
        return False

async def main():
    """Run all tests"""
    print("🧪 Testing Jobs GraphQL Queries\n")
    
    # Test basic jobs query
    basic_success = await test_jobs_query()
    print()
    
    # Test filtering
    filter_success = await test_job_filtering()
    print()
    
    if basic_success and filter_success:
        print("🎉 All Jobs GraphQL tests passed!")
    else:
        print("❌ Some tests failed.")

if __name__ == "__main__":
    asyncio.run(main())