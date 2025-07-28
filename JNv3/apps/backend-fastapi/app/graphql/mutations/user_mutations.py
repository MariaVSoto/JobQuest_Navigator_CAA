"""
User related GraphQL mutations
User profile management and updates
"""

import strawberry
from typing import Optional

from app.graphql.types.user_types import UserType, UserUpdateInput


@strawberry.type
class UserMutation:
    """User related mutations"""
    
    @strawberry.mutation
    async def update_profile(self, input: UserUpdateInput, info) -> Optional[UserType]:
        """
        Update user profile information
        """
        # TODO: Implement user profile update with authentication
        # For now, return mock updated user
        try:
            # Placeholder for actual database update
            return UserType(
                id="1",
                email="demo@example.com",
                username="demo_user",
                full_name=input.full_name or "Demo User",
                bio=input.bio or "Updated bio",
                current_job_title=input.current_job_title or "Software Developer",
                years_of_experience=input.years_of_experience or 5,
                industry=input.industry or "Technology",
                career_level=input.career_level or "mid",
                job_search_status=input.job_search_status or "actively_looking",
                preferred_work_type=input.preferred_work_type or "remote",
                date_joined="2023-01-01T00:00:00Z",
                salary_expectation_min=input.salary_expectation_min or 80000.0,
                salary_expectation_max=input.salary_expectation_max or 120000.0
            )
        except Exception as e:
            print(f"Error updating profile: {e}")
            return None
    
    @strawberry.mutation
    async def delete_account(self, info) -> bool:
        """
        Delete user account
        """
        # TODO: Implement account deletion with proper authentication
        return False