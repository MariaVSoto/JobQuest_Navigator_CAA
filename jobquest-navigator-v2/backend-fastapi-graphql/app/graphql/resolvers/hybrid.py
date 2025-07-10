"""
Hybrid resolvers that can switch between FastAPI and Django implementations
Enables gradual migration with feature flags
"""

import strawberry
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
import logging

from app.core.database import get_db
from app.core.config import settings
from app.graphql.types import JobType, UserType, JobApplicationType
from app.graphql.proxy import (
    get_jobs_from_django, 
    get_user_applications_from_django,
    apply_to_job_via_django,
    save_job_via_django
)
from app.graphql.auth import get_current_user, get_optional_current_user
from app.models import User

logger = logging.getLogger(__name__)


class MigrationFlags:
    """
    Feature flags to control which implementation to use
    Set these to True to use FastAPI, False to use Django proxy
    """
    USE_FASTAPI_USERS = True          # User management in FastAPI
    USE_FASTAPI_JOBS = False          # Job listings still from Django (has location data)
    USE_FASTAPI_APPLICATIONS = False  # Applications still from Django
    USE_FASTAPI_COMPANIES = True      # Companies in FastAPI (no location dependency)
    USE_FASTAPI_SKILLS = True         # Skills in FastAPI (simple data)


@strawberry.type
class HybridQuery:
    """
    Hybrid query resolvers that can switch between implementations
    """

    @strawberry.field
    async def jobs_hybrid(
        self,
        info,
        search: Optional[str] = None,
        location: Optional[str] = None,
        company: Optional[str] = None,
        job_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        remote_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        current_user: Optional[User] = Depends(get_optional_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> List[JobType]:
        """
        Hybrid job query - uses Django for location-based features,
        FastAPI for simple job management
        """
        
        if MigrationFlags.USE_FASTAPI_JOBS:
            # Use FastAPI implementation (no location features)
            from app.graphql.queries.job import JobQuery
            job_query = JobQuery()
            return await job_query.jobs(
                info, search, None, company, job_type, 
                experience_level, remote_type, limit, offset,
                current_user, db
            )
        else:
            # Use Django proxy for location-based job search
            auth_header = None
            if current_user:
                # In real implementation, construct proper JWT header
                auth_header = f"Bearer {current_user.id}"  # Simplified
            
            django_jobs = await get_jobs_from_django(
                search=search,
                location=location,  # Location search available in Django
                limit=limit,
                offset=offset,
                auth_header=auth_header
            )
            
            if not django_jobs:
                logger.warning("Django jobs query failed, falling back to empty result")
                return []
            
            # Convert Django response to FastAPI types
            # This is a simplified conversion - in practice, you'd map all fields
            job_types = []
            for django_job in django_jobs:
                # Create minimal JobType from Django data
                # Note: This is a simplified mapping
                job_types.append(JobType(
                    id=django_job["id"],
                    title=django_job["title"],
                    company_id="",  # Would map from Django company
                    company=None,   # Would convert Django company
                    category=None,
                    description=django_job["description"],
                    requirements=None,
                    benefits=None,
                    location_text=django_job.get("location", {}).get("name", ""),
                    salary_min=django_job.get("salaryMin"),
                    salary_max=django_job.get("salaryMax"),
                    salary_currency="USD",
                    salary_period="yearly",
                    job_type=django_job.get("jobType", "full_time"),
                    contract_type="permanent",
                    experience_level=None,
                    remote_type=django_job.get("remoteType", "on_site"),
                    user_input=False,  # Django jobs are external
                    external_id=None,
                    external_url=None,
                    source="django_proxy",
                    posted_date=django_job["postedDate"],
                    expires_date=None,
                    created_at=django_job["postedDate"],
                    required_skills=[],
                    is_saved=django_job.get("isSaved", False),
                    is_applied=django_job.get("isApplied", False),
                ))
            
            return job_types

    @strawberry.field 
    async def my_applications_hybrid(
        self,
        info,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> List[JobApplicationType]:
        """
        Hybrid applications query - can switch between Django and FastAPI
        """
        
        if MigrationFlags.USE_FASTAPI_APPLICATIONS:
            # Use FastAPI implementation
            from app.graphql.queries.job import JobQuery
            job_query = JobQuery()
            return await job_query.my_applications(info, current_user, db)
        else:
            # Use Django proxy
            auth_header = f"Bearer {current_user.id}"  # Simplified
            
            django_applications = await get_user_applications_from_django(auth_header)
            
            if not django_applications:
                logger.warning("Django applications query failed, falling back to empty result")
                return []
            
            # Convert Django response to FastAPI types
            # This is a simplified conversion
            application_types = []
            for django_app in django_applications:
                # Create minimal JobApplicationType from Django data
                application_types.append(JobApplicationType(
                    id=django_app["id"],
                    user_id=str(current_user.id),
                    job_id=django_app["job"]["id"],
                    job=None,  # Would convert Django job data
                    status=django_app["status"],
                    applied_date=django_app["appliedDate"],
                    last_updated=django_app["lastUpdated"],
                    cover_letter=None,
                    notes=None,
                    optimized_resume_data=None,
                    ai_suggestions=None,
                    skills_analysis=None,
                    created_at=django_app["appliedDate"],
                ))
            
            return application_types


@strawberry.type
class HybridMutation:
    """
    Hybrid mutation resolvers that can switch between implementations
    """

    @strawberry.mutation
    async def apply_to_job_hybrid(
        self,
        info,
        job_id: strawberry.ID,
        cover_letter: Optional[str] = None,
        notes: Optional[str] = None,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> Dict[str, Any]:
        """
        Hybrid job application - can route to Django or FastAPI
        """
        
        if MigrationFlags.USE_FASTAPI_APPLICATIONS:
            # Use FastAPI implementation
            from app.graphql.mutations.job import JobMutation
            from app.graphql.types import ApplyToJobInput
            
            job_mutation = JobMutation()
            input_data = ApplyToJobInput(
                job_id=job_id,
                cover_letter=cover_letter,
                notes=notes
            )
            return await job_mutation.apply_to_job(info, input_data, current_user, db)
        else:
            # Use Django proxy
            auth_header = f"Bearer {current_user.id}"  # Simplified
            
            result = await apply_to_job_via_django(
                job_id=str(job_id),
                cover_letter=cover_letter,
                notes=notes,
                auth_header=auth_header
            )
            
            # Convert Django response format
            if "data" in result and "applyToJob" in result["data"]:
                django_result = result["data"]["applyToJob"]
                return {
                    "success": django_result["success"],
                    "errors": django_result.get("errors", []),
                    "application": django_result.get("application")
                }
            else:
                return {
                    "success": False,
                    "errors": result.get("errors", ["Unknown error"]),
                    "application": None
                }

    @strawberry.mutation
    async def save_job_hybrid(
        self,
        info,
        job_id: strawberry.ID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> Dict[str, Any]:
        """
        Hybrid save job - can route to Django or FastAPI
        """
        
        if MigrationFlags.USE_FASTAPI_APPLICATIONS:
            # Use FastAPI implementation
            from app.graphql.mutations.job import JobMutation
            
            job_mutation = JobMutation()
            return await job_mutation.save_job(info, job_id, current_user, db)
        else:
            # Use Django proxy
            auth_header = f"Bearer {current_user.id}"  # Simplified
            
            result = await save_job_via_django(
                job_id=str(job_id),
                auth_header=auth_header
            )
            
            # Convert Django response format
            if "data" in result and "saveJob" in result["data"]:
                django_result = result["data"]["saveJob"]
                return {
                    "success": django_result["success"],
                    "errors": django_result.get("errors", []),
                    "savedJob": django_result.get("savedJob")
                }
            else:
                return {
                    "success": False,
                    "errors": result.get("errors", ["Unknown error"]),
                    "savedJob": None
                }


def get_migration_status() -> Dict[str, bool]:
    """
    Get current migration status for monitoring/debugging
    """
    return {
        "users": MigrationFlags.USE_FASTAPI_USERS,
        "jobs": MigrationFlags.USE_FASTAPI_JOBS,
        "applications": MigrationFlags.USE_FASTAPI_APPLICATIONS,
        "companies": MigrationFlags.USE_FASTAPI_COMPANIES,
        "skills": MigrationFlags.USE_FASTAPI_SKILLS,
    }


def set_migration_flag(feature: str, use_fastapi: bool) -> bool:
    """
    Dynamically set migration flags (for admin/testing)
    
    Args:
        feature: Feature name (users, jobs, applications, etc.)
        use_fastapi: True to use FastAPI, False to use Django
        
    Returns:
        True if flag was set successfully
    """
    flag_mapping = {
        "users": "USE_FASTAPI_USERS",
        "jobs": "USE_FASTAPI_JOBS", 
        "applications": "USE_FASTAPI_APPLICATIONS",
        "companies": "USE_FASTAPI_COMPANIES",
        "skills": "USE_FASTAPI_SKILLS",
    }
    
    if feature in flag_mapping:
        setattr(MigrationFlags, flag_mapping[feature], use_fastapi)
        logger.info(f"Migration flag {feature} set to {'FastAPI' if use_fastapi else 'Django'}")
        return True
    
    return False