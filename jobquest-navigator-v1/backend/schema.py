"""
Main GraphQL schema for JobQuest Navigator.
Combines all app schemas into a unified GraphQL API.
"""

import graphene
import graphql_jwt
from core.schema import UserQuery, UserMutation
from core.debug_auth import DebugAuthQuery
from jobs.schema import JobQuery, JobMutation


class Query(UserQuery, JobQuery, DebugAuthQuery, graphene.ObjectType):
    """Root Query combining all app queries."""
    pass


class Mutation(UserMutation, JobMutation, graphene.ObjectType):
    """Root Mutation combining all app mutations."""
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)