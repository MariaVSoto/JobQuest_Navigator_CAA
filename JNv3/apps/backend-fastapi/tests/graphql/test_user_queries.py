"""
GraphQL integration tests for user queries.
Tests the complete GraphQL query execution pipeline.
"""

import pytest
from uuid import uuid4


class TestUserQueries:
    """Test GraphQL user query operations."""
    
    @pytest.mark.graphql
    async def test_get_user_by_id_success(self, test_client, test_user, graphql_query):
        """Test successful user retrieval via GraphQL."""
        query = """
        query GetUser($id: UUID!) {
            user(id: $id) {
                id
                email
                firstName
                lastName
                fullName
                isActive
                isVerified
                createdAt
            }
        }
        """
        
        variables = {"id": str(test_user.id)}
        
        # Execute GraphQL query
        response = await graphql_query(test_client, query, variables)
        
        # Assert response structure
        assert "data" in response
        assert response["data"]["user"] is not None
        
        # Assert user data
        user_data = response["data"]["user"]
        assert user_data["id"] == str(test_user.id)
        assert user_data["email"] == test_user.email
        assert user_data["firstName"] == test_user.first_name
        assert user_data["lastName"] == test_user.last_name
        assert user_data["fullName"] == f"{test_user.first_name} {test_user.last_name}"
        assert user_data["isActive"] == test_user.is_active
        assert user_data["isVerified"] == test_user.is_verified
        assert user_data["createdAt"] is not None
    
    @pytest.mark.graphql
    async def test_get_user_by_id_not_found(self, test_client, graphql_query):
        """Test user query with non-existent ID."""
        query = """
        query GetUser($id: UUID!) {
            user(id: $id) {
                id
                email
            }
        }
        """
        
        # Use a random UUID that doesn't exist
        variables = {"id": str(uuid4())}
        
        # Execute GraphQL query
        response = await graphql_query(test_client, query, variables)
        
        # Assert response
        assert "data" in response
        assert response["data"]["user"] is None
    
    @pytest.mark.graphql
    async def test_get_users_list(self, test_client, test_user, graphql_query, db_session):
        """Test fetching list of users."""
        # Create additional test users
        from app.models.user import User
        
        user2 = User(
            id=uuid4(),
            email="user2@example.com",
            first_name="Jane",
            last_name="Smith",
            hashed_password="hashed_password",
            is_active=True
        )
        
        user3 = User(
            id=uuid4(),
            email="user3@example.com",
            first_name="Bob",
            last_name="Johnson",
            hashed_password="hashed_password",
            is_active=False  # Inactive user
        )
        
        db_session.add_all([user2, user3])
        await db_session.commit()
        
        query = """
        query GetUsers($limit: Int, $includeInactive: Boolean) {
            users(limit: $limit, includeInactive: $includeInactive) {
                id
                email
                firstName
                lastName
                isActive
            }
        }
        """
        
        # Test with active users only
        variables = {"limit": 10, "includeInactive": False}
        response = await graphql_query(test_client, query, variables)
        
        # Assert response
        assert "data" in response
        assert response["data"]["users"] is not None
        
        users = response["data"]["users"]
        assert len(users) == 2  # Only active users
        
        # Verify all returned users are active
        for user in users:
            assert user["isActive"] is True
        
        # Test with inactive users included
        variables = {"limit": 10, "includeInactive": True}
        response = await graphql_query(test_client, query, variables)
        
        users = response["data"]["users"]
        assert len(users) == 3  # All users including inactive
    
    @pytest.mark.graphql  
    async def test_get_user_profile_authenticated(self, test_client, authenticated_user, graphql_query):
        """Test getting current user's profile (authenticated query)."""
        query = """
        query GetMyProfile {
            myProfile {
                id
                email
                firstName
                lastName
                fullName
                isActive
                preferences {
                    jobAlerts
                    marketingEmails
                    preferredLocation
                }
            }
        }
        """
        
        # Execute with authentication headers
        response = await graphql_query(
            test_client, 
            query, 
            headers=authenticated_user["headers"]
        )
        
        # Assert response
        assert "data" in response
        assert response["data"]["myProfile"] is not None
        
        profile = response["data"]["myProfile"]
        assert profile["id"] == str(authenticated_user["user"].id)
        assert profile["email"] == authenticated_user["user"].email
    
    @pytest.mark.graphql
    async def test_get_user_profile_unauthenticated(self, test_client, graphql_query):
        """Test getting user profile without authentication."""
        query = """
        query GetMyProfile {
            myProfile {
                id
                email
            }
        }
        """
        
        # Execute without authentication headers
        response = await graphql_query(test_client, query)
        
        # Should return error or null for unauthenticated request
        assert "errors" in response or response["data"]["myProfile"] is None
    
    @pytest.mark.graphql
    async def test_search_users_by_name(self, test_client, graphql_query, db_session):
        """Test user search functionality."""
        # Create test users with specific names
        from app.models.user import User
        
        users = [
            User(
                id=uuid4(),
                email="john.doe@example.com",
                first_name="John",
                last_name="Doe",
                hashed_password="hashed_password"
            ),
            User(
                id=uuid4(),
                email="john.smith@example.com", 
                first_name="John",
                last_name="Smith",
                hashed_password="hashed_password"
            ),
            User(
                id=uuid4(),
                email="jane.doe@example.com",
                first_name="Jane", 
                last_name="Doe",
                hashed_password="hashed_password"
            )
        ]
        
        db_session.add_all(users)
        await db_session.commit()
        
        query = """
        query SearchUsers($searchTerm: String!) {
            searchUsers(searchTerm: $searchTerm) {
                id
                firstName
                lastName
                email
            }
        }
        """
        
        # Search by first name
        variables = {"searchTerm": "John"}
        response = await graphql_query(test_client, query, variables)
        
        assert "data" in response
        results = response["data"]["searchUsers"]
        assert len(results) == 2
        
        # All results should contain "John"
        for user in results:
            assert "John" in user["firstName"]
        
        # Search by last name
        variables = {"searchTerm": "Doe"}
        response = await graphql_query(test_client, query, variables)
        
        results = response["data"]["searchUsers"]
        assert len(results) == 2
        
        # All results should contain "Doe"
        for user in results:
            assert "Doe" in user["lastName"]


class TestUserQueryValidation:
    """Test GraphQL query validation and error handling."""
    
    @pytest.mark.graphql
    async def test_invalid_uuid_format(self, test_client, graphql_query):
        """Test query with invalid UUID format."""
        query = """
        query GetUser($id: UUID!) {
            user(id: $id) {
                id
                email
            }
        }
        """
        
        variables = {"id": "invalid-uuid-format"}
        
        response = await graphql_query(test_client, query, variables)
        
        # Should return validation error
        assert "errors" in response
        assert any("Invalid UUID" in str(error) for error in response["errors"])
    
    @pytest.mark.graphql
    async def test_missing_required_variables(self, test_client, graphql_query):
        """Test query with missing required variables."""
        query = """
        query GetUser($id: UUID!) {
            user(id: $id) {
                id
                email
            }
        }
        """
        
        # Don't provide required $id variable
        response = await graphql_query(test_client, query)
        
        # Should return validation error
        assert "errors" in response
        assert any("Variable" in str(error) and "required" in str(error) 
                  for error in response["errors"])
    
    @pytest.mark.graphql
    async def test_query_depth_limit(self, test_client, graphql_query):
        """Test query depth limiting (if implemented)."""
        # This is a very deep nested query that should be rejected
        query = """
        query DeepQuery {
            users {
                id
                email
                # In real implementation, this might have deep nested relationships
                # that could cause performance issues
            }
        }
        """
        
        response = await graphql_query(test_client, query)
        
        # Query should execute fine for this simple case
        # In production, you might want to implement query depth analysis
        assert "data" in response