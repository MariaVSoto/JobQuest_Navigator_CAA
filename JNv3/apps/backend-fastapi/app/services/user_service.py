"""
User service layer for business logic
Handles user management, authentication, and profile operations
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.user import User, UserPreference, ActivityLog
from app.core.database import get_db, AsyncSessionLocal


class UserService:
    """Service for user-related business logic"""
    
    def __init__(self, db_session: AsyncSession = None):
        self.db_session = db_session
    
    async def create_user(
        self,
        email: str,
        full_name: str = None,
        password_hash: str = None,
        cognito_user_id: str = None
    ) -> User:
        """Create a new user"""
        async with get_db_session() as session:
            user = User(
                email=email,
                full_name=full_name,
                password_hash=password_hash,
                cognito_user_id=cognito_user_id
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        async with get_db_session() as session:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
    
    async def get_user_by_cognito_id(self, cognito_user_id: str) -> Optional[User]:
        """Get user by Cognito user ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(User).where(User.cognito_user_id == cognito_user_id)
            )
            return result.scalar_one_or_none()
    
    async def update_user(
        self,
        user_id: UUID,
        **kwargs
    ) -> Optional[User]:
        """Update user information"""
        async with get_db_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                
                await session.commit()
                await session.refresh(user)
            
            return user
    
    async def create_user_preference(
        self,
        user_id: UUID,
        preferred_job_types: List[str] = None,
        preferred_locations: List[str] = None,
        salary_range_min: int = None,
        salary_range_max: int = None,
        **kwargs
    ) -> UserPreference:
        """Create user job preferences"""
        async with get_db_session() as session:
            preference = UserPreference(
                user_id=user_id,
                preferred_job_types=preferred_job_types or [],
                preferred_locations=preferred_locations or [],
                salary_range_min=salary_range_min,
                salary_range_max=salary_range_max,
                **kwargs
            )
            session.add(preference)
            await session.commit()
            await session.refresh(preference)
            return preference
    
    async def get_user_preferences(self, user_id: UUID) -> Optional[UserPreference]:
        """Get user preferences"""
        async with get_db_session() as session:
            result = await session.execute(
                select(UserPreference).where(UserPreference.user_id == user_id)
            )
            return result.scalar_one_or_none()
    
    async def log_user_activity(
        self,
        user_id: UUID,
        activity_type: str,
        description: str,
        metadata: dict = None
    ) -> ActivityLog:
        """Log user activity"""
        async with get_db_session() as session:
            activity = ActivityLog(
                user_id=user_id,
                activity_type=activity_type,
                description=description,
                metadata=metadata or {}
            )
            session.add(activity)
            await session.commit()
            await session.refresh(activity)
            return activity
    
    async def get_user_activities(
        self,
        user_id: UUID,
        limit: int = 50
    ) -> List[ActivityLog]:
        """Get user activity history"""
        async with get_db_session() as session:
            result = await session.execute(
                select(ActivityLog)
                .where(ActivityLog.user_id == user_id)
                .order_by(ActivityLog.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
    
    async def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate user account"""
        async with get_db_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                user.is_active = False
                await session.commit()
                return True
            
            return False