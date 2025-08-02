"""
GraphQL queries for Resume operations
"""

import strawberry
import logging
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.resume import Resume, ResumeProcessingLog
from app.services.storage import storage_service
from app.core.database import AsyncSessionLocal
from app.graphql.types.resume_types import (
    ResumeType, ResumeListType, ResumeListResponse, PersonalInfoType,
    ExperienceType, EducationType, ProjectType, ResumeFileInfoType,
    ResumeProcessingLogType
)

logger = logging.getLogger(__name__)


@strawberry.type
class ResumeQueries:
    """Resume-related GraphQL queries"""
    
    @strawberry.field
    async def resumes(
        self, 
        info,
        limit: Optional[int] = 50,
        offset: Optional[int] = 0
    ) -> ResumeListResponse:
        """Get user's resumes"""
        try:
            # Get user from context
            user = getattr(info.context, 'user', None)
            if not user:
                return ResumeListResponse(
                    success=False,
                    message="Authentication required",
                    resumes=[],
                    total_count=0
                )
            
            async with AsyncSessionLocal() as session:
                # Query user's resumes
                query = (
                    select(Resume)
                    .where(Resume.user_id == user.id)
                    .order_by(Resume.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                )
                
                result = await session.execute(query)
                resumes = result.scalars().all()
                
                # Convert to GraphQL types
                resume_list = []
                for resume in resumes:
                    personal_info = None
                    if resume.personal_info:
                        personal_info = PersonalInfoType(**resume.personal_info)
                    
                    resume_item = ResumeListType(
                        id=str(resume.id),
                        title=resume.title,
                        user_id=str(resume.user_id),
                        personal_info=personal_info,
                        target_role=resume.target_role,
                        target_industry=resume.target_industry,
                        source_type=resume.source_type,
                        processing_status=resume.processing_status,
                        status_display=resume.status_display,
                        is_default=resume.is_default,
                        view_count=resume.view_count,
                        created_at=resume.created_at,
                        updated_at=resume.updated_at
                    )
                    resume_list.append(resume_item)
                
                logger.info(f"Retrieved {len(resume_list)} resumes for user {user.id}")
                
                return ResumeListResponse(
                    success=True,
                    message=f"Retrieved {len(resume_list)} resumes",
                    resumes=resume_list,
                    total_count=len(resume_list)
                )
                
        except Exception as e:
            logger.error(f"Error retrieving resumes: {e}")
            return ResumeListResponse(
                success=False,
                message=f"Failed to retrieve resumes: {str(e)}",
                resumes=[],
                total_count=0
            )
    
    @strawberry.field
    async def resume(self, info, id: str) -> Optional[ResumeType]:
        """Get a specific resume by ID"""
        try:
            # Get user from context
            user = getattr(info.context, 'user', None)
            if not user:
                logger.warning("Unauthenticated request for resume")
                return None
            
            async with AsyncSessionLocal() as session:
                # Query resume with processing logs
                query = (
                    select(Resume)
                    .options(selectinload(Resume.processing_logs))
                    .where(Resume.id == id, Resume.user_id == user.id)
                )
                
                result = await session.execute(query)
                resume = result.scalar_one_or_none()
                
                if not resume:
                    logger.warning(f"Resume not found: {id}")
                    return None
                
                # Convert personal info
                personal_info = None
                if resume.personal_info:
                    personal_info = PersonalInfoType(**resume.personal_info)
                
                # Convert experience
                experience_list = []
                if resume.experience:
                    for exp in resume.experience:
                        experience_list.append(ExperienceType(**exp))
                
                # Convert education
                education_list = []
                if resume.education:
                    for edu in resume.education:
                        education_list.append(EducationType(**edu))
                
                # Convert projects
                projects_list = []
                if resume.projects:
                    for proj in resume.projects:
                        projects_list.append(ProjectType(**proj))
                
                # Convert file info
                file_info = None
                if resume.file_path:
                    try:
                        download_url = storage_service.get_file_url(resume.file_path)
                    except:
                        download_url = None
                    
                    file_info = ResumeFileInfoType(
                        original_filename=resume.original_filename,
                        file_path=resume.file_path,
                        file_size=resume.file_size,
                        file_type=resume.file_type,
                        file_size_display=resume.file_size_display,
                        download_url=download_url
                    )
                
                # Convert processing logs
                processing_logs = []
                for log in resume.processing_logs:
                    processing_logs.append(ResumeProcessingLogType(
                        id=str(log.id),
                        operation=log.operation,
                        status=log.status,
                        message=log.message,
                        processing_time=log.processing_time,
                        created_at=log.created_at
                    ))
                
                # Create full resume type
                full_resume = ResumeType(
                    id=str(resume.id),
                    title=resume.title,
                    user_id=str(resume.user_id),
                    personal_info=personal_info,
                    summary=resume.summary,
                    experience=experience_list if experience_list else None,
                    education=education_list if education_list else None,
                    skills=resume.skills,
                    projects=projects_list if projects_list else None,
                    target_role=resume.target_role,
                    target_industry=resume.target_industry,
                    keywords=resume.keywords,
                    file_info=file_info,
                    source_type=resume.source_type,
                    processing_status=resume.processing_status,
                    processing_error=resume.processing_error,
                    status_display=resume.status_display,
                    version=resume.version,
                    is_default=resume.is_default,
                    is_public=resume.is_public,
                    view_count=resume.view_count,
                    created_at=resume.created_at,
                    updated_at=resume.updated_at,
                    processing_logs=processing_logs if processing_logs else None
                )
                
                # Increment view count
                resume.view_count += 1
                await session.commit()
                
                logger.info(f"Retrieved resume: {id}")
                return full_resume
                
        except Exception as e:
            logger.error(f"Error retrieving resume {id}: {e}")
            return None
    
    @strawberry.field
    async def resume_file_url(self, info, resume_id: str) -> Optional[str]:
        """Get download URL for resume file"""
        try:
            # Get user from context
            user = getattr(info.context, 'user', None)
            if not user:
                return None
            
            async with AsyncSessionLocal() as session:
                # Find resume
                resume = await session.get(Resume, resume_id)
                if not resume or str(resume.user_id) != str(user.id):
                    return None
                
                if not resume.file_path:
                    return None
                
                # Generate download URL
                download_url = storage_service.get_file_url(resume.file_path)
                return download_url
                
        except Exception as e:
            logger.error(f"Error generating file URL for resume {resume_id}: {e}")
            return None
    
    @strawberry.field
    async def storage_health(self, info) -> dict:
        """Check storage service health (admin only)"""
        try:
            # Get user from context
            user = getattr(info.context, 'user', None)
            if not user:
                return {"status": "unauthorized"}
            
            # For now, allow all authenticated users to check health
            # In production, you might want to restrict this to admin users
            
            health_status = storage_service.health_check()
            return health_status
            
        except Exception as e:
            logger.error(f"Error checking storage health: {e}")
            return {"status": "error", "message": str(e)}