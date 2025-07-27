"""
Performance monitoring and metrics collection for JobQuest Navigator v2
"""

import time
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from collections import defaultdict, deque
import psutil
import traceback

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Single metric measurement point."""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class RequestMetrics:
    """Metrics for a single HTTP request."""
    path: str
    method: str
    status_code: int
    duration_ms: float
    timestamp: datetime
    user_id: Optional[str] = None
    graphql_operation: Optional[str] = None
    database_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: List[str] = field(default_factory=list)


class MetricsCollector:
    """Collects and aggregates application metrics."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        
        # Request metrics
        self.request_history: deque = deque(maxlen=max_history)
        self.active_requests: Dict[str, datetime] = {}
        
        # Performance metrics
        self.response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.request_counts: Dict[str, int] = defaultdict(int)
        
        # Database metrics
        self.db_query_times: deque = deque(maxlen=100)
        self.db_connection_pool_stats: Dict[str, Any] = {}
        
        # Cache metrics
        self.cache_hit_rate: deque = deque(maxlen=100)
        self.cache_operations: deque = deque(maxlen=100)
        
        # System metrics
        self.system_metrics: Dict[str, deque] = {
            "cpu_percent": deque(maxlen=60),  # Last 60 measurements
            "memory_percent": deque(maxlen=60),
            "memory_used_mb": deque(maxlen=60),
        }
        
        # Start background metrics collection
        self._start_system_monitoring()
    
    def record_request(self, metrics: RequestMetrics):
        """Record metrics for a completed request."""
        self.request_history.append(metrics)
        
        # Update aggregated metrics
        endpoint_key = f"{metrics.method}:{metrics.path}"
        self.response_times[endpoint_key].append(metrics.duration_ms)
        self.request_counts[endpoint_key] += 1
        
        if metrics.status_code >= 400:
            self.error_counts[endpoint_key] += 1
        
        logger.debug(f"Request metrics recorded: {endpoint_key} - {metrics.duration_ms:.2f}ms")
    
    def record_db_query(self, duration_ms: float):
        """Record database query execution time."""
        self.db_query_times.append(duration_ms)
    
    def record_cache_operation(self, operation_type: str, hit: bool, duration_ms: float):
        """Record cache operation metrics."""
        self.cache_operations.append({
            "type": operation_type,
            "hit": hit,
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow()
        })
        
        # Update hit rate calculation
        recent_ops = list(self.cache_operations)[-50:]  # Last 50 operations
        if recent_ops:
            hits = sum(1 for op in recent_ops if op["hit"])
            hit_rate = (hits / len(recent_ops)) * 100
            self.cache_hit_rate.append(hit_rate)
    
    def _start_system_monitoring(self):
        """Start background task for system metrics collection."""
        async def collect_system_metrics():
            while True:
                try:
                    # CPU and memory metrics
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    
                    self.system_metrics["cpu_percent"].append(cpu_percent)
                    self.system_metrics["memory_percent"].append(memory.percent)
                    self.system_metrics["memory_used_mb"].append(memory.used / (1024 * 1024))
                    
                    await asyncio.sleep(30)  # Collect every 30 seconds
                except Exception as e:
                    logger.error(f"Error collecting system metrics: {e}")
                    await asyncio.sleep(60)  # Longer wait on error
        
        # Start the background task
        asyncio.create_task(collect_system_metrics())
    
    def get_performance_summary(self, minutes: int = 15) -> Dict[str, Any]:
        """Get performance summary for the last N minutes."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        recent_requests = [
            req for req in self.request_history 
            if req.timestamp >= cutoff_time
        ]
        
        if not recent_requests:
            return {"message": "No recent requests", "timeframe_minutes": minutes}
        
        # Calculate aggregated metrics
        total_requests = len(recent_requests)
        avg_response_time = sum(req.duration_ms for req in recent_requests) / total_requests
        error_count = sum(1 for req in recent_requests if req.status_code >= 400)
        error_rate = (error_count / total_requests) * 100
        
        # Response time percentiles
        response_times = sorted([req.duration_ms for req in recent_requests])
        p50_idx = int(len(response_times) * 0.5)
        p95_idx = int(len(response_times) * 0.95)
        p99_idx = int(len(response_times) * 0.99)
        
        # Slowest endpoints
        endpoint_times = defaultdict(list)
        for req in recent_requests:
            endpoint_key = f"{req.method}:{req.path}"
            endpoint_times[endpoint_key].append(req.duration_ms)
        
        slowest_endpoints = sorted([
            {
                "endpoint": endpoint,
                "avg_response_time": sum(times) / len(times),
                "request_count": len(times)
            }
            for endpoint, times in endpoint_times.items()
        ], key=lambda x: x["avg_response_time"], reverse=True)[:5]
        
        return {
            "timeframe_minutes": minutes,
            "total_requests": total_requests,
            "avg_response_time_ms": round(avg_response_time, 2),
            "error_rate_percent": round(error_rate, 2),
            "error_count": error_count,
            "response_time_percentiles": {
                "p50": response_times[p50_idx] if p50_idx < len(response_times) else 0,
                "p95": response_times[p95_idx] if p95_idx < len(response_times) else 0,
                "p99": response_times[p99_idx] if p99_idx < len(response_times) else 0,
            },
            "slowest_endpoints": slowest_endpoints,
            "system_metrics": {
                "cpu_percent": list(self.system_metrics["cpu_percent"])[-5:] if self.system_metrics["cpu_percent"] else [],
                "memory_percent": list(self.system_metrics["memory_percent"])[-5:] if self.system_metrics["memory_percent"] else [],
                "memory_used_mb": list(self.system_metrics["memory_used_mb"])[-5:] if self.system_metrics["memory_used_mb"] else [],
            },
            "cache_hit_rate": list(self.cache_hit_rate)[-10:] if self.cache_hit_rate else [],
            "database_query_times": list(self.db_query_times)[-10:] if self.db_query_times else [],
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get application health status with key metrics."""
        recent_summary = self.get_performance_summary(minutes=5)
        
        # Determine health status
        health_issues = []
        status = "healthy"
        
        # Check error rate
        error_rate = recent_summary.get("error_rate_percent", 0)
        if error_rate > 10:
            health_issues.append(f"High error rate: {error_rate:.1f}%")
            status = "unhealthy"
        elif error_rate > 5:
            health_issues.append(f"Elevated error rate: {error_rate:.1f}%")
            status = "degraded"
        
        # Check response time
        avg_response_time = recent_summary.get("avg_response_time_ms", 0)
        if avg_response_time > 2000:
            health_issues.append(f"Slow response time: {avg_response_time:.0f}ms")
            status = "unhealthy"
        elif avg_response_time > 1000:
            health_issues.append(f"Elevated response time: {avg_response_time:.0f}ms")
            status = "degraded"
        
        # Check system resources
        cpu_values = list(self.system_metrics["cpu_percent"])
        memory_values = list(self.system_metrics["memory_percent"])
        
        if cpu_values and cpu_values[-1] > 90:
            health_issues.append(f"High CPU usage: {cpu_values[-1]:.1f}%")
            status = "unhealthy"
        
        if memory_values and memory_values[-1] > 90:
            health_issues.append(f"High memory usage: {memory_values[-1]:.1f}%")
            status = "unhealthy"
        
        return {
            "status": status,
            "issues": health_issues,
            "summary": recent_summary,
            "timestamp": datetime.utcnow().isoformat(),
        }


# Global metrics collector instance
metrics_collector = MetricsCollector()


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to collect performance metrics for all HTTP requests."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = id(request)
        
        # Track active request
        metrics_collector.active_requests[str(request_id)] = datetime.utcnow()
        
        # Extract user context if available
        user_id = None
        if hasattr(request.state, 'user') and request.state.user:
            user_id = str(request.state.user.id)
        
        response = None
        errors = []
        
        try:
            # Execute request
            response = await call_next(request)
        except Exception as e:
            errors.append(str(e))
            logger.error(f"Request failed: {e}\n{traceback.format_exc()}")
            raise
        finally:
            # Calculate metrics
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            # Clean up active request tracking
            metrics_collector.active_requests.pop(str(request_id), None)
            
            # Record metrics
            request_metrics = RequestMetrics(
                path=request.url.path,
                method=request.method,
                status_code=response.status_code if response else 500,
                duration_ms=duration_ms,
                timestamp=datetime.utcnow(),
                user_id=user_id,
                errors=errors
            )
            
            # Extract GraphQL operation name if this is a GraphQL request
            if request.url.path.endswith('/graphql') and hasattr(request.state, 'graphql_operation'):
                request_metrics.graphql_operation = request.state.graphql_operation
            
            metrics_collector.record_request(request_metrics)
            
            # Add performance headers to response
            if response:
                response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
                response.headers["X-Request-ID"] = str(request_id)
        
        return response


@asynccontextmanager
async def track_database_query():
    """Context manager to track database query performance."""
    start_time = time.time()
    try:
        yield
    finally:
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        metrics_collector.record_db_query(duration_ms)


@asynccontextmanager  
async def track_cache_operation(operation_type: str):
    """Context manager to track cache operation performance."""
    start_time = time.time()
    hit = False
    try:
        yield {"hit": lambda: setattr(locals(), 'hit', True)}
    finally:
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        metrics_collector.record_cache_operation(operation_type, hit, duration_ms)


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return metrics_collector