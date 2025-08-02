"""
User related GraphQL types
Strawberry type definitions maintaining compatibility with original Graphene schema
"""

import strawberry
from typing import Optional, List
from datetime import datetime, date


@strawberry.type
class User:
    """
    User GraphQL type - simplified and consistent naming
    """
    id: str
    email: str
    username: str
    
    # Profile information
    fullName: Optional[str] = None
    bio: Optional[str] = None
    currentJobTitle: Optional[str] = None
    yearsOfExperience: Optional[int] = None
    industry: Optional[str] = None
    careerLevel: Optional[str] = None
    jobSearchStatus: Optional[str] = None
    preferredWorkType: Optional[str] = None
    
    # Timestamps
    dateJoined: Optional[datetime] = None
    lastLogin: Optional[datetime] = None
    
    # Salary expectations
    salaryExpectationMin: Optional[float] = None
    salaryExpectationMax: Optional[float] = None


# Backward compatibility alias
UserType = User


@strawberry.input
class UserUpdateInput:
    """Input type for updating user profile"""
    fullName: Optional[str] = None
    bio: Optional[str] = None
    currentJobTitle: Optional[str] = None
    yearsOfExperience: Optional[int] = None
    industry: Optional[str] = None
    careerLevel: Optional[str] = None
    jobSearchStatus: Optional[str] = None
    preferredWorkType: Optional[str] = None
    salaryExpectationMin: Optional[float] = None
    salaryExpectationMax: Optional[float] = None


@strawberry.input
class UserRegistrationInput:
    """Input type for user registration"""
    email: str
    username: str
    password: str
    fullName: Optional[str] = None


@strawberry.type
class UserResponse:
    """Standard user operation response"""
    success: bool
    user: Optional[User] = None
    errors: Optional[List[str]] = None


@strawberry.input
class LoginInput:
    """Input type for user login"""
    email: str
    password: str


@strawberry.type
class AuthResponse:
    """Authentication response payload"""
    success: bool
    user: Optional[User] = None
    token: Optional[str] = None
    message: Optional[str] = None
    errors: Optional[List[str]] = None