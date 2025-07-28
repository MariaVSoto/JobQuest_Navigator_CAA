"""
User-related GraphQL queries for Strawberry Schema
"""

import strawberry
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.graphql.types import UserType, CompanyType
from app.models import User, Company
from app.graphql.auth import get_current_user


@strawberry.type
class UserQuery:
    """User-related queries."""

    @strawberry.field
    async def me(self, info) -> Optional[UserType]:
        """Get current authenticated user."""
        # Get dependencies manually for Strawberry
        db = await get_db().__anext__()
        try:
            current_user = await get_current_user(info, db)
            if not current_user:
                return None
                
            return UserType(
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
        finally:
            await db.close()

    @strawberry.field
    async def user(
        self,
        info,
        id: strawberry.ID
    ) -> Optional[UserType]:
        """Get user by ID, but only for the currently authenticated user."""
        # Get dependencies manually for Strawberry
        db = await get_db().__anext__()
        try:
            current_user = await get_current_user(info, db)
            if not current_user:
                raise Exception("Authentication required")
                
            # CRITICAL: Prevent users from querying other users' data
            if str(current_user.id) != str(id):
                raise Exception("You can only query your own user data.")
                
            return UserType(
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
        finally:
            await db.close()

    @strawberry.field
    async def companies(
        self,
        info
    ) -> List[CompanyType]:
        """Get all companies."""
        # Get dependencies manually for Strawberry
        db = await get_db().__anext__()
        try:
            result = await db.execute(select(Company).order_by(Company.name))
            companies = result.scalars().all()
            
            return [
                CompanyType(
                    id=str(company.id),
                    name=company.name,
                    slug=company.slug,
                    description=company.description,
                    website=company.website,
                    logo_url=company.logo_url,
                    industry=company.industry,
                    company_size=company.company_size,
                    founded_year=company.founded_year,
                    email=company.email,
                    phone=company.phone,
                    linkedin_url=company.linkedin_url,
                    twitter_handle=company.twitter_handle,
                    glassdoor_id=company.glassdoor_id,
                    glassdoor_rating=company.glassdoor_rating,
                    glassdoor_review_count=company.glassdoor_review_count,
                    ai_research_data=company.ai_research_data,
                    ai_research_model=company.ai_research_model,
                    ai_research_status=company.ai_research_status,
                    ai_research_generated_at=company.ai_research_generated_at,
                    created_at=company.created_at,
                )
                for company in companies
            ]
        finally:
            await db.close()

    @strawberry.field
    async def search_companies(
        self,
        info,
        query: str,
        limit: int = 10
    ) -> List[CompanyType]:
        """Search companies by query string."""
        # Get dependencies manually for Strawberry
        db = await get_db().__anext__()
        try:
            search_filter = (
                Company.name.ilike(f"%{query}%") |
                Company.description.ilike(f"%{query}%") |
                Company.industry.ilike(f"%{query}%")
            )
            
            result = await db.execute(
                select(Company)
                .where(search_filter)
                .order_by(Company.name)
                .limit(limit)
            )
            companies = result.scalars().all()
            
            return [
                CompanyType(
                    id=str(company.id),
                    name=company.name,
                    slug=company.slug,
                    description=company.description,
                    website=company.website,
                    logo_url=company.logo_url,
                    industry=company.industry,
                    company_size=company.company_size,
                    founded_year=company.founded_year,
                    email=company.email,
                    phone=company.phone,
                    linkedin_url=company.linkedin_url,
                    twitter_handle=company.twitter_handle,
                    glassdoor_id=company.glassdoor_id,
                    glassdoor_rating=company.glassdoor_rating,
                    glassdoor_review_count=company.glassdoor_review_count,
                    ai_research_data=company.ai_research_data,
                    ai_research_model=company.ai_research_model,
                    ai_research_status=company.ai_research_status,
                    ai_research_generated_at=company.ai_research_generated_at,
                    created_at=company.created_at,
                )
                for company in companies
            ]
        finally:
            await db.close()