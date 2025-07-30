"""
Backend test fixtures and configuration.
Provides comprehensive test setup for FastAPI + GraphQL backend.
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Dict, Any, List
from datetime import datetime, timedelta
from uuid import uuid4
import json
import os
from pathlib import Path

# Database and ORM imports
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import event
from sqlalchemy.engine import Engine

# FastAPI and testing imports
from fastapi.testclient import TestClient
from httpx import AsyncClient
import factory
from factory.alchemy import SQLAlchemyModelFactory

# Application imports
from app.main import app
from app.core.database import get_db_session, Base
from app.core.config import get_settings
from app.models.user import User
from app.models.job import Job, JobApplication
from app.models.resume import Resume
from app.auth.cognito import CognitoAuth

# Test data imports
from .factories import UserFactory, JobFactory, ResumeFactory, JobApplicationFactory
from .mock_data import MockDataProvider


# Test Database Configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,  # Set to True for SQL debugging
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Begin a transaction
        transaction = await session.begin()
        
        try:
            yield session
        finally:
            # Rollback the transaction
            await transaction.rollback()
            await session.close()


@pytest.fixture(scope="function")
def override_get_db(db_session):
    """Override the database dependency."""
    async def _override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db_session] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(override_get_db):
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture(scope="function")
async def async_client(override_get_db):
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# Authentication Fixtures
@pytest.fixture
def mock_cognito_auth():
    """Mock Cognito authentication."""
    class MockCognitoAuth(CognitoAuth):
        def __init__(self):
            pass
        
        async def verify_token(self, token: str) -> Dict[str, Any]:
            if token == "valid_token":
                return {
                    "sub": "test-user-id",
                    "email": "test@example.com",
                    "cognito:username": "testuser",
                    "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp())
                }
            elif token == "expired_token":
                return {
                    "sub": "test-user-id",
                    "email": "test@example.com",
                    "cognito:username": "testuser",
                    "exp": int((datetime.utcnow() - timedelta(hours=1)).timestamp())
                }
            else:
                raise ValueError("Invalid token")
        
        async def refresh_token(self, refresh_token: str) -> Dict[str, str]:
            if refresh_token == "valid_refresh":
                return {
                    "access_token": "new_access_token",
                    "id_token": "new_id_token",
                    "refresh_token": "new_refresh_token"
                }
            else:
                raise ValueError("Invalid refresh token")
    
    return MockCognitoAuth()


@pytest.fixture
def auth_headers():
    """Generate authentication headers."""
    return {"Authorization": "Bearer valid_token"}


@pytest.fixture
def invalid_auth_headers():
    """Generate invalid authentication headers."""
    return {"Authorization": "Bearer invalid_token"}


# User Fixtures
@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = UserFactory.build()
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin user."""
    user = UserFactory.build(
        is_admin=True,
        email="admin@example.com",
        cognito_username="admin"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def multiple_users(db_session: AsyncSession) -> List[User]:
    """Create multiple test users."""
    users = UserFactory.build_batch(5)
    for user in users:
        db_session.add(user)
    await db_session.commit()
    for user in users:
        await db_session.refresh(user)
    return users


# Job Fixtures
@pytest.fixture
async def test_job(db_session: AsyncSession, test_user: User) -> Job:
    """Create a test job."""
    job = JobFactory.build(created_by_id=test_user.id)
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)
    return job


@pytest.fixture
async def multiple_jobs(db_session: AsyncSession, test_user: User) -> List[Job]:
    """Create multiple test jobs."""
    jobs = JobFactory.build_batch(10, created_by_id=test_user.id)
    for job in jobs:
        db_session.add(job)
    await db_session.commit()
    for job in jobs:
        await db_session.refresh(job)
    return jobs


@pytest.fixture
async def job_with_applications(
    db_session: AsyncSession, 
    test_job: Job, 
    multiple_users: List[User]
) -> Job:
    """Create a job with multiple applications."""
    applications = []
    for user in multiple_users[:3]:  # First 3 users apply
        application = JobApplicationFactory.build(
            user_id=user.id,
            job_id=test_job.id
        )
        applications.append(application)
        db_session.add(application)
    
    await db_session.commit()
    for application in applications:
        await db_session.refresh(application)
    
    await db_session.refresh(test_job)
    return test_job


# Resume Fixtures
@pytest.fixture
async def test_resume(db_session: AsyncSession, test_user: User) -> Resume:
    """Create a test resume."""
    resume = ResumeFactory.build(user_id=test_user.id)
    db_session.add(resume)
    await db_session.commit()
    await db_session.refresh(resume)
    return resume


@pytest.fixture
async def multiple_resumes(
    db_session: AsyncSession, 
    test_user: User
) -> List[Resume]:
    """Create multiple resumes for a user."""
    resumes = ResumeFactory.build_batch(3, user_id=test_user.id)
    for resume in resumes:
        db_session.add(resume)
    await db_session.commit()
    for resume in resumes:
        await db_session.refresh(resume)
    return resumes


# Application Fixtures
@pytest.fixture
async def test_application(
    db_session: AsyncSession,
    test_user: User,
    test_job: Job
) -> JobApplication:
    """Create a test job application."""
    application = JobApplicationFactory.build(
        user_id=test_user.id,
        job_id=test_job.id
    )
    db_session.add(application)
    await db_session.commit()
    await db_session.refresh(application)
    return application


# GraphQL Fixtures
@pytest.fixture
def graphql_query():
    """Helper for executing GraphQL queries."""
    async def _execute_query(
        client: AsyncClient,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ):
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = await client.post(
            "/graphql",
            json=payload,
            headers=headers or {}
        )
        return response.json()
    
    return _execute_query


@pytest.fixture
def graphql_mutation():
    """Helper for executing GraphQL mutations."""
    async def _execute_mutation(
        client: AsyncClient,
        mutation: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ):
        payload = {"query": mutation}
        if variables:
            payload["variables"] = variables
        
        response = await client.post(
            "/graphql",
            json=payload,
            headers=headers or {}
        )
        return response.json()
    
    return _execute_mutation


# Mock Data Fixtures
@pytest.fixture
def mock_data_provider():
    """Provide mock data for testing."""
    return MockDataProvider()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "location": "San Francisco, CA",
        "bio": "Software engineer with 5 years of experience",
        "skills": ["Python", "JavaScript", "React", "PostgreSQL"],
        "experience_level": "mid",
        "preferred_salary_min": 80000,
        "preferred_salary_max": 120000,
        "remote_preference": "hybrid"
    }


@pytest.fixture
def sample_job_data():
    """Sample job data for testing."""
    return {
        "title": "Senior Software Engineer",
        "description": "We are looking for a senior software engineer...",
        "company": "Tech Company Inc.",
        "location": "San Francisco, CA",
        "job_type": "full_time",
        "experience_level": "senior",
        "salary_min": 100000,
        "salary_max": 150000,
        "remote_ok": True,
        "skills_required": ["Python", "Django", "PostgreSQL", "AWS"],
        "benefits": ["Health Insurance", "401k", "PTO"],
        "requirements": [
            "5+ years of software development experience",
            "Experience with Python and Django",
            "Strong problem-solving skills"
        ]
    }


@pytest.fixture
def sample_resume_data():
    """Sample resume data for testing."""
    return {
        "title": "Software Engineer Resume",
        "content": {
            "personal_info": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "location": "San Francisco, CA"
            },
            "summary": "Experienced software engineer with expertise in full-stack development",
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "Tech Corp",
                    "location": "San Francisco, CA",
                    "start_date": "2020-01-01",
                    "end_date": "2023-12-31",
                    "description": "Developed web applications using Python and React"
                }
            ],
            "education": [
                {
                    "degree": "BS Computer Science",
                    "school": "University of California",
                    "location": "Berkeley, CA",
                    "graduation_date": "2019-05-15"
                }
            ],
            "skills": ["Python", "JavaScript", "React", "PostgreSQL", "AWS"],
            "certifications": ["AWS Certified Developer"]
        }
    }


# File Upload Fixtures
@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing."""
    from io import BytesIO
    import tempfile
    
    # Create a temporary PDF file
    content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000053 00000 n \n0000000125 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n202\n%%EOF"
    
    return BytesIO(content)


# Async Utilities
@pytest.fixture
def async_test_utils():
    """Utilities for async testing."""
    class AsyncTestUtils:
        @staticmethod
        async def wait_for_condition(condition_func, timeout=5.0, interval=0.1):
            """Wait for a condition to become true."""
            start_time = asyncio.get_event_loop().time()
            while (asyncio.get_event_loop().time() - start_time) < timeout:
                if await condition_func():
                    return True
                await asyncio.sleep(interval)
            return False
        
        @staticmethod
        async def create_and_commit(session: AsyncSession, model_instance):
            """Create and commit a model instance."""
            session.add(model_instance)
            await session.commit()
            await session.refresh(model_instance)
            return model_instance
    
    return AsyncTestUtils()


# Performance Testing Fixtures
@pytest.fixture
def performance_monitor():
    """Monitor performance during tests."""
    import time
    import psutil
    import threading
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.peak_memory = 0
            self.monitoring = False
            self.thread = None
        
        def start(self):
            self.start_time = time.time()
            self.monitoring = True
            self.thread = threading.Thread(target=self._monitor_memory)
            self.thread.daemon = True
            self.thread.start()
        
        def stop(self):
            self.end_time = time.time()
            self.monitoring = False
            if self.thread:
                self.thread.join(timeout=1)
            return self.get_metrics()
        
        def _monitor_memory(self):
            process = psutil.Process()
            while self.monitoring:
                memory_mb = process.memory_info().rss / 1024 / 1024
                self.peak_memory = max(self.peak_memory, memory_mb)
                time.sleep(0.1)
        
        def get_metrics(self):
            duration = (self.end_time - self.start_time) if self.end_time else 0
            return {
                "duration_seconds": duration,
                "peak_memory_mb": self.peak_memory
            }
    
    return PerformanceMonitor()


# Cleanup Fixtures
@pytest.fixture(autouse=True)
async def cleanup_database(db_session: AsyncSession):
    """Automatically cleanup database after each test."""
    yield
    # Cleanup is handled by transaction rollback in db_session fixture


# Configuration Fixtures
@pytest.fixture
def test_settings():
    """Test application settings."""
    settings = get_settings()
    settings.database_url = TEST_DATABASE_URL
    settings.environment = "test"
    settings.log_level = "DEBUG"
    settings.jwt_secret = "test-secret-key"
    return settings


# Redis Mock Fixture
@pytest.fixture
async def mock_redis():
    """Mock Redis for testing."""
    class MockRedis:
        def __init__(self):
            self.data = {}
            self.expirations = {}
        
        async def get(self, key: str):
            if key in self.expirations:
                if datetime.utcnow().timestamp() > self.expirations[key]:
                    del self.data[key]
                    del self.expirations[key]
                    return None
            return self.data.get(key)
        
        async def set(self, key: str, value: str, ex: int = None):
            self.data[key] = value
            if ex:
                self.expirations[key] = datetime.utcnow().timestamp() + ex
        
        async def delete(self, key: str):
            self.data.pop(key, None)
            self.expirations.pop(key, None)
        
        async def flushall(self):
            self.data.clear()
            self.expirations.clear()
    
    return MockRedis()


# External API Mock Fixtures
@pytest.fixture
def mock_openai_responses():
    """Mock OpenAI API responses."""
    return {
        "job_suggestions": {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "suggestions": [
                                {
                                    "title": "Senior Python Developer",
                                    "match_score": 0.95,
                                    "reasons": ["Strong Python skills", "Experience match"]
                                }
                            ]
                        })
                    }
                }
            ]
        },
        "resume_analysis": {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "skills": ["Python", "JavaScript", "SQL"],
                            "experience_level": "senior",
                            "improvement_suggestions": ["Add more project details"]
                        })
                    }
                }
            ]
        }
    }


# Test Markers
pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.backend,
]