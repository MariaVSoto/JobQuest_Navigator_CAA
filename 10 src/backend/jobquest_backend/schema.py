"""
Main GraphQL schema for JobQuest Navigator.
Combines all app-specific schemas into a unified GraphQL API.
"""

import graphene
import graphql_jwt
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model

# Import app-specific schemas
from jobs.schema import JobQuery, JobMutation
from core.schema import UserQuery, UserMutation

User = get_user_model()


class Query(
    UserQuery,
    JobQuery,
    graphene.ObjectType
):
    """
    Main GraphQL query class that combines all queries from different apps.
    """
    pass


class Mutation(
    UserMutation,
    JobMutation,
    graphene.ObjectType
):
    """
    Main GraphQL mutation class that combines all mutations from different apps.
    """
    # JWT Authentication mutations
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


# Create the main schema
schema = graphene.Schema(query=Query, mutation=Mutation)