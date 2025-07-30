"""
Unit tests for Job Service
Tests all job-related business logic and service methods
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.services.job_service import JobService
from app.models.job import Job, JobApplication
from app.core.exceptions import (
    JobNotFoundError, 
    InvalidJobStatusError, 
    UnauthorizedError,
    ValidationError
)


class TestJobService:
    """Test suite for JobService class."""

    @pytest.fixture
    def job_service(self, db_session):
        """Create JobService instance for testing."""
        return JobService(db_session)

    @pytest.fixture
    def sample_job_data(self):
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
                "Experience with Python and Django"
            ]
        }

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_create_job_success(self, job_service, sample_job_data, test_user):
        """Test successful job creation."""
        # Act
        job = await job_service.create_job(sample_job_data, test_user.id)
        
        # Assert
        assert job.title == sample_job_data["title"]
        assert job.company == sample_job_data["company"]
        assert job.created_by_id == test_user.id
        assert job.status == "draft"
        assert job.created_at is not None

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_create_job_invalid_data(self, job_service, test_user):
        """Test job creation with invalid data."""
        # Arrange
        invalid_data = {
            "title": "",  # Empty title
            "salary_min": -1000,  # Invalid salary
            "experience_level": "invalid_level"
        }
        
        # Act & Assert
        with pytest.raises(ValidationError):
            await job_service.create_job(invalid_data, test_user.id)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_job_by_id_success(self, job_service, test_job):
        """Test successful retrieval of job by ID."""
        # Act
        job = await job_service.get_job_by_id(test_job.id)
        
        # Assert
        assert job.id == test_job.id
        assert job.title == test_job.title

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_job_by_id_not_found(self, job_service):
        """Test retrieval of non-existent job by ID."""
        # Act & Assert
        with pytest.raises(JobNotFoundError):
            await job_service.get_job_by_id("non-existent-id")

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_update_job_success(self, job_service, test_job, test_user):
        """Test successful job update."""
        # Arrange
        update_data = {
            "title": "Updated Job Title",
            "description": "Updated description",
            "salary_max": 160000
        }
        
        # Act
        updated_job = await job_service.update_job(test_job.id, update_data, test_user.id)
        
        # Assert
        assert updated_job.title == "Updated Job Title"
        assert updated_job.description == "Updated description"
        assert updated_job.salary_max == 160000
        assert updated_job.updated_at > test_job.updated_at

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_update_job_unauthorized(self, job_service, test_job, multiple_users):
        """Test job update by unauthorized user."""
        # Arrange
        unauthorized_user = multiple_users[0]
        update_data = {"title": "Unauthorized Update"}
        
        # Act & Assert
        with pytest.raises(UnauthorizedError):
            await job_service.update_job(test_job.id, update_data, unauthorized_user.id)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_delete_job_success(self, job_service, test_job, test_user):
        """Test successful job deletion (soft delete)."""
        # Act
        result = await job_service.delete_job(test_job.id, test_user.id)
        
        # Assert
        assert result is True
        deleted_job = await job_service.get_job_by_id(test_job.id)
        assert deleted_job.status == "cancelled"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_publish_job_success(self, job_service, test_job, test_user):
        """Test successful job publishing."""
        # Arrange
        test_job.status = "draft"
        
        # Act
        published_job = await job_service.publish_job(test_job.id, test_user.id)
        
        # Assert
        assert published_job.status == "published"
        assert published_job.published_at is not None

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_publish_job_invalid_status(self, job_service, test_job, test_user):
        """Test publishing job with invalid status."""
        # Arrange
        test_job.status = "closed"
        
        # Act & Assert
        with pytest.raises(InvalidJobStatusError):
            await job_service.publish_job(test_job.id, test_user.id)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_close_job_success(self, job_service, test_job, test_user):
        """Test successful job closing."""
        # Arrange
        test_job.status = "published"
        
        # Act
        closed_job = await job_service.close_job(test_job.id, test_user.id)
        
        # Assert
        assert closed_job.status == "closed"
        assert closed_job.closed_at is not None

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_search_jobs_by_title(self, job_service, multiple_jobs):
        """Test searching jobs by title."""
        # Arrange
        search_term = "Engineer"
        
        # Act
        jobs = await job_service.search_jobs_by_title(search_term)
        
        # Assert
        assert len(jobs) > 0
        for job in jobs:
            assert search_term.lower() in job.title.lower()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_search_jobs_by_location(self, job_service, multiple_jobs):
        """Test searching jobs by location."""
        # Arrange
        location = "San Francisco"
        
        # Act
        jobs = await job_service.search_jobs_by_location(location)
        
        # Assert
        assert len(jobs) > 0
        for job in jobs:
            assert location.lower() in job.location.lower()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_search_jobs_by_skills(self, job_service, multiple_jobs):
        """Test searching jobs by required skills."""
        # Arrange
        skills = ["Python", "Django"]
        
        # Act
        jobs = await job_service.search_jobs_by_skills(skills)
        
        # Assert
        assert len(jobs) > 0
        for job in jobs:
            job_skills = job.skills_required or []
            assert any(skill in job_skills for skill in skills)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_filter_jobs_by_salary_range(self, job_service, multiple_jobs):
        """Test filtering jobs by salary range."""
        # Arrange
        min_salary = 80000
        max_salary = 120000
        
        # Act
        jobs = await job_service.filter_jobs_by_salary_range(min_salary, max_salary)
        
        # Assert
        assert len(jobs) > 0
        for job in jobs:
            assert job.salary_min >= min_salary or job.salary_max <= max_salary

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_filter_jobs_by_experience_level(self, job_service, multiple_jobs):
        """Test filtering jobs by experience level."""
        # Arrange
        experience_level = "senior"
        
        # Act
        jobs = await job_service.filter_jobs_by_experience_level(experience_level)
        
        # Assert
        assert len(jobs) > 0
        for job in jobs:
            assert job.experience_level == experience_level

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_filter_jobs_by_remote_ok(self, job_service, multiple_jobs):
        """Test filtering jobs by remote work availability."""
        # Act
        remote_jobs = await job_service.filter_jobs_by_remote_ok(True)
        
        # Assert
        assert len(remote_jobs) > 0
        for job in remote_jobs:
            assert job.remote_ok is True

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_jobs_paginated(self, job_service, multiple_jobs):
        """Test getting paginated list of jobs."""
        # Act
        result = await job_service.get_jobs_paginated(page=1, page_size=5)
        
        # Assert
        assert "jobs" in result
        assert "total_count" in result
        assert "page" in result
        assert "page_size" in result
        assert "total_pages" in result
        assert len(result["jobs"]) <= 5

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_jobs_by_company(self, job_service, multiple_jobs):
        """Test getting jobs by company."""
        # Arrange
        company_name = multiple_jobs[0].company
        
        # Act
        jobs = await job_service.get_jobs_by_company(company_name)
        
        # Assert
        assert len(jobs) > 0
        for job in jobs:
            assert job.company == company_name

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_jobs_by_user(self, job_service, test_user, multiple_jobs):
        """Test getting jobs created by a specific user."""
        # Act
        jobs = await job_service.get_jobs_by_user(test_user.id)
        
        # Assert
        assert len(jobs) > 0
        for job in jobs:
            assert job.created_by_id == test_user.id

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_featured_jobs(self, job_service, multiple_jobs):
        """Test getting featured jobs."""
        # Arrange - Mark some jobs as featured
        for job in multiple_jobs[:3]:
            job.is_featured = True
        
        # Act
        featured_jobs = await job_service.get_featured_jobs(limit=5)
        
        # Assert
        assert len(featured_jobs) > 0
        for job in featured_jobs:
            assert job.is_featured is True

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_recent_jobs(self, job_service, multiple_jobs):
        """Test getting recently posted jobs."""
        # Act
        recent_jobs = await job_service.get_recent_jobs(days=7, limit=10)
        
        # Assert
        assert len(recent_jobs) <= 10
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        for job in recent_jobs:
            assert job.created_at >= cutoff_date

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_expiring_jobs(self, job_service, multiple_jobs):
        """Test getting jobs expiring soon."""
        # Arrange - Set some jobs to expire soon
        future_date = datetime.utcnow() + timedelta(days=3)
        for job in multiple_jobs[:2]:
            job.application_deadline = future_date
        
        # Act
        expiring_jobs = await job_service.get_expiring_jobs(days=7)
        
        # Assert
        assert len(expiring_jobs) > 0
        for job in expiring_jobs:
            assert job.application_deadline is not None

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_increment_view_count(self, job_service, test_job):
        """Test incrementing job view count."""
        # Arrange
        original_count = test_job.view_count
        
        # Act
        updated_job = await job_service.increment_view_count(test_job.id)
        
        # Assert
        assert updated_job.view_count == original_count + 1

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_job_statistics(self, job_service, test_job):
        """Test getting job statistics."""
        # Act
        stats = await job_service.get_job_statistics(test_job.id)
        
        # Assert
        assert "view_count" in stats
        assert "application_count" in stats
        assert "average_application_score" in stats
        assert isinstance(stats["view_count"], int)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_apply_to_job_success(self, job_service, test_job, test_user, test_resume):
        """Test successful job application."""
        # Arrange
        application_data = {
            "cover_letter": "I am interested in this position...",
            "resume_id": test_resume.id
        }
        
        # Act
        application = await job_service.apply_to_job(
            test_job.id, test_user.id, application_data
        )
        
        # Assert
        assert application.job_id == test_job.id
        assert application.user_id == test_user.id
        assert application.status == "submitted"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_apply_to_job_duplicate_application(self, job_service, test_application):
        """Test applying to job when application already exists."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await job_service.apply_to_job(
                test_application.job_id, 
                test_application.user_id, 
                {"cover_letter": "Another application"}
            )
        
        assert "already applied" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_job_applications(self, job_service, job_with_applications):
        """Test getting applications for a job."""
        # Act
        applications = await job_service.get_job_applications(job_with_applications.id)
        
        # Assert
        assert len(applications) > 0
        for application in applications:
            assert application.job_id == job_with_applications.id

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_update_application_status(self, job_service, test_application, test_user):
        """Test updating job application status."""
        # Arrange
        new_status = "interview_scheduled"
        
        # Act
        updated_application = await job_service.update_application_status(
            test_application.id, new_status, test_user.id
        )
        
        # Assert
        assert updated_application.status == new_status
        assert updated_application.last_updated_at > test_application.last_updated_at

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_bulk_update_applications(self, job_service, job_with_applications, test_user):
        """Test bulk updating multiple applications."""
        # Arrange
        application_ids = [app.id for app in job_with_applications.applications[:2]]
        new_status = "rejected"
        
        # Act
        updated_count = await job_service.bulk_update_applications(
            application_ids, {"status": new_status}, test_user.id
        )
        
        # Assert
        assert updated_count == 2

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_similar_jobs(self, job_service, test_job):
        """Test finding similar jobs based on job characteristics."""
        # Act
        similar_jobs = await job_service.get_similar_jobs(test_job.id, limit=5)
        
        # Assert
        assert isinstance(similar_jobs, list)
        assert len(similar_jobs) <= 5
        assert all(job.id != test_job.id for job in similar_jobs)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_job_recommendations_for_user(self, job_service, test_user):
        """Test getting job recommendations for a user."""
        # Act
        recommendations = await job_service.get_job_recommendations_for_user(
            test_user.id, limit=10
        )
        
        # Assert
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 10
        for rec in recommendations:
            assert "job" in rec
            assert "match_score" in rec
            assert 0 <= rec["match_score"] <= 1

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_calculate_job_match_score(self, job_service, test_job, test_user):
        """Test calculating job match score for a user."""
        # Act
        match_score = await job_service.calculate_job_match_score(test_job.id, test_user.id)
        
        # Assert
        assert isinstance(match_score, float)
        assert 0 <= match_score <= 1

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_validate_job_data_success(self, job_service, sample_job_data):
        """Test successful job data validation."""
        # Act
        is_valid, errors = await job_service.validate_job_data(sample_job_data)
        
        # Assert
        assert is_valid is True
        assert len(errors) == 0

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_validate_job_data_failure(self, job_service):
        """Test job data validation with invalid data."""
        # Arrange
        invalid_data = {
            "title": "",
            "salary_min": -1000,
            "experience_level": "invalid_level",
            "job_type": "invalid_type"
        }
        
        # Act
        is_valid, errors = await job_service.validate_job_data(invalid_data)
        
        # Assert
        assert is_valid is False
        assert len(errors) > 0

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_archive_old_jobs(self, job_service, multiple_jobs):
        """Test archiving old jobs."""
        # Arrange - Make some jobs old
        old_date = datetime.utcnow() - timedelta(days=365)
        for job in multiple_jobs[:2]:
            job.created_at = old_date
        
        # Act
        archived_count = await job_service.archive_old_jobs(days=180)
        
        # Assert
        assert archived_count >= 0

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_export_job_data(self, job_service, test_job):
        """Test exporting job data."""
        # Act
        job_data = await job_service.export_job_data(test_job.id)
        
        # Assert
        assert "job_info" in job_data
        assert "applications" in job_data
        assert "statistics" in job_data
        assert job_data["job_info"]["title"] == test_job.title

    @pytest.mark.asyncio
    @pytest.mark.unit
    @patch('app.services.job_service.send_notification')
    async def test_notify_job_status_change(self, mock_send_notification, job_service, test_job):
        """Test sending notifications when job status changes."""
        # Arrange
        mock_send_notification.return_value = True
        
        # Act
        result = await job_service.notify_job_status_change(test_job.id, "published")
        
        # Assert
        assert result is True
        mock_send_notification.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_job_analytics(self, job_service, test_job):
        """Test getting job analytics data."""
        # Act
        analytics = await job_service.get_job_analytics(test_job.id)
        
        # Assert
        assert "views_over_time" in analytics
        assert "applications_over_time" in analytics
        assert "top_skills_in_applications" in analytics
        assert "geographic_distribution" in analytics

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_duplicate_job(self, job_service, test_job, test_user):
        """Test duplicating a job."""
        # Act
        duplicated_job = await job_service.duplicate_job(test_job.id, test_user.id)
        
        # Assert
        assert duplicated_job.id != test_job.id
        assert duplicated_job.title == f"Copy of {test_job.title}"
        assert duplicated_job.created_by_id == test_user.id
        assert duplicated_job.status == "draft"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_job_service_performance_search(self, job_service, performance_monitor):
        """Test job search performance."""
        # Arrange
        performance_monitor.start()
        
        # Act
        results = await job_service.search_jobs(
            query="engineer",
            location="San Francisco",
            skills=["Python", "JavaScript"],
            limit=50
        )
        
        # Assert
        metrics = performance_monitor.stop()
        assert metrics["duration_seconds"] < 2.0  # Search should be fast
        assert len(results) <= 50

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_concurrent_job_applications(self, job_service, test_job, multiple_users):
        """Test handling concurrent applications to the same job."""
        # Arrange
        application_tasks = []
        for user in multiple_users[:5]:
            application_data = {
                "cover_letter": f"Application from user {user.id}",
                "resume_id": f"resume-{user.id}"
            }
            task = job_service.apply_to_job(test_job.id, user.id, application_data)
            application_tasks.append(task)
        
        # Act
        results = await asyncio.gather(*application_tasks, return_exceptions=True)
        
        # Assert
        successful_applications = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_applications) == 5  # All should succeed