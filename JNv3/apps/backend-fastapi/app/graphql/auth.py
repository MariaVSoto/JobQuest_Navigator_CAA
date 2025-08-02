"""
Authentication module for GraphQL
AWS Cognito integration with FastAPI dependencies
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import boto3
import json
import jwt
from jwt.exceptions import PyJWTError
import requests
from functools import lru_cache

from app.core.config import settings
from app.core.database import get_db
from app.models import User

# FastAPI security scheme
security = HTTPBearer()


class CognitoTokenValidator:
    """AWS Cognito JWT token validator."""
    
    def __init__(self):
        self.region = settings.aws_region
        self.user_pool_id = settings.cognito_user_pool_id
        self.client_id = settings.cognito_client_id
        self.jwks_url = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json"
        
    @lru_cache(maxsize=32)
    def get_jwks(self):
        """Get JSON Web Key Set from Cognito."""
        try:
            response = requests.get(self.jwks_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get JWKS: {str(e)}"
            )
    
    def validate_token(self, token: str) -> dict:
        """Validate JWT token and return claims."""
        try:
            # Get token header without verification to extract kid
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get('kid')
            
            if not kid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token missing key ID"
                )
            
            # Get JWKS and find the right key
            jwks = self.get_jwks()
            key = None
            
            for jwk in jwks.get('keys', []):
                if jwk.get('kid') == kid:
                    key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
                    break
            
            if not key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unable to find appropriate key"
                )
            
            # Verify and decode token
            payload = jwt.decode(
                token,
                key,
                algorithms=['RS256'],
                audience=self.client_id,
                issuer=f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}"
            )
            
            return payload
            
        except PyJWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}"
            )


# Global token validator instance
token_validator = CognitoTokenValidator()


async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user from JWT token.
    Returns None if no valid token or user not found.
    """
    if not credentials:
        return None
        
    try:
        # Validate token and get claims
        payload = token_validator.validate_token(credentials.credentials)
        
        # Extract user info from token
        cognito_sub = payload.get('sub')
        email = payload.get('email')
        
        if not cognito_sub:
            return None
            
        # Find user by cognito_sub or email
        result = await db.execute(
            select(User).where(
                (User.cognito_sub == cognito_sub) | 
                (User.email == email)
            )
        )
        user = result.scalar_one_or_none()
        
        # If user exists but doesn't have cognito_sub, update it
        if user and not user.cognito_sub:
            user.cognito_sub = cognito_sub
            await db.commit()
            
        return user
        
    except HTTPException:
        # Re-raise HTTP exceptions (authentication failures)
        raise
    except Exception:
        # For any other error, return None (no user)
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user (required).
    Raises HTTPException if not authenticated.
    """
    user = await get_current_user_from_token(credentials, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.
    Does not raise exceptions for missing authentication.
    """
    if not credentials:
        return None
        
    try:
        return await get_current_user_from_token(credentials, db)
    except HTTPException:
        return None