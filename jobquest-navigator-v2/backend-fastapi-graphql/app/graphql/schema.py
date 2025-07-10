"""
Main GraphQL schema combining all types, queries and mutations
Strawberry GraphQL implementation maintaining compatibility with original Graphene schema
"""

import strawberry
from typing import List, Optional

from app.graphql.queries.user import UserQuery
from app.graphql.queries.job import JobQuery
from app.graphql.mutations.user import UserMutation
from app.graphql.mutations.job import JobMutation
from app.graphql.mutations.user_job import UserJobMutation
from app.graphql.resolvers.hybrid import HybridQuery, HybridMutation


@strawberry.type
class Query(UserQuery, JobQuery, HybridQuery):
    """
    Root Query type combining all query resolvers
    Includes hybrid resolvers for gradual migration
    """
    
    @strawberry.field
    async def hello(self) -> str:
        return "Hello from JobQuest Navigator v2!"
    
    @strawberry.field
    async def migration_status(self) -> str:
        """Check which features are using FastAPI vs Django"""
        from app.graphql.resolvers.hybrid import get_migration_status
        status = get_migration_status()
        return f"FastAPI: {list(k for k, v in status.items() if v)}, Django: {list(k for k, v in status.items() if not v)}"


@strawberry.type
class Mutation(UserMutation, JobMutation, UserJobMutation, HybridMutation):
    """
    Root Mutation type combining all mutation resolvers
    Includes hybrid mutations for gradual migration and user job creation
    """
    pass


# Create main schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)