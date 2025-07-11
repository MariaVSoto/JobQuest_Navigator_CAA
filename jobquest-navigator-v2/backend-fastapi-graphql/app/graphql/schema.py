"""
Main GraphQL schema combining all types, queries and mutations
Strawberry GraphQL implementation maintaining compatibility with original Graphene schema
"""

import strawberry
from typing import List, Optional

# Temporarily disable problematic imports to fix schema loading
# from app.graphql.queries.user import UserQuery  
# from app.graphql.queries.job import JobQuery
# from app.graphql.mutations.user import UserMutation
# from app.graphql.mutations.job import JobMutation
# from app.graphql.mutations.user_job import UserJobMutation
# from app.graphql.resolvers.hybrid import HybridQuery, HybridMutation


@strawberry.type
class User:
    id: str
    email: str
    username: str
    fullName: Optional[str] = None
    bio: Optional[str] = None
    currentJobTitle: Optional[str] = None
    yearsOfExperience: Optional[int] = None
    industry: Optional[str] = None
    careerLevel: Optional[str] = None
    jobSearchStatus: Optional[str] = None
    preferredWorkType: Optional[str] = None

@strawberry.type
class Query:
    """
    Root Query type - minimal implementation to get schema working
    """
    
    @strawberry.field
    async def hello(self) -> str:
        return "Hello from JobQuest Navigator v2!"
    
    @strawberry.field
    async def migration_status(self) -> str:
        """Check which features are using FastAPI vs Django"""
        return "Migration in progress - basic schema loaded"
    
    @strawberry.field
    async def me(self) -> Optional[User]:
        """Get current user - minimal implementation for demo"""
        # For demo purposes, return a mock user
        # In production, this would get user from authentication context
        return User(
            id="demo-user-id",
            email="test@example.com",
            username="testuser",
            fullName="Test User",
            bio="Demo user for testing",
            currentJobTitle="Software Developer",
            yearsOfExperience=5,
            industry="Technology",
            careerLevel="mid",
            jobSearchStatus="actively_looking",
            preferredWorkType="hybrid"
        )


@strawberry.input
class RegisterUserInput:
    email: str
    username: str
    password: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None

@strawberry.type
class RegisterUserResponse:
    success: bool
    errors: Optional[List[str]] = None
    user: Optional[User] = None  # Return full User object

@strawberry.type
class TokenResponse:
    token: Optional[str] = None

@strawberry.type
class Mutation:
    """
    Root Mutation type - minimal implementation to get schema working
    """
    
    @strawberry.field
    async def test_mutation(self, message: str) -> str:
        return f"Test mutation received: {message}"
    
    @strawberry.field
    async def register_user(
        self,
        email: str,
        username: str,
        password: str,
        firstName: Optional[str] = None,
        lastName: Optional[str] = None
    ) -> RegisterUserResponse:
        """Register a new user - minimal implementation for demo"""
        # For demo purposes, always return success
        # In production, this would validate inputs and create user in database
        
        # Create a demo user object with the provided data
        demo_user = User(
            id="demo-user-id",
            email=email,
            username=username,
            fullName=f"{firstName or ''} {lastName or ''}".strip() or None,
            bio="New user registered via demo",
            currentJobTitle="Software Developer",
            yearsOfExperience=0,
            industry="Technology",
            careerLevel="entry",
            jobSearchStatus="actively_looking",
            preferredWorkType="hybrid"
        )
        
        return RegisterUserResponse(
            success=True,
            user=demo_user,
            errors=None
        )
    
    @strawberry.field
    async def token_auth(
        self,
        username: str,
        password: str
    ) -> TokenResponse:
        """Authenticate user and return token - minimal implementation for demo"""
        # For demo purposes, always return a mock token
        # In production, this would validate credentials and return JWT
        return TokenResponse(token="mock-jwt-token-for-demo")
    
    @strawberry.field
    async def verify_token(
        self,
        token: str
    ) -> bool:
        """Verify token - minimal implementation for demo"""
        # For demo purposes, always return True for non-empty tokens
        return bool(token)


# Create main schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)