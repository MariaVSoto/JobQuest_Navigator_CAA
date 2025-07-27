"""
Unit tests for service layer classes.
Tests business logic and data access operations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.user_service import UserService
from app.services.job_service import JobService
from app.models.user import User
from app.models.job import Job, Company


class TestUserService:
    """Test UserService business logic."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = AsyncMock()
        return session
    
    @pytest.fixture
    def user_service(self, mock_db_session):
        """Create UserService instance with mocked dependencies."""
        return UserService(mock_db_session)
    
    async def test_get_user_by_id_success(self, user_service, mock_db_session):
        """Test successful user retrieval by ID."""
        # Arrange
        user_id = uuid4()
        expected_user = User(
            id=user_id,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            hashed_password="hashed_password"
        )
        
        # Mock the database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = expected_user
        mock_db_session.execute.return_value = mock_result
        
        # Act
        result = await user_service.get_user_by_id(user_id)
        
        # Assert
        assert result == expected_user
        mock_db_session.execute.assert_called_once()
    
    async def test_get_user_by_id_not_found(self, user_service, mock_db_session):
        """Test user retrieval when user doesn't exist."""
        # Arrange
        user_id = uuid4()
        
        # Mock the database query to return None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Act
        result = await user_service.get_user_by_id(user_id)
        
        # Assert
        assert result is None
        mock_db_session.execute.assert_called_once()
    
    async def test_get_user_by_email_success(self, user_service, mock_db_session):
        """Test successful user retrieval by email."""
        # Arrange
        email = "test@example.com"
        expected_user = User(
            id=uuid4(),
            email=email,
            first_name="John",
            last_name="Doe",
            hashed_password="hashed_password"
        )
        
        # Mock the database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = expected_user
        mock_db_session.execute.return_value = mock_result
        
        # Act
        result = await user_service.get_user_by_email(email)
        
        # Assert
        assert result == expected_user
        assert result.email == email
        mock_db_session.execute.assert_called_once()
    
    async def test_create_user_success(self, user_service, mock_db_session):
        """Test successful user creation."""
        # Arrange
        user_data = {
            "email": "newuser@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "password": "secure_password"
        }
        
        # Mock password hashing
        user_service._hash_password = MagicMock(return_value="hashed_secure_password")
        
        # Act
        result = await user_service.create_user(user_data)
        
        # Assert
        assert isinstance(result, User)
        assert result.email == user_data["email"]
        assert result.first_name == user_data["first_name"]
        assert result.last_name == user_data["last_name"]
        assert result.hashed_password == "hashed_secure_password"
        
        # Verify database operations
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()


class TestJobService:
    """Test JobService business logic."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = AsyncMock()
        return session
    
    @pytest.fixture
    def job_service(self, mock_db_session):
        """Create JobService instance with mocked dependencies."""
        return JobService(mock_db_session)
    
    async def test_get_job_by_id_success(self, job_service, mock_db_session):
        """Test successful job retrieval by ID."""
        # Arrange
        job_id = uuid4()
        company_id = uuid4()
        user_id = uuid4()
        
        expected_job = Job(
            id=job_id,
            title="Software Engineer",
            company_id=company_id,
            location="San Francisco, CA",
            job_type="full_time",
            work_arrangement="hybrid",
            posted_by_user_id=user_id
        )
        
        # Mock the database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = expected_job
        mock_db_session.execute.return_value = mock_result
        
        # Act
        result = await job_service.get_job_by_id(job_id)
        
        # Assert
        assert result == expected_job
        assert result.id == job_id
        mock_db_session.execute.assert_called_once()
    
    async def test_get_jobs_by_user_success(self, job_service, mock_db_session):
        """Test successful retrieval of jobs by user."""
        # Arrange
        user_id = uuid4()
        company_id = uuid4()
        
        expected_jobs = [
            Job(
                id=uuid4(),
                title="Frontend Developer",
                company_id=company_id,
                location="Remote",
                job_type="full_time",
                work_arrangement="remote",
                posted_by_user_id=user_id
            ),
            Job(
                id=uuid4(),
                title="Backend Developer",
                company_id=company_id,
                location="New York, NY",
                job_type="full_time",
                work_arrangement="office",
                posted_by_user_id=user_id
            )
        ]
        
        # Mock the database query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = expected_jobs
        mock_db_session.execute.return_value = mock_result
        
        # Act
        result = await job_service.get_jobs_by_user(user_id)
        
        # Assert
        assert len(result) == 2
        assert all(job.posted_by_user_id == user_id for job in result)
        mock_db_session.execute.assert_called_once()
    
    async def test_create_job_success(self, job_service, mock_db_session):
        """Test successful job creation."""
        # Arrange
        job_data = {
            "title": "Senior Python Developer",
            "company_name": "Tech Startup Inc",
            "location": "Austin, TX",
            "job_type": "full_time",
            "work_arrangement": "hybrid",
            "description": "Exciting Python role",
            "requirements": ["Python", "Django", "PostgreSQL"],
            "salary_min": 100000,
            "salary_max": 140000,
            "user_id": uuid4()
        }
        
        # Mock company creation/retrieval
        company = Company(
            id=uuid4(),
            name=job_data["company_name"],
            industry="Technology",
            location=job_data["location"]
        )
        job_service._get_or_create_company = AsyncMock(return_value=company)
        
        # Act
        result = await job_service.create_job(job_data)
        
        # Assert
        assert isinstance(result, Job)
        assert result.title == job_data["title"]
        assert result.company_id == company.id
        assert result.location == job_data["location"]
        assert result.salary_min == job_data["salary_min"]
        assert result.salary_max == job_data["salary_max"]
        assert result.posted_by_user_id == job_data["user_id"]
        
        # Verify database operations
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    async def test_search_jobs_success(self, job_service, mock_db_session):
        """Test successful job search."""
        # Arrange
        search_params = {
            "query": "python developer",
            "location": "san francisco",
            "job_type": "full_time",
            "limit": 10
        }
        
        expected_jobs = [
            Job(
                id=uuid4(),
                title="Python Developer",
                company_id=uuid4(),
                location="San Francisco, CA",
                job_type="full_time",
                work_arrangement="hybrid",
                posted_by_user_id=uuid4()
            )
        ]
        
        # Mock the database query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = expected_jobs
        mock_db_session.execute.return_value = mock_result
        
        # Act
        result = await job_service.search_jobs(search_params)
        
        # Assert
        assert len(result) == 1
        assert "Python" in result[0].title
        mock_db_session.execute.assert_called_once()


class TestServiceIntegration:
    """Test service layer integration scenarios."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = AsyncMock()
        return session
    
    async def test_user_job_creation_workflow(self, mock_db_session):
        """Test the complete workflow of user creating a job."""
        # Arrange
        user_service = UserService(mock_db_session)
        job_service = JobService(mock_db_session)
        
        # Mock user retrieval
        user = User(
            id=uuid4(),
            email="jobcreator@example.com",
            first_name="Job",
            last_name="Creator",
            hashed_password="hashed_password"
        )
        user_service.get_user_by_id = AsyncMock(return_value=user)
        
        # Mock company creation
        company = Company(
            id=uuid4(),
            name="New Company",
            industry="Technology",
            location="Portland, OR"
        )
        job_service._get_or_create_company = AsyncMock(return_value=company)
        
        # Job data
        job_data = {
            "title": "Full Stack Developer",
            "company_name": "New Company",
            "location": "Portland, OR",
            "job_type": "full_time",
            "work_arrangement": "remote",
            "user_id": user.id
        }
        
        # Act
        created_job = await job_service.create_job(job_data)
        
        # Assert
        assert created_job.posted_by_user_id == user.id
        assert created_job.company_id == company.id
        assert created_job.title == job_data["title"]
        
        # Verify service interactions
        job_service._get_or_create_company.assert_called_once()
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()