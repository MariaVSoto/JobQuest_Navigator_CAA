"""
Job-related GraphQL mutations for Strawberry Schema
"""

import strawberry
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import Depends
from datetime import datetime

from app.core.database import get_db
from app.graphql.types import (
    JobApplicationResponse, SavedJobResponse, StandardResponse,
    JobApplicationInput, UpdateApplicationStatusInput,
    JobApplication as JobApplicationType, SavedJob as SavedJobType, 
    Job as JobType, Company as CompanyType
)
from app.models import Job, JobApplication, SavedJob, User, Company
from app.graphql.auth import get_current_user


@strawberry.type
class JobMutation:
    """Job-related mutations."""

    @strawberry.mutation
    async def apply_to_job(
        self,
        info,
        input: JobApplicationInput,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> JobApplicationResponse:
        """Apply to a job."""
        try:
            # Check if job exists and is active
            job_result = await db.execute(
                select(Job).where(and_(Job.id == input.job_id, Job.is_active == True))
            )
            job = job_result.scalar_one_or_none()
            
            if not job:
                return JobApplicationResponse(
                    success=False,
                    errors=["Job not found or not active."]
                )
            
            # Check if user has already applied
            existing_app = await db.execute(
                select(JobApplication).where(
                    and_(
                        JobApplication.user_id == current_user.id,
                        JobApplication.job_id == input.job_id
                    )
                )
            )
            
            if existing_app.scalar_one_or_none():
                return JobApplicationResponse(
                    success=False,
                    errors=["You have already applied to this job."]
                )
            
            # Create job application
            application = JobApplication(
                user_id=current_user.id,
                job_id=input.job_id,
                cover_letter=input.cover_letter or "",
                notes=input.notes or "",
                status="applied"
            )
            
            db.add(application)
            await db.commit()
            await db.refresh(application)
            
            # Get job details for response
            job_with_company = await db.execute(
                select(Job).join(Company).where(Job.id == input.job_id)
            )
            job_data = job_with_company.scalar_one()
            
            company_result = await db.execute(
                select(Company).where(Company.id == job_data.company_id)
            )
            company_data = company_result.scalar_one()
            
            job_type = JobType(
                id=str(job_data.id),
                title=job_data.title,
                company_id=str(job_data.company_id),
                category_id=str(job_data.category_id) if job_data.category_id else None,
                company=CompanyType(
                    id=str(company_data.id),
                    name=company_data.name,
                    slug=company_data.slug,
                    description=company_data.description,
                    website=company_data.website,
                    logo_url=company_data.logo_url,
                    industry=company_data.industry,
                    company_size=company_data.company_size,
                    founded_year=company_data.founded_year,
                    email=company_data.email,
                    phone=company_data.phone,
                    linkedin_url=company_data.linkedin_url,
                    twitter_handle=company_data.twitter_handle,
                    glassdoor_id=company_data.glassdoor_id,
                    glassdoor_rating=company_data.glassdoor_rating,
                    glassdoor_review_count=company_data.glassdoor_review_count,
                    ai_research_data=company_data.ai_research_data,
                    ai_research_model=company_data.ai_research_model,
                    ai_research_status=company_data.ai_research_status,
                    ai_research_generated_at=company_data.ai_research_generated_at,
                    created_at=company_data.created_at,
                ),
                category=None,  # Simplified for response
                description=job_data.description,
                requirements=job_data.requirements,
                benefits=job_data.benefits,
                location_text=job_data.location_text,
                salary_min=job_data.salary_min,
                salary_max=job_data.salary_max,
                salary_currency=job_data.salary_currency,
                salary_period=job_data.salary_period,
                job_type=job_data.job_type,
                contract_type=job_data.contract_type,
                experience_level=job_data.experience_level,
                remote_type=job_data.remote_type,
                user_input=job_data.user_input,
                external_id=job_data.external_id,
                external_url=job_data.external_url,
                source=job_data.source,
                posted_date=job_data.posted_date,
                expires_date=job_data.expires_date,
                created_at=job_data.created_at,
                required_skills=[],  # Simplified for response
                is_saved=False,
                is_applied=True,
            )
            
            application_type = JobApplicationType(
                id=str(application.id),
                user_id=str(application.user_id),
                job_id=str(application.job_id),
                job=job_type,
                status=application.status,
                applied_date=application.applied_date,
                last_updated=application.last_updated,
                cover_letter=application.cover_letter,
                notes=application.notes,
                optimized_resume_data=application.optimized_resume_data,
                ai_suggestions=application.ai_suggestions,
                skills_analysis=application.skills_analysis,
                created_at=application.created_at,
            )
            
            return JobApplicationResponse(
                application=application_type,
                success=True,
                errors=[]
            )
            
        except Exception as e:
            await db.rollback()
            return JobApplicationResponse(
                success=False,
                errors=[f"Application failed: {str(e)}"]
            )

    @strawberry.mutation
    async def update_application_status(
        self,
        info,
        input: UpdateApplicationStatusInput,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> JobApplicationResponse:
        """Update job application status."""
        try:
            # Find user's application
            app_result = await db.execute(
                select(JobApplication).where(
                    and_(
                        JobApplication.id == input.application_id,
                        JobApplication.user_id == current_user.id
                    )
                )
            )
            application = app_result.scalar_one_or_none()
            
            if not application:
                return JobApplicationResponse(
                    success=False,
                    errors=["Application not found."]
                )
            
            # Validate status
            valid_statuses = [
                'applied', 'screening', 'interview', 'offer', 'rejected', 'withdrawn'
            ]
            if input.status not in valid_statuses:
                return JobApplicationResponse(
                    success=False,
                    errors=[f"Invalid status. Valid options: {valid_statuses}"]
                )
            
            # Update application
            application.status = input.status
            if input.notes:
                application.notes = input.notes
            application.last_updated = datetime.utcnow()
            
            await db.commit()
            await db.refresh(application)
            
            # Get job details for response
            job_result = await db.execute(
                select(Job).join(Company).where(Job.id == application.job_id)
            )
            job_data = job_result.scalar_one()
            
            company_result = await db.execute(
                select(Company).where(Company.id == job_data.company_id)
            )
            company_data = company_result.scalar_one()
            
            job_type = JobType(
                id=str(job_data.id),
                title=job_data.title,
                company_id=str(job_data.company_id),
                category_id=str(job_data.category_id) if job_data.category_id else None,
                company=CompanyType(
                    id=str(company_data.id),
                    name=company_data.name,
                    slug=company_data.slug,
                    description=company_data.description,
                    website=company_data.website,
                    logo_url=company_data.logo_url,
                    industry=company_data.industry,
                    company_size=company_data.company_size,
                    founded_year=company_data.founded_year,
                    email=company_data.email,
                    phone=company_data.phone,
                    linkedin_url=company_data.linkedin_url,
                    twitter_handle=company_data.twitter_handle,
                    glassdoor_id=company_data.glassdoor_id,
                    glassdoor_rating=company_data.glassdoor_rating,
                    glassdoor_review_count=company_data.glassdoor_review_count,
                    ai_research_data=company_data.ai_research_data,
                    ai_research_model=company_data.ai_research_model,
                    ai_research_status=company_data.ai_research_status,
                    ai_research_generated_at=company_data.ai_research_generated_at,
                    created_at=company_data.created_at,
                ),
                category=None,  # Simplified for response
                description=job_data.description,
                requirements=job_data.requirements,
                benefits=job_data.benefits,
                location_text=job_data.location_text,
                salary_min=job_data.salary_min,
                salary_max=job_data.salary_max,
                salary_currency=job_data.salary_currency,
                salary_period=job_data.salary_period,
                job_type=job_data.job_type,
                contract_type=job_data.contract_type,
                experience_level=job_data.experience_level,
                remote_type=job_data.remote_type,
                user_input=job_data.user_input,
                external_id=job_data.external_id,
                external_url=job_data.external_url,
                source=job_data.source,
                posted_date=job_data.posted_date,
                expires_date=job_data.expires_date,
                created_at=job_data.created_at,
                required_skills=[],  # Simplified for response
                is_saved=False,
                is_applied=True,
            )
            
            application_type = JobApplicationType(
                id=str(application.id),
                user_id=str(application.user_id),
                job_id=str(application.job_id),
                job=job_type,
                status=application.status,
                applied_date=application.applied_date,
                last_updated=application.last_updated,
                cover_letter=application.cover_letter,
                notes=application.notes,
                optimized_resume_data=application.optimized_resume_data,
                ai_suggestions=application.ai_suggestions,
                skills_analysis=application.skills_analysis,
                created_at=application.created_at,
            )
            
            return JobApplicationResponse(
                application=application_type,
                success=True,
                errors=[]
            )
            
        except Exception as e:
            await db.rollback()
            return JobApplicationResponse(
                success=False,
                errors=[f"Status update failed: {str(e)}"]
            )

    @strawberry.mutation
    async def save_job(
        self,
        info,
        job_id: strawberry.ID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> SavedJobResponse:
        """Save a job for later."""
        try:
            # Check if job exists and is active
            job_result = await db.execute(
                select(Job).where(and_(Job.id == job_id, Job.is_active == True))
            )
            job = job_result.scalar_one_or_none()
            
            if not job:
                return SavedJobResponse(
                    success=False,
                    errors=["Job not found or not active."]
                )
            
            # Check if already saved
            existing_saved = await db.execute(
                select(SavedJob).where(
                    and_(
                        SavedJob.user_id == current_user.id,
                        SavedJob.job_id == job_id
                    )
                )
            )
            
            if existing_saved.scalar_one_or_none():
                return SavedJobResponse(
                    success=False,
                    errors=["Job is already saved."]
                )
            
            # Create saved job record
            saved_job = SavedJob(
                user_id=current_user.id,
                job_id=job_id
            )
            
            db.add(saved_job)
            await db.commit()
            await db.refresh(saved_job)
            
            # Get job details for response (simplified)
            saved_job_type = SavedJobType(
                id=str(saved_job.id),
                user_id=str(saved_job.user_id),
                job_id=str(saved_job.job_id),
                job=JobType(
                    id=str(job.id),
                    title=job.title,
                    company_id=str(job.company_id),
                    category_id=str(job.category_id) if job.category_id else None,
                    company=CompanyType(
                        id="",  # Simplified
                        name="",
                        created_at=job.created_at,
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
                    is_saved=True,
                    is_applied=False,
                ),
                saved_date=saved_job.saved_date,
                notes=saved_job.notes,
                created_at=saved_job.created_at,
            )
            
            return SavedJobResponse(
                saved_job=saved_job_type,
                success=True,
                errors=[]
            )
            
        except Exception as e:
            await db.rollback()
            return SavedJobResponse(
                success=False,
                errors=[f"Save job failed: {str(e)}"]
            )

    @strawberry.mutation
    async def unsave_job(
        self,
        info,
        job_id: strawberry.ID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> StandardResponse:
        """Remove a job from saved jobs."""
        try:
            # Find and delete saved job record
            result = await db.execute(
                select(SavedJob).where(
                    and_(
                        SavedJob.user_id == current_user.id,
                        SavedJob.job_id == job_id
                    )
                )
            )
            saved_job = result.scalar_one_or_none()
            
            if not saved_job:
                return StandardResponse(
                    success=False,
                    errors=["Saved job not found."]
                )
            
            await db.delete(saved_job)
            await db.commit()
            
            return StandardResponse(
                success=True,
                message="Job removed from saved jobs.",
                errors=[]
            )
            
        except Exception as e:
            await db.rollback()
            return StandardResponse(
                success=False,
                errors=[f"Unsave job failed: {str(e)}"]
            )