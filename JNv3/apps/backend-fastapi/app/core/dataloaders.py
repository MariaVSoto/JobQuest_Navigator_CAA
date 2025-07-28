"""
DataLoader implementations for GraphQL to prevent N+1 query problems.
Provides efficient batch loading for related data in GraphQL resolvers.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
import asyncio
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.job import Job, Company, JobApplication


class BaseDataLoader:
    """Base DataLoader class with common functionality."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self._cache: Dict[str, Any] = {}
        self._batch_requests: Dict[str, List] = defaultdict(list)
        self._batch_promises: Dict[str, List] = defaultdict(list)
    
    async def _execute_batch(self, loader_key: str, batch_fn, keys: List[Any]) -> List[Any]:
        """Execute a batch load operation with caching."""
        cache_key = f"{loader_key}:{','.join(str(k) for k in keys)}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        results = await batch_fn(keys)
        self._cache[cache_key] = results
        return results


class CompanyDataLoader(BaseDataLoader):
    """DataLoader for Company entities to prevent N+1 queries when loading job companies."""
    
    async def load(self, company_id: UUID) -> Optional[Company]:
        """Load a single company by ID."""
        companies = await self.load_many([company_id])
        return companies[0] if companies else None
    
    async def load_many(self, company_ids: List[UUID]) -> List[Optional[Company]]:
        """Batch load multiple companies by their IDs."""
        if not company_ids:
            return []
        
        return await self._execute_batch(
            "companies", 
            self._batch_load_companies, 
            company_ids
        )
    
    async def _batch_load_companies(self, company_ids: List[UUID]) -> List[Optional[Company]]:
        """Execute the actual batch query for companies."""
        query = select(Company).where(Company.id.in_(company_ids))
        result = await self.db_session.execute(query)
        companies = result.scalars().all()
        
        # Create a mapping for O(1) lookup
        company_map = {company.id: company for company in companies}
        
        # Return companies in the same order as requested IDs
        return [company_map.get(company_id) for company_id in company_ids]


class UserDataLoader(BaseDataLoader):
    """DataLoader for User entities to prevent N+1 queries when loading job creators."""
    
    async def load(self, user_id: UUID) -> Optional[User]:
        """Load a single user by ID."""
        users = await self.load_many([user_id])
        return users[0] if users else None
    
    async def load_many(self, user_ids: List[UUID]) -> List[Optional[User]]:
        """Batch load multiple users by their IDs."""
        if not user_ids:
            return []
        
        return await self._execute_batch(
            "users",
            self._batch_load_users,
            user_ids
        )
    
    async def _batch_load_users(self, user_ids: List[UUID]) -> List[Optional[User]]:
        """Execute the actual batch query for users."""
        query = select(User).where(User.id.in_(user_ids))
        result = await self.db_session.execute(query)
        users = result.scalars().all()
        
        # Create a mapping for O(1) lookup
        user_map = {user.id: user for user in users}
        
        # Return users in the same order as requested IDs
        return [user_map.get(user_id) for user_id in user_ids]


class JobApplicationDataLoader(BaseDataLoader):
    """DataLoader for JobApplication entities to efficiently load user application status."""
    
    async def load_user_application_for_job(self, user_id: UUID, job_id: UUID) -> Optional[JobApplication]:
        """Load application status for a specific user and job."""
        applications = await self.load_user_applications_for_jobs(user_id, [job_id])
        return applications.get(job_id)
    
    async def load_user_applications_for_jobs(
        self, 
        user_id: UUID, 
        job_ids: List[UUID]
    ) -> Dict[UUID, Optional[JobApplication]]:
        """Batch load user applications for multiple jobs."""
        if not job_ids:
            return {}
        
        cache_key = f"user_applications:{user_id}"
        
        if cache_key not in self._cache:
            applications = await self._batch_load_user_applications(user_id, job_ids)
            self._cache[cache_key] = applications
        
        cached_applications = self._cache[cache_key]
        return {job_id: cached_applications.get(job_id) for job_id in job_ids}
    
    async def _batch_load_user_applications(
        self, 
        user_id: UUID, 
        job_ids: List[UUID]
    ) -> Dict[UUID, JobApplication]:
        """Execute the actual batch query for user applications."""
        query = select(JobApplication).where(
            JobApplication.user_id == user_id,
            JobApplication.job_id.in_(job_ids)
        )
        result = await self.db_session.execute(query)
        applications = result.scalars().all()
        
        # Create a mapping by job_id
        return {app.job_id: app for app in applications}


class JobDataLoader(BaseDataLoader):
    """DataLoader for Job entities with eager loading of related data."""
    
    async def load(self, job_id: UUID) -> Optional[Job]:
        """Load a single job by ID with related data."""
        jobs = await self.load_many([job_id])
        return jobs[0] if jobs else None
    
    async def load_many(self, job_ids: List[UUID]) -> List[Optional[Job]]:
        """Batch load multiple jobs by their IDs with related data."""
        if not job_ids:
            return []
        
        return await self._execute_batch(
            "jobs_with_relations",
            self._batch_load_jobs_with_relations,
            job_ids
        )
    
    async def _batch_load_jobs_with_relations(self, job_ids: List[UUID]) -> List[Optional[Job]]:
        """Execute the actual batch query for jobs with eager loading."""
        query = (
            select(Job)
            .options(
                selectinload(Job.company),
                selectinload(Job.posted_by_user)
            )
            .where(Job.id.in_(job_ids))
        )
        result = await self.db_session.execute(query)
        jobs = result.scalars().all()
        
        # Create a mapping for O(1) lookup
        job_map = {job.id: job for job in jobs}
        
        # Return jobs in the same order as requested IDs
        return [job_map.get(job_id) for job_id in job_ids]


class DataLoaderRegistry:
    """Registry to manage all DataLoader instances for a request."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self._loaders: Dict[str, BaseDataLoader] = {}
    
    def get_company_loader(self) -> CompanyDataLoader:
        """Get or create CompanyDataLoader instance."""
        if 'company' not in self._loaders:
            self._loaders['company'] = CompanyDataLoader(self.db_session)
        return self._loaders['company']
    
    def get_user_loader(self) -> UserDataLoader:
        """Get or create UserDataLoader instance."""
        if 'user' not in self._loaders:
            self._loaders['user'] = UserDataLoader(self.db_session)
        return self._loaders['user']
    
    def get_job_application_loader(self) -> JobApplicationDataLoader:
        """Get or create JobApplicationDataLoader instance."""
        if 'job_application' not in self._loaders:
            self._loaders['job_application'] = JobApplicationDataLoader(self.db_session)
        return self._loaders['job_application']
    
    def get_job_loader(self) -> JobDataLoader:
        """Get or create JobDataLoader instance."""
        if 'job' not in self._loaders:
            self._loaders['job'] = JobDataLoader(self.db_session)
        return self._loaders['job']
    
    def clear_cache(self):
        """Clear all cached data in all loaders."""
        for loader in self._loaders.values():
            loader._cache.clear()


# Context manager for DataLoader lifecycle
class DataLoaderContext:
    """Context manager to handle DataLoader lifecycle in GraphQL requests."""
    
    def __init__(self, db_session: AsyncSession):
        self.registry = DataLoaderRegistry(db_session)
    
    async def __aenter__(self):
        return self.registry
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Clear cache after request to prevent memory leaks
        self.registry.clear_cache()


# Helper function to get DataLoader registry from GraphQL context
def get_dataloaders(info) -> DataLoaderRegistry:
    """Get DataLoader registry from GraphQL execution context."""
    if not hasattr(info.context, 'dataloaders'):
        # Create new registry if not exists
        info.context.dataloaders = DataLoaderRegistry(info.context.db_session)
    
    return info.context.dataloaders