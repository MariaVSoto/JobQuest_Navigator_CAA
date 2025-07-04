import uuid
from typing import Optional, List
from datetime import datetime
from enum import Enum

from fastapi_users import schemas
from pydantic import BaseModel, EmailStr


class UserRead(schemas.BaseUser[uuid.UUID]):
    """User read schema - returned when fetching user data"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    current_job_title: Optional[str] = None
    years_of_experience: Optional[int] = 0
    industry: Optional[str] = None
    career_level: Optional[str] = None
    job_search_status: Optional[str] = None
    preferred_work_type: Optional[str] = None
    preferred_location: Optional[str] = None
    desired_salary_min: Optional[int] = None
    desired_salary_max: Optional[int] = None
    salary_currency: Optional[str] = "USD"
    skills: Optional[str] = None
    interests: Optional[str] = None
    profile_visibility: Optional[str] = "private"
    email_notifications: Optional[bool] = True
    job_alerts: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class UserCreate(schemas.BaseUserCreate):
    """User creation schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    current_job_title: Optional[str] = None
    years_of_experience: Optional[int] = 0
    industry: Optional[str] = None
    career_level: Optional[str] = None
    job_search_status: Optional[str] = None
    preferred_work_type: Optional[str] = None
    preferred_location: Optional[str] = None
    desired_salary_min: Optional[int] = None
    desired_salary_max: Optional[int] = None
    salary_currency: Optional[str] = "USD"
    skills: Optional[str] = None
    interests: Optional[str] = None
    profile_visibility: Optional[str] = "private"
    email_notifications: Optional[bool] = True
    job_alerts: Optional[bool] = True


class UserUpdate(schemas.BaseUserUpdate):
    """User update schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    current_job_title: Optional[str] = None
    years_of_experience: Optional[int] = None
    industry: Optional[str] = None
    career_level: Optional[str] = None
    job_search_status: Optional[str] = None
    preferred_work_type: Optional[str] = None
    preferred_location: Optional[str] = None
    desired_salary_min: Optional[int] = None
    desired_salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    skills: Optional[str] = None
    interests: Optional[str] = None
    profile_visibility: Optional[str] = None
    email_notifications: Optional[bool] = None
    job_alerts: Optional[bool] = None


# Additional schemas for extended functionality
class UserProfileUpdate(BaseModel):
    """Separate schema for profile updates"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    current_job_title: Optional[str] = None
    years_of_experience: Optional[int] = None
    industry: Optional[str] = None


class UserCareerPreferences(BaseModel):
    """Schema for career preferences"""
    career_level: Optional[str] = None
    job_search_status: Optional[str] = None
    preferred_work_type: Optional[str] = None
    preferred_location: Optional[str] = None
    desired_salary_min: Optional[int] = None
    desired_salary_max: Optional[int] = None
    salary_currency: Optional[str] = None


class UserNotificationSettings(BaseModel):
    """Schema for notification settings"""
    email_notifications: Optional[bool] = None
    job_alerts: Optional[bool] = None
    profile_visibility: Optional[str] = None


class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class UserStats(BaseModel):
    """User statistics schema"""
    total_applications: int = 0
    saved_jobs: int = 0
    profile_views: int = 0
    last_activity: Optional[datetime] = None


# Account Management Schemas
class AccountStatus(str, Enum):
    """Account status enumeration"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    LOCKED = "locked"
    PENDING_VERIFICATION = "pending_verification"
    DELETED = "deleted"


class SuspensionReason(str, Enum):
    """Suspension reason enumeration"""
    SPAM = "spam"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    HARASSMENT = "harassment"
    FAKE_PROFILE = "fake_profile"
    TERMS_VIOLATION = "terms_violation"
    SECURITY_CONCERN = "security_concern"
    OTHER = "other"


class AccountManagementAction(BaseModel):
    """Schema for account management actions"""
    user_id: uuid.UUID
    action: str  # suspend, activate, lock, unlock, delete
    reason: Optional[str] = None
    duration_hours: Optional[int] = None  # For temporary suspensions
    admin_notes: Optional[str] = None


class AccountSuspension(BaseModel):
    """Schema for account suspension details"""
    user_id: uuid.UUID
    reason: SuspensionReason
    description: Optional[str] = None
    suspended_until: Optional[datetime] = None
    is_permanent: bool = False
    admin_id: uuid.UUID
    admin_notes: Optional[str] = None


class LoginAttempt(BaseModel):
    """Schema for login attempt tracking"""
    user_email: str
    ip_address: str
    user_agent: str
    success: bool
    attempted_at: datetime
    failure_reason: Optional[str] = None


class UserAccountStatus(BaseModel):
    """Schema for user account status response"""
    user_id: uuid.UUID
    email: str
    status: AccountStatus
    is_verified: bool
    is_locked: bool
    lock_expires_at: Optional[datetime] = None
    is_suspended: bool
    suspended_until: Optional[datetime] = None
    suspension_reason: Optional[str] = None
    failed_login_attempts: int = 0
    last_login: Optional[datetime] = None
    created_at: datetime


class AdminUserList(BaseModel):
    """Schema for admin user list view"""
    users: List[UserAccountStatus]
    total_count: int
    page: int
    per_page: int
    total_pages: int


class EmailNotification(BaseModel):
    """Schema for email notification requests"""
    to_email: str
    to_name: Optional[str] = None
    template: str
    context: dict
    priority: str = "normal"  # low, normal, high


class BulkEmailRequest(BaseModel):
    """Schema for bulk email requests"""
    user_ids: List[uuid.UUID]
    template: str
    context: dict
    send_immediately: bool = False