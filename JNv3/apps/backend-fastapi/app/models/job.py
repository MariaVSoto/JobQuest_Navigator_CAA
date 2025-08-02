"""
Job related models for SQLAlchemy
Simplified version focusing on user input rather than external APIs
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Company(BaseModel):
    """
    Company model simplified without location complexity
    """
    __tablename__ = 'companies'
    __table_args__ = {'extend_existing': True}
    
    name = Column(String(200), nullable=False)
    slug = Column(String(220), unique=True, nullable=True)
    
    # Basic Information
    description = Column(Text, nullable=True)
    website = Column(String(200), nullable=True)
    logo_url = Column(String(500), nullable=True)
    
    # Company Details
    industry = Column(String(100), nullable=True)
    company_size = Column(String(20), nullable=True)  # startup, small, medium, large, enterprise
    founded_year = Column(Integer, nullable=True)
    
    # Contact Information
    email = Column(String(254), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Social Media & External IDs
    linkedin_url = Column(String(500), nullable=True)
    twitter_handle = Column(String(50), nullable=True)
    glassdoor_id = Column(String(50), nullable=True)
    
    # Ratings & Reviews (aggregated data)
    glassdoor_rating = Column(Numeric(3, 1), nullable=True)
    glassdoor_review_count = Column(Integer, default=0)
    
    # AI Research Data (JSON string)
    ai_research_data = Column(Text, nullable=True)
    ai_research_model = Column(String(50), nullable=True)
    ai_research_prompt_version = Column(String(50), nullable=True)
    ai_research_generated_at = Column(DateTime, nullable=True)
    ai_research_status = Column(String(10), default='NONE', index=True)  # PENDING, COMPLETED, FAILED, NONE
    
    def __repr__(self):
        return f"<Company(name='{self.name}')>"
    
    def has_ai_research(self) -> bool:
        """Check if company has completed AI research data."""
        return self.ai_research_status == 'COMPLETED' and self.ai_research_data is not None
    
    def needs_ai_research(self) -> bool:
        """Check if company needs AI research generation."""
        return self.ai_research_status in ['NONE', 'FAILED']


class Category(BaseModel):
    """Job category model for classification."""
    __tablename__ = 'categories'
    __table_args__ = {'extend_existing': True}
    
    name = Column(String(100), unique=True, nullable=False)
    
    def __repr__(self):
        return f"<Category(name='{self.name}')>"


class Skill(BaseModel):
    """Skill model for job requirements and user skills."""
    __tablename__ = 'skills'
    __table_args__ = {'extend_existing': True}
    
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(105), unique=True, nullable=False)
    category = Column(String(50), nullable=False)  # programming, framework, database, cloud, devops, design, management, communication, language, other
    description = Column(Text, nullable=True)
    
    # Skill metadata
    is_technical = Column(Boolean, default=True)
    popularity_score = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<Skill(name='{self.name}')>"


class Job(BaseModel):
    """
    Job model simplified for user input
    No external API dependencies
    """
    __tablename__ = 'jobs'
    __table_args__ = {'extend_existing': True}
    
    # Basic job information
    title = Column(String(200), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id'), nullable=True)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    
    # Location as simple string (no complex geo data)
    location_text = Column(String(200), nullable=True)  # e.g., "Remote", "New York, NY", "San Francisco, CA"
    
    # Salary information
    salary_min = Column(Numeric(10, 2), nullable=True)
    salary_max = Column(Numeric(10, 2), nullable=True)
    salary_currency = Column(String(3), default='USD')
    salary_period = Column(String(20), default='yearly')  # hourly, daily, weekly, monthly, yearly
    
    # Job details
    job_type = Column(String(50), default='full_time')  # full_time, part_time, contract, freelance, internship
    contract_type = Column(String(50), default='permanent')  # permanent, contract, temporary, apprenticeship, volunteer
    experience_level = Column(String(50), nullable=True)  # entry, junior, mid, senior, lead, manager
    remote_type = Column(String(50), default='on_site')  # on_site, remote, hybrid
    
    # User input flags
    user_input = Column(Boolean, default=True)  # True for user-created jobs
    external_id = Column(String(100), nullable=True)  # For future external API integration
    external_url = Column(String(500), nullable=True)
    source = Column(String(50), default='user_input')
    
    # Status and dates
    posted_date = Column(DateTime, default=datetime.utcnow)
    expires_date = Column(DateTime, nullable=True)
    
    # Relationships
    company = relationship("Company", backref="jobs")
    category = relationship("Category", backref="jobs")
    
    def __repr__(self):
        return f"<Job(title='{self.title}', company='{self.company.name if self.company else 'N/A'}')>"


class JobSkill(BaseModel):
    """Skills required for jobs."""
    __tablename__ = 'job_skills'
    __table_args__ = {'extend_existing': True}
    
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey('skills.id'), nullable=False)
    is_required = Column(Boolean, default=True)  # vs nice-to-have
    proficiency_level = Column(String(20), nullable=True)  # beginner, intermediate, advanced, expert
    
    # Relationships
    job = relationship("Job", backref="required_skills")
    skill = relationship("Skill", backref="job_requirements")
    
    def __repr__(self):
        return f"<JobSkill(job_id='{self.job_id}', skill_id='{self.skill_id}')>"


class JobApplication(BaseModel):
    """User job applications."""
    __tablename__ = 'job_applications'
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'), nullable=False)
    
    status = Column(String(50), default='applied')  # applied, screening, interview, offer, rejected, withdrawn
    applied_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Application tracking
    cover_letter = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # AI optimization data (JSON strings)
    optimized_resume_data = Column(Text, nullable=True)
    ai_suggestions = Column(Text, nullable=True)
    skills_analysis = Column(Text, nullable=True)
    
    # Relationships
    job = relationship("Job", backref="applications")
    
    def __repr__(self):
        return f"<JobApplication(user_id='{self.user_id}', job_id='{self.job_id}')>"


class SavedJob(BaseModel):
    """User saved jobs."""
    __tablename__ = 'saved_jobs'
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'), nullable=False)
    saved_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # Relationships
    job = relationship("Job", backref="saved_by")
    
    def __repr__(self):
        return f"<SavedJob(user_id='{self.user_id}', job_id='{self.job_id}')>"


class UserSkill(BaseModel):
    """User's skills and proficiency."""
    __tablename__ = 'user_skills'
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    skill_id = Column(UUID(as_uuid=True), ForeignKey('skills.id'), nullable=False)
    proficiency_level = Column(String(20), nullable=False)  # beginner, intermediate, advanced, expert
    years_experience = Column(Integer, nullable=True)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    skill = relationship("Skill", backref="user_skills")
    
    def __repr__(self):
        return f"<UserSkill(user_id='{self.user_id}', skill='{self.skill.name if self.skill else 'N/A'}')>"