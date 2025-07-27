"""
GraphQL Cache Middleware for intelligent query result caching
"""

import hashlib
import json
import logging
from typing import Any, Dict, Optional, List
from datetime import datetime

from strawberry.extensions import Extension
from strawberry.types import ExecutionResult

from app.services.enhanced_cache_service import get_enhanced_cache_service

logger = logging.getLogger(__name__)


class GraphQLCacheExtension(Extension):
    """
    Strawberry extension for caching GraphQL query results.
    Provides intelligent caching with user context awareness.
    """
    
    def __init__(self):
        self.cache_service = None
        
        # Queries that should not be cached
        self.no_cache_operations = {
            "mutation",  # Never cache mutations
            "subscription",  # Never cache subscriptions
        }
        
        # Field patterns that should not be cached (contain user-specific or real-time data)
        self.no_cache_fields = {
            "currentUser",
            "myProfile", 
            "myApplications",
            "notifications",
            "realTimeData",
        }
        
        # Custom TTL for specific operations
        self.operation_ttl = {
            "getJobs": 180,        # 3 minutes for job listings
            "getJob": 600,         # 10 minutes for job details
            "getCompanies": 3600,  # 1 hour for company listings
            "searchJobs": 120,     # 2 minutes for search results
            "getUserProfile": 1800, # 30 minutes for user profiles (if not current user)
        }
    
    async def on_request_start(self):
        """Initialize cache service for this request."""
        self.cache_service = await get_enhanced_cache_service()
    
    def _should_cache_operation(self, operation_name: str, operation_type: str, query_fields: List[str]) -> bool:
        """Determine if an operation should be cached."""
        # Don't cache mutations or subscriptions
        if operation_type.lower() in self.no_cache_operations:
            return False
        
        # Don't cache if any field is in the no-cache list
        for field in query_fields:
            if any(no_cache_field in field for no_cache_field in self.no_cache_fields):
                return False
        
        return True
    
    def _extract_query_fields(self, query: str) -> List[str]:
        """Extract field names from GraphQL query (simple implementation)."""
        # This is a simplified field extraction
        # In production, you might want to use a proper GraphQL parser
        fields = []
        lines = query.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and '{' not in line and '}' not in line:
                # Extract field name (before any parentheses or spaces)
                field_name = line.split('(')[0].split(' ')[0].strip()
                if field_name and not field_name.startswith('__'):  # Skip introspection fields
                    fields.append(field_name)
        return fields
    
    def _generate_cache_key(
        self, 
        operation_name: str, 
        query: str, 
        variables: Optional[Dict], 
        user_id: Optional[str]
    ) -> str:
        """Generate cache key for GraphQL operation."""
        # Create a deterministic hash of the query and variables
        query_hash = hashlib.md5(query.encode()).hexdigest()[:16]
        
        # Include variables in cache key
        variables_str = json.dumps(variables or {}, sort_keys=True, default=str)
        variables_hash = hashlib.md5(variables_str.encode()).hexdigest()[:8]
        
        # Include user context for user-specific caching
        user_context = f"user:{user_id}" if user_id else "anonymous"
        
        return f"jobquest:graphql:{operation_name}:{query_hash}:{variables_hash}:{user_context}"
    
    def _get_operation_ttl(self, operation_name: str) -> int:
        """Get TTL for a specific operation."""
        return self.operation_ttl.get(operation_name, 300)  # Default 5 minutes
    
    async def on_execute(self):
        """Hook into GraphQL execution to implement caching."""
        if not self.cache_service:
            # Cache service not available, proceed with execution
            yield
            return
        
        execution_context = self.execution_context
        operation_name = execution_context.operation_name
        query = execution_context.query
        variables = execution_context.variable_values
        
        # Get user context (if available)
        user_id = None
        if hasattr(execution_context.context, 'user') and execution_context.context.user:
            user_id = str(execution_context.context.user.id)
        
        # Extract operation type and fields
        operation_type = "query"  # Default to query
        if query:
            query_str = str(query)
            if query_str.strip().startswith('mutation'):
                operation_type = "mutation"
            elif query_str.strip().startswith('subscription'):
                operation_type = "subscription"
        
        query_fields = self._extract_query_fields(str(query))
        
        # Check if we should cache this operation
        should_cache = self._should_cache_operation(
            operation_name or "unknown", 
            operation_type, 
            query_fields
        )
        
        if not should_cache:
            logger.debug(f"Skipping cache for operation: {operation_name} (type: {operation_type})")
            yield
            return
        
        # Generate cache key
        cache_key = self._generate_cache_key(
            operation_name or "unknown",
            str(query),
            variables,
            user_id
        )
        
        # Try to get from cache
        try:
            cached_result = await self.cache_service.get(cache_key)
            if cached_result:
                logger.debug(f"GraphQL cache hit: {operation_name}")
                
                # Return cached result
                yield ExecutionResult(
                    data=cached_result.get("data"),
                    errors=cached_result.get("errors"),
                    extensions={"cached": True, "cached_at": cached_result.get("cached_at")}
                )
                return
        except Exception as e:
            logger.error(f"Error retrieving from cache: {e}")
        
        # Cache miss - execute query and cache result
        logger.debug(f"GraphQL cache miss: {operation_name}")
        
        # Execute the GraphQL operation
        result = yield
        
        # Cache the result if successful and cacheable
        if result and not result.errors:
            try:
                cache_data = {
                    "data": result.data,
                    "errors": result.errors,
                    "cached_at": datetime.utcnow().isoformat(),
                    "operation_name": operation_name,
                    "user_id": user_id
                }
                
                ttl = self._get_operation_ttl(operation_name or "unknown")
                await self.cache_service.set(cache_key, cache_data, ttl)
                
                logger.debug(f"Cached GraphQL result: {operation_name} (TTL: {ttl}s)")
                
                # Add cache metadata to response
                if not result.extensions:
                    result.extensions = {}
                result.extensions["cached"] = False
                result.extensions["cache_key"] = cache_key
                
            except Exception as e:
                logger.error(f"Error caching GraphQL result: {e}")


class SmartCacheExtension(Extension):
    """
    Advanced caching extension with dependency tracking and smart invalidation.
    """
    
    def __init__(self):
        self.cache_service = None
        self.dependency_tracker = {
            # Define which operations depend on which data types
            "getJobs": ["job", "company"],
            "getJob": ["job", "company", "user"],
            "searchJobs": ["job", "company"],
            "getCompanies": ["company"],
            "getUserProfile": ["user"],
            "getJobApplications": ["application", "job", "user"],
        }
    
    async def on_request_start(self):
        """Initialize cache service."""
        self.cache_service = await get_enhanced_cache_service()
    
    def _get_cache_tags(self, operation_name: str, variables: Dict) -> List[str]:
        """Generate cache tags for dependency tracking."""
        tags = []
        
        # Add operation-specific tags
        if operation_name in self.dependency_tracker:
            tags.extend(self.dependency_tracker[operation_name])
        
        # Add entity-specific tags based on variables
        if "jobId" in variables:
            tags.append(f"job:{variables['jobId']}")
        if "userId" in variables:
            tags.append(f"user:{variables['userId']}")
        if "companyId" in variables:
            tags.append(f"company:{variables['companyId']}")
        
        return tags
    
    async def invalidate_by_tags(self, tags: List[str]):
        """Invalidate cache entries by tags."""
        if not self.cache_service:
            return
        
        for tag in tags:
            pattern = f"jobquest:graphql:*:{tag}:*"
            await self.cache_service.invalidate_pattern(pattern)


# Utility functions for manual cache operations

async def invalidate_graphql_cache_for_user(user_id: str):
    """Invalidate all cached GraphQL results for a specific user."""
    cache_service = await get_enhanced_cache_service()
    pattern = f"jobquest:graphql:*:user:{user_id}"
    await cache_service.invalidate_pattern(pattern)


async def invalidate_graphql_cache_for_operation(operation_name: str):
    """Invalidate all cached results for a specific GraphQL operation."""
    cache_service = await get_enhanced_cache_service()
    pattern = f"jobquest:graphql:{operation_name}:*"
    await cache_service.invalidate_pattern(pattern)


async def get_graphql_cache_stats() -> Dict[str, Any]:
    """Get GraphQL-specific cache statistics."""
    cache_service = await get_enhanced_cache_service()
    
    if not cache_service.redis_client:
        return {"status": "unavailable"}
    
    try:
        # Count GraphQL cache entries
        graphql_keys = await cache_service.redis_client.keys("jobquest:graphql:*")
        
        # Group by operation
        operation_counts = {}
        for key in graphql_keys:
            parts = key.split(":")
            if len(parts) >= 3:
                operation = parts[2]
                operation_counts[operation] = operation_counts.get(operation, 0) + 1
        
        return {
            "status": "available",
            "total_cached_operations": len(graphql_keys),
            "operations_breakdown": operation_counts,
            "cache_keys_sample": graphql_keys[:10]  # First 10 keys for debugging
        }
    except Exception as e:
        logger.error(f"Error getting GraphQL cache stats: {e}")
        return {"status": "error", "error": str(e)}