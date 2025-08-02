"""
User models for SQLAlchemy
Simplified version without Location dependencies
"""

import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    """
    Custom User model based on Django User
    Simplified version without Location relationships
    """
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    # Authentication fields
    email = Column(String(254), unique=True, nullable=False, index=True)
    username = Column(String(150), unique=True, nullable=False)
    
    # Profile Information
    full_name = Column(String(255), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    bio = Column(Text, nullable=True)
    
    # Career Information
    current_job_title = Column(String(200), nullable=True)
    years_of_experience = Column(Integer, nullable=True)
    industry = Column(String(100), nullable=True)
    career_level = Column(String(20), nullable=True)  # entry, junior, mid, senior, lead, manager, director, executive
    
    # Job Search Preferences
    job_search_status = Column(String(20), default='not_looking')  # not_looking, casually_looking, actively_looking, open_to_offers
    salary_expectation_min = Column(Numeric(10, 2), nullable=True)
    salary_expectation_max = Column(Numeric(10, 2), nullable=True)
    preferred_work_type = Column(String(20), nullable=True)  # remote, hybrid, onsite, flexible
    
    # Timestamps
    date_joined = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    last_login_ip = Column(String(45), nullable=True)  # Support IPv6
    
    # AWS Cognito integration
    cognito_sub = Column(String(255), unique=True, nullable=True, index=True)  # Cognito user ID
    
    def __repr__(self):
        return f"<User(email='{self.email}', username='{self.username}')>"
    
    @property
    def display_name(self):
        return self.full_name or self.username


class UserPreference(BaseModel):
    """
    User preferences for personalization
    Simplified version without location preferences
    """
    __tablename__ = 'user_preferences'
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Job Search Preferences
    job_alert_frequency = Column(String(20), default='weekly')  # never, daily, weekly, monthly
    
    # Resume Preferences
    auto_save_resume = Column(Boolean, default=True)
    resume_privacy_level = Column(String(20), default='private')  # private, public, recruiters_only
    
    # AI Suggestions Preferences
    enable_ai_suggestions = Column(Boolean, default=True)
    ai_suggestion_frequency = Column(String(20), default='daily')  # real_time, daily, weekly
    
    # Notification Preferences
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    
    # Privacy Settings
    profile_visibility = Column(String(20), default='private')  # private, public, connections_only
    
    # Theme and UI Preferences
    theme = Column(String(10), default='auto')  # light, dark, auto
    language = Column(String(10), default='en')
    timezone = Column(String(50), default='UTC')
    
    def __repr__(self):
        return f"<UserPreference(user_id='{self.user_id}')>"


class ActivityLog(BaseModel):
    """
    Activity log for tracking user actions
    """
    __tablename__ = 'activity_logs'
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Context information
    epic = Column(String(20), nullable=False)  # core, jobs, resumes, ai_suggestions, skills, certifications, company_research
    
    # Technical details
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Additional context data (JSON)
    context_data = Column(Text, nullable=True)  # JSON string
    
    def __repr__(self):
        return f"<ActivityLog(user_id='{self.user_id}', action='{self.action}')>"