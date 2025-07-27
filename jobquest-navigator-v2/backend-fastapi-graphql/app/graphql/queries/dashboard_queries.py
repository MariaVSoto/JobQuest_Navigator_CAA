"""
Dashboard-related GraphQL queries
"""

import strawberry
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db_session
from app.services.dashboard_service import DashboardService
from app.graphql.types.dashboard_types import (
    DashboardStats, DashboardActivity, DashboardData, 
    ApplicationStatusStats, DashboardFilters
)


@strawberry.type
class DashboardQuery:
    """
    Dashboard-related GraphQL queries
    """

    @strawberry.field
    async def dashboard_stats(
        self, 
        user_id: str,
        date_range_days: Optional[int] = 30
    ) -> DashboardStats:
        """
        Get dashboard statistics for a user
        """
        async with get_async_db_session() as db:
            dashboard_service = DashboardService(db)
            return await dashboard_service.get_dashboard_stats(user_id, date_range_days or 30)

    @strawberry.field
    async def dashboard_data(
        self,
        user_id: str,
        filters: Optional[DashboardFilters] = None
    ) -> DashboardData:
        """
        Get complete dashboard data including stats, activities, and recent applications
        """
        if not filters:
            filters = DashboardFilters()
            
        async with get_async_db_session() as db:
            dashboard_service = DashboardService(db)
            return await dashboard_service.get_dashboard_data(
                user_id=user_id,
                date_range_days=filters.date_range_days or 30,
                include_activities=filters.include_activities if filters.include_activities is not None else True,
                activity_limit=filters.activity_limit or 10
            )

    @strawberry.field 
    async def application_status_stats(
        self,
        user_id: str
    ) -> ApplicationStatusStats:
        """
        Get application statistics grouped by status
        """
        async with get_async_db_session() as db:
            dashboard_service = DashboardService(db)
            return await dashboard_service.get_application_status_stats(user_id)

    @strawberry.field
    async def recent_activities(
        self,
        user_id: str,
        limit: Optional[int] = 10
    ) -> list[DashboardActivity]:
        """
        Get recent user activities
        """
        async with get_async_db_session() as db:
            dashboard_service = DashboardService(db)
            return await dashboard_service.get_recent_activities(user_id, limit or 10)