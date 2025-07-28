"""
Job-related GraphQL queries for Strawberry Schema
"""

import strawberry
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, exists
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.graphql.types import (
    Job as JobGraphQLType, JobApplication, SavedJob, 
    CompanyType
)
from app.models import (
    Job, Skill, JobApplication, SavedJob, Category, 
    Company, JobSkill, User
)
from app.graphql.auth import get_current_user, get_optional_current_user


@strawberry.type
class JobQuery:
    """Job-related queries."""

    @strawberry.field
    async def job(
        self,
        info,
        id: strawberry.ID
    ) -> Optional[JobGraphQLType]:
        """Get job by ID."""
        # Get database session and current user manually
        db: AsyncSession = await get_db().__anext__()
        current_user = await get_optional_current_user(info.context.request)
        
        try:
            result = await db.execute(
                select(Job)
                .options(
                    selectinload(Job.company),
                    selectinload(Job.category),
                    selectinload(Job.required_skills).selectinload(JobSkill.skill)
                )
                .where(and_(Job.id == id, Job.is_active == True))
            )
            job = result.scalar_one_or_none()
            
            if not job:
                return None
                
            # Check if user has saved or applied to this job
            is_saved = False
            is_applied = False
            
            if current_user:
                saved_result = await db.execute(
                    select(SavedJob).where(
                        and_(SavedJob.user_id == current_user.id, SavedJob.job_id == job.id)
                    )
                )
                is_saved = saved_result.scalar_one_or_none() is not None
            
                applied_result = await db.execute(
                    select(JobApplication).where(
                        and_(JobApplication.user_id == current_user.id, JobApplication.job_id == job.id)
                    )
                )
                is_applied = applied_result.scalar_one_or_none() is not None
            
            # Convert required skills
            required_skills = [
                JobSkillType(
                    job_id=str(js.job_id),
                    skill_id=str(js.skill_id),
                    skill=SkillType(
                        id=str(js.skill.id),
                        name=js.skill.name,
                        slug=js.skill.slug,
                        category=js.skill.category,
                        description=js.skill.description,
                        is_technical=js.skill.is_technical,
                        popularity_score=js.skill.popularity_score,
                        created_at=js.skill.created_at,
                    ),
                    is_required=js.is_required,
                    proficiency_level=js.proficiency_level,
                )
                for js in job.required_skills
            ]
            
            return JobType(
                id=str(job.id),
                title=job.title,
                company_id=str(job.company_id),
                category_id=str(job.category_id) if job.category_id else None,
                company=CompanyType(
                    id=str(job.company.id),
                    name=job.company.name,
                    slug=job.company.slug,
                    description=job.company.description,
                    website=job.company.website,
                    logo_url=job.company.logo_url,
                    industry=job.company.industry,
                    company_size=job.company.company_size,
                    founded_year=job.company.founded_year,
                    email=job.company.email,
                    phone=job.company.phone,
                    linkedin_url=job.company.linkedin_url,
                    twitter_handle=job.company.twitter_handle,
                    glassdoor_id=job.company.glassdoor_id,
                    glassdoor_rating=job.company.glassdoor_rating,
                    glassdoor_review_count=job.company.glassdoor_review_count,
                    ai_research_data=job.company.ai_research_data,
                    ai_research_model=job.company.ai_research_model,
                    ai_research_status=job.company.ai_research_status,
                    ai_research_generated_at=job.company.ai_research_generated_at,
                    created_at=job.company.created_at,
                ),
                category=CategoryType(
                    id=str(job.category.id),
                    name=job.category.name,
                    created_at=job.category.created_at,
                ) if job.category else None,
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
                required_skills=required_skills,
                is_saved=is_saved,
                is_applied=is_applied,
            )
        
        except Exception as e:
            print(f"Error fetching job {id}: {e}")
            return None
        finally:
            await db.close()

    @strawberry.field
    async def jobs(
        self,
        info,
        search: Optional[str] = None,
        location: Optional[str] = None,
        company: Optional[str] = None,
        job_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        remote_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[JobGraphQLType]:
        """Get jobs with various filters."""
        # Get database session and current user manually
        db: AsyncSession = await get_db().__anext__()
        current_user = await get_optional_current_user(info.context.request)
        
        try:
            query = select(Job).options(
            selectinload(Job.company),
            selectinload(Job.category),
            selectinload(Job.required_skills).selectinload(JobSkill.skill)
        ).where(Job.is_active == True)
        
        # Apply filters
        if search:
            query = query.where(
                or_(
                    Job.title.ilike(f"%{search}%"),
                    Job.description.ilike(f"%{search}%"),
                    Job.requirements.ilike(f"%{search}%")
                )
            )
        
        if location:
            query = query.where(Job.location_text.ilike(f"%{location}%"))
        
        if company:
            query = query.join(Company).where(Company.name.ilike(f"%{company}%"))
        
        if job_type:
            query = query.where(Job.job_type == job_type)
        
        if experience_level:
            query = query.where(Job.experience_level == experience_level)
        
        if remote_type:
            query = query.where(Job.remote_type == remote_type)
        
        # Order and paginate
        query = query.order_by(Job.posted_date.desc()).offset(offset).limit(limit)
        
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        # Get user's saved and applied jobs if authenticated
        saved_job_ids = set()
        applied_job_ids = set()
        
        if current_user:
            saved_result = await db.execute(
                select(SavedJob.job_id).where(SavedJob.user_id == current_user.id)
            )
            saved_job_ids = {row[0] for row in saved_result.fetchall()}
            
            applied_result = await db.execute(
                select(JobApplication.job_id).where(JobApplication.user_id == current_user.id)
            )
            applied_job_ids = {row[0] for row in applied_result.fetchall()}
        
        # Convert to GraphQL types
        job_types = []
        for job in jobs:
            required_skills = [
                JobSkillType(
                    job_id=str(js.job_id),
                    skill_id=str(js.skill_id),
                    skill=SkillType(
                        id=str(js.skill.id),
                        name=js.skill.name,
                        slug=js.skill.slug,
                        category=js.skill.category,
                        description=js.skill.description,
                        is_technical=js.skill.is_technical,
                        popularity_score=js.skill.popularity_score,
                        created_at=js.skill.created_at,
                    ),
                    is_required=js.is_required,
                    proficiency_level=js.proficiency_level,
                )
                for js in job.required_skills
            ]
            
            job_types.append(JobType(
                id=str(job.id),
                title=job.title,
                company_id=str(job.company_id),
                category_id=str(job.category_id) if job.category_id else None,
                company=CompanyType(
                    id=str(job.company.id),
                    name=job.company.name,
                    slug=job.company.slug,
                    description=job.company.description,
                    website=job.company.website,
                    logo_url=job.company.logo_url,
                    industry=job.company.industry,
                    company_size=job.company.company_size,
                    founded_year=job.company.founded_year,
                    email=job.company.email,
                    phone=job.company.phone,
                    linkedin_url=job.company.linkedin_url,
                    twitter_handle=job.company.twitter_handle,
                    glassdoor_id=job.company.glassdoor_id,
                    glassdoor_rating=job.company.glassdoor_rating,
                    glassdoor_review_count=job.company.glassdoor_review_count,
                    ai_research_data=job.company.ai_research_data,
                    ai_research_model=job.company.ai_research_model,
                    ai_research_status=job.company.ai_research_status,
                    ai_research_generated_at=job.company.ai_research_generated_at,
                    created_at=job.company.created_at,
                ),
                category=CategoryType(
                    id=str(job.category.id),
                    name=job.category.name,
                    created_at=job.category.created_at,
                ) if job.category else None,
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
                required_skills=required_skills,
                is_saved=job.id in saved_job_ids,
                is_applied=job.id in applied_job_ids,
            ))
        
        return job_types

    @strawberry.field
    async def skills(
        self,
        info,
        db: AsyncSession = Depends(get_db)
    ) -> List[SkillType]:
        """Get all skills."""
        result = await db.execute(select(Skill).order_by(Skill.name))
        skills = result.scalars().all()
        
        return [
            SkillType(
                id=str(skill.id),
                name=skill.name,
                slug=skill.slug,
                category=skill.category,
                description=skill.description,
                is_technical=skill.is_technical,
                popularity_score=skill.popularity_score,
                created_at=skill.created_at,
            )
            for skill in skills
        ]

    @strawberry.field
    async def my_applications(
        self,
        info,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> List[JobApplicationType]:
        """Get current user's job applications."""
        result = await db.execute(
            select(JobApplication)
            .options(
                selectinload(JobApplication.job)
                .selectinload(Job.company)
            )
            .where(JobApplication.user_id == current_user.id)
            .order_by(JobApplication.applied_date.desc())
        )
        applications = result.scalars().all()
        
        application_types = []
        for app in applications:
            # Get job details
            job = JobType(
                id=str(app.job.id),
                title=app.job.title,
                company_id=str(app.job.company_id),
                category_id=str(app.job.category_id) if app.job.category_id else None,
                company=CompanyType(
                    id=str(app.job.company.id),
                    name=app.job.company.name,
                    slug=app.job.company.slug,
                    description=app.job.company.description,
                    website=app.job.company.website,
                    logo_url=app.job.company.logo_url,
                    industry=app.job.company.industry,
                    company_size=app.job.company.company_size,
                    founded_year=app.job.company.founded_year,
                    email=app.job.company.email,
                    phone=app.job.company.phone,
                    linkedin_url=app.job.company.linkedin_url,
                    twitter_handle=app.job.company.twitter_handle,
                    glassdoor_id=app.job.company.glassdoor_id,
                    glassdoor_rating=app.job.company.glassdoor_rating,
                    glassdoor_review_count=app.job.company.glassdoor_review_count,
                    ai_research_data=app.job.company.ai_research_data,
                    ai_research_model=app.job.company.ai_research_model,
                    ai_research_status=app.job.company.ai_research_status,
                    ai_research_generated_at=app.job.company.ai_research_generated_at,
                    created_at=app.job.company.created_at,
                ),
                category=None,  # Simplified for applications view
                description=app.job.description,
                requirements=app.job.requirements,
                benefits=app.job.benefits,
                location_text=app.job.location_text,
                salary_min=app.job.salary_min,
                salary_max=app.job.salary_max,
                salary_currency=app.job.salary_currency,
                salary_period=app.job.salary_period,
                job_type=app.job.job_type,
                contract_type=app.job.contract_type,
                experience_level=app.job.experience_level,
                remote_type=app.job.remote_type,
                user_input=app.job.user_input,
                external_id=app.job.external_id,
                external_url=app.job.external_url,
                source=app.job.source,
                posted_date=app.job.posted_date,
                expires_date=app.job.expires_date,
                created_at=app.job.created_at,
                required_skills=[],  # Simplified for applications view
                is_saved=False,
                is_applied=True,
            )
            
            application_types.append(JobApplicationType(
                id=str(app.id),
                user_id=str(app.user_id),
                job_id=str(app.job_id),
                job=job,
                status=app.status,
                applied_date=app.applied_date,
                last_updated=app.last_updated,
                cover_letter=app.cover_letter,
                notes=app.notes,
                optimized_resume_data=app.optimized_resume_data,
                ai_suggestions=app.ai_suggestions,
                skills_analysis=app.skills_analysis,
                created_at=app.created_at,
            ))
        
        return application_types