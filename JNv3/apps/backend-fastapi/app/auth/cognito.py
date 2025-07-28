"""
AWS Cognito authentication integration
Handles JWT token validation and user authentication
"""

import jwt
import json
import requests
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from functools import lru_cache
import asyncio

from app.core.config import settings


class CognitoAuth:
    """AWS Cognito authentication handler"""
    
    def __init__(self):
        self.region = settings.cognito_region
        self.user_pool_id = settings.cognito_user_pool_id
        self.client_id = settings.cognito_client_id
        self.jwks_url = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json"
        self._jwks_cache = None
    
    @lru_cache(maxsize=1)
    def get_jwks(self) -> Dict[str, Any]:
        """Get JSON Web Key Set from Cognito"""
        try:
            response = requests.get(self.jwks_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch JWKS: {str(e)}"
            )
    
    def get_public_key(self, token_header: Dict[str, Any]) -> str:
        """Extract public key from JWKS for token validation"""
        kid = token_header.get("kid")
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token header"
            )
        
        jwks = self.get_jwks()
        
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                # Convert JWK to PEM format
                return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Public key not found"
        )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token with Cognito"""
        try:
            # Decode header without verification to get kid
            header = jwt.get_unverified_header(token)
            
            # Get public key
            public_key = self.get_public_key(header)
            
            # Verify and decode token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}"
            )
            
            return payload
        
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}"
            )
    
    def extract_user_info(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user information from JWT payload"""
        return {
            "cognito_user_id": payload.get("sub"),
            "email": payload.get("email"),
            "email_verified": payload.get("email_verified", False),
            "username": payload.get("cognito:username"),
            "token_use": payload.get("token_use"),
            "auth_time": payload.get("auth_time"),
            "iss": payload.get("iss"),
            "exp": payload.get("exp"),
            "iat": payload.get("iat")
        }


# Global instance
cognito_auth = CognitoAuth()


def verify_cognito_token(token: str) -> Dict[str, Any]:
    """Verify Cognito JWT token and return user info"""
    if not settings.cognito_user_pool_id or not settings.cognito_client_id:
        # For development - return mock user data
        return {
            "cognito_user_id": "dev_user_123",
            "email": "dev@example.com",
            "email_verified": True,
            "username": "dev_user",
            "token_use": "access",
            "development_mode": True
        }
    
    payload = cognito_auth.verify_token(token)
    return cognito_auth.extract_user_info(payload)


def create_mock_token(email: str, cognito_user_id: str = None) -> str:
    """Create mock JWT token for development"""
    import time
    
    payload = {
        "sub": cognito_user_id or "dev_user_123",
        "email": email,
        "email_verified": True,
        "cognito:username": email.split("@")[0],
        "token_use": "access",
        "auth_time": int(time.time()),
        "iss": f"https://cognito-idp.{settings.cognito_region}.amazonaws.com/{settings.cognito_user_pool_id or 'dev'}",
        "exp": int(time.time()) + 3600,  # 1 hour
        "iat": int(time.time()),
        "development_mode": True
    }
    
    # Use HS256 for development (simpler)
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def validate_mock_token(token: str) -> Dict[str, Any]:
    """Validate mock development token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return cognito_auth.extract_user_info(payload)
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid development token: {str(e)}"
        )