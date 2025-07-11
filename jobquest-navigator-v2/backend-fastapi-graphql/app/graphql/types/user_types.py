"""
User related GraphQL types
Strawberry type definitions maintaining compatibility with original Graphene schema
"""

import strawberry
from typing import Optional, List
from datetime import datetime, date


@strawberry.type
class UserType:
    """
    User GraphQL type maintaining compatibility with Django User model
    """
    id: str
    email: str
    username: str
    
    # Profile information
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    bio: Optional[str] = None
    current_job_title: Optional[str] = None
    years_of_experience: Optional[int] = None
    industry: Optional[str] = None
    career_level: Optional[str] = None
    job_search_status: str = "not_looking"
    preferred_work_type: Optional[str] = None
    
    # Timestamps
    date_joined: datetime
    last_login: Optional[datetime] = None
    
    # Salary expectations
    salary_expectation_min: Optional[float] = None
    salary_expectation_max: Optional[float] = None


@strawberry.input
class UserUpdateInput:
    """Input type for updating user profile"""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    current_job_title: Optional[str] = None
    years_of_experience: Optional[int] = None
    industry: Optional[str] = None
    career_level: Optional[str] = None
    job_search_status: Optional[str] = None
    preferred_work_type: Optional[str] = None
    salary_expectation_min: Optional[float] = None
    salary_expectation_max: Optional[float] = None


@strawberry.input
class UserRegistrationInput:
    """Input type for user registration"""
    email: str
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@strawberry.type
class AuthPayload:
    """Authentication response payload"""
    success: bool
    user: Optional[UserType] = None
    token: Optional[str] = None
    errors: Optional[List[str]] = None


@strawberry.type
class UserResponse:
    """Standard user operation response"""
    success: bool
    user: Optional[UserType] = None
    errors: Optional[List[str]] = None


@strawberry.input
class RegisterUserInput:
    """Input type for user registration via Cognito"""
    email: str
    password: str
    full_name: Optional[str] = None


@strawberry.input
class UpdateUserProfileInput:
    """Input type for updating user profile"""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    current_job_title: Optional[str] = None
    years_of_experience: Optional[int] = None
    industry: Optional[str] = None
    career_level: Optional[str] = None
    job_search_status: Optional[str] = None
    preferred_work_type: Optional[str] = None
    salary_expectation_min: Optional[float] = None
    salary_expectation_max: Optional[float] = None