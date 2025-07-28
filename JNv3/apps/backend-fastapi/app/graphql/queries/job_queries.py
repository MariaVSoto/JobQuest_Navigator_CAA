"""
Job related GraphQL queries
Simplified queries for user-input based job management
"""

import strawberry
from typing import List, Optional
from datetime import datetime

from app.graphql.types.job_types import JobType, JobApplicationType, CompanyType


@strawberry.type
class JobQuery:
    """Job related queries"""
    
    @strawberry.field
    async def jobs(self, limit: Optional[int] = 10) -> List[JobType]:
        """
        Get jobs list - simplified for user input model
        Returns demo data during initial development
        """
        # TODO: Replace with actual database queries
        demo_company = CompanyType(
            id="1",
            name="Demo Tech Company",
            description="A technology company for demonstration",
            website="https://demo-tech.com",
            industry="Technology",
            company_size="medium",
            ai_research_status="NONE"
        )
        
        return [
            JobType(
                id="1",
                title="Senior Python Developer",
                company=demo_company,
                description="Exciting Python development role with FastAPI and GraphQL",
                requirements="5+ years Python experience, FastAPI knowledge preferred",
                salary_min=90000.0,
                salary_max=130000.0,
                salary_currency="USD",
                job_type="full_time",
                experience_level="senior",
                remote_type="remote",
                user_input=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
    
    @strawberry.field
    async def job_by_id(self, id: str) -> Optional[JobType]:
        """Get job by ID"""
        # TODO: Implement database query
        return None
    
    @strawberry.field
    async def my_applications(self, info) -> List[JobApplicationType]:
        """Get current user's job applications"""
        # TODO: Implement with authentication and database queries
        return []
    
    @strawberry.field
    async def companies(self, search: Optional[str] = None) -> List[CompanyType]:
        """Search companies"""
        # TODO: Implement company search
        return []