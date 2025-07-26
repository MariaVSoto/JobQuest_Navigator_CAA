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
    SecureAuthResponse, SessionValidationResponse
)

# Import queries (we'll implement these in the existing query modules)
# from .queries import UserQuery, JobQuery

# Import mutations (we'll implement these in the existing mutation modules)  
# from .mutations import UserMutation, JobMutation


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


@strawberry.type
class Mutation:
    """
    Root Mutation type - modular implementation
    """
    
    @strawberry.field
    async def test_mutation(self, message: str) -> str:
        """Test mutation for schema validation"""
        return f"Echo: {message}"


# Create the schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)