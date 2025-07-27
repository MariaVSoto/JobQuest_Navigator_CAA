"""
Main GraphQL schema - modular version
Strawberry GraphQL implementation with clean module separation
"""

import strawberry
from typing import List, Optional
from datetime import datetime

# Import types from modular structure
from .types import (
    User, Job, Company, JobApplication, SavedJob,
    SecureAuthResponse, SessionValidationResponse,
    DashboardStats, DashboardData, ApplicationStatusStats, DashboardFilters,
    UserRegistrationInput, AuthResponse
)

# Import queries and dashboard functionality
try:
    from .queries.dashboard_queries import DashboardQuery
except ImportError as e:
    print(f"Warning: Could not import DashboardQuery: {e}")
    # Create a dummy DashboardQuery class
    class DashboardQuery:
        pass

# Import mutations
from .mutations.auth_mutations import AuthMutation
from .mutations.user_mutations import UserMutation


@strawberry.type
class Query:
    """
    Root Query type - modular implementation
    """
    
    @strawberry.field
    async def hello(self) -> str:
        return "Hello from JobQuest Navigator v2!"
    
    @strawberry.field
    async def migration_status(self) -> str:
        """Check which features are using FastAPI vs Django"""
        return "Migration in progress - modular schema loaded"
    
    @strawberry.field
    async def me(self) -> Optional[User]:
        """Get current user - demo implementation"""
        return User(
            id="demo-user-id",
            email="test@example.com",
            username="testuser",
            fullName="Test User",
            bio="Demo user for testing",
            currentJobTitle="Software Developer",
            yearsOfExperience=5,
            industry="Technology",
            careerLevel="mid",
            jobSearchStatus="actively_looking",
            preferredWorkType="hybrid"
        )
    
    @strawberry.field
    async def jobs(
        self, 
        limit: Optional[int] = 20,
        offset: Optional[int] = 0,
        search: Optional[str] = None,
        location: Optional[str] = None,
        jobType: Optional[str] = None,
        experienceLevel: Optional[str] = None,
        remoteType: Optional[str] = None,
        userCreated: Optional[bool] = None
    ) -> List[Job]:
        """Get job listings with filtering - simplified demo version"""
        # For now, return demo data - this will be moved to job service
        demo_company = Company(
            id="demo-company-1",
            name="TechCorp Inc",
            description="Leading technology company",
            website="https://techcorp.com",
            industry="Technology",
            companySize="500-1000"
        )
        
        demo_jobs = [
            Job(
                id="demo-job-1",
                title="Senior Software Engineer",
                description="We are looking for a senior software engineer...",
                requirements="5+ years experience, Python, React",
                benefits="Health insurance, 401k, flexible hours",
                locationText="San Francisco, CA",
                salaryMin=120000.0,
                salaryMax=180000.0,
                salaryCurrency="USD",
                salaryPeriod="yearly",
                jobType="full_time",
                contractType="permanent",
                experienceLevel="senior",
                remoteType="hybrid",
                userInput=True,
                source="user_input",
                postedDate=datetime.now(),
                company=demo_company,
                isSaved=False,
                isApplied=False
            ),
            Job(
                id="demo-job-2", 
                title="Frontend Developer",
                description="Join our frontend team...",
                requirements="3+ years React, TypeScript",
                benefits="Competitive salary, stock options",
                locationText="Remote",
                salaryMin=90000.0,
                salaryMax=130000.0,
                salaryCurrency="USD",
                salaryPeriod="yearly",
                jobType="full_time",
                contractType="permanent",
                experienceLevel="mid",
                remoteType="remote",
                userInput=True,
                source="user_input",
                postedDate=datetime.now(),
                company=demo_company,
                isSaved=True,
                isApplied=False
            )
        ]
        
        # Apply basic filtering
        filtered_jobs = demo_jobs
        if search:
            filtered_jobs = [j for j in filtered_jobs if search.lower() in j.title.lower()]
        if location:
            filtered_jobs = [j for j in filtered_jobs if location.lower() in j.locationText.lower()]
        if jobType:
            filtered_jobs = [j for j in filtered_jobs if j.jobType == jobType]
        if remoteType:
            filtered_jobs = [j for j in filtered_jobs if j.remoteType == remoteType]
            
        # Apply pagination
        start = offset or 0
        end = start + (limit or 20)
        return filtered_jobs[start:end]
    
    # Dashboard queries
    @strawberry.field
    async def dashboard_stats(
        self, 
        user_id: str,
        date_range_days: Optional[int] = 30
    ) -> DashboardStats:
        """Get dashboard statistics for a user"""
        dashboard_query = DashboardQuery()
        return await dashboard_query.dashboard_stats(user_id, date_range_days)
    
    @strawberry.field
    async def dashboard_data(
        self,
        user_id: str,
        filters: Optional[DashboardFilters] = None
    ) -> DashboardData:
        """Get complete dashboard data"""
        dashboard_query = DashboardQuery()
        return await dashboard_query.dashboard_data(user_id, filters)
    
    @strawberry.field 
    async def application_status_stats(
        self,
        user_id: str
    ) -> ApplicationStatusStats:
        """Get application statistics grouped by status"""
        dashboard_query = DashboardQuery()
        return await dashboard_query.application_status_stats(user_id)


@strawberry.type
class Mutation:
    """
    Root Mutation type - modular implementation
    """
    
    @strawberry.field
    async def test_mutation(self, message: str) -> str:
        """Test mutation for schema validation"""
        return f"Echo: {message}"
    
    # Authentication mutations
    @strawberry.field
    async def login(self, username: str, password: str) -> AuthResponse:
        """User login"""
        auth_mutation = AuthMutation()
        return await auth_mutation.login(username, password)
    
    @strawberry.field
    async def register(self, input: UserRegistrationInput) -> AuthResponse:
        """User registration using AuthMutation"""
        auth_mutation = AuthMutation()
        return await auth_mutation.register(input)
    
    @strawberry.field
    async def registerUser(
        self, 
        email: str, 
        username: str, 
        password: str, 
        firstName: Optional[str] = None, 
        lastName: Optional[str] = None
    ) -> AuthResponse:
        """User registration - matches frontend expectations"""
        try:
            # For development, return success with mock user creation
            # TODO: Implement actual user creation in database
            
            # Use already imported types
            
            # Mock user creation
            mock_user = User(
                id=f"user-{email.replace('@', '-').replace('.', '-')}",
                email=email,
                username=username,
                fullName=f"{firstName or ''} {lastName or ''}".strip() or username,
                bio="New user",
                currentJobTitle="",
                yearsOfExperience=0,
                industry="",
                careerLevel="entry",
                jobSearchStatus="not_looking",
                preferredWorkType="office"
            )
            
            return AuthResponse(
                success=True,
                user=mock_user,
                token="mock-registration-token",
                message="Registration successful",
                errors=None
            )
            
        except Exception as e:
            print(f"Registration error: {e}")
            return AuthResponse(
                success=False,
                user=None,
                token=None,
                message="Registration failed",
                errors=[str(e)]
            )


# Create the schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)