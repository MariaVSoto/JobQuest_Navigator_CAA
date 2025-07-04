from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import uuid

from app.db import get_async_session, User
from app.schemas import (
    UserRead, 
    UserProfileUpdate, 
    UserCareerPreferences, 
    UserNotificationSettings,
    UserStats
)
from app.users import current_active_user, current_user

router = APIRouter()


@router.get("/me/profile", response_model=UserRead)
async def get_my_profile(user: User = Depends(current_active_user)):
    """Get current user's complete profile"""
    return user


@router.patch("/me/profile", response_model=UserRead)
async def update_my_profile(
    profile_data: UserProfileUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Update current user's profile information"""
    
    # Update fields that are provided
    update_data = profile_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    # Update full_name if first_name or last_name changed
    if 'first_name' in update_data or 'last_name' in update_data:
        full_name_parts = []
        if user.first_name:
            full_name_parts.append(user.first_name)
        if user.last_name:
            full_name_parts.append(user.last_name)
        user.full_name = " ".join(full_name_parts) if full_name_parts else None
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return user


@router.patch("/me/career-preferences", response_model=UserRead)
async def update_career_preferences(
    preferences: UserCareerPreferences,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Update current user's career preferences"""
    
    update_data = preferences.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return user


@router.patch("/me/notifications", response_model=UserRead)
async def update_notification_settings(
    settings_data: UserNotificationSettings,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Update current user's notification settings"""
    
    update_data = settings_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return user


@router.get("/me/stats", response_model=UserStats)
async def get_user_stats(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get current user's statistics"""
    
    # This would typically query other services for job applications, saved jobs etc.
    # For now, return mock data
    return UserStats(
        total_applications=0,
        saved_jobs=0,
        profile_views=0,
        last_activity=user.last_login
    )


@router.get("/search", response_model=List[UserRead])
async def search_users(
    query: str = "",
    industry: str = None,
    career_level: str = None,
    location: str = None,
    limit: int = 20,
    offset: int = 0,
    current_user_auth: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Search for users (for networking, recruiting, etc.)"""
    
    # Build search query
    stmt = select(User).where(
        User.is_active == True,
        User.profile_visibility.in_(["public", "recruiters_only"])
    )
    
    if query:
        stmt = stmt.where(
            User.full_name.ilike(f"%{query}%") |
            User.current_job_title.ilike(f"%{query}%") |
            User.bio.ilike(f"%{query}%")
        )
    
    if industry:
        stmt = stmt.where(User.industry.ilike(f"%{industry}%"))
    
    if career_level:
        stmt = stmt.where(User.career_level == career_level)
    
    if location:
        stmt = stmt.where(User.preferred_location.ilike(f"%{location}%"))
    
    stmt = stmt.offset(offset).limit(limit)
    
    result = await session.execute(stmt)
    users = result.scalars().all()
    
    return users


@router.get("/{user_id}/profile", response_model=UserRead)
async def get_user_profile(
    user_id: uuid.UUID,
    current_user_auth: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get a specific user's public profile"""
    
    stmt = select(User).where(
        User.id == user_id,
        User.is_active == True,
        User.profile_visibility.in_(["public", "recruiters_only"])
    )
    
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or profile is private"
        )
    
    return user


@router.get("/stats/platform", response_model=dict)
async def get_platform_stats(
    admin_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get platform statistics (admin only for now)"""
    
    # Count total users
    total_users_stmt = select(func.count(User.id))
    total_users_result = await session.execute(total_users_stmt)
    total_users = total_users_result.scalar()
    
    # Count active users
    active_users_stmt = select(func.count(User.id)).where(User.is_active == True)
    active_users_result = await session.execute(active_users_stmt)
    active_users = active_users_result.scalar()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users
    }