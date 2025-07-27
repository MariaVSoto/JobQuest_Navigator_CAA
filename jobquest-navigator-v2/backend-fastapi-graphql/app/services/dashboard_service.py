"""
Dashboard service for calculating user statistics and recent activities
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.user import User, ActivityLog
from app.models.job import Job, JobApplication, SavedJob, Company
from app.graphql.types.dashboard_types import (
    DashboardStats, DashboardActivity, DashboardData, ApplicationStatusStats
)


class DashboardService:
    """
    Service for dashboard-related operations
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_dashboard_data(
        self, 
        user_id: str, 
        date_range_days: int = 30,
        include_activities: bool = True,
        activity_limit: int = 10
    ) -> DashboardData:
        """
        Get complete dashboard data for a user
        """
        try:
            # Calculate statistics
            stats = await self.get_dashboard_stats(user_id, date_range_days)
            
            # Get recent activities
            activities = []
            if include_activities:
                activities = await self.get_recent_activities(user_id, activity_limit)
            
            # Get recent applications
            recent_applications = await self.get_recent_applications(user_id, limit=5)
            
            return DashboardData(
                stats=stats,
                recent_activities=activities,
                recent_applications=recent_applications
            )
        except Exception as e:
            print(f"Error getting dashboard data: {e}")
            # Return default/empty data on error
            return DashboardData(
                stats=DashboardStats(
                    total_applications=0,
                    interviews_scheduled=0,
                    saved_jobs=0,
                    profile_views=0
                ),
                recent_activities=[],
                recent_applications=[]
            )

    async def get_dashboard_stats(self, user_id: str, date_range_days: int = 30) -> DashboardStats:
        """
        Calculate dashboard statistics for a user
        """
        try:
            # Date range for recent statistics
            cutoff_date = datetime.utcnow() - timedelta(days=date_range_days)
            
            # Total applications
            total_applications_query = select(func.count(JobApplication.id)).where(
                JobApplication.user_id == user_id
            )
            total_applications_result = await self.db_session.execute(total_applications_query)
            total_applications = total_applications_result.scalar() or 0
            
            # Applications this month
            applications_this_month_query = select(func.count(JobApplication.id)).where(
                and_(
                    JobApplication.user_id == user_id,
                    JobApplication.applied_date >= cutoff_date
                )
            )
            applications_this_month_result = await self.db_session.execute(applications_this_month_query)
            applications_this_month = applications_this_month_result.scalar() or 0
            
            # Interviews scheduled (applications with interview or offer status)
            interviews_query = select(func.count(JobApplication.id)).where(
                and_(
                    JobApplication.user_id == user_id,
                    or_(
                        JobApplication.status == 'interview',
                        JobApplication.status == 'offer',
                        JobApplication.status == 'final_interview'
                    )
                )
            )
            interviews_result = await self.db_session.execute(interviews_query)
            interviews_scheduled = interviews_result.scalar() or 0
            
            # Saved jobs count
            saved_jobs_query = select(func.count(SavedJob.id)).where(
                SavedJob.user_id == user_id
            )
            saved_jobs_result = await self.db_session.execute(saved_jobs_query)
            saved_jobs = saved_jobs_result.scalar() or 0
            
            # Active applications (pending, applied, interview status)
            active_applications_query = select(func.count(JobApplication.id)).where(
                and_(
                    JobApplication.user_id == user_id,
                    or_(
                        JobApplication.status == 'pending',
                        JobApplication.status == 'applied',
                        JobApplication.status == 'interview',
                        JobApplication.status == 'final_interview'
                    )
                )
            )
            active_applications_result = await self.db_session.execute(active_applications_query)
            active_applications = active_applications_result.scalar() or 0
            
            # Calculate response rate
            responded_applications_query = select(func.count(JobApplication.id)).where(
                and_(
                    JobApplication.user_id == user_id,
                    or_(
                        JobApplication.status == 'interview',
                        JobApplication.status == 'offer',
                        JobApplication.status == 'rejected'
                    )
                )
            )
            responded_applications_result = await self.db_session.execute(responded_applications_query)
            responded_applications = responded_applications_result.scalar() or 0
            
            response_rate = 0.0
            if total_applications > 0:
                response_rate = (responded_applications / total_applications) * 100
            
            # Profile views (placeholder - would be implemented with actual tracking)
            profile_views = 47  # Mock data for now
            
            return DashboardStats(
                total_applications=total_applications,
                interviews_scheduled=interviews_scheduled,
                saved_jobs=saved_jobs,
                profile_views=profile_views,
                applications_this_month=applications_this_month,
                response_rate=round(response_rate, 1),
                active_applications=active_applications
            )
            
        except Exception as e:
            print(f"Error calculating dashboard stats: {e}")
            # Return default stats on error
            return DashboardStats(
                total_applications=0,
                interviews_scheduled=0,
                saved_jobs=0,
                profile_views=0,
                applications_this_month=0,
                response_rate=0.0,
                active_applications=0
            )

    async def get_application_status_stats(self, user_id: str) -> ApplicationStatusStats:
        """
        Get application statistics grouped by status
        """
        try:
            # Query applications grouped by status
            status_query = select(
                JobApplication.status,
                func.count(JobApplication.id).label('count')
            ).where(
                JobApplication.user_id == user_id
            ).group_by(JobApplication.status)
            
            status_result = await self.db_session.execute(status_query)
            status_counts = dict(status_result.fetchall())
            
            return ApplicationStatusStats(
                pending=status_counts.get('pending', 0),
                applied=status_counts.get('applied', 0),
                interview=status_counts.get('interview', 0) + status_counts.get('final_interview', 0),
                offer=status_counts.get('offer', 0),
                rejected=status_counts.get('rejected', 0),
                withdrawn=status_counts.get('withdrawn', 0)
            )
            
        except Exception as e:
            print(f"Error getting status stats: {e}")
            return ApplicationStatusStats(
                pending=0, applied=0, interview=0, 
                offer=0, rejected=0, withdrawn=0
            )

    async def get_recent_activities(self, user_id: str, limit: int = 10) -> List[DashboardActivity]:
        """
        Get recent user activities for the dashboard
        """
        try:
            # Query recent activity logs
            activities_query = select(ActivityLog).where(
                ActivityLog.user_id == user_id
            ).order_by(ActivityLog.created_at.desc()).limit(limit)
            
            activities_result = await self.db_session.execute(activities_query)
            activities = activities_result.scalars().all()
            
            dashboard_activities = []
            for activity in activities:
                # Parse context data if available
                related_job_id = None
                related_job_title = None
                related_company_name = None
                
                # Try to extract job info from context or description
                if activity.context_data:
                    try:
                        import json
                        context = json.loads(activity.context_data)
                        related_job_id = context.get('job_id')
                        related_job_title = context.get('job_title')
                        related_company_name = context.get('company_name')
                    except:
                        pass
                
                dashboard_activities.append(DashboardActivity(
                    id=str(activity.id),
                    type=activity.action.lower(),
                    content=activity.description or activity.action,
                    timestamp=activity.created_at,
                    related_job_id=related_job_id,
                    related_job_title=related_job_title,
                    related_company_name=related_company_name
                ))
            
            return dashboard_activities
            
        except Exception as e:
            print(f"Error getting recent activities: {e}")
            # Return mock activities as fallback
            return self.get_mock_activities()

    async def get_recent_applications(self, user_id: str, limit: int = 5):
        """
        Get recent job applications for the dashboard
        """
        try:
            # Query recent applications with job and company info
            applications_query = select(JobApplication).options(
                selectinload(JobApplication.job).selectinload(Job.company)
            ).where(
                JobApplication.user_id == user_id
            ).order_by(JobApplication.applied_date.desc()).limit(limit)
            
            applications_result = await self.db_session.execute(applications_query)
            applications = applications_result.scalars().all()
            
            return applications
            
        except Exception as e:
            print(f"Error getting recent applications: {e}")
            return []

    def get_mock_activities(self) -> List[DashboardActivity]:
        """
        Get mock activities for fallback/demo purposes
        """
        mock_activities = [
            DashboardActivity(
                id="mock-activity-1",
                type="application",
                content="Applied to Software Engineer at TechCorp",
                timestamp=datetime.utcnow() - timedelta(hours=2),
                related_job_id="mock-job-1",
                related_job_title="Software Engineer",
                related_company_name="TechCorp"
            ),
            DashboardActivity(
                id="mock-activity-2",
                type="save",
                content="Saved Full Stack Developer at StartupXYZ",
                timestamp=datetime.utcnow() - timedelta(days=1),
                related_job_id="mock-job-2",
                related_job_title="Full Stack Developer", 
                related_company_name="StartupXYZ"
            ),
            DashboardActivity(
                id="mock-activity-3",
                type="view",
                content="Viewed Senior Developer at BigTech",
                timestamp=datetime.utcnow() - timedelta(days=2),
                related_job_id="mock-job-3",
                related_job_title="Senior Developer",
                related_company_name="BigTech"
            ),
            DashboardActivity(
                id="mock-activity-4",
                type="interview",
                content="Interview scheduled with DevCompany",
                timestamp=datetime.utcnow() - timedelta(days=3),
                related_job_id="mock-job-4",
                related_job_title="Backend Developer",
                related_company_name="DevCompany"
            )
        ]
        
        return mock_activities

    async def log_activity(
        self, 
        user_id: str, 
        action: str, 
        description: str, 
        epic: str = "dashboard",
        context_data: Optional[Dict[str, Any]] = None
    ):
        """
        Log a user activity
        """
        try:
            import json
            
            activity = ActivityLog(
                user_id=user_id,
                action=action,
                description=description,
                epic=epic,
                context_data=json.dumps(context_data) if context_data else None,
                created_at=datetime.utcnow()
            )
            
            self.db_session.add(activity)
            await self.db_session.commit()
            
        except Exception as e:
            print(f"Error logging activity: {e}")
            # Don't raise error for logging failures