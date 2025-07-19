import uuid
from typing import Optional
import logging
from datetime import datetime

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
)
from fastapi_users.authentication.strategy import JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase

from app.config import settings
from app.db import User, get_user_db

logger = logging.getLogger(__name__)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """Custom user manager with JobQuest specific logic"""
    
    reset_password_token_secret = settings.secret_key
    verification_token_secret = settings.secret_key

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """Called after a user registers"""
        logger.info(f"User {user.id} has registered with email {user.email}")
        
        # Set full_name if not provided
        if not user.full_name and (user.first_name or user.last_name):
            full_name_parts = []
            if user.first_name:
                full_name_parts.append(user.first_name)
            if user.last_name:
                full_name_parts.append(user.last_name)
            user.full_name = " ".join(full_name_parts)
        
        # Send welcome email with verification
        try:
            from app.email_service import email_service
            # Get verification token if user needs verification
            verification_token = None
            if not user.is_verified:
                verification_token = await self.request_verify(user, request)
            
            await email_service.send_welcome_email(
                user_email=user.email,
                user_name=user.first_name or user.email.split('@')[0],
                verification_token=verification_token
            )
            logger.info(f"Welcome email sent to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")

    async def on_after_login(
        self,
        user: User,
        request: Optional[Request] = None,
        response = None,
    ):
        """Called after a user logs in"""
        logger.info(f"User {user.id} logged in successfully")
        
        # Track login attempt for security
        try:
            from app.account_management import account_manager
            ip_address = getattr(request, 'client', {}).get('host', 'unknown') if request else 'unknown'
            user_agent = request.headers.get('user-agent', 'unknown') if request else 'unknown'
            
            await account_manager.track_login_attempt(
                user_email=user.email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=True
            )
        except Exception as e:
            logger.error(f"Failed to track login attempt: {str(e)}")

    async def on_after_login_failed(
        self,
        request: Optional[Request] = None,
        credentials = None
    ):
        """Called after a failed login attempt"""
        if request and hasattr(credentials, 'username'):
            logger.warning(f"Failed login attempt for {credentials.username}")
            
            # Track failed login attempt
            try:
                from app.account_management import account_manager
                ip_address = getattr(request, 'client', {}).get('host', 'unknown')
                user_agent = request.headers.get('user-agent', 'unknown')
                
                await account_manager.track_login_attempt(
                    user_email=credentials.username,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False,
                    failure_reason="Invalid credentials"
                )
            except Exception as e:
                logger.error(f"Failed to track failed login attempt: {str(e)}")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Called after a user requests password reset"""
        logger.info(f"Password reset requested for user {user.id}")
        
        # Send password reset email
        try:
            from app.email_service import email_service
            await email_service.send_password_reset_email(
                user_email=user.email,
                user_name=user.first_name or user.email.split('@')[0],
                reset_token=token
            )
            logger.info(f"Password reset email sent to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Called after a user requests email verification"""
        logger.info(f"Email verification requested for user {user.id}")
        
        # Send verification email
        try:
            from app.email_service import email_service
            await email_service.send_verification_email(
                user_email=user.email,
                user_name=user.first_name or user.email.split('@')[0],
                verification_token=token
            )
            logger.info(f"Verification email sent to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
    
    async def on_after_verify(
        self, user: User, request: Optional[Request] = None
    ):
        """Called after a user verifies their email"""
        logger.info(f"User {user.id} has verified their email address")
        
        # Could send a "verification successful" email here if desired
        # Or trigger other post-verification actions


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


# Authentication setup
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.jwt_secret, lifetime_seconds=settings.jwt_lifetime_seconds)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# FastAPI Users instance
fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

# Dependencies for protecting routes
current_active_user = fastapi_users.current_user(active=True)
current_user = fastapi_users.current_user()
current_superuser = fastapi_users.current_user(active=True, superuser=True)