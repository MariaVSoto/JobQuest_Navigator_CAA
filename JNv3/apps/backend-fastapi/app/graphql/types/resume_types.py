"""
GraphQL types for Resume operations
"""

import strawberry
from typing import List, Optional, Any
from datetime import datetime


@strawberry.type
class PersonalInfoType:
    """Personal information in resume"""
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None


@strawberry.type
class ExperienceType:
    """Work experience entry"""
    company: str
    position: str
    start_date: str
    end_date: Optional[str] = None
    current: bool = False
    description: Optional[str] = None


@strawberry.type
class EducationType:
    """Education entry"""
    school: str
    degree: str
    field: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    current: bool = False
    gpa: Optional[str] = None


@strawberry.type
class ProjectType:
    """Project entry"""
    name: str
    description: Optional[str] = None
    technologies: Optional[str] = None
    link: Optional[str] = None


@strawberry.type
class ResumeFileInfoType:
    """File information for uploaded resumes"""
    original_filename: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    file_size_display: Optional[str] = None
    download_url: Optional[str] = None


@strawberry.type
class ResumeProcessingLogType:
    """Resume processing log entry"""
    id: str
    operation: str
    status: str
    message: Optional[str] = None
    processing_time: Optional[float] = None
    created_at: datetime


@strawberry.type
class ResumeType:
    """Complete resume type"""
    id: str
    title: str
    user_id: str
    
    # Content sections
    personal_info: Optional[PersonalInfoType] = None
    summary: Optional[str] = None
    experience: Optional[List[ExperienceType]] = None
    education: Optional[List[EducationType]] = None
    skills: Optional[List[str]] = None
    projects: Optional[List[ProjectType]] = None
    
    # Targeting
    target_role: Optional[str] = None
    target_industry: Optional[str] = None
    keywords: Optional[List[str]] = None
    
    # File information
    file_info: Optional[ResumeFileInfoType] = None
    
    # Processing status
    source_type: str = "manual"
    processing_status: str = "completed"
    processing_error: Optional[str] = None
    status_display: str
    
    # Metadata
    version: int = 1
    is_default: bool = False
    is_public: bool = False
    view_count: int = 0
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Processing logs
    processing_logs: Optional[List[ResumeProcessingLogType]] = None


@strawberry.type
class ResumeListType:
    """Resume list with metadata"""
    id: str
    title: str
    user_id: str
    personal_info: Optional[PersonalInfoType] = None
    target_role: Optional[str] = None
    target_industry: Optional[str] = None
    source_type: str = "manual"
    processing_status: str = "completed"
    status_display: str
    is_default: bool = False
    view_count: int = 0
    created_at: datetime
    updated_at: datetime


# Input types for mutations
@strawberry.input
class PersonalInfoInput:
    """Personal information input"""
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None


@strawberry.input
class ExperienceInput:
    """Work experience input"""
    company: str
    position: str
    start_date: str
    end_date: Optional[str] = None
    current: bool = False
    description: Optional[str] = None


@strawberry.input
class EducationInput:
    """Education input"""
    school: str
    degree: str
    field: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    current: bool = False
    gpa: Optional[str] = None


@strawberry.input
class ProjectInput:
    """Project input"""
    name: str
    description: Optional[str] = None
    technologies: Optional[str] = None
    link: Optional[str] = None


@strawberry.input
class CreateResumeInput:
    """Input for creating/updating resume"""
    title: str
    personal_info: Optional[PersonalInfoInput] = None
    summary: Optional[str] = None
    experience: Optional[List[ExperienceInput]] = None
    education: Optional[List[EducationInput]] = None
    skills: Optional[List[str]] = None
    projects: Optional[List[ProjectInput]] = None
    target_role: Optional[str] = None
    target_industry: Optional[str] = None
    keywords: Optional[List[str]] = None


@strawberry.input
class UploadResumeFileInput:
    """Input for PDF upload"""
    title: str
    file_data: str  # Base64 encoded file data
    filename: str
    content_type: Optional[str] = None


# Response types
@strawberry.type
class ResumeResponse:
    """Standard response for resume operations"""
    success: bool
    message: Optional[str] = None
    errors: Optional[List[str]] = None
    resume_id: Optional[str] = None
    resume: Optional[ResumeType] = None


@strawberry.type
class ResumeListResponse:
    """Response for resume list queries"""
    success: bool
    message: Optional[str] = None
    resumes: Optional[List[ResumeListType]] = None
    total_count: int = 0


@strawberry.type
class FileUploadResponse:
    """Response for file upload operations"""
    success: bool
    message: Optional[str] = None
    errors: Optional[List[str]] = None
    resume_id: Optional[str] = None
    processing_status: Optional[str] = None
    download_url: Optional[str] = None


@strawberry.type
class ProcessPDFResponse:
    """Response for PDF processing operations"""
    success: bool
    message: Optional[str] = None
    errors: Optional[List[str]] = None
    # extracted_data: Optional[ResumeType] = None  # Temporarily disabled
    processing_time: Optional[float] = None