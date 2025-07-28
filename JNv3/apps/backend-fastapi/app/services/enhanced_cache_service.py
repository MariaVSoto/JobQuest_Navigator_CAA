"""
Enhanced Cache Service with advanced caching strategies and invalidation
"""

import json
import hashlib
import logging
from typing import Any, Optional, Dict, List, Union, Callable, Set
from datetime import datetime, timedelta
import redis.asyncio as redis_async
from functools import wraps
import asyncio

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheInvalidationStrategy:
    """Manages cache invalidation patterns and dependencies."""
    
    def __init__(self):
        # Define invalidation dependencies
        self.invalidation_map = {
            "user_update": ["user:*", "graphql:user:*"],
            "job_create": ["jobs:*", "search:*", "graphql:jobs:*"],
            "job_update": ["jobs:*", "job:{job_id}:*", "search:*", "graphql:jobs:*"],
            "job_delete": ["jobs:*", "job:{job_id}:*", "search:*", "graphql:jobs:*"],
            "company_update": ["company:{company_id}:*", "jobs:*", "search:*"],
            "application_create": ["application:user:{user_id}:*", "jobs:*"],
            "application_update": ["application:{application_id}:*", "application:user:{user_id}:*"],
        }
    
    def get_patterns_to_invalidate(self, event: str, **context) -> List[str]:
        """Get cache patterns to invalidate for a given event."""
        patterns = self.invalidation_map.get(event, [])
        
        # Format patterns with context variables
        formatted_patterns = []
        for pattern in patterns:
            try:
                formatted_pattern = pattern.format(**context)
                formatted_patterns.append(f"jobquest:{formatted_pattern}")
            except KeyError:
                # If context is missing, use the pattern as-is
                formatted_patterns.append(f"jobquest:{pattern}")
        
        return formatted_patterns


class EnhancedCacheService:
    """Advanced caching service with intelligent invalidation and performance monitoring."""
    
    def __init__(self):
        self.redis_client: Optional[redis_async.Redis] = None
        self.invalidation_strategy = CacheInvalidationStrategy()
        
        # Performance tracking
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "invalidations": 0,
        }
        
        # TTL configurations
        self.ttl_config = {
            "default": 300,
            "search": 180,
            "company": 3600,
            "user": 1800,
            "job_detail": 600,
            "graphql_query": 300,
            "application": 900,
            "session": 86400,
        }
    
    async def connect(self):
        """Initialize Redis connection with retry logic."""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                self.redis_client = redis_async.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30,
                )
                await self.redis_client.ping()
                logger.info("✅ Enhanced Redis cache service connected")
                return
            except Exception as e:
                logger.warning(f"Redis connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error("❌ Redis connection failed after all retries")
                    self.redis_client = None
    
    async def disconnect(self):
        """Close Redis connection gracefully."""
        if self.redis_client:
            try:
                await self.redis_client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
    
    def _generate_cache_key(self, category: str, identifier: str, **params) -> str:
        """Generate hierarchical cache key with consistent hashing."""
        if params:
            # Sort parameters for consistent key generation
            sorted_params = sorted(params.items())
            params_str = json.dumps(sorted_params, sort_keys=True)
            params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
            return f"jobquest:{category}:{identifier}:{params_hash}"
        else:
            return f"jobquest:{category}:{identifier}"
    
    async def get_or_set(
        self, 
        key: str, 
        fetch_func: Callable, 
        ttl: Optional[int] = None,
        category: str = "default"
    ) -> Any:
        """
        Get cached value or execute fetch function and cache the result.
        This is the primary caching pattern.
        """
        if not self.redis_client:
            return await fetch_func()
        
        try:
            # Try to get from cache
            cached_value = await self.redis_client.get(key)
            if cached_value:
                self.cache_stats["hits"] += 1
                logger.debug(f"Cache hit: {key}")
                return json.loads(cached_value)
            
            # Cache miss - fetch data
            self.cache_stats["misses"] += 1
            logger.debug(f"Cache miss: {key}")
            
            data = await fetch_func()
            if data is not None:
                await self.set(key, data, ttl or self.ttl_config.get(category, self.ttl_config["default"]))
            
            return data
            
        except Exception as e:
            logger.error(f"Cache get_or_set error for key {key}: {e}")
            return await fetch_func()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis_client:
            return None
        
        try:
            cached_value = await self.redis_client.get(key)
            if cached_value:
                self.cache_stats["hits"] += 1
                return json.loads(cached_value)
            else:
                self.cache_stats["misses"] += 1
                return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in cache with TTL."""
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.setex(
                key,
                ttl,
                json.dumps(value, default=str, ensure_ascii=False)
            )
            self.cache_stats["sets"] += 1
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete specific key from cache."""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            if result:
                logger.debug(f"Cache deleted: {key}")
            return bool(result)
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern."""
        if not self.redis_client:
            return 0
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                deleted = await self.redis_client.delete(*keys)
                self.cache_stats["invalidations"] += deleted
                logger.info(f"Invalidated {deleted} keys matching pattern: {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache invalidation error for pattern {pattern}: {e}")
            return 0
    
    async def invalidate_by_event(self, event: str, **context) -> int:
        """Invalidate cache based on application events."""
        patterns = self.invalidation_strategy.get_patterns_to_invalidate(event, **context)
        total_invalidated = 0
        
        for pattern in patterns:
            invalidated = await self.invalidate_pattern(pattern)
            total_invalidated += invalidated
        
        logger.info(f"Event '{event}' invalidated {total_invalidated} cache entries")
        return total_invalidated
    
    # GraphQL-specific caching methods
    
    async def cache_graphql_query(
        self, 
        query: str, 
        variables: Dict[str, Any], 
        user_id: Optional[str],
        result: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Cache GraphQL query results."""
        cache_key = self._generate_cache_key(
            "graphql",
            "query",
            query_hash=hashlib.md5(query.encode()).hexdigest()[:16],
            variables=variables,
            user_id=user_id
        )
        
        return await self.set(
            cache_key, 
            result, 
            ttl or self.ttl_config["graphql_query"]
        )
    
    async def get_graphql_query_cache(
        self, 
        query: str, 
        variables: Dict[str, Any], 
        user_id: Optional[str]
    ) -> Optional[Any]:
        """Get cached GraphQL query results."""
        cache_key = self._generate_cache_key(
            "graphql",
            "query",
            query_hash=hashlib.md5(query.encode()).hexdigest()[:16],
            variables=variables,
            user_id=user_id
        )
        
        return await self.get(cache_key)
    
    # Specialized caching methods for different data types
    
    async def cache_user_data(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Cache user profile data."""
        key = self._generate_cache_key("user", user_id)
        return await self.set(key, data, self.ttl_config["user"])
    
    async def get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user data."""
        key = self._generate_cache_key("user", user_id)
        return await self.get(key)
    
    async def cache_job_detail(self, job_id: str, data: Dict[str, Any]) -> bool:
        """Cache individual job details."""
        key = self._generate_cache_key("job", job_id)
        return await self.set(key, data, self.ttl_config["job_detail"])
    
    async def get_job_detail(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get cached job details."""
        key = self._generate_cache_key("job", job_id)
        return await self.get(key)
    
    async def cache_search_results(
        self, 
        search_params: Dict[str, Any], 
        results: List[Dict[str, Any]]
    ) -> bool:
        """Cache job search results."""
        key = self._generate_cache_key("search", "jobs", **search_params)
        return await self.set(key, results, self.ttl_config["search"])
    
    async def get_search_results(self, search_params: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Get cached search results."""
        key = self._generate_cache_key("search", "jobs", **search_params)
        return await self.get(key)
    
    # Monitoring and statistics
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_operations = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_operations * 100) if total_operations > 0 else 0
        
        redis_info = {}
        if self.redis_client:
            try:
                redis_info = await self.redis_client.info()
            except Exception as e:
                logger.error(f"Error getting Redis info: {e}")
        
        return {
            "cache_stats": self.cache_stats.copy(),
            "hit_rate_percentage": round(hit_rate, 2),
            "redis_memory_used": redis_info.get("used_memory_human", "N/A"),
            "redis_connected_clients": redis_info.get("connected_clients", 0),
            "total_keys": redis_info.get("db0", {}).get("keys", 0) if "db0" in redis_info else 0,
        }
    
    async def clear_all_cache(self) -> bool:
        """Clear all application cache (use with caution)."""
        if not self.redis_client:
            return False
        
        try:
            keys = await self.redis_client.keys("jobquest:*")
            if keys:
                await self.redis_client.delete(*keys)
                logger.warning(f"Cleared all cache: {len(keys)} keys deleted")
                return True
            return True
        except Exception as e:
            logger.error(f"Error clearing all cache: {e}")
            return False


# Cache decorator for functions
def cached(
    category: str = "default",
    ttl: Optional[int] = None,
    key_func: Optional[Callable] = None
):
    """
    Decorator to cache function results.
    
    Args:
        category: Cache category for TTL configuration
        ttl: Custom TTL in seconds
        key_func: Function to generate cache key from function args
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_service = await get_enhanced_cache_service()
            
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                func_name = f"{func.__module__}.{func.__name__}"
                args_str = json.dumps([str(arg) for arg in args], sort_keys=True)
                kwargs_str = json.dumps(kwargs, sort_keys=True, default=str)
                key_hash = hashlib.md5(f"{args_str}:{kwargs_str}".encode()).hexdigest()[:8]
                cache_key = f"jobquest:func:{func_name}:{key_hash}"
            
            return await cache_service.get_or_set(
                cache_key,
                lambda: func(*args, **kwargs),
                ttl,
                category
            )
        return wrapper
    return decorator


# Global enhanced cache service instance
enhanced_cache_service = EnhancedCacheService()


async def get_enhanced_cache_service() -> EnhancedCacheService:
    """Dependency for getting enhanced cache service."""
    if not enhanced_cache_service.redis_client:
        await enhanced_cache_service.connect()
    return enhanced_cache_service