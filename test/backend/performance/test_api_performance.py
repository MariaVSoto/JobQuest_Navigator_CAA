"""
Performance tests for API endpoints
Tests response times, throughput, and resource usage
"""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

from httpx import AsyncClient
from locust import HttpUser, task, between
import matplotlib.pyplot as plt
import pandas as pd


class TestAPIPerformance:
    """Performance tests for API endpoints."""

    @pytest.fixture
    def performance_client(self):
        """Create performance test client."""
        return AsyncClient(base_url="http://localhost:8000")

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_job_listing_response_time(self, performance_client):
        """Test job listing endpoint response time."""
        response_times = []
        
        for _ in range(100):
            start_time = time.time()
            response = await performance_client.get("/api/jobs")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to ms
            response_times.append(response_time)
            
            assert response.status_code == 200
        
        # Performance assertions
        avg_response_time = sum(response_times) / len(response_times)
        p95_response_time = sorted(response_times)[int(0.95 * len(response_times))]
        
        assert avg_response_time < 200, f"Average response time {avg_response_time}ms exceeds 200ms"
        assert p95_response_time < 500, f"95th percentile response time {p95_response_time}ms exceeds 500ms"

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_concurrent_job_creation(self, performance_client, test_user):
        """Test concurrent job creation performance."""
        job_data = {
            "title": "Performance Test Job",
            "description": "Test job for performance testing",
            "company": "Test Company",
            "location": "Remote",
            "salary_min": 50000,
            "salary_max": 80000
        }
        
        async def create_job():
            start_time = time.time()
            response = await performance_client.post(
                "/api/jobs",
                json=job_data,
                headers={"Authorization": f"Bearer {test_user.token}"}
            )
            end_time = time.time()
            return response.status_code, (end_time - start_time) * 1000
        
        # Create 50 concurrent job creation requests
        tasks = [create_job() for _ in range(50)]
        results = await asyncio.gather(*tasks)
        
        # Analyze results
        successful_requests = [r for r in results if r[0] == 201]
        response_times = [r[1] for r in results]
        
        success_rate = len(successful_requests) / len(results)
        avg_response_time = sum(response_times) / len(response_times)
        
        assert success_rate >= 0.95, f"Success rate {success_rate} is below 95%"
        assert avg_response_time < 1000, f"Average response time {avg_response_time}ms exceeds 1000ms"

    @pytest.mark.performance
    def test_database_query_performance(self, db_session, multiple_jobs):
        """Test database query performance."""
        from app.services.job_service import JobService
        
        job_service = JobService(db_session)
        
        # Test search performance
        search_times = []
        for _ in range(20):
            start_time = time.time()
            jobs = asyncio.run(job_service.search_jobs_by_title("Engineer"))
            end_time = time.time()
            
            search_times.append((end_time - start_time) * 1000)
        
        avg_search_time = sum(search_times) / len(search_times)
        assert avg_search_time < 100, f"Average search time {avg_search_time}ms exceeds 100ms"

    @pytest.mark.performance
    def test_memory_usage_under_load(self, performance_client):
        """Test memory usage under load."""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        async def memory_test():
            tasks = []
            for _ in range(1000):
                tasks.append(performance_client.get("/api/jobs"))
            
            await asyncio.gather(*tasks)
        
        asyncio.run(memory_test())
        gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        assert memory_increase < 100, f"Memory increased by {memory_increase}MB, exceeds 100MB limit"


class JobQuestLoadTest(HttpUser):
    """Locust load test for JobQuest Navigator."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Login before starting tests."""
        response = self.client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        if response.status_code == 200:
            self.token = response.json()["token"]
        else:
            self.token = None

    @task(3)
    def browse_jobs(self):
        """Simulate browsing job listings."""
        self.client.get("/api/jobs?page=1&limit=20")

    @task(2)
    def search_jobs(self):
        """Simulate searching for jobs."""
        search_terms = ["python", "javascript", "engineer", "developer", "manager"]
        term = self.environment.parsed_options.choice(search_terms)
        self.client.get(f"/api/jobs/search?q={term}")

    @task(1)
    def view_job_details(self):
        """Simulate viewing job details."""
        # First get a list of jobs
        response = self.client.get("/api/jobs?limit=10")
        if response.status_code == 200:
            jobs = response.json().get("jobs", [])
            if jobs:
                job_id = jobs[0]["id"]
                self.client.get(f"/api/jobs/{job_id}")

    @task(1)
    def view_user_profile(self):
        """Simulate viewing user profile."""
        if self.token:
            self.client.get(
                "/api/users/me",
                headers={"Authorization": f"Bearer {self.token}"}
            )

    @task(1)
    def create_job_application(self):
        """Simulate creating a job application."""
        if self.token:
            # Get a job to apply to
            response = self.client.get("/api/jobs?limit=1")
            if response.status_code == 200:
                jobs = response.json().get("jobs", [])
                if jobs:
                    job_id = jobs[0]["id"]
                    self.client.post(
                        f"/api/jobs/{job_id}/apply",
                        json={
                            "cover_letter": "I am interested in this position.",
                            "resume_id": "test-resume-id"
                        },
                        headers={"Authorization": f"Bearer {self.token}"}
                    )


def run_load_test():
    """Run load test using Locust programmatically."""
    import subprocess
    import os
    
    # Run locust in headless mode
    cmd = [
        "locust",
        "--headless",
        "-u", "50",  # 50 users
        "-r", "5",   # 5 users spawned per second
        "-t", "300", # Run for 5 minutes
        "--host", "http://localhost:8000",
        "--html", "test/reports/performance/load-test-report.html",
        "--csv", "test/reports/performance/load-test"
    ]
    
    subprocess.run(cmd, cwd=os.path.dirname(__file__))


if __name__ == "__main__":
    """Run performance tests standalone."""
    run_load_test()