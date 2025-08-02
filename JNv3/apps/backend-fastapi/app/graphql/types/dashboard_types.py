"""
Dashboard-related GraphQL types for JobQuest Navigator v2
"""

import strawberry
from typing import Optional, Dict, Any
from datetime import datetime
from .job_types import JobApplication


@strawberry.type
class DashboardStats:
    """
    Dashboard statistics aggregation
    """
    total_applications: int = strawberry.field(description="Total number of job applications submitted")
    interviews_scheduled: int = strawberry.field(description="Number of interviews scheduled or completed")
    saved_jobs: int = strawberry.field(description="Number of jobs saved by the user")
    profile_views: int = strawberry.field(description="Number of profile views (placeholder for future implementation)")
    
    # Additional useful statistics
    applications_this_month: Optional[int] = strawberry.field(description="Applications submitted this month")
    response_rate: Optional[float] = strawberry.field(description="Response rate percentage for applications")
    active_applications: Optional[int] = strawberry.field(description="Applications with pending/interview status")


@strawberry.type
class DashboardActivity:
    """
    Recent activity item for dashboard
    """
    id: str = strawberry.field(description="Activity ID")
    type: str = strawberry.field(description="Activity type: application, save, view, interview")
    content: str = strawberry.field(description="Activity description")
    timestamp: datetime = strawberry.field(description="When the activity occurred")
    related_job_id: Optional[str] = strawberry.field(description="Related job ID if applicable")
    related_job_title: Optional[str] = strawberry.field(description="Related job title if applicable")
    related_company_name: Optional[str] = strawberry.field(description="Related company name if applicable")


@strawberry.type
class DashboardData:
    """
    Complete dashboard data response
    """
    stats: DashboardStats = strawberry.field(description="Dashboard statistics")
    recent_activities: list[DashboardActivity] = strawberry.field(description="Recent user activities")
    recent_applications: list[JobApplication] = strawberry.field(description="Recent job applications")


@strawberry.type
class ApplicationStatusStats:
    """
    Statistics grouped by application status
    """
    pending: int = strawberry.field(description="Number of pending applications")
    applied: int = strawberry.field(description="Number of applied applications")
    interview: int = strawberry.field(description="Number of applications in interview stage")
    offer: int = strawberry.field(description="Number of applications with offers")
    rejected: int = strawberry.field(description="Number of rejected applications")
    withdrawn: int = strawberry.field(description="Number of withdrawn applications")


@strawberry.input
class DashboardFilters:
    """
    Optional filters for dashboard data
    """
    date_range_days: Optional[int] = strawberry.field(
        default=30, 
        description="Number of days to look back for statistics"
    )
    include_activities: Optional[bool] = strawberry.field(
        default=True, 
        description="Whether to include recent activities"
    )
    activity_limit: Optional[int] = strawberry.field(
        default=10, 
        description="Maximum number of activities to return"
    )