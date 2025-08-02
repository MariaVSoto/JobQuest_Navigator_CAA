"""
Common GraphQL types shared across modules
Strawberry type definitions for common responses and structures
"""

import strawberry
from typing import Optional, List
from datetime import datetime


@strawberry.type
class SecureAuthResponse:
    """Response for secure authentication operations"""
    success: bool
    user: Optional["User"] = None  # Forward reference
    message: Optional[str] = None
    errors: Optional[List[str]] = None


@strawberry.type
class SessionValidationResponse:
    """Response for session validation"""
    valid: bool
    user: Optional["User"] = None  # Forward reference
    message: Optional[str] = None


@strawberry.type
class Company:
    """Company information type"""
    id: str
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    logoUrl: Optional[str] = None
    industry: Optional[str] = None
    companySize: Optional[str] = None
    foundedYear: Optional[int] = None


@strawberry.input
class CompanyInput:
    """Input type for company creation/update"""
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    logoUrl: Optional[str] = None
    industry: Optional[str] = None
    companySize: Optional[str] = None
    foundedYear: Optional[int] = None


@strawberry.type
class StandardResponse:
    """Standard response type for mutations"""
    success: bool
    message: Optional[str] = None
    errors: Optional[List[str]] = None


@strawberry.type
class PaginationInfo:
    """Pagination information for list queries"""
    hasNextPage: bool
    hasPreviousPage: bool
    totalCount: int
    currentPage: int
    pageSize: int