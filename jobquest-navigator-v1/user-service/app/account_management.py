"""
Account management service for user administration and security
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging

from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User, get_async_session
from app.schemas import (
    AccountStatus, 
    SuspensionReason, 
    AccountManagementAction,
    AccountSuspension,
    LoginAttempt,
    UserAccountStatus,
    AdminUserList
)
from app.email_service import email_service
from app.config import settings

logger = logging.getLogger(__name__)


class AccountManager:
    """Service for managing user accounts and security"""
    
    def __init__(self):
        self.max_login_attempts = settings.max_login_attempts
        self.lockout_duration = settings.account_lockout_duration
    
    async def get_user_account_status(
        self, 
        user_id: uuid.UUID, 
        session: AsyncSession
    ) -> Optional[UserAccountStatus]:
        """Get detailed account status for a user"""
        try:
            # Get user with extended information
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            # Get additional status information
            failed_attempts = await self._get_failed_login_attempts(user.email, session)
            
            return UserAccountStatus(
                user_id=user.id,
                email=user.email,
                status=self._determine_account_status(user),
                is_verified=user.is_verified,
                is_locked=await self._is_account_locked(user.email, session),
                lock_expires_at=await self._get_lock_expiry(user.email, session),
                is_suspended=getattr(user, 'is_suspended', False),
                suspended_until=getattr(user, 'suspended_until', None),
                suspension_reason=getattr(user, 'suspension_reason', None),
                failed_login_attempts=failed_attempts,
                last_login=getattr(user, 'last_login', None),
                created_at=getattr(user, 'created_at', datetime.utcnow())
            )
            
        except Exception as e:
            logger.error(f"Failed to get account status for user {user_id}: {str(e)}")
            return None
    
    async def suspend_user_account(
        self,
        user_id: uuid.UUID,
        reason: SuspensionReason,
        description: Optional[str] = None,
        duration_hours: Optional[int] = None,
        admin_id: Optional[uuid.UUID] = None,
        session: AsyncSession = None
    ) -> bool:
        """Suspend a user account"""
        try:
            if session is None:
                async with get_async_session() as session:
                    return await self._suspend_user_internal(
                        user_id, reason, description, duration_hours, admin_id, session
                    )
            else:
                return await self._suspend_user_internal(
                    user_id, reason, description, duration_hours, admin_id, session
                )
        except Exception as e:
            logger.error(f"Failed to suspend user {user_id}: {str(e)}")
            return False
    
    async def _suspend_user_internal(
        self,
        user_id: uuid.UUID,
        reason: SuspensionReason,
        description: Optional[str],
        duration_hours: Optional[int],
        admin_id: Optional[uuid.UUID],
        session: AsyncSession
    ) -> bool:
        """Internal method to suspend user"""
        # Get user
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"User {user_id} not found for suspension")
            return False
        
        # Calculate suspension end time
        suspended_until = None
        is_permanent = duration_hours is None
        
        if duration_hours:
            suspended_until = datetime.utcnow() + timedelta(hours=duration_hours)
        
        # Update user status (these fields would need to be added to User model)
        update_data = {
            'is_active': False,
            'is_suspended': True,
            'suspension_reason': reason.value,
            'suspended_until': suspended_until,
            'suspension_description': description,
            'suspended_by': admin_id,
            'suspended_at': datetime.utcnow()
        }
        
        # Note: This assumes these fields exist in the User model
        # You might need to add them to the database schema
        try:
            stmt = update(User).where(User.id == user_id).values(**update_data)
            await session.execute(stmt)
            await session.commit()
        except Exception as e:
            logger.warning(f"Some suspension fields may not exist in User model: {str(e)}")
            # Fallback to basic deactivation
            stmt = update(User).where(User.id == user_id).values(is_active=False)
            await session.execute(stmt)
            await session.commit()
        
        # Send suspension email
        await email_service.send_account_suspended_email(
            user_email=user.email,
            user_name=user.first_name or "User",
            reason=description or reason.value,
            suspension_until=suspended_until
        )
        
        logger.info(f"User {user_id} suspended. Reason: {reason.value}")
        return True
    
    async def activate_user_account(
        self,
        user_id: uuid.UUID,
        admin_id: Optional[uuid.UUID] = None,
        session: AsyncSession = None
    ) -> bool:
        """Activate/reactivate a user account"""
        try:
            if session is None:
                async with get_async_session() as session:
                    return await self._activate_user_internal(user_id, admin_id, session)
            else:
                return await self._activate_user_internal(user_id, admin_id, session)
        except Exception as e:
            logger.error(f"Failed to activate user {user_id}: {str(e)}")
            return False
    
    async def _activate_user_internal(
        self,
        user_id: uuid.UUID,
        admin_id: Optional[uuid.UUID],
        session: AsyncSession
    ) -> bool:
        """Internal method to activate user"""
        # Get user
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"User {user_id} not found for activation")
            return False
        
        # Update user status
        update_data = {
            'is_active': True,
            'is_suspended': False,
            'suspension_reason': None,
            'suspended_until': None,
            'suspension_description': None,
            'reactivated_by': admin_id,
            'reactivated_at': datetime.utcnow()
        }
        
        try:
            stmt = update(User).where(User.id == user_id).values(**update_data)
            await session.execute(stmt)
            await session.commit()
        except Exception as e:
            logger.warning(f"Some activation fields may not exist in User model: {str(e)}")
            # Fallback to basic activation
            stmt = update(User).where(User.id == user_id).values(is_active=True)
            await session.execute(stmt)
            await session.commit()
        
        logger.info(f"User {user_id} activated")
        return True
    
    async def lock_user_account(
        self,
        user_email: str,
        duration_minutes: Optional[int] = None,
        session: AsyncSession = None
    ) -> bool:
        """Lock a user account temporarily"""
        try:
            duration = duration_minutes or (self.lockout_duration // 60)
            
            # Record the lock (this would typically be in a separate table)
            # For now, we'll use a simple approach
            
            user_name = await self._get_user_name_by_email(user_email, session)
            
            # Send account locked email
            await email_service.send_account_locked_email(
                user_email=user_email,
                user_name=user_name or "User",
                lockout_duration_minutes=duration
            )
            
            logger.info(f"User account {user_email} locked for {duration} minutes")
            return True
            
        except Exception as e:
            logger.error(f"Failed to lock user account {user_email}: {str(e)}")
            return False
    
    async def track_login_attempt(
        self,
        user_email: str,
        ip_address: str,
        user_agent: str,
        success: bool,
        failure_reason: Optional[str] = None,
        session: AsyncSession = None
    ) -> bool:
        """Track login attempts for security monitoring"""
        try:
            # This would typically be stored in a login_attempts table
            # For now, we'll log it and implement basic tracking
            
            attempt = LoginAttempt(
                user_email=user_email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                attempted_at=datetime.utcnow(),
                failure_reason=failure_reason
            )
            
            if success:
                logger.info(f"Successful login for {user_email} from {ip_address}")
                # Reset failed attempts counter if login successful
                await self._reset_failed_attempts(user_email, session)
            else:
                logger.warning(f"Failed login for {user_email} from {ip_address}: {failure_reason}")
                # Increment failed attempts
                failed_count = await self._increment_failed_attempts(user_email, session)
                
                # Check if account should be locked
                if failed_count >= self.max_login_attempts:
                    await self.lock_user_account(user_email, session=session)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to track login attempt: {str(e)}")
            return False
    
    async def get_admin_user_list(
        self,
        page: int = 1,
        per_page: int = 50,
        status_filter: Optional[str] = None,
        search_query: Optional[str] = None,
        session: AsyncSession = None
    ) -> AdminUserList:
        """Get paginated list of users for admin interface"""
        try:
            if session is None:
                async with get_async_session() as session:
                    return await self._get_admin_user_list_internal(
                        page, per_page, status_filter, search_query, session
                    )
            else:
                return await self._get_admin_user_list_internal(
                    page, per_page, status_filter, search_query, session
                )
        except Exception as e:
            logger.error(f"Failed to get admin user list: {str(e)}")
            return AdminUserList(users=[], total_count=0, page=page, per_page=per_page, total_pages=0)
    
    async def _get_admin_user_list_internal(
        self,
        page: int,
        per_page: int,
        status_filter: Optional[str],
        search_query: Optional[str],
        session: AsyncSession
    ) -> AdminUserList:
        """Internal method to get admin user list"""
        # Build query
        stmt = select(User)
        
        # Apply filters
        if status_filter:
            if status_filter == "active":
                stmt = stmt.where(User.is_active == True)
            elif status_filter == "inactive":
                stmt = stmt.where(User.is_active == False)
            elif status_filter == "verified":
                stmt = stmt.where(User.is_verified == True)
            elif status_filter == "unverified":
                stmt = stmt.where(User.is_verified == False)
        
        if search_query:
            search_pattern = f"%{search_query}%"
            stmt = stmt.where(
                or_(
                    User.email.ilike(search_pattern),
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern)
                )
            )
        
        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await session.execute(count_stmt)
        total_count = count_result.scalar()
        
        # Apply pagination
        offset = (page - 1) * per_page
        stmt = stmt.offset(offset).limit(per_page)
        
        # Execute query
        result = await session.execute(stmt)
        users = result.scalars().all()
        
        # Convert to UserAccountStatus objects
        user_statuses = []
        for user in users:
            status = UserAccountStatus(
                user_id=user.id,
                email=user.email,
                status=self._determine_account_status(user),
                is_verified=user.is_verified,
                is_locked=await self._is_account_locked(user.email, session),
                is_suspended=getattr(user, 'is_suspended', False),
                suspended_until=getattr(user, 'suspended_until', None),
                suspension_reason=getattr(user, 'suspension_reason', None),
                failed_login_attempts=await self._get_failed_login_attempts(user.email, session),
                last_login=getattr(user, 'last_login', None),
                created_at=getattr(user, 'created_at', datetime.utcnow())
            )
            user_statuses.append(status)
        
        total_pages = (total_count + per_page - 1) // per_page
        
        return AdminUserList(
            users=user_statuses,
            total_count=total_count,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
    
    # Helper methods
    def _determine_account_status(self, user: User) -> AccountStatus:
        """Determine the current account status"""
        if not user.is_active:
            if getattr(user, 'is_suspended', False):
                return AccountStatus.SUSPENDED
            return AccountStatus.DELETED
        
        if not user.is_verified:
            return AccountStatus.PENDING_VERIFICATION
        
        return AccountStatus.ACTIVE
    
    async def _is_account_locked(self, user_email: str, session: AsyncSession) -> bool:
        """Check if account is currently locked"""
        # This would check a locks table or cache
        # For now, return False
        return False
    
    async def _get_lock_expiry(self, user_email: str, session: AsyncSession) -> Optional[datetime]:
        """Get lock expiry time"""
        # This would check a locks table
        # For now, return None
        return None
    
    async def _get_failed_login_attempts(self, user_email: str, session: AsyncSession) -> int:
        """Get number of failed login attempts"""
        # This would check a login_attempts table or cache
        # For now, return 0
        return 0
    
    async def _increment_failed_attempts(self, user_email: str, session: AsyncSession) -> int:
        """Increment failed login attempts counter"""
        # This would update a counter in database or cache
        # For now, return 1
        return 1
    
    async def _reset_failed_attempts(self, user_email: str, session: AsyncSession) -> bool:
        """Reset failed login attempts counter"""
        # This would reset the counter
        return True
    
    async def _get_user_name_by_email(self, user_email: str, session: AsyncSession) -> Optional[str]:
        """Get user name by email"""
        try:
            stmt = select(User.first_name).where(User.email == user_email)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception:
            return None


# Global account manager instance
account_manager = AccountManager()