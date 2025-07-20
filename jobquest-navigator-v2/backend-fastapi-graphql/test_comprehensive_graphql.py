#!/usr/bin/env python3
"""
Comprehensive GraphQL Testing Suite for JobQuest Navigator v2
Tests all GraphQL queries, mutations, and functionality
"""

import asyncio
import json
from app.graphql.schema import schema

class GraphQLTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_results = []

    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
            
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })

    async def test_basic_queries(self):
        """Test basic GraphQL queries"""
        print("\n🔍 Testing Basic GraphQL Queries")
        
        # Test hello query
        hello_query = "{ hello }"
        try:
            result = await schema.execute(hello_query)
            if result.errors:
                self.log_test("Hello Query", False, f"Errors: {result.errors}")
            else:
                expected = "Hello from JobQuest Navigator v2!"
                actual = result.data.get('hello')
                self.log_test("Hello Query", actual == expected, f"Response: {actual}")
        except Exception as e:
            self.log_test("Hello Query", False, f"Exception: {e}")

        # Test migration status query
        migration_query = "{ migrationStatus }"
        try:
            result = await schema.execute(migration_query)
            if result.errors:
                self.log_test("Migration Status Query", False, f"Errors: {result.errors}")
            else:
                response = result.data.get('migrationStatus')
                self.log_test("Migration Status Query", response is not None, f"Response: {response}")
        except Exception as e:
            self.log_test("Migration Status Query", False, f"Exception: {e}")

    async def test_user_queries(self):
        """Test user-related GraphQL queries"""
        print("\n👤 Testing User GraphQL Queries")
        
        # Test me query
        me_query = """
        {
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
        """
        try:
            result = await schema.execute(me_query)
            if result.errors:
                self.log_test("Me Query", False, f"Errors: {result.errors}")
            else:
                user = result.data.get('me')
                self.log_test("Me Query", user is not None and user.get('id'), 
                             f"User: {user.get('fullName')} ({user.get('email')})")
        except Exception as e:
            self.log_test("Me Query", False, f"Exception: {e}")

        # Test user by ID query
        user_query = """
        {
            user(id: "test-user-id") {
                id
                email
                username
                fullName
                currentJobTitle
                industry
            }
        }
        """
        try:
            result = await schema.execute(user_query)
            if result.errors:
                self.log_test("User by ID Query", False, f"Errors: {result.errors}")
            else:
                user = result.data.get('user')
                self.log_test("User by ID Query", user is not None and user.get('id'), 
                             f"User: {user.get('fullName') if user else 'None'}")
        except Exception as e:
            self.log_test("User by ID Query", False, f"Exception: {e}")

    async def test_job_queries(self):
        """Test job-related GraphQL queries"""
        print("\n💼 Testing Job GraphQL Queries")
        
        # Test jobs query
        jobs_query = """
        {
            jobs(limit: 5) {
                id
                title
                description
                requirements
                benefits
                locationText
                salaryMin
                salaryMax
                salaryCurrency
                jobType
                experienceLevel
                remoteType
                source
                postedDate
                company {
                    id
                    name
                    industry
                }
                isSaved
                isApplied
            }
        }
        """
        try:
            result = await schema.execute(jobs_query)
            if result.errors:
                self.log_test("Jobs Query", False, f"Errors: {result.errors}")
            else:
                jobs = result.data.get('jobs', [])
                self.log_test("Jobs Query", len(jobs) > 0, 
                             f"Retrieved {len(jobs)} jobs")
                if jobs:
                    first_job = jobs[0]
                    self.log_test("Job Data Structure", 
                                 all(key in first_job for key in ['id', 'title', 'company']),
                                 f"First job: {first_job.get('title')}")
        except Exception as e:
            self.log_test("Jobs Query", False, f"Exception: {e}")

        # Test job with filters
        filtered_jobs_query = """
        {
            jobs(limit: 3, search: "developer", experienceLevel: "senior") {
                id
                title
                experienceLevel
            }
        }
        """
        try:
            result = await schema.execute(filtered_jobs_query)
            if result.errors:
                self.log_test("Filtered Jobs Query", False, f"Errors: {result.errors}")
            else:
                jobs = result.data.get('jobs', [])
                self.log_test("Filtered Jobs Query", isinstance(jobs, list), 
                             f"Retrieved {len(jobs)} filtered jobs")
        except Exception as e:
            self.log_test("Filtered Jobs Query", False, f"Exception: {e}")

        # Test single job query
        job_query = """
        {
            job(id: "test-job-id") {
                id
                title
                company {
                    name
                }
            }
        }
        """
        try:
            result = await schema.execute(job_query)
            if result.errors:
                self.log_test("Single Job Query", False, f"Errors: {result.errors}")
            else:
                job = result.data.get('job')
                self.log_test("Single Job Query", job is not None, 
                             f"Job: {job.get('title') if job else 'None'}")
        except Exception as e:
            self.log_test("Single Job Query", False, f"Exception: {e}")

    async def test_application_queries(self):
        """Test application-related GraphQL queries"""
        print("\n📋 Testing Application GraphQL Queries")
        
        # Test applications query
        applications_query = """
        {
            applications(limit: 5) {
                id
                userId
                jobId
                status
                appliedDate
                lastUpdated
                coverLetter
                notes
                job {
                    id
                    title
                }
            }
        }
        """
        try:
            result = await schema.execute(applications_query)
            if result.errors:
                self.log_test("Applications Query", False, f"Errors: {result.errors}")
            else:
                applications = result.data.get('applications', [])
                self.log_test("Applications Query", len(applications) >= 0, 
                             f"Retrieved {len(applications)} applications")
                if applications:
                    first_app = applications[0]
                    self.log_test("Application Data Structure", 
                                 all(key in first_app for key in ['id', 'userId', 'jobId', 'status']),
                                 f"First application status: {first_app.get('status')}")
        except Exception as e:
            self.log_test("Applications Query", False, f"Exception: {e}")

        # Test single application query
        application_query = """
        {
            application(id: "test-app-id") {
                id
                status
                job {
                    title
                }
            }
        }
        """
        try:
            result = await schema.execute(application_query)
            if result.errors:
                self.log_test("Single Application Query", False, f"Errors: {result.errors}")
            else:
                application = result.data.get('application')
                self.log_test("Single Application Query", application is not None, 
                             f"Application status: {application.get('status') if application else 'None'}")
        except Exception as e:
            self.log_test("Single Application Query", False, f"Exception: {e}")

        # Test saved jobs query
        saved_jobs_query = """
        {
            savedJobs(limit: 5) {
                id
                userId
                jobId
                savedDate
                notes
                job {
                    title
                }
            }
        }
        """
        try:
            result = await schema.execute(saved_jobs_query)
            if result.errors:
                self.log_test("Saved Jobs Query", False, f"Errors: {result.errors}")
            else:
                saved_jobs = result.data.get('savedJobs', [])
                self.log_test("Saved Jobs Query", len(saved_jobs) >= 0, 
                             f"Retrieved {len(saved_jobs)} saved jobs")
        except Exception as e:
            self.log_test("Saved Jobs Query", False, f"Exception: {e}")

    async def test_mutations(self):
        """Test GraphQL mutations"""
        print("\n🔧 Testing GraphQL Mutations")
        
        # Test user registration
        register_mutation = '''
        mutation {
            registerUser(
                email: "test@example.com"
                username: "testuser"
                password: "testpassword"
                firstName: "Test"
                lastName: "User"
            ) {
                success
                errors
                user {
                    id
                    email
                    username
                    fullName
                }
            }
        }
        '''
        try:
            result = await schema.execute(register_mutation)
            if result.errors:
                self.log_test("User Registration Mutation", False, f"Errors: {result.errors}")
            else:
                registration = result.data.get('registerUser')
                success = registration.get('success', False)
                self.log_test("User Registration Mutation", success, 
                             f"Registration success: {success}")
        except Exception as e:
            self.log_test("User Registration Mutation", False, f"Exception: {e}")

        # Test token authentication
        auth_mutation = '''
        mutation {
            tokenAuth(username: "testuser", password: "testpassword") {
                token
            }
        }
        '''
        try:
            result = await schema.execute(auth_mutation)
            if result.errors:
                self.log_test("Token Auth Mutation", False, f"Errors: {result.errors}")
            else:
                auth = result.data.get('tokenAuth')
                token = auth.get('token') if auth else None
                self.log_test("Token Auth Mutation", token is not None, 
                             f"Token received: {bool(token)}")
        except Exception as e:
            self.log_test("Token Auth Mutation", False, f"Exception: {e}")

        # Test job creation
        create_job_mutation = '''
        mutation {
            createJob(input: {
                title: "Test Software Engineer"
                companyName: "Test Company"
                locationText: "Los Angeles, CA"
                description: "Test job description"
                salaryMin: 80000
                salaryMax: 120000
                jobType: "full_time"
                experienceLevel: "mid"
            }) {
                success
                jobId
                errors
            }
        }
        '''
        try:
            result = await schema.execute(create_job_mutation)
            if result.errors:
                self.log_test("Create Job Mutation", False, f"Errors: {result.errors}")
            else:
                job_creation = result.data.get('createJob')
                success = job_creation.get('success', False)
                self.log_test("Create Job Mutation", success, 
                             f"Job creation success: {success}")
        except Exception as e:
            self.log_test("Create Job Mutation", False, f"Exception: {e}")

        # Test resume creation
        create_resume_mutation = '''
        mutation {
            createResume(input: {
                title: "Test Resume"
                personalInfo: {
                    fullName: "Test User"
                    email: "test@example.com"
                    phone: "123-456-7890"
                    location: "Los Angeles, CA"
                }
                summary: "Test summary"
                targetRole: "Software Engineer"
            }) {
                success
                resumeId
                message
                errors
            }
        }
        '''
        try:
            result = await schema.execute(create_resume_mutation)
            if result.errors:
                self.log_test("Create Resume Mutation", False, f"Errors: {result.errors}")
            else:
                resume_creation = result.data.get('createResume')
                success = resume_creation.get('success', False)
                self.log_test("Create Resume Mutation", success, 
                             f"Resume creation success: {success}")
        except Exception as e:
            self.log_test("Create Resume Mutation", False, f"Exception: {e}")

    async def test_schema_introspection(self):
        """Test GraphQL schema introspection"""
        print("\n🔍 Testing GraphQL Schema Introspection")
        
        introspection_query = """
        {
            __schema {
                types {
                    name
                    kind
                }
                queryType {
                    name
                }
                mutationType {
                    name
                }
            }
        }
        """
        try:
            result = await schema.execute(introspection_query)
            if result.errors:
                self.log_test("Schema Introspection", False, f"Errors: {result.errors}")
            else:
                schema_info = result.data.get('__schema')
                types = schema_info.get('types', [])
                query_type = schema_info.get('queryType', {}).get('name')
                mutation_type = schema_info.get('mutationType', {}).get('name')
                
                self.log_test("Schema Introspection", len(types) > 0, 
                             f"Found {len(types)} types")
                self.log_test("Query Type", query_type == "Query", 
                             f"Query type: {query_type}")
                self.log_test("Mutation Type", mutation_type == "Mutation", 
                             f"Mutation type: {mutation_type}")
        except Exception as e:
            self.log_test("Schema Introspection", False, f"Exception: {e}")

    async def run_all_tests(self):
        """Run all GraphQL tests"""
        print("🧪 Starting Comprehensive GraphQL Test Suite")
        print("=" * 60)
        
        await self.test_basic_queries()
        await self.test_user_queries()
        await self.test_job_queries()
        await self.test_application_queries()
        await self.test_mutations()
        await self.test_schema_introspection()
        
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        if self.failed > 0:
            print("\n⚠️  Failed Tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['test']}: {result['details']}")
        
        return self.passed, self.failed

async def main():
    """Main test runner"""
    tester = GraphQLTester()
    passed, failed = await tester.run_all_tests()
    
    if failed == 0:
        print("\n🎉 All GraphQL tests passed! Schema is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)