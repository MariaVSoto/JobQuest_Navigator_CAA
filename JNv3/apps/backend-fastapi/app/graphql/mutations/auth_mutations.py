"""
Authentication related GraphQL mutations
Cognito integration for user authentication
"""

import strawberry
from typing import Optional
from fastapi import Response, Request, HTTPException
from strawberry.fastapi import BaseContext

from app.graphql.types.user_types import AuthResponse, UserRegistrationInput, User
from app.graphql.types.common_types import SecureAuthResponse
from app.auth.cognito import verify_cognito_token, create_mock_token
from app.core.config import settings


@strawberry.type
class AuthMutation:
    """Authentication mutations"""
    
    @strawberry.mutation
    async def register(self, input: UserRegistrationInput) -> AuthResponse:
        """
        User registration mutation - matches frontend expectations
        Will integrate with AWS Cognito
        """
        return await self.registerUser(
            email=input.email,
            username=input.username,
            password=input.password,
            fullName=input.fullName
        )
    
    @strawberry.mutation
    async def registerUser(self, email: str, username: str, password: str, fullName: str = None) -> AuthResponse:
        """
        User registration mutation - matches frontend expectations
        Will integrate with AWS Cognito
        """
        try:
            # Use provided full name or default to username
            fullName = fullName or username
            
            # Check if Cognito is configured
            if not settings.cognito_user_pool_id or not settings.cognito_client_id:
                # Development mode - return mock user with development token
                mock_user = User(
                    id=f"dev-user-{email.replace('@', '-').replace('.', '-')}",
                    email=email,
                    username=username,
                    fullName=fullName,
                    bio="Development mode user",
                    currentJobTitle="",
                    yearsOfExperience=0,
                    industry="",
                    careerLevel="entry",
                    jobSearchStatus="not_looking",
                    preferredWorkType="office"
                )
                
                # Create development JWT token
                dev_token = create_mock_token(mock_user.email, mock_user.id)
                
                return AuthResponse(
                    success=True,
                    user=mock_user,
                    token=dev_token,
                    message="Development registration successful",
                    errors=None
                )
            
            # Production mode - integrate with AWS Cognito
            import boto3
            from botocore.exceptions import ClientError
            
            try:
                # Initialize Cognito client
                cognito_client = boto3.client('cognito-idp', region_name=settings.cognito_region)
                
                # Create user in Cognito
                response = cognito_client.admin_create_user(
                    UserPoolId=settings.cognito_user_pool_id,
                    Username=username,
                    UserAttributes=[
                        {'Name': 'email', 'Value': email},
                        {'Name': 'email_verified', 'Value': 'true'},
                        {'Name': 'name', 'Value': fullName}
                    ],
                    TemporaryPassword=password,
                    MessageAction='SUPPRESS'  # Don't send welcome email
                )
                
                # Set permanent password
                cognito_client.admin_set_user_password(
                    UserPoolId=settings.cognito_user_pool_id,
                    Username=username,
                    Password=password,
                    Permanent=True
                )
                
                # Create user object
                cognito_user = User(
                    id=response['User']['Username'],
                    email=email,
                    username=username,
                    fullName=fullName,
                    bio="",
                    currentJobTitle="",
                    yearsOfExperience=0,
                    industry="",
                    careerLevel="entry",
                    jobSearchStatus="not_looking",
                    preferredWorkType="office"
                )
                
                # Create mock token for now (in production, use actual Cognito auth flow)
                cognito_token = create_mock_token(cognito_user.email, cognito_user.id)
                
                return AuthResponse(
                    success=True,
                    user=cognito_user,
                    token=cognito_token,
                    message="Registration successful - user created in Cognito",
                    errors=None
                )
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'UsernameExistsException':
                    return AuthResponse(
                        success=False,
                        user=None,
                        token=None,
                        message="Registration failed",
                        errors=["Username already exists"]
                    )
                else:
                    return AuthResponse(
                        success=False,
                        user=None,
                        token=None,
                        message="Registration failed",
                        errors=[f"Cognito error: {e.response['Error']['Message']}"]
                    )
            
        except Exception as e:
            return AuthResponse(
                success=False,
                user=None,
                token=None,
                message="Registration failed",
                errors=[str(e)]
            )
    
    @strawberry.mutation
    async def login(self, username: str, password: str) -> AuthResponse:
        """
        User login mutation with AWS Cognito integration
        """
        try:
            # Check if Cognito is configured
            if not settings.cognito_user_pool_id or not settings.cognito_client_id:
                # Development mode - return mock user with development token
                mock_user = User(
                    id=f"dev-user-{username.replace('@', '-').replace('.', '-')}",
                    email=username if '@' in username else f"{username}@example.com",
                    username=username,
                    fullName=f"Dev User {username.capitalize()}",
                    bio="Development mode user",
                    currentJobTitle="Software Developer",
                    yearsOfExperience=3,
                    industry="Technology",
                    careerLevel="mid",
                    jobSearchStatus="actively_looking",
                    preferredWorkType="remote"
                )
                
                # Create development JWT token
                dev_token = create_mock_token(mock_user.email, mock_user.id)
                
                return AuthResponse(
                    success=True,
                    user=mock_user,
                    token=dev_token,
                    message="Development login successful",
                    errors=None
                )
            
            # Production mode - integrate with AWS Cognito
            import boto3
            from botocore.exceptions import ClientError
            
            try:
                # Initialize Cognito client
                cognito_client = boto3.client('cognito-idp', region_name=settings.cognito_region)
                
                # Authenticate with Cognito
                response = cognito_client.admin_initiate_auth(
                    UserPoolId=settings.cognito_user_pool_id,
                    ClientId=settings.cognito_client_id,
                    AuthFlow='ADMIN_NO_SRP_AUTH',
                    AuthParameters={
                        'USERNAME': username,
                        'PASSWORD': password
                    }
                )
                
                # Get authentication result
                auth_result = response['AuthenticationResult']
                access_token = auth_result['AccessToken']
                
                # Get user information from Cognito
                user_response = cognito_client.get_user(AccessToken=access_token)
                
                # Extract user attributes
                user_attributes = {attr['Name']: attr['Value'] for attr in user_response['UserAttributes']}
                
                # Create user object from Cognito data
                cognito_user = User(
                    id=user_response['Username'],
                    email=user_attributes.get('email', username if '@' in username else f"{username}@example.com"),
                    username=user_response['Username'],
                    fullName=user_attributes.get('name', f"User {username.capitalize()}"),
                    bio="",
                    currentJobTitle="",
                    yearsOfExperience=0,
                    industry="",
                    careerLevel="entry",
                    jobSearchStatus="not_looking",
                    preferredWorkType="office"
                )
                
                return AuthResponse(
                    success=True,
                    user=cognito_user,
                    token=access_token,
                    message="Login successful",
                    errors=None
                )
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'NotAuthorizedException':
                    return AuthResponse(
                        success=False,
                        user=None,
                        token=None,
                        message="Login failed",
                        errors=["Invalid username or password"]
                    )
                elif error_code == 'UserNotFoundException':
                    return AuthResponse(
                        success=False,
                        user=None,
                        token=None,
                        message="Login failed",
                        errors=["User not found"]
                    )
                else:
                    return AuthResponse(
                        success=False,
                        user=None,
                        token=None,
                        message="Login failed",
                        errors=[f"Authentication error: {e.response['Error']['Message']}"]
                    )
            
        except Exception as e:
            return AuthResponse(
                success=False,
                user=None,
                token=None,
                message="Login failed",
                errors=[str(e)]
            )
    
    
    @strawberry.mutation
    async def logout(self) -> bool:
        """
        User logout mutation
        """
        # TODO: Implement Cognito logout/token invalidation
        return True
    
    @strawberry.mutation
    async def refresh_token(self, refresh_token: str) -> AuthResponse:
        """
        Refresh authentication token
        """
        # TODO: Implement Cognito token refresh
        return AuthResponse(
            success=True,
            user=None,
            token="new-dev-token-placeholder",
            errors=None
        )
    
    async def verify_token(self, token: str) -> bool:
        """
        Verify JWT token using Cognito or development validation
        """
        try:
            if not token or not token.strip():
                return False
            
            # Use the Cognito verification service
            user_info = verify_cognito_token(token)
            return bool(user_info and user_info.get('cognito_user_id'))
            
        except Exception as e:
            print(f"Token verification error: {e}")
            return False
    
    @strawberry.mutation
    async def secure_login(self, info: strawberry.Info, username: str, password: str) -> SecureAuthResponse:
        """
        Secure login with HttpOnly cookie authentication
        Prevents XSS attacks by storing JWT token in secure HttpOnly cookies
        """
        try:
            # TODO: Implement actual Cognito authentication
            # For development, return mock user data
            mock_user = User(
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
                preferred_work_type="remote"
            )
            
            # Generate secure JWT token (in production, use proper JWT with expiration)
            mock_token = f"secure-jwt-token-{username}-dev"
            
            # Get FastAPI response object
            response: Response = info.context["response"]
            
            # Set HttpOnly cookie with security flags
            response.set_cookie(
                key="auth_token",
                value=mock_token,
                httponly=True,           # Prevents XSS access
                secure=False,            # Set to True in production with HTTPS
                samesite="strict",       # CSRF protection
                max_age=1800,           # 30 minutes
                path="/"
            )
            
            # Set refresh token cookie (longer expiration)
            response.set_cookie(
                key="refresh_token",
                value=f"refresh-{mock_token}",
                httponly=True,
                secure=False,
                samesite="strict",
                max_age=86400,          # 24 hours
                path="/auth"            # Restrict to auth endpoints
            )
            
            return SecureAuthResponse(
                success=True,
                user=mock_user,
                message="Secure login successful",
                errors=None
            )
            
        except Exception as e:
            return SecureAuthResponse(
                success=False,
                user=None,
                message="Login failed",
                errors=[str(e)]
            )
    
    @strawberry.mutation
    async def secure_logout(self, info: strawberry.Info) -> SecureAuthResponse:
        """
        Secure logout with HttpOnly cookie cleanup
        """
        try:
            # Get FastAPI response object
            response: Response = info.context["response"]
            
            # Clear authentication cookies
            response.delete_cookie(
                key="auth_token",
                path="/",
                httponly=True,
                secure=False,
                samesite="strict"
            )
            
            response.delete_cookie(
                key="refresh_token", 
                path="/auth",
                httponly=True,
                secure=False,
                samesite="strict"
            )
            
            return SecureAuthResponse(
                success=True,
                user=None,
                message="Secure logout successful",
                errors=None
            )
            
        except Exception as e:
            return SecureAuthResponse(
                success=False,
                user=None,
                message="Logout failed",
                errors=[str(e)]
            )
    
    @strawberry.mutation
    async def refresh_secure_token(self, info: strawberry.Info) -> SecureAuthResponse:
        """
        Refresh authentication token using HttpOnly cookies
        """
        try:
            # Get FastAPI request object to read cookies
            request: Request = info.context["request"]
            response: Response = info.context["response"]
            
            # Get refresh token from HttpOnly cookie
            refresh_token = request.cookies.get("refresh_token")
            
            if not refresh_token:
                return SecureAuthResponse(
                    success=False,
                    user=None,
                    message="No refresh token found",
                    errors=["Refresh token not found"]
                )
            
            # TODO: Validate refresh token with Cognito
            # For development, generate new mock token
            mock_user = User(
                id="dev-user-123",
                email="dev@example.com", 
                username="devuser",
                full_name="Development User",
                bio="Mock user for development",
                current_job_title="Developer",
                years_of_experience=3,
                industry="Technology",
                career_level="mid",
                job_search_status="actively_looking",
                preferred_work_type="remote"
            )
            
            new_token = f"refreshed-jwt-token-{mock_user.username}-dev"
            
            # Set new HttpOnly cookie
            response.set_cookie(
                key="auth_token",
                value=new_token,
                httponly=True,
                secure=False,
                samesite="strict",
                max_age=1800,
                path="/"
            )
            
            return SecureAuthResponse(
                success=True,
                user=mock_user,
                message="Token refreshed successfully",
                errors=None
            )
            
        except Exception as e:
            return SecureAuthResponse(
                success=False,
                user=None,
                message="Token refresh failed",
                errors=[str(e)]
            )