"""
Unit tests for User Service
Tests all user-related business logic and service methods
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any

from app.services.user_service import UserService
from app.models.user import User
from app.core.exceptions import (
    UserNotFoundError, 
    UserAlreadyExistsError, 
    InvalidCredentialsError,
    ValidationError
)


class TestUserService:
    """Test suite for UserService class."""

    @pytest.fixture
    def user_service(self, db_session):
        """Create UserService instance for testing."""
        return UserService(db_session)

    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing."""
        return {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1234567890",
            "location": "San Francisco, CA",
            "bio": "Software engineer with 5 years of experience",
            "skills": ["Python", "JavaScript", "React"],
            "experience_level": "mid",
            "preferred_salary_min": 80000,
            "preferred_salary_max": 120000,
            "remote_preference": "hybrid"
        }

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_create_user_success(self, user_service, sample_user_data):
        """Test successful user creation."""
        # Act
        user = await user_service.create_user(sample_user_data)
        
        # Assert
        assert user.email == sample_user_data["email"]
        assert user.first_name == sample_user_data["first_name"]
        assert user.last_name == sample_user_data["last_name"]
        assert user.is_active is True
        assert user.is_verified is False
        assert user.created_at is not None

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_create_user_duplicate_email(self, user_service, sample_user_data, test_user):
        """Test user creation with duplicate email fails."""
        # Arrange
        sample_user_data["email"] = test_user.email
        
        # Act & Assert
        with pytest.raises(UserAlreadyExistsError):
            await user_service.create_user(sample_user_data)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_create_user_invalid_email(self, user_service, sample_user_data):
        """Test user creation with invalid email fails."""
        # Arrange
        sample_user_data["email"] = "invalid-email"
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await user_service.create_user(sample_user_data)
        
        assert "email" in str(exc_info.value)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_create_user_missing_required_fields(self, user_service):
        """Test user creation with missing required fields fails."""
        # Arrange
        incomplete_data = {"email": "test@example.com"}
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await user_service.create_user(incomplete_data)
        
        assert "first_name" in str(exc_info.value)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_user_by_id_success(self, user_service, test_user):
        """Test successful retrieval of user by ID."""
        # Act
        user = await user_service.get_user_by_id(test_user.id)
        
        # Assert
        assert user.id == test_user.id
        assert user.email == test_user.email

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_user_by_id_not_found(self, user_service):
        """Test retrieval of non-existent user by ID."""
        # Act & Assert
        with pytest.raises(UserNotFoundError):
            await user_service.get_user_by_id("non-existent-id")

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_user_by_email_success(self, user_service, test_user):
        """Test successful retrieval of user by email."""
        # Act
        user = await user_service.get_user_by_email(test_user.email)
        
        # Assert
        assert user.id == test_user.id
        assert user.email == test_user.email

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_user_by_email_not_found(self, user_service):
        """Test retrieval of non-existent user by email."""
        # Act & Assert
        with pytest.raises(UserNotFoundError):
            await user_service.get_user_by_email("nonexistent@example.com")

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_update_user_success(self, user_service, test_user):
        """Test successful user update."""
        # Arrange
        update_data = {
            "first_name": "Jane",
            "bio": "Updated bio",
            "location": "New York, NY"
        }
        
        # Act
        updated_user = await user_service.update_user(test_user.id, update_data)
        
        # Assert
        assert updated_user.first_name == "Jane"
        assert updated_user.bio == "Updated bio"
        assert updated_user.location == "New York, NY"
        assert updated_user.updated_at > test_user.updated_at

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_update_user_not_found(self, user_service):
        """Test update of non-existent user."""
        # Arrange
        update_data = {"first_name": "Jane"}
        
        # Act & Assert
        with pytest.raises(UserNotFoundError):
            await user_service.update_user("non-existent-id", update_data)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_update_user_duplicate_email(self, user_service, multiple_users):
        """Test user update with duplicate email fails."""
        # Arrange
        user1, user2 = multiple_users[0], multiple_users[1]
        update_data = {"email": user2.email}
        
        # Act & Assert
        with pytest.raises(UserAlreadyExistsError):
            await user_service.update_user(user1.id, update_data)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_update_user_invalid_data(self, user_service, test_user):
        """Test user update with invalid data."""
        # Arrange
        update_data = {"email": "invalid-email"}
        
        # Act & Assert
        with pytest.raises(ValidationError):
            await user_service.update_user(test_user.id, update_data)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_delete_user_success(self, user_service, test_user):
        """Test successful user deletion (soft delete)."""
        # Act
        result = await user_service.delete_user(test_user.id)
        
        # Assert
        assert result is True
        deleted_user = await user_service.get_user_by_id(test_user.id)
        assert deleted_user.is_active is False

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_delete_user_not_found(self, user_service):
        """Test deletion of non-existent user."""
        # Act & Assert
        with pytest.raises(UserNotFoundError):
            await user_service.delete_user("non-existent-id")

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_activate_user_success(self, user_service, test_user):
        """Test successful user activation."""
        # Arrange
        test_user.is_active = False
        
        # Act
        activated_user = await user_service.activate_user(test_user.id)
        
        # Assert
        assert activated_user.is_active is True

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_deactivate_user_success(self, user_service, test_user):
        """Test successful user deactivation."""
        # Act
        deactivated_user = await user_service.deactivate_user(test_user.id)
        
        # Assert
        assert deactivated_user.is_active is False

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_verify_user_success(self, user_service, test_user):
        """Test successful user verification."""
        # Arrange
        test_user.is_verified = False
        
        # Act
        verified_user = await user_service.verify_user(test_user.id)
        
        # Assert
        assert verified_user.is_verified is True

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_search_users_by_skills(self, user_service, multiple_users):
        """Test searching users by skills."""
        # Arrange
        skills = ["Python", "JavaScript"]
        
        # Act
        users = await user_service.search_users_by_skills(skills)
        
        # Assert
        assert len(users) > 0
        for user in users:
            user_skills = user.skills or []
            assert any(skill in user_skills for skill in skills)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_search_users_by_location(self, user_service, multiple_users):
        """Test searching users by location."""
        # Arrange
        location = "San Francisco"
        
        # Act
        users = await user_service.search_users_by_location(location)
        
        # Assert
        assert len(users) > 0
        for user in users:
            assert location.lower() in (user.location or "").lower()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_search_users_by_experience_level(self, user_service, multiple_users):
        """Test searching users by experience level."""
        # Arrange
        experience_level = "senior"
        
        # Act
        users = await user_service.search_users_by_experience_level(experience_level)
        
        # Assert
        assert len(users) > 0
        for user in users:
            assert user.experience_level == experience_level

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_user_statistics(self, user_service, test_user):
        """Test getting user statistics."""
        # Act
        stats = await user_service.get_user_statistics(test_user.id)
        
        # Assert
        assert "profile_views" in stats
        assert "applications_sent" in stats
        assert "applications_received" in stats
        assert "jobs_posted" in stats
        assert isinstance(stats["profile_views"], int)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_update_last_login(self, user_service, test_user):
        """Test updating user's last login timestamp."""
        # Arrange
        original_last_login = test_user.last_login
        
        # Act
        updated_user = await user_service.update_last_login(test_user.id)
        
        # Assert
        assert updated_user.last_login > original_last_login

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_users_paginated(self, user_service, multiple_users):
        """Test getting paginated list of users."""
        # Act
        result = await user_service.get_users_paginated(page=1, page_size=3)
        
        # Assert
        assert "users" in result
        assert "total_count" in result
        assert "page" in result
        assert "page_size" in result
        assert "total_pages" in result
        assert len(result["users"]) <= 3

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_update_user_preferences(self, user_service, test_user):
        """Test updating user preferences."""
        # Arrange
        preferences = {
            "email_notifications": False,
            "job_alerts": True,
            "profile_visibility": "private"
        }
        
        # Act
        updated_user = await user_service.update_user_preferences(test_user.id, preferences)
        
        # Assert
        assert updated_user.email_notifications is False
        assert updated_user.job_alerts is True
        assert updated_user.profile_visibility == "private"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_add_user_skill(self, user_service, test_user):
        """Test adding a skill to user."""
        # Arrange
        new_skill = "Docker"
        
        # Act
        updated_user = await user_service.add_user_skill(test_user.id, new_skill)
        
        # Assert
        assert new_skill in updated_user.skills

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_remove_user_skill(self, user_service, test_user):
        """Test removing a skill from user."""
        # Arrange
        skill_to_remove = test_user.skills[0] if test_user.skills else "Python"
        
        # Act
        updated_user = await user_service.remove_user_skill(test_user.id, skill_to_remove)
        
        # Assert
        assert skill_to_remove not in (updated_user.skills or [])

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_user_activity_feed(self, user_service, test_user):
        """Test getting user activity feed."""
        # Act
        activities = await user_service.get_user_activity_feed(test_user.id, limit=10)
        
        # Assert
        assert isinstance(activities, list)
        assert len(activities) <= 10

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_check_user_permissions(self, user_service, test_user, admin_user):
        """Test checking user permissions."""
        # Act
        regular_user_perms = await user_service.check_user_permissions(test_user.id)
        admin_user_perms = await user_service.check_user_permissions(admin_user.id)
        
        # Assert
        assert regular_user_perms["can_post_jobs"] is True
        assert regular_user_perms["can_moderate"] is False
        assert admin_user_perms["can_moderate"] is True

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_export_user_data(self, user_service, test_user):
        """Test exporting user data (GDPR compliance)."""
        # Act
        user_data = await user_service.export_user_data(test_user.id)
        
        # Assert
        assert "personal_info" in user_data
        assert "profile_data" in user_data
        assert "applications" in user_data
        assert "resumes" in user_data
        assert user_data["personal_info"]["email"] == test_user.email

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_validate_user_data_success(self, user_service, sample_user_data):
        """Test successful user data validation."""
        # Act
        is_valid, errors = await user_service.validate_user_data(sample_user_data)
        
        # Assert
        assert is_valid is True
        assert len(errors) == 0

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_validate_user_data_failure(self, user_service):
        """Test user data validation with invalid data."""
        # Arrange
        invalid_data = {
            "email": "invalid-email",
            "preferred_salary_min": -1000,
            "experience_level": "invalid_level"
        }
        
        # Act
        is_valid, errors = await user_service.validate_user_data(invalid_data)
        
        # Assert
        assert is_valid is False
        assert len(errors) > 0
        assert any("email" in error for error in errors)

    @pytest.mark.asyncio
    @pytest.mark.unit
    @patch('app.services.user_service.send_email')
    async def test_send_welcome_email(self, mock_send_email, user_service, test_user):
        """Test sending welcome email to new user."""
        # Arrange
        mock_send_email.return_value = True
        
        # Act
        result = await user_service.send_welcome_email(test_user.id)
        
        # Assert
        assert result is True
        mock_send_email.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.unit
    @patch('app.services.user_service.generate_verification_token')
    async def test_send_verification_email(self, mock_generate_token, user_service, test_user):
        """Test sending verification email."""
        # Arrange
        mock_generate_token.return_value = "verification-token"
        
        # Act
        result = await user_service.send_verification_email(test_user.id)
        
        # Assert
        assert result is True
        mock_generate_token.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_bulk_update_users(self, user_service, multiple_users):
        """Test bulk updating multiple users."""
        # Arrange
        user_ids = [user.id for user in multiple_users[:3]]
        update_data = {"is_verified": True}
        
        # Act
        updated_count = await user_service.bulk_update_users(user_ids, update_data)
        
        # Assert
        assert updated_count == 3

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_similar_users(self, user_service, test_user):
        """Test finding similar users based on profile."""
        # Act
        similar_users = await user_service.get_similar_users(test_user.id, limit=5)
        
        # Assert
        assert isinstance(similar_users, list)
        assert len(similar_users) <= 5
        assert all(user.id != test_user.id for user in similar_users)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_calculate_profile_completeness(self, user_service, test_user):
        """Test calculating user profile completeness percentage."""
        # Act
        completeness = await user_service.calculate_profile_completeness(test_user.id)
        
        # Assert
        assert isinstance(completeness, dict)
        assert "percentage" in completeness
        assert "missing_fields" in completeness
        assert 0 <= completeness["percentage"] <= 100

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_service_performance_under_load(self, user_service, performance_monitor):
        """Test service performance under load."""
        # Arrange
        performance_monitor.start()
        
        # Act
        tasks = []
        for i in range(100):
            task = user_service.get_user_by_id(f"user-{i}")
            tasks.append(task)
        
        # Some tasks will fail (user not found), but we're testing performance
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Assert
        metrics = performance_monitor.stop()
        assert metrics["duration_seconds"] < 5.0  # Should complete within 5 seconds
        assert metrics["peak_memory_mb"] < 100  # Should not use excessive memory

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_concurrent_user_updates(self, user_service, test_user):
        """Test handling concurrent updates to the same user."""
        # Arrange
        update_tasks = []
        for i in range(10):
            update_data = {"bio": f"Updated bio {i}"}
            task = user_service.update_user(test_user.id, update_data)
            update_tasks.append(task)
        
        # Act
        results = await asyncio.gather(*update_tasks, return_exceptions=True)
        
        # Assert
        # At least some updates should succeed
        successful_updates = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_updates) > 0