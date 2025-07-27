"""
User-created job mutations for FastAPI GraphQL
Allows users to input their own job positions
"""

import strawberry
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from datetime import datetime
import uuid

from app.core.database import get_db
from app.graphql.types import Job as JobType, Company as CompanyType, StandardResponse
from app.models import Job, Company, User
from app.graphql.auth import get_current_user


@strawberry.input
class CreateUserJobInput:
    """Input for creating a user job position."""
    title: str
    company_name: str
    location_text: str
    description: str
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "USD"
    salary_period: str = "yearly"
    job_type: str = "full_time"
    contract_type: str = "permanent"
    experience_level: Optional[str] = None
    remote_type: str = "on_site"


@strawberry.input
class UpdateUserJobInput:
    """Input for updating a user job position."""
    title: Optional[str] = None
    company_name: Optional[str] = None
    location_text: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    salary_period: Optional[str] = None
    job_type: Optional[str] = None
    contract_type: Optional[str] = None
    experience_level: Optional[str] = None
    remote_type: Optional[str] = None


@strawberry.type
class UserJobResponse:
    """Response for user job mutations."""
    job: Optional[JobType] = None
    success: bool
    errors: List[str]


@strawberry.type
class UserJobMutation:
    """User job-related mutations."""

    @strawberry.mutation
    async def create_user_job(
        self,
        info,
        input: CreateUserJobInput,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> UserJobResponse:
        """Create a new user-input job position."""
        try:
            # Find or create company
            company_result = await db.execute(
                select(Company).where(Company.name.ilike(f"%{input.company_name}%"))
            )
            company = company_result.scalar_one_or_none()
            
            if not company:
                # Create new company
                company = Company(
                    name=input.company_name,
                    slug=input.company_name.lower().replace(' ', '-').replace('/', '-'),
                    description=f"Company profile for {input.company_name}",
                )
                db.add(company)
                await db.flush()  # Get company ID
            
            # Create job
            job = Job(
                title=input.title,
                company_id=company.id,
                category_id=None,  # Optional for user input
                description=input.description,
                requirements=input.requirements,
                benefits=input.benefits,
                location_text=input.location_text,
                salary_min=input.salary_min,
                salary_max=input.salary_max,
                salary_currency=input.salary_currency,
                salary_period=input.salary_period,
                job_type=input.job_type,
                contract_type=input.contract_type,
                experience_level=input.experience_level,
                remote_type=input.remote_type,
                user_input=True,  # Mark as user input
                source="user_input",
                posted_date=datetime.utcnow(),
            )
            
            db.add(job)
            await db.commit()
            await db.refresh(job)
            await db.refresh(company)
            
            # Convert to GraphQL type
            job_type = JobType(
                id=str(job.id),
                title=job.title,
                company_id=str(job.company_id),
                category_id=str(job.category_id) if job.category_id else None,
                company=CompanyType(
                    id=str(company.id),
                    name=company.name,
                    slug=company.slug,
                    description=company.description,
                    website=company.website,
                    logo_url=company.logo_url,
                    industry=company.industry,
                    company_size=company.company_size,
                    founded_year=company.founded_year,
                    email=company.email,
                    phone=company.phone,
                    linkedin_url=company.linkedin_url,
                    twitter_handle=company.twitter_handle,
                    glassdoor_id=company.glassdoor_id,
                    glassdoor_rating=company.glassdoor_rating,
                    glassdoor_review_count=company.glassdoor_review_count,
                    ai_research_data=company.ai_research_data,
                    ai_research_model=company.ai_research_model,
                    ai_research_status=company.ai_research_status,
                    ai_research_generated_at=company.ai_research_generated_at,
                    created_at=company.created_at,
                ),
                category=None,
                description=job.description,
                requirements=job.requirements,
                benefits=job.benefits,
                location_text=job.location_text,
                salary_min=job.salary_min,
                salary_max=job.salary_max,
                salary_currency=job.salary_currency,
                salary_period=job.salary_period,
                job_type=job.job_type,
                contract_type=job.contract_type,
                experience_level=job.experience_level,
                remote_type=job.remote_type,
                user_input=job.user_input,
                external_id=job.external_id,
                external_url=job.external_url,
                source=job.source,
                posted_date=job.posted_date,
                expires_date=job.expires_date,
                created_at=job.created_at,
                required_skills=[],  # Can be added later
                is_saved=False,
                is_applied=False,
            )
            
            return UserJobResponse(
                job=job_type,
                success=True,
                errors=[]
            )
            
        except Exception as e:
            await db.rollback()
            return UserJobResponse(
                success=False,
                errors=[f"Failed to create job: {str(e)}"]
            )

    @strawberry.mutation
    async def update_user_job(
        self,
        info,
        job_id: strawberry.ID,
        input: UpdateUserJobInput,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> UserJobResponse:
        """Update a user-created job position."""
        try:
            # Find job and verify it's user input
            job_result = await db.execute(
                select(Job).where(
                    Job.id == job_id,
                    Job.user_input == True,
                    Job.is_active == True
                )
            )
            job = job_result.scalar_one_or_none()
            
            if not job:
                return UserJobResponse(
                    success=False,
                    errors=["Job not found or not user-created."]
                )
            
            # Update company if company name changed
            if input.company_name:
                company_result = await db.execute(
                    select(Company).where(Company.name.ilike(f"%{input.company_name}%"))
                )
                company = company_result.scalar_one_or_none()
                
                if not company:
                    # Create new company
                    company = Company(
                        name=input.company_name,
                        slug=input.company_name.lower().replace(' ', '-').replace('/', '-'),
                        description=f"Company profile for {input.company_name}",
                    )
                    db.add(company)
                    await db.flush()
                
                job.company_id = company.id
            
            # Update job fields
            if input.title is not None:
                job.title = input.title
            if input.location_text is not None:
                job.location_text = input.location_text
            if input.description is not None:
                job.description = input.description
            if input.requirements is not None:
                job.requirements = input.requirements
            if input.benefits is not None:
                job.benefits = input.benefits
            if input.salary_min is not None:
                job.salary_min = input.salary_min
            if input.salary_max is not None:
                job.salary_max = input.salary_max
            if input.salary_currency is not None:
                job.salary_currency = input.salary_currency
            if input.salary_period is not None:
                job.salary_period = input.salary_period
            if input.job_type is not None:
                job.job_type = input.job_type
            if input.contract_type is not None:
                job.contract_type = input.contract_type
            if input.experience_level is not None:
                job.experience_level = input.experience_level
            if input.remote_type is not None:
                job.remote_type = input.remote_type
            
            await db.commit()
            await db.refresh(job)
            
            # Get company for response
            company_result = await db.execute(
                select(Company).where(Company.id == job.company_id)
            )
            company = company_result.scalar_one()
            
            # Convert to GraphQL type
            job_type = JobType(
                id=str(job.id),
                title=job.title,
                company_id=str(job.company_id),
                category_id=str(job.category_id) if job.category_id else None,
                company=CompanyType(
                    id=str(company.id),
                    name=company.name,
                    slug=company.slug,
                    description=company.description,
                    website=company.website,
                    logo_url=company.logo_url,
                    industry=company.industry,
                    company_size=company.company_size,
                    founded_year=company.founded_year,
                    email=company.email,
                    phone=company.phone,
                    linkedin_url=company.linkedin_url,
                    twitter_handle=company.twitter_handle,
                    glassdoor_id=company.glassdoor_id,
                    glassdoor_rating=company.glassdoor_rating,
                    glassdoor_review_count=company.glassdoor_review_count,
                    ai_research_data=company.ai_research_data,
                    ai_research_model=company.ai_research_model,
                    ai_research_status=company.ai_research_status,
                    ai_research_generated_at=company.ai_research_generated_at,
                    created_at=company.created_at,
                ),
                category=None,
                description=job.description,
                requirements=job.requirements,
                benefits=job.benefits,
                location_text=job.location_text,
                salary_min=job.salary_min,
                salary_max=job.salary_max,
                salary_currency=job.salary_currency,
                salary_period=job.salary_period,
                job_type=job.job_type,
                contract_type=job.contract_type,
                experience_level=job.experience_level,
                remote_type=job.remote_type,
                user_input=job.user_input,
                external_id=job.external_id,
                external_url=job.external_url,
                source=job.source,
                posted_date=job.posted_date,
                expires_date=job.expires_date,
                created_at=job.created_at,
                required_skills=[],
                is_saved=False,
                is_applied=False,
            )
            
            return UserJobResponse(
                job=job_type,
                success=True,
                errors=[]
            )
            
        except Exception as e:
            await db.rollback()
            return UserJobResponse(
                success=False,
                errors=[f"Failed to update job: {str(e)}"]
            )

    @strawberry.mutation
    async def delete_user_job(
        self,
        info,
        job_id: strawberry.ID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> StandardResponse:
        """Delete a user-created job position."""
        try:
            # Find job and verify it's user input
            job_result = await db.execute(
                select(Job).where(
                    Job.id == job_id,
                    Job.user_input == True,
                    Job.is_active == True
                )
            )
            job = job_result.scalar_one_or_none()
            
            if not job:
                return StandardResponse(
                    success=False,
                    errors=["Job not found or not user-created."]
                )
            
            # Soft delete (set is_active to False)
            job.is_active = False
            
            await db.commit()
            
            return StandardResponse(
                success=True,
                message="Job position deleted successfully.",
                errors=[]
            )
            
        except Exception as e:
            await db.rollback()
            return StandardResponse(
                success=False,
                errors=[f"Failed to delete job: {str(e)}"]
            )