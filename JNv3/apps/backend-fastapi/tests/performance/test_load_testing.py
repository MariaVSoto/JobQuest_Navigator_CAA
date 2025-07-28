"""
Load testing for JobQuest Navigator v2 backend
Tests performance under various load conditions
"""

import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.core.database import get_db_session
from app.core.monitoring import metrics_collector


class LoadTestResults:
    """Container for load test results and analysis."""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.status_codes: List[int] = []
        self.errors: List[str] = []
        self.start_time: float = 0
        self.end_time: float = 0
        
    def add_result(self, response_time: float, status_code: int, error: str = None):
        """Add a single request result."""
        self.response_times.append(response_time)
        self.status_codes.append(status_code)
        if error:
            self.errors.append(error)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the load test."""
        if not self.response_times:
            return {"error": "No results recorded"}
        
        total_time = self.end_time - self.start_time
        total_requests = len(self.response_times)
        successful_requests = len([code for code in self.status_codes if 200 <= code < 400])
        error_count = len(self.errors)
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "error_count": error_count,
            "error_rate_percent": (error_count / total_requests) * 100 if total_requests > 0 else 0,
            "total_time_seconds": round(total_time, 2),
            "requests_per_second": round(total_requests / total_time, 2) if total_time > 0 else 0,
            "response_time_stats": {
                "min_ms": round(min(self.response_times), 2),
                "max_ms": round(max(self.response_times), 2),
                "mean_ms": round(statistics.mean(self.response_times), 2),
                "median_ms": round(statistics.median(self.response_times), 2),
                "p95_ms": round(statistics.quantiles(self.response_times, n=20)[18], 2),  # 95th percentile
                "p99_ms": round(statistics.quantiles(self.response_times, n=100)[98], 2),  # 99th percentile
            },
            "status_code_distribution": {
                str(code): self.status_codes.count(code) 
                for code in set(self.status_codes)
            }
        }


@pytest.mark.asyncio
@pytest.mark.performance
class TestLoadPerformance:
    """Load testing for API endpoints under various conditions."""
    
    async def make_request(self, client: httpx.AsyncClient, method: str, url: str, **kwargs) -> tuple:
        """Make a single HTTP request and measure performance."""
        start_time = time.time()
        error = None
        status_code = 0
        
        try:
            if method.upper() == "GET":
                response = await client.get(url, **kwargs)
            elif method.upper() == "POST":
                response = await client.post(url, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            status_code = response.status_code
            
        except Exception as e:
            error = str(e)
            status_code = 500
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        return response_time, status_code, error
    
    async def run_concurrent_requests(
        self,
        client: httpx.AsyncClient,
        method: str,
        url: str,
        concurrent_users: int,
        requests_per_user: int,
        **request_kwargs
    ) -> LoadTestResults:
        """Run concurrent requests to test load performance."""
        results = LoadTestResults()
        results.start_time = time.time()
        
        async def user_session():
            """Simulate a single user making multiple requests."""
            for _ in range(requests_per_user):
                response_time, status_code, error = await self.make_request(
                    client, method, url, **request_kwargs
                )
                results.add_result(response_time, status_code, error)
                
                # Small delay between requests to simulate real user behavior
                await asyncio.sleep(0.1)
        
        # Run concurrent user sessions
        tasks = [user_session() for _ in range(concurrent_users)]
        await asyncio.gather(*tasks)
        
        results.end_time = time.time()
        return results
    
    @pytest.mark.slow
    async def test_health_endpoint_load(self):
        """Test health endpoint under load."""
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            results = await self.run_concurrent_requests(
                client=client,
                method="GET",
                url="/health",
                concurrent_users=50,
                requests_per_user=10
            )
            
            summary = results.get_summary()
            
            # Assertions for performance requirements
            assert summary["error_rate_percent"] < 1.0, f"Error rate too high: {summary['error_rate_percent']}%"
            assert summary["response_time_stats"]["p95_ms"] < 100, f"95th percentile too slow: {summary['response_time_stats']['p95_ms']}ms"
            assert summary["requests_per_second"] > 100, f"Throughput too low: {summary['requests_per_second']} RPS"
            
            print(f"Health endpoint performance: {summary}")
    
    @pytest.mark.slow
    async def test_graphql_query_load(self):
        """Test GraphQL queries under load."""
        query = """
        query GetJobs {
            jobs(limit: 10) {
                id
                title
                company {
                    name
                }
                location
            }
        }
        """
        
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            results = await self.run_concurrent_requests(
                client=client,
                method="POST",
                url="/graphql",
                concurrent_users=20,
                requests_per_user=5,
                json={"query": query}
            )
            
            summary = results.get_summary()
            
            # Assertions for GraphQL performance
            assert summary["error_rate_percent"] < 5.0, f"Error rate too high: {summary['error_rate_percent']}%"
            assert summary["response_time_stats"]["p95_ms"] < 500, f"95th percentile too slow: {summary['response_time_stats']['p95_ms']}ms"
            
            print(f"GraphQL query performance: {summary}")
    
    @pytest.mark.slow
    async def test_database_query_performance(self, db_session: AsyncSession):
        """Test database query performance under load."""
        from app.services.job_service import JobService
        
        job_service = JobService(db_session)
        
        async def run_db_queries():
            """Run multiple database queries."""
            start_time = time.time()
            
            tasks = []
            for _ in range(50):  # 50 concurrent queries
                tasks.append(job_service.get_all_jobs(limit=20))
            
            await asyncio.gather(*tasks)
            
            end_time = time.time()
            return end_time - start_time
        
        # Run the test
        total_time = await run_db_queries()
        queries_per_second = 50 / total_time
        
        # Performance assertions
        assert queries_per_second > 10, f"Database query throughput too low: {queries_per_second:.2f} QPS"
        assert total_time < 10, f"Total query time too long: {total_time:.2f}s"
        
        print(f"Database performance: {queries_per_second:.2f} queries/second")


@pytest.mark.asyncio
@pytest.mark.performance
class TestCachePerformance:
    """Test caching system performance."""
    
    @pytest.mark.slow
    async def test_cache_hit_performance(self):
        """Test cache hit rates and performance."""
        from app.services.enhanced_cache_service import get_enhanced_cache_service
        
        cache_service = await get_enhanced_cache_service()
        
        # Warm up cache
        test_data = {"test": "data", "numbers": list(range(100))}
        await cache_service.set("test_key_1", test_data, 3600)
        await cache_service.set("test_key_2", test_data, 3600)
        
        # Measure cache hit performance
        start_time = time.time()
        
        hit_tasks = []
        for i in range(1000):
            key = f"test_key_{(i % 2) + 1}"  # Alternate between 2 cached keys
            hit_tasks.append(cache_service.get(key))
        
        results = await asyncio.gather(*hit_tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all hits were successful
        successful_hits = len([r for r in results if r is not None])
        hit_rate = (successful_hits / len(results)) * 100
        
        # Performance assertions
        assert hit_rate > 95, f"Cache hit rate too low: {hit_rate:.1f}%"
        assert total_time < 1.0, f"Cache access too slow: {total_time:.2f}s for 1000 operations"
        
        cache_ops_per_second = 1000 / total_time
        print(f"Cache performance: {cache_ops_per_second:.0f} operations/second, {hit_rate:.1f}% hit rate")
    
    async def test_cache_invalidation_performance(self):
        """Test cache invalidation performance."""
        from app.services.enhanced_cache_service import get_enhanced_cache_service
        
        cache_service = await get_enhanced_cache_service()
        
        # Create many cache entries
        for i in range(100):
            await cache_service.set(f"test_pattern_{i}", {"data": i}, 3600)
        
        # Measure invalidation performance
        start_time = time.time()
        invalidated = await cache_service.invalidate_pattern("jobquest:test_pattern_*")
        end_time = time.time()
        
        invalidation_time = end_time - start_time
        
        # Performance assertions
        assert invalidated >= 50, f"Not enough keys invalidated: {invalidated}"
        assert invalidation_time < 0.5, f"Invalidation too slow: {invalidation_time:.2f}s"
        
        print(f"Cache invalidation: {invalidated} keys in {invalidation_time:.3f}s")


@pytest.mark.asyncio
@pytest.mark.performance  
class TestMemoryUsage:
    """Test memory usage under load."""
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)  # Convert to MB
    
    @pytest.mark.slow
    async def test_memory_leak_detection(self):
        """Test for memory leaks during sustained load."""
        initial_memory = self.get_memory_usage()
        
        # Run sustained operations
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            for round_num in range(5):  # 5 rounds of requests
                tasks = []
                for _ in range(100):  # 100 requests per round
                    tasks.append(client.get("/health"))
                
                await asyncio.gather(*tasks)
                
                # Check memory usage
                current_memory = self.get_memory_usage()
                memory_increase = current_memory - initial_memory
                
                print(f"Round {round_num + 1}: Memory usage: {current_memory:.1f}MB (+{memory_increase:.1f}MB)")
                
                # Allow some memory growth but not excessive
                assert memory_increase < 100, f"Excessive memory growth: {memory_increase:.1f}MB"
                
                # Small delay between rounds
                await asyncio.sleep(1)
        
        # Final memory check
        final_memory = self.get_memory_usage()
        total_increase = final_memory - initial_memory
        
        print(f"Total memory increase: {total_increase:.1f}MB")
        assert total_increase < 50, f"Potential memory leak detected: {total_increase:.1f}MB increase"


# Utility function to run performance tests
async def run_performance_benchmark():
    """Run a comprehensive performance benchmark."""
    print("Starting performance benchmark...")
    
    benchmark_results = {
        "timestamp": time.time(),
        "system_info": {},
        "test_results": {}
    }
    
    # System information
    import psutil
    benchmark_results["system_info"] = {
        "cpu_count": psutil.cpu_count(),
        "memory_total_mb": psutil.virtual_memory().total / (1024 * 1024),
        "python_version": __import__("sys").version,
    }
    
    # Run basic performance tests
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        # Test 1: Health endpoint baseline
        start_time = time.time()
        response = await client.get("/health")
        health_time = (time.time() - start_time) * 1000
        
        benchmark_results["test_results"]["health_endpoint_ms"] = round(health_time, 2)
        benchmark_results["test_results"]["health_status_code"] = response.status_code
        
        # Test 2: Simple GraphQL query
        query = '{ __typename }'
        start_time = time.time()
        response = await client.post("/graphql", json={"query": query})
        graphql_time = (time.time() - start_time) * 1000
        
        benchmark_results["test_results"]["simple_graphql_ms"] = round(graphql_time, 2)
        benchmark_results["test_results"]["graphql_status_code"] = response.status_code
    
    print(f"Performance benchmark completed: {benchmark_results}")
    return benchmark_results


if __name__ == "__main__":
    # Run benchmark if script is executed directly
    asyncio.run(run_performance_benchmark())