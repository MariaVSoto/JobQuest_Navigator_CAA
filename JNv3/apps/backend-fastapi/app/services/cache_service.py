"""
Enhanced Redis Cache Service for JobQuest Navigator
Provides comprehensive caching functionality with invalidation strategies
"""

import json
import hashlib
import logging
from typing import Any, Optional, Dict, List, Union, Callable
from datetime import datetime, timedelta
import redis.asyncio as redis_async
from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Enhanced async Redis cache service with comprehensive caching strategies"""
    
    def __init__(self):
        self.redis_client: Optional[redis_async.Redis] = None
        
        # TTL configurations for different data types
        self.ttl_config = {
            "default": 300,         # 5 minutes default TTL
            "search": 180,          # 3 minutes for search results
            "company": 3600,        # 1 hour for company data
            "user": 1800,           # 30 minutes for user data
            "job_detail": 600,      # 10 minutes for individual job details
            "graphql_query": 300,   # 5 minutes for GraphQL query results
            "application": 900,     # 15 minutes for application data
            "session": 86400,       # 24 hours for session data
        }
        
        # Cache key patterns for organized invalidation
        self.key_patterns = {
            "jobs": "jobquest:jobs:*",
            "companies": "jobquest:company:*",
            "users": "jobquest:user:*",
            "applications": "jobquest:application:*",
            "search": "jobquest:search:*",
            "graphql": "jobquest:graphql:*",
        }
    
    async def connect(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis_async.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            await self.redis_client.ping()
            print("✅ Redis cache service connected")
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            self.redis_client = None
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate consistent cache key from parameters"""
        # Sort parameters for consistent key generation
        sorted_params = sorted(kwargs.items())
        params_str = json.dumps(sorted_params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"jobquest:{prefix}:{params_hash}"
    
    async def get_job_search_results(
        self, 
        limit: int = 20,
        offset: int = 0,
        search: Optional[str] = None,
        location: Optional[str] = None,
        job_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        remote_type: Optional[str] = None,
        user_created: Optional[bool] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Get cached job search results"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._generate_cache_key(
                "jobs",
                limit=limit,
                offset=offset,
                search=search,
                location=location,
                job_type=job_type,
                experience_level=experience_level,
                remote_type=remote_type,
                user_created=user_created
            )
            
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                print(f"🚀 Cache hit for job search: {cache_key}")
                return json.loads(cached_data)
            
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set_job_search_results(
        self,
        results: List[Dict[str, Any]],
        limit: int = 20,
        offset: int = 0,
        search: Optional[str] = None,
        location: Optional[str] = None,
        job_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        remote_type: Optional[str] = None,
        user_created: Optional[bool] = None
    ) -> bool:
        """Cache job search results"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_cache_key(
                "jobs",
                limit=limit,
                offset=offset,
                search=search,
                location=location,
                job_type=job_type,
                experience_level=experience_level,
                remote_type=remote_type,
                user_created=user_created
            )
            
            # Add cache metadata
            cache_data = {
                "results": results,
                "cached_at": datetime.utcnow().isoformat(),
                "params": {
                    "limit": limit,
                    "offset": offset,
                    "search": search,
                    "location": location,
                    "job_type": job_type,
                    "experience_level": experience_level,
                    "remote_type": remote_type,
                    "user_created": user_created
                }
            }
            
            await self.redis_client.setex(
                cache_key,
                self.search_ttl,
                json.dumps(cache_data, default=str)
            )
            
            print(f"💾 Cached job search results: {cache_key}")
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def get_company_data(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get cached company data"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = f"jobquest:company:{company_id}"
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                print(f"🚀 Cache hit for company: {company_id}")
                return json.loads(cached_data)
            return None
        except Exception as e:
            print(f"Cache get error for company {company_id}: {e}")
            return None
    
    async def set_company_data(self, company_id: str, company_data: Dict[str, Any]) -> bool:
        """Cache company data"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = f"jobquest:company:{company_id}"
            await self.redis_client.setex(
                cache_key,
                self.company_ttl,
                json.dumps(company_data, default=str)
            )
            print(f"💾 Cached company data: {company_id}")
            return True
        except Exception as e:
            print(f"Cache set error for company {company_id}: {e}")
            return False
    
    async def invalidate_job_caches(self):
        """Invalidate all job-related caches (call when jobs are created/updated)"""
        if not self.redis_client:
            return
        
        try:
            # Find all job search cache keys
            job_keys = await self.redis_client.keys("jobquest:jobs:*")
            if job_keys:
                await self.redis_client.delete(*job_keys)
                print(f"🗑️ Invalidated {len(job_keys)} job search cache entries")
        except Exception as e:
            print(f"Cache invalidation error: {e}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        if not self.redis_client:
            return {"status": "disconnected"}
        
        try:
            info = await self.redis_client.info()
            job_keys = await self.redis_client.keys("jobquest:jobs:*")
            company_keys = await self.redis_client.keys("jobquest:company:*")
            
            return {
                "status": "connected",
                "total_keys": info.get("db0", {}).get("keys", 0),
                "job_cache_entries": len(job_keys),
                "company_cache_entries": len(company_keys),
                "memory_used": info.get("used_memory_human", "N/A"),
                "uptime": info.get("uptime_in_seconds", 0)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Global cache service instance
cache_service = CacheService()


async def get_cache_service() -> CacheService:
    """Dependency for getting cache service"""
    if not cache_service.redis_client:
        await cache_service.connect()
    return cache_service