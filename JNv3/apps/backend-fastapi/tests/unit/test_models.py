"""
Unit tests for SQLAlchemy models.
Tests model creation, validation, and relationships.
"""

import pytest
from uuid import uuid4
from datetime import datetime

from app.models.user import User
from app.models.job import Job, Company


class TestUser:
    """Test User model functionality."""
    
    def test_user_creation(self):
        """Test basic user creation."""
        user_id = uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            hashed_password="hashed_password_here"
        )
        
        assert user.id == user_id
        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.is_active is True  # Default value
        assert user.is_verified is False  # Default value
    
    def test_user_full_name_property(self):
        """Test the full_name property."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            hashed_password="hashed_password_here"
        )
        
        assert user.full_name == "John Doe"
    
    def test_user_repr(self):
        """Test user string representation."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            hashed_password="hashed_password_here"
        )
        
        assert "test@example.com" in repr(user)


class TestCompany:
    """Test Company model functionality."""
    
    def test_company_creation(self):
        """Test basic company creation."""
        company_id = uuid4()
        company = Company(
            id=company_id,
            name="Test Corp",
            industry="Technology",
            location="San Francisco, CA"
        )
        
        assert company.id == company_id
        assert company.name == "Test Corp"
        assert company.industry == "Technology"
        assert company.location == "San Francisco, CA"
        assert company.is_active is True  # Default value
    
    def test_company_optional_fields(self):
        """Test company creation with optional fields."""
        company = Company(
            id=uuid4(),
            name="Test Corp",
            industry="Technology",
            location="San Francisco, CA",
            description="A great company",
            website="https://testcorp.com",
            size_category="large"
        )
        
        assert company.description == "A great company"
        assert company.website == "https://testcorp.com" 
        assert company.size_category == "large"


class TestJob:
    """Test Job model functionality."""
    
    def test_job_creation(self):
        """Test basic job creation."""
        job_id = uuid4()
        company_id = uuid4()
        user_id = uuid4()
        
        job = Job(
            id=job_id,
            title="Software Engineer",
            company_id=company_id,
            location="Remote",
            job_type="full_time",
            work_arrangement="remote",
            posted_by_user_id=user_id
        )
        
        assert job.id == job_id
        assert job.title == "Software Engineer"
        assert job.company_id == company_id
        assert job.location == "Remote"
        assert job.job_type == "full_time"
        assert job.work_arrangement == "remote"
        assert job.posted_by_user_id == user_id
        assert job.user_input is True  # Default value
        assert job.is_active is True  # Default value
    
    def test_job_with_salary(self):
        """Test job creation with salary information."""
        job = Job(
            id=uuid4(),
            title="Senior Engineer",
            company_id=uuid4(),
            location="New York, NY",
            job_type="full_time",
            work_arrangement="hybrid",
            posted_by_user_id=uuid4(),
            salary_min=120000,
            salary_max=180000,
            salary_currency="USD"
        )
        
        assert job.salary_min == 120000
        assert job.salary_max == 180000
        assert job.salary_currency == "USD"
    
    def test_job_with_requirements(self):
        """Test job with requirements list."""
        requirements = ["Python", "FastAPI", "GraphQL", "PostgreSQL"]
        
        job = Job(
            id=uuid4(),
            title="Backend Developer",
            company_id=uuid4(),
            location="Austin, TX",
            job_type="full_time",
            work_arrangement="office",
            posted_by_user_id=uuid4(),
            requirements=requirements
        )
        
        assert job.requirements == requirements
        assert len(job.requirements) == 4
        assert "Python" in job.requirements
    
    def test_job_timestamps(self):
        """Test that timestamps are handled correctly."""
        job = Job(
            id=uuid4(),
            title="DevOps Engineer",
            company_id=uuid4(),
            location="Seattle, WA",
            job_type="contract",
            work_arrangement="remote",
            posted_by_user_id=uuid4()
        )
        
        # In real database usage, these would be set automatically
        # Here we're just testing the fields exist
        assert hasattr(job, 'created_at')
        assert hasattr(job, 'updated_at')


class TestModelRelationships:
    """Test relationships between models."""
    
    async def test_job_company_relationship(self, db_session):
        """Test the job-company relationship."""
        # This would be tested in integration tests with actual database
        # Here we just verify the relationship attributes exist
        job = Job(
            id=uuid4(),
            title="Test Job",
            company_id=uuid4(),
            location="Test Location",
            job_type="full_time",
            work_arrangement="remote",
            posted_by_user_id=uuid4()
        )
        
        # Check that company_id field exists for foreign key
        assert hasattr(job, 'company_id')
        
        # In actual database tests, we would verify:
        # - job.company returns the related Company instance
        # - company.jobs returns list of related Job instances