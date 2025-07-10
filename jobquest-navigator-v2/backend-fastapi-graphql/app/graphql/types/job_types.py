"""
Job related GraphQL types
Strawberry type definitions for simplified job management (user input based)
"""

import strawberry
from typing import Optional, List
from datetime import datetime


@strawberry.type
class CompanyType:
    """
    Company GraphQL type - simplified version without location complexity
    """
    id: str
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    
    # AI research data
    ai_research_status: str = "NONE"
    ai_research_data: Optional[str] = None  # JSON string
    ai_research_generated_at: Optional[datetime] = None


@strawberry.type
class JobType:
    """
    Job GraphQL type - simplified for user input model
    """
    id: str
    title: str
    company: CompanyType
    description: str
    requirements: Optional[str] = None
    
    # Salary information
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "USD"
    
    # Job details
    job_type: str = "full_time"
    experience_level: Optional[str] = None
    remote_type: str = "on_site"
    
    # User input fields
    user_input: bool = True
    created_at: datetime
    updated_at: datetime


@strawberry.type
class SkillType:
    """Skill GraphQL type"""
    id: str
    name: str
    category: str
    description: Optional[str] = None
    is_technical: bool = True


@strawberry.type
class JobApplicationType:
    """Job application tracking type"""
    id: str
    job: JobType
    status: str = "applied"
    applied_date: datetime
    notes: Optional[str] = None
    
    # Resume optimization data
    optimized_resume_data: Optional[str] = None  # JSON string
    ai_suggestions: Optional[str] = None  # JSON string


@strawberry.input
class JobInput:
    """Input type for creating/updating jobs (user input)"""
    title: str
    company_name: str
    description: str
    requirements: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_type: Optional[str] = "full_time"
    experience_level: Optional[str] = None
    remote_type: Optional[str] = "on_site"


@strawberry.input
class JobApplicationInput:
    """Input type for job applications"""
    job_id: str
    notes: Optional[str] = None