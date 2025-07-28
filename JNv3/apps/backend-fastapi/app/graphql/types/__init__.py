"""
GraphQL types module - centralized exports for all GraphQL types
"""

# Common types
from .common_types import (
    Company,
    CompanyInput,
    SecureAuthResponse,
    SessionValidationResponse,
    StandardResponse,
    PaginationInfo
)

# User types
from .user_types import (
    User,
    UserType,  # Backward compatibility
    UserUpdateInput,
    UserRegistrationInput,
    UserResponse,
    LoginInput,
    AuthResponse
)

# Job types
from .job_types import (
    Job,
    JobType,  # Backward compatibility
    CompanyType,  # Backward compatibility
    JobApplication,
    SavedJob,
    JobInput,
    JobApplicationInput,
    SavedJobInput,
    JobResponse,
    JobApplicationResponse,
    SavedJobResponse,
    UpdateApplicationStatusInput
)

# Dashboard types
from .dashboard_types import (
    DashboardStats,
    DashboardActivity,
    DashboardData,
    ApplicationStatusStats,
    DashboardFilters
)

# Resume types
from .resume_types import (
    ResumeType,
    ResumeListType,
    PersonalInfoType,
    ExperienceType,
    EducationType,
    ProjectType,
    ResumeFileInfoType,
    PersonalInfoInput,
    ExperienceInput,
    EducationInput,
    ProjectInput,
    CreateResumeInput,
    UploadResumeFileInput,
    ResumeResponse,
    ResumeListResponse,
    FileUploadResponse,
    ProcessPDFResponse
)

__all__ = [
    # Common types
    "Company",
    "CompanyInput", 
    "SecureAuthResponse",
    "SessionValidationResponse",
    "StandardResponse",
    "PaginationInfo",
    
    # User types
    "User",
    "UserType",
    "UserUpdateInput",
    "UserRegistrationInput",
    "UserResponse",
    "LoginInput",
    "AuthResponse",
    
    # Job types
    "Job",
    "JobType",
    "CompanyType",
    "JobApplication",
    "SavedJob",
    "JobInput",
    "JobApplicationInput",
    "SavedJobInput",
    "JobResponse",
    "JobApplicationResponse",
    "SavedJobResponse",
    "UpdateApplicationStatusInput",
    
    # Dashboard types
    "DashboardStats",
    "DashboardActivity", 
    "DashboardData",
    "ApplicationStatusStats",
    "DashboardFilters",
    
    # Resume types
    "ResumeType",
    "ResumeListType",
    "PersonalInfoType",
    "ExperienceType",
    "EducationType",
    "ProjectType",
    "ResumeFileInfoType",
    "PersonalInfoInput",
    "ExperienceInput",
    "EducationInput",
    "ProjectInput",
    "CreateResumeInput",
    "UploadResumeFileInput",
    "ResumeResponse",
    "ResumeListResponse",
    "FileUploadResponse",
    "ProcessPDFResponse"
]