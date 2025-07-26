"""
User related GraphQL queries
Proxy resolvers that initially call the original Django GraphQL endpoint
"""

import strawberry
from typing import Optional
import httpx
import json
from fastapi import Request

from app.graphql.types.user_types import UserType, SessionValidationPayload
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
    
    @strawberry.field
    async def validate_session(self, info: strawberry.Info) -> SessionValidationPayload:
        """
        Validate current session using HttpOnly cookies
        Returns user data if session is valid
        """
        try:
            # Get FastAPI request object to read cookies
            request: Request = info.context["request"]
            
            # Get auth token from HttpOnly cookie
            auth_token = request.cookies.get("auth_token")
            
            if not auth_token:
                return SessionValidationPayload(
                    valid=False,
                    user=None,
                    message="No authentication token found"
                )
            
            # TODO: Validate token with Cognito or JWT verification
            # For development, accept any token that starts with our prefix
            if auth_token.startswith("secure-jwt-token-") or auth_token.startswith("refreshed-jwt-token-"):
                # Extract username from token (development only)
                parts = auth_token.split("-")
                username = parts[3] if len(parts) > 3 else "devuser"
                
                mock_user = UserType(
                    id="dev-user-123",
                    email="dev@example.com",
                    username=username,
                    full_name="Development User",
                    bio="Mock user for development",
                    current_job_title="Developer",
                    years_of_experience=3,
                    industry="Technology",
                    career_level="mid",
                    job_search_status="actively_looking",
                    preferred_work_type="remote",
                    date_joined="2023-01-01T00:00:00Z",
                    salary_expectation_min=80000.0,
                    salary_expectation_max=120000.0
                )
                
                return SessionValidationPayload(
                    valid=True,
                    user=mock_user,
                    message="Session is valid"
                )
            else:
                return SessionValidationPayload(
                    valid=False,
                    user=None,
                    message="Invalid authentication token"
                )
                
        except Exception as e:
            return SessionValidationPayload(
                valid=False,
                user=None,
                message=f"Session validation failed: {str(e)}"
            )