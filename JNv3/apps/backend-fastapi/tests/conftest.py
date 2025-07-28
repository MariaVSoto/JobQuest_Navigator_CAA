"""
Test configuration and fixtures for JobQuest Navigator v2 backend.
Provides shared test fixtures for database, authentication, and GraphQL testing.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import httpx
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.config import settings
from app.core.database import get_db_session, Base
from app.models.user import User
from app.models.job import Job, Company


# Test database URL - SQLite in memory for speed
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine with special configuration for SQLite
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,
    },
    echo=False  # Set to True for SQL debugging
)

TestSessionLocal = async_sessionmaker(
    test_engine, 
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test.
    Tables are created and dropped for each test to ensure isolation.
    """
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
    
    # Drop all tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def test_client(db_session: AsyncSession) -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    Create test client with database dependency override.
    """
    # Override database dependency
    app.dependency_overrides[get_db_session] = lambda: db_session
    
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user in the database."""
    user = User(
        id=uuid4(),
        email="test@example.com",
        first_name="Test",
        last_name="User",
        hashed_password="$2b$12$dummy_hashed_password",
        is_active=True,
        is_verified=True
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


@pytest.fixture
async def authenticated_user(test_client: httpx.AsyncClient, test_user: User) -> dict:
    """
    Create an authenticated user with token.
    Returns user data with authentication token.
    """
    # For now, we'll create a mock token
    # In real implementation, this would use your auth service
    token = "test_jwt_token_" + str(test_user.id)
    
    return {
        "user": test_user,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }


@pytest.fixture
async def test_company(db_session: AsyncSession) -> Company:
    """Create a test company in the database."""
    company = Company(
        id=uuid4(),
        name="Test Corp",
        industry="Technology",
        location="San Francisco, CA",
        description="A test company for testing purposes",
        website="https://testcorp.com",
        size_category="medium"
    )
    
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)
    
    return company


@pytest.fixture
async def test_job(db_session: AsyncSession, test_company: Company, test_user: User) -> Job:
    """Create a test job in the database."""
    job = Job(
        id=uuid4(),
        title="Senior Software Engineer",
        company_id=test_company.id,
        location="San Francisco, CA",
        job_type="full_time",
        work_arrangement="hybrid",
        description="A great software engineering role",
        requirements=["Python", "FastAPI", "GraphQL"],
        salary_min=120000,
        salary_max=180000,
        posted_by_user_id=test_user.id,
        user_input=True
    )
    
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)
    
    return job


@pytest.fixture
def graphql_query():
    """Helper for GraphQL query testing."""
    async def _query(client: httpx.AsyncClient, query: str, variables: dict = None, headers: dict = None):
        """Execute a GraphQL query and return the response."""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
            
        response = await client.post("/graphql", json=payload, headers=headers or {})
        return response.json()
    
    return _query


# Sample GraphQL queries for testing
SAMPLE_QUERIES = {
    "GET_USER": """
        query GetUser($id: UUID!) {
            user(id: $id) {
                id
                email
                firstName
                lastName
                isActive
            }
        }
    """,
    
    "GET_JOBS": """
        query GetJobs($limit: Int) {
            jobs(limit: $limit) {
                id
                title
                company {
                    name
                }
                location
                jobType
                salaryMin
                salaryMax
            }
        }
    """,
    
    "CREATE_JOB": """
        mutation CreateJob($input: UserJobInput!) {
            createUserJob(input: $input) {
                success
                message
                job {
                    id
                    title
                    company {
                        name
                    }
                }
            }
        }
    """
}


@pytest.fixture
def sample_queries():
    """Provide sample GraphQL queries for testing."""
    return SAMPLE_QUERIES