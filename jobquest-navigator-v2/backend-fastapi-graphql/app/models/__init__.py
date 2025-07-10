"""
SQLAlchemy models for JobQuest Navigator v2
"""

from .base import Base, BaseModel
from .user import User, UserPreference, ActivityLog
from .job import (
    Company, Category, Skill, Job, JobSkill, 
    JobApplication, SavedJob, UserSkill
)

__all__ = [
    # Base
    "Base",
    "BaseModel",
    
    # User models
    "User",
    "UserPreference", 
    "ActivityLog",
    
    # Job models
    "Company",
    "Category", 
    "Skill",
    "Job",
    "JobSkill",
    "JobApplication",
    "SavedJob",
    "UserSkill",
]