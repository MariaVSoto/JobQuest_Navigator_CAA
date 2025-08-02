"""
Authentication module for AWS Cognito integration
Provides middleware, decorators, and utilities for user authentication
"""

from .cognito import (
    CognitoAuth,
    cognito_auth,
    verify_cognito_token,
    create_mock_token,
    validate_mock_token
)

from .middleware import (
    AuthContext,
    get_auth_context,
    get_current_user,
    require_auth,
    require_auth_graphql,
    current_user_field,
    get_current_user_graphql,
    require_user_graphql,
    get_context
)

__all__ = [
    # Cognito utilities
    "CognitoAuth",
    "cognito_auth",
    "verify_cognito_token",
    "create_mock_token",
    "validate_mock_token",
    
    # Middleware and context
    "AuthContext",
    "get_auth_context",
    "get_context",
    
    # FastAPI dependencies
    "get_current_user",
    "require_auth",
    
    # GraphQL utilities
    "require_auth_graphql",
    "current_user_field",
    "get_current_user_graphql",
    "require_user_graphql"
]