"""
GraphQL types for Strawberry Schema
Converted from Django Graphene types
"""

import strawberry
from typing import List, Optional, Union
from datetime import datetime, date
from decimal import Decimal

# User related types

@strawberry.type
class UserType:
    """GraphQL type for User model."""
    id: strawberry.ID
    email: str
    username: str
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    bio: Optional[str] = None
    current_job_title: Optional[str] = None
    years_of_experience: Optional[int] = None
    industry: Optional[str] = None
    career_level: Optional[str] = None
    job_search_status: str = "not_looking"
    salary_expectation_min: Optional[Decimal] = None
    salary_expectation_max: Optional[Decimal] = None
    preferred_work_type: Optional[str] = None
    date_joined: datetime
    last_login: Optional[datetime] = None


@strawberry.type
class UserPreferenceType:
    """GraphQL type for UserPreference model."""
    user_id: strawberry.ID
    job_alert_frequency: str = "weekly"
    auto_save_resume: bool = True
    resume_privacy_level: str = "private"
    enable_ai_suggestions: bool = True
    ai_suggestion_frequency: str = "daily"
    email_notifications: bool = True
    push_notifications: bool = True
    sms_notifications: bool = False
    profile_visibility: str = "private"
    theme: str = "auto"
    language: str = "en"
    timezone: str = "UTC"


@strawberry.type
class ActivityLogType:
    """GraphQL type for ActivityLog model."""
    id: strawberry.ID
    user_id: strawberry.ID
    action: str
    description: Optional[str] = None
    epic: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[str] = None
    created_at: datetime


# Company and Job related types

@strawberry.type
class CompanyType:
    """GraphQL type for Company model."""
    id: strawberry.ID
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    founded_year: Optional[int] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_handle: Optional[str] = None
    glassdoor_id: Optional[str] = None
    glassdoor_rating: Optional[Decimal] = None
    glassdoor_review_count: int = 0
    ai_research_data: Optional[str] = None
    ai_research_model: Optional[str] = None
    ai_research_status: str = "NONE"
    ai_research_generated_at: Optional[datetime] = None
    created_at: datetime


@strawberry.type
class CategoryType:
    """GraphQL type for Category model."""
    id: strawberry.ID
    name: str
    created_at: datetime


@strawberry.type
class SkillType:
    """GraphQL type for Skill model."""
    id: strawberry.ID
    name: str
    slug: str
    category: str
    description: Optional[str] = None
    is_technical: bool = True
    popularity_score: int = 0
    created_at: datetime


@strawberry.type
class JobSkillType:
    """GraphQL type for JobSkill model."""
    job_id: strawberry.ID
    skill_id: strawberry.ID
    skill: SkillType
    is_required: bool = True
    proficiency_level: Optional[str] = None


@strawberry.type
class JobType:
    """GraphQL type for Job model."""
    id: strawberry.ID
    title: str
    company_id: strawberry.ID
    category_id: Optional[strawberry.ID] = None
    company: CompanyType
    category: Optional[CategoryType] = None
    description: str
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    location_text: Optional[str] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    salary_currency: str = "USD"
    salary_period: str = "yearly"
    job_type: str = "full_time"
    contract_type: str = "permanent"
    experience_level: Optional[str] = None
    remote_type: str = "on_site"
    user_input: bool = True
    external_id: Optional[str] = None
    external_url: Optional[str] = None
    source: str = "user_input"
    posted_date: datetime
    expires_date: Optional[datetime] = None
    created_at: datetime
    
    # User-specific fields (to be resolved dynamically)
    required_skills: List[JobSkillType]
    is_saved: bool = False
    is_applied: bool = False


@strawberry.type
class JobApplicationType:
    """GraphQL type for JobApplication model."""
    id: strawberry.ID
    user_id: strawberry.ID
    job_id: strawberry.ID
    job: JobType
    status: str = "applied"
    applied_date: datetime
    last_updated: datetime
    cover_letter: Optional[str] = None
    notes: Optional[str] = None
    optimized_resume_data: Optional[str] = None
    ai_suggestions: Optional[str] = None
    skills_analysis: Optional[str] = None
    created_at: datetime


@strawberry.type
class SavedJobType:
    """GraphQL type for SavedJob model."""
    id: strawberry.ID
    user_id: strawberry.ID
    job_id: strawberry.ID
    job: JobType
    saved_date: datetime
    notes: Optional[str] = None
    created_at: datetime


@strawberry.type
class UserSkillType:
    """GraphQL type for UserSkill model."""
    id: strawberry.ID
    user_id: strawberry.ID
    skill_id: strawberry.ID
    skill: SkillType
    proficiency_level: str
    years_experience: Optional[int] = None
    is_verified: bool = False
    created_at: datetime


# Response types for mutations

@strawberry.type
class UserResponse:
    """Response type for user mutations."""
    user: Optional[UserType] = None
    success: bool
    errors: List[str]


@strawberry.type
class JobApplicationResponse:
    """Response type for job application mutations."""
    application: Optional[JobApplicationType] = None
    success: bool
    errors: List[str]


@strawberry.type
class SavedJobResponse:
    """Response type for saved job mutations."""
    saved_job: Optional[SavedJobType] = None
    success: bool
    errors: List[str]


@strawberry.type
class GeneralResponse:
    """General response type for simple mutations."""
    success: bool
    message: Optional[str] = None
    errors: List[str]


# Input types for mutations

@strawberry.input
class RegisterUserInput:
    """Input type for user registration."""
    email: str
    username: str
    password: str
    full_name: Optional[str] = None


@strawberry.input
class UpdateUserProfileInput:
    """Input type for updating user profile."""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    current_job_title: Optional[str] = None
    years_of_experience: Optional[int] = None
    industry: Optional[str] = None
    career_level: Optional[str] = None
    job_search_status: Optional[str] = None
    preferred_work_type: Optional[str] = None


@strawberry.input
class ApplyToJobInput:
    """Input type for job application."""
    job_id: strawberry.ID
    cover_letter: Optional[str] = None
    notes: Optional[str] = None


@strawberry.input
class UpdateApplicationStatusInput:
    """Input type for updating application status."""
    application_id: strawberry.ID
    status: str
    notes: Optional[str] = None