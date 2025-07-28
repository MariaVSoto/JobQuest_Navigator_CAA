"""
Job service layer for business logic
Handles job management, applications, and company research
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID
from datetime import datetime

from app.models.job import Job, Company, Skill, JobApplication, JobSkill
from app.core.database import get_db, AsyncSessionLocal


class JobService:
    """Service for job-related business logic"""
    
    def __init__(self, db_session: AsyncSession = None):
        self.db_session = db_session
    
    async def create_user_job(
        self,
        user_id: UUID,
        title: str,
        company_name: str,
        location_text: str = None,
        description: str = None,
        requirements: str = None,
        salary_range: str = None,
        work_type: str = "full_time",
        job_type: str = "permanent",
        **kwargs
    ) -> Job:
        """Create a user-input job opportunity"""
        async with get_db_session() as session:
            # Create or get company
            company = await self._get_or_create_company(session, company_name)
            
            # Create job
            job = Job(
                title=title,
                company_id=company.id,
                location_text=location_text,
                description=description,
                requirements=requirements,
                salary_range=salary_range,
                work_type=work_type,
                job_type=job_type,
                user_input=True,
                created_by_user_id=user_id,
                **kwargs
            )
            
            session.add(job)
            await session.commit()
            await session.refresh(job)
            return job
    
    async def get_user_jobs(
        self,
        user_id: UUID,
        status: str = None,
        limit: int = 50
    ) -> List[Job]:
        """Get jobs created by user"""
        async with get_db_session() as session:
            query = select(Job).where(Job.created_by_user_id == user_id)
            
            if status:
                query = query.where(Job.status == status)
            
            query = query.order_by(Job.created_at.desc()).limit(limit)
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def get_job_by_id(self, job_id: UUID) -> Optional[Job]:
        """Get job by ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Job).where(Job.id == job_id)
            )
            return result.scalar_one_or_none()
    
    async def update_job(
        self,
        job_id: UUID,
        user_id: UUID,
        **kwargs
    ) -> Optional[Job]:
        """Update job (only by creator)"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Job).where(
                    and_(
                        Job.id == job_id,
                        Job.created_by_user_id == user_id
                    )
                )
            )
            job = result.scalar_one_or_none()
            
            if job:
                for key, value in kwargs.items():
                    if hasattr(job, key):
                        setattr(job, key, value)
                
                await session.commit()
                await session.refresh(job)
            
            return job
    
    async def delete_job(self, job_id: UUID, user_id: UUID) -> bool:
        """Soft delete job (only by creator)"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Job).where(
                    and_(
                        Job.id == job_id,
                        Job.created_by_user_id == user_id
                    )
                )
            )
            job = result.scalar_one_or_none()
            
            if job:
                job.is_active = False
                await session.commit()
                return True
            
            return False
    
    async def apply_to_job(
        self,
        user_id: UUID,
        job_id: UUID,
        cover_letter: str = None,
        resume_url: str = None,
        application_notes: str = None
    ) -> JobApplication:
        """Apply to a job"""
        async with get_db_session() as session:
            application = JobApplication(
                user_id=user_id,
                job_id=job_id,
                cover_letter=cover_letter,
                resume_url=resume_url,
                application_notes=application_notes,
                status="applied",
                applied_at=datetime.utcnow()
            )
            
            session.add(application)
            await session.commit()
            await session.refresh(application)
            return application
    
    async def get_user_applications(
        self,
        user_id: UUID,
        status: str = None,
        limit: int = 50
    ) -> List[JobApplication]:
        """Get user's job applications"""
        async with get_db_session() as session:
            query = select(JobApplication).where(JobApplication.user_id == user_id)
            
            if status:
                query = query.where(JobApplication.status == status)
            
            query = query.order_by(JobApplication.applied_at.desc()).limit(limit)
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def update_application_status(
        self,
        application_id: UUID,
        user_id: UUID,
        status: str,
        notes: str = None
    ) -> Optional[JobApplication]:
        """Update application status"""
        async with get_db_session() as session:
            result = await session.execute(
                select(JobApplication).where(
                    and_(
                        JobApplication.id == application_id,
                        JobApplication.user_id == user_id
                    )
                )
            )
            application = result.scalar_one_or_none()
            
            if application:
                application.status = status
                if notes:
                    application.application_notes = notes
                
                await session.commit()
                await session.refresh(application)
            
            return application
    
    async def add_job_skills(
        self,
        job_id: UUID,
        skill_names: List[str]
    ) -> List[JobSkill]:
        """Add skills to a job"""
        async with get_db_session() as session:
            job_skills = []
            
            for skill_name in skill_names:
                # Get or create skill
                skill = await self._get_or_create_skill(session, skill_name)
                
                # Create job-skill relationship
                job_skill = JobSkill(
                    job_id=job_id,
                    skill_id=skill.id
                )
                session.add(job_skill)
                job_skills.append(job_skill)
            
            await session.commit()
            return job_skills
    
    async def get_job_skills(self, job_id: UUID) -> List[Skill]:
        """Get skills for a job"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Skill)
                .join(JobSkill)
                .where(JobSkill.job_id == job_id)
            )
            return result.scalars().all()
    
    async def search_jobs(
        self,
        query: str = None,
        location: str = None,
        job_type: str = None,
        work_type: str = None,
        user_id: UUID = None,
        limit: int = 50
    ) -> List[Job]:
        """Search jobs with filters"""
        async with get_db_session() as session:
            filters = [Job.is_active == True]
            
            if query:
                filters.append(
                    Job.title.ilike(f"%{query}%") |
                    Job.description.ilike(f"%{query}%")
                )
            
            if location:
                filters.append(Job.location_text.ilike(f"%{location}%"))
            
            if job_type:
                filters.append(Job.job_type == job_type)
            
            if work_type:
                filters.append(Job.work_type == work_type)
            
            if user_id:
                filters.append(Job.created_by_user_id == user_id)
            
            result = await session.execute(
                select(Job)
                .where(and_(*filters))
                .order_by(Job.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
    
    async def _get_or_create_company(
        self,
        session: AsyncSession,
        company_name: str
    ) -> Company:
        """Get existing company or create new one"""
        result = await session.execute(
            select(Company).where(Company.name == company_name)
        )
        company = result.scalar_one_or_none()
        
        if not company:
            company = Company(name=company_name)
            session.add(company)
            await session.flush()
        
        return company
    
    async def _get_or_create_skill(
        self,
        session: AsyncSession,
        skill_name: str
    ) -> Skill:
        """Get existing skill or create new one"""
        result = await session.execute(
            select(Skill).where(Skill.name == skill_name)
        )
        skill = result.scalar_one_or_none()
        
        if not skill:
            skill = Skill(name=skill_name)
            session.add(skill)
            await session.flush()
        
        return skill