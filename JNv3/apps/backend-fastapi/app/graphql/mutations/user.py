"""
User-related GraphQL mutations for Strawberry Schema
"""

import strawberry
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
import boto3
from botocore.exceptions import ClientError

from app.core.database import get_db
from app.core.config import settings
from app.graphql.types import (
    UserResponse, UserRegistrationInput, UserUpdateInput,
    UserType
)
from app.models import User
from app.graphql.auth import get_current_user


@strawberry.type
class UserMutation:
    """User-related mutations."""

    @strawberry.mutation
    async def register_user(
        self,
        info,
        input: UserRegistrationInput,
        db: AsyncSession = Depends(get_db)
    ) -> UserResponse:
        """Register a new user with AWS Cognito."""
        try:
            # Check if user already exists in database
            existing_user = await db.execute(
                select(User).where(
                    (User.email == input.email) |
                    (User.username == input.username)
                )
            )
            if existing_user.scalar_one_or_none():
                return UserResponse(
                    success=False,
                    errors=["User with this email or username already exists."]
                )
            
            # Create user in AWS Cognito
            cognito_client = boto3.client(
                'cognito-idp',
                region_name=settings.aws_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key
            )
            
            # Create Cognito user
            cognito_response = cognito_client.admin_create_user(
                UserPoolId=settings.cognito_user_pool_id,
                Username=input.username,
                UserAttributes=[
                    {'Name': 'email', 'Value': input.email},
                    {'Name': 'email_verified', 'Value': 'true'}
                ],
                TemporaryPassword=input.password,
                MessageAction='SUPPRESS'  # Don't send welcome email
            )
            
            # Set permanent password
            cognito_client.admin_set_user_password(
                UserPoolId=settings.cognito_user_pool_id,
                Username=input.username,
                Password=input.password,
                Permanent=True
            )
            
            # Get Cognito user sub (unique ID)
            cognito_sub = cognito_response['User']['Username']
            
            # Create user in database
            new_user = User(
                email=input.email,
                username=input.username,
                full_name=input.full_name,
                cognito_sub=cognito_sub
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            user_type = UserType(
                id=str(new_user.id),
                email=new_user.email,
                username=new_user.username,
                full_name=new_user.full_name,
                date_of_birth=new_user.date_of_birth,
                bio=new_user.bio,
                current_job_title=new_user.current_job_title,
                years_of_experience=new_user.years_of_experience,
                industry=new_user.industry,
                career_level=new_user.career_level,
                job_search_status=new_user.job_search_status,
                salary_expectation_min=new_user.salary_expectation_min,
                salary_expectation_max=new_user.salary_expectation_max,
                preferred_work_type=new_user.preferred_work_type,
                date_joined=new_user.date_joined,
                last_login=new_user.last_login,
            )
            
            return UserResponse(
                user=user_type,
                success=True,
                errors=[]
            )
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UsernameExistsException':
                return UserResponse(
                    success=False,
                    errors=["Username already exists in Cognito."]
                )
            elif error_code == 'InvalidPasswordException':
                return UserResponse(
                    success=False,
                    errors=["Password does not meet requirements."]
                )
            else:
                return UserResponse(
                    success=False,
                    errors=[f"Cognito error: {e.response['Error']['Message']}"]
                )
        except Exception as e:
            await db.rollback()
            return UserResponse(
                success=False,
                errors=[f"Registration failed: {str(e)}"]
            )

    @strawberry.mutation
    async def update_user_profile(
        self,
        info,
        input: UserUpdateInput,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> UserResponse:
        """Update user profile information."""
        try:
            # Update user fields safely using input data
            if input.full_name is not None:
                current_user.full_name = input.full_name
            if input.bio is not None:
                current_user.bio = input.bio
            if input.current_job_title is not None:
                current_user.current_job_title = input.current_job_title
            if input.years_of_experience is not None:
                current_user.years_of_experience = input.years_of_experience
            if input.industry is not None:
                current_user.industry = input.industry
            if input.career_level is not None:
                current_user.career_level = input.career_level
            if input.job_search_status is not None:
                current_user.job_search_status = input.job_search_status
            if input.preferred_work_type is not None:
                current_user.preferred_work_type = input.preferred_work_type
            
            await db.commit()
            await db.refresh(current_user)
            
            user_type = UserType(
                id=str(current_user.id),
                email=current_user.email,
                username=current_user.username,
                full_name=current_user.full_name,
                date_of_birth=current_user.date_of_birth,
                bio=current_user.bio,
                current_job_title=current_user.current_job_title,
                years_of_experience=current_user.years_of_experience,
                industry=current_user.industry,
                career_level=current_user.career_level,
                job_search_status=current_user.job_search_status,
                salary_expectation_min=current_user.salary_expectation_min,
                salary_expectation_max=current_user.salary_expectation_max,
                preferred_work_type=current_user.preferred_work_type,
                date_joined=current_user.date_joined,
                last_login=current_user.last_login,
            )
            
            return UserResponse(
                user=user_type,
                success=True,
                errors=[]
            )
            
        except Exception as e:
            await db.rollback()
            return UserResponse(
                success=False,
                errors=[f"Profile update failed: {str(e)}"]
            )