"""
User related GraphQL queries
Proxy resolvers that initially call the original Django GraphQL endpoint
"""

import strawberry
from typing import Optional
import httpx
import json

from app.graphql.types.user_types import UserType
from app.core.config import settings


@strawberry.type
class UserQuery:
    """User related queries"""
    
    @strawberry.field
    async def me(self, info) -> Optional[UserType]:
        """
        Get current user profile
        Initially proxies to Django GraphQL endpoint during migration
        """
        # TODO: Replace with direct database query after migration
        try:
            # For now, return mock data to establish the schema
            # This will be replaced with actual database queries
            return UserType(
                id="1",
                email="demo@example.com",
                username="demo_user",
                full_name="Demo User",
                bio="Demo profile for v2 development",
                current_job_title="Software Developer",
                years_of_experience=5,
                industry="Technology",
                career_level="mid",
                job_search_status="actively_looking",
                preferred_work_type="remote",
                date_joined="2023-01-01T00:00:00Z",
                salary_expectation_min=80000.0,
                salary_expectation_max=120000.0
            )
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
    
    @strawberry.field
    async def user_by_id(self, id: str) -> Optional[UserType]:
        """
        Get user by ID
        Placeholder for future implementation
        """
        # TODO: Implement after database models are ready
        return None