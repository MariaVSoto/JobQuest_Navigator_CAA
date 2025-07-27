"""
Job related GraphQL types
Strawberry type definitions for simplified job management (user input based)
"""

import strawberry
from typing import Optional, List
from datetime import datetime
from .common_types import Company
from app.core.dataloaders import get_dataloaders


@strawberry.type
class Job:
    """
    Job GraphQL type - consistent naming with main schema
    """
    id: str
    title: str
    description: str
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    locationText: Optional[str] = None
    
    # Salary information
    salaryMin: Optional[float] = None
    salaryMax: Optional[float] = None
    salaryCurrency: str = "USD"
    salaryPeriod: str = "yearly"
    
    # Job details
    jobType: str = "full_time"
    contractType: str = "permanent"
    experienceLevel: Optional[str] = None
    remoteType: str = "on_site"
    
    # User input fields
    userInput: bool = True
    source: str = "user_input"
    postedDate: datetime
    expiresDate: Optional[datetime] = None
    
    # Optimized relationships using DataLoaders
    @strawberry.field
    async def company(self, info) -> Optional[Company]:
        """Load company using DataLoader to prevent N+1 queries."""
        if not hasattr(self, '_company_id') or self._company_id is None:
            return None
        
        dataloaders = get_dataloaders(info)
        company_loader = dataloaders.get_company_loader()
        return await company_loader.load(self._company_id)
    
    @strawberry.field
    async def isSaved(self, info) -> bool:
        """Check if job is saved by current user using DataLoader."""
        current_user = getattr(info.context, 'user', None)
        if not current_user:
            return False
        
        dataloaders = get_dataloaders(info)
        application_loader = dataloaders.get_job_application_loader()
        # This would need a separate SavedJobDataLoader implementation
        # For now, return False as placeholder
        return False
    
    @strawberry.field
    async def isApplied(self, info) -> bool:
        """Check if user has applied to this job using DataLoader."""
        current_user = getattr(info.context, 'user', None)
        if not current_user:
            return False
        
        dataloaders = get_dataloaders(info)
        application_loader = dataloaders.get_job_application_loader()
        application = await application_loader.load_user_application_for_job(
            current_user.id, 
            self.id
        )
        return application is not None


# Backward compatibility
JobType = Job
CompanyType = Company


@strawberry.type
class JobApplication:
    """Job application tracking type"""
    id: str
    userId: str
    jobId: str
    status: str = "applied"
    appliedDate: datetime
    lastUpdated: datetime
    coverLetter: Optional[str] = None
    notes: Optional[str] = None
    optimizedResumeData: Optional[str] = None
    aiSuggestions: Optional[str] = None
    skillsAnalysis: Optional[str] = None
    job: Optional[Job] = None


@strawberry.type
class SavedJob:
    """Saved job GraphQL type"""
    id: str
    userId: str
    jobId: str
    savedDate: datetime
    notes: Optional[str] = None
    job: Optional[Job] = None


@strawberry.input
class JobInput:
    """Input type for creating/updating jobs (user input)"""
    title: str
    companyName: str
    description: str
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    locationText: Optional[str] = None
    salaryMin: Optional[float] = None
    salaryMax: Optional[float] = None
    salaryCurrency: Optional[str] = "USD"
    salaryPeriod: Optional[str] = "yearly"
    jobType: Optional[str] = "full_time"
    contractType: Optional[str] = "permanent"
    experienceLevel: Optional[str] = None
    remoteType: Optional[str] = "on_site"


@strawberry.input
class JobApplicationInput:
    """Input type for job applications"""
    jobId: str
    coverLetter: Optional[str] = None
    notes: Optional[str] = None


@strawberry.input
class SavedJobInput:
    """Input type for saving jobs"""
    jobId: str
    notes: Optional[str] = None


@strawberry.type
class JobResponse:
    """Job operation response"""
    success: bool
    job: Optional[Job] = None
    errors: Optional[List[str]] = None


@strawberry.type
class JobApplicationResponse:
    """Job application operation response"""
    success: bool
    jobApplication: Optional[JobApplication] = None
    errors: Optional[List[str]] = None


@strawberry.type
class SavedJobResponse:
    """Saved job operation response"""
    success: bool
    savedJob: Optional[SavedJob] = None
    errors: Optional[List[str]] = None


@strawberry.input
class UpdateApplicationStatusInput:
    """Input for updating application status"""
    applicationId: str
    status: str
    notes: Optional[str] = None