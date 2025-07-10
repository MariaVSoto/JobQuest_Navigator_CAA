"""
Authentication middleware for FastAPI and GraphQL
Handles token extraction, validation, and user context
"""

from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import strawberry
from strawberry.types import Info

from app.auth.cognito import verify_cognito_token, validate_mock_token
from app.services.user_service import UserService
from app.models.user import User
from app.core.config import settings


# HTTP Bearer token scheme for FastAPI
security = HTTPBearer(auto_error=False)


class AuthContext:
    """Authentication context for GraphQL"""
    
    def __init__(self, request: Request):
        self.request = request
        self.user: Optional[User] = None
        self.user_info: Optional[Dict[str, Any]] = None
        self.token: Optional[str] = None
    
    async def authenticate(self):
        """Authenticate user from request"""
        # Extract token from Authorization header
        auth_header = self.request.headers.get("Authorization")
        if not auth_header:
            return
        
        if not auth_header.startswith("Bearer "):
            return
        
        self.token = auth_header[7:]  # Remove "Bearer " prefix
        
        try:
            # Verify token
            if settings.debug and not settings.cognito_user_pool_id:
                # Development mode - use mock validation
                self.user_info = validate_mock_token(self.token)
            else:
                # Production mode - use Cognito validation
                self.user_info = verify_cognito_token(self.token)
            
            # Get or create user in database
            user_service = UserService()
            cognito_user_id = self.user_info.get("cognito_user_id")
            email = self.user_info.get("email")
            
            if cognito_user_id and email:
                # Try to find existing user
                self.user = await user_service.get_user_by_cognito_id(cognito_user_id)
                
                if not self.user:
                    # Try to find by email
                    self.user = await user_service.get_user_by_email(email)
                    
                    if self.user:
                        # Update with Cognito ID
                        self.user = await user_service.update_user(
                            self.user.id,
                            cognito_user_id=cognito_user_id
                        )
                    else:
                        # Create new user
                        self.user = await user_service.create_user(
                            email=email,
                            cognito_user_id=cognito_user_id,
                            full_name=self.user_info.get("username", email.split("@")[0])
                        )
        
        except HTTPException:
            # Invalid token
            self.user = None
            self.user_info = None
            self.token = None
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.user is not None
    
    @property
    def user_id(self) -> Optional[str]:
        """Get authenticated user ID"""
        return str(self.user.id) if self.user else None


async def get_auth_context(request: Request) -> AuthContext:
    """Get authentication context for GraphQL"""
    context = AuthContext(request)
    await context.authenticate()
    return context


# FastAPI dependencies
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """FastAPI dependency to get current authenticated user"""
    if not credentials:
        return None
    
    try:
        # Verify token
        if settings.debug and not settings.cognito_user_pool_id:
            user_info = validate_mock_token(credentials.credentials)
        else:
            user_info = verify_cognito_token(credentials.credentials)
        
        # Get user from database
        user_service = UserService()
        cognito_user_id = user_info.get("cognito_user_id")
        
        if cognito_user_id:
            user = await user_service.get_user_by_cognito_id(cognito_user_id)
            return user
    
    except HTTPException:
        return None
    
    return None


async def require_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """FastAPI dependency that requires authentication"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    user = await get_current_user(credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    return user


# GraphQL decorators and utilities
def require_auth_graphql():
    """Decorator for GraphQL resolvers that require authentication"""
    def decorator(func):
        async def wrapper(*args, info: Info, **kwargs):
            context: AuthContext = info.context.get("auth")
            
            if not context or not context.is_authenticated:
                raise Exception("Authentication required")
            
            return await func(*args, info=info, **kwargs)
        
        return wrapper
    return decorator


@strawberry.field
def current_user_field(info: Info) -> Optional["User"]:
    """GraphQL field to get current authenticated user"""
    context: AuthContext = info.context.get("auth")
    return context.user if context else None


def get_current_user_graphql(info: Info) -> Optional[User]:
    """Helper to get current user in GraphQL resolvers"""
    context: AuthContext = info.context.get("auth")
    return context.user if context else None


def require_user_graphql(info: Info) -> User:
    """Helper that requires authenticated user in GraphQL resolvers"""
    user = get_current_user_graphql(info)
    if not user:
        raise Exception("Authentication required")
    return user


# Context provider for GraphQL
async def get_context(request: Request) -> Dict[str, Any]:
    """Get context for GraphQL requests"""
    auth_context = await get_auth_context(request)
    
    return {
        "request": request,
        "auth": auth_context
    }