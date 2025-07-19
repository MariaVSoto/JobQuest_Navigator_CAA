"""
Custom GraphQL JWT authentication for JobQuest Navigator.
"""

import graphene
import graphql_jwt
from graphql import GraphQLError
from django.contrib.auth import authenticate
import jwt
from django.conf import settings
import datetime


class CustomJSONWebToken(graphene.Mutation):
    """
    Custom JWT mutation that includes both email and username in the token payload.
    """
    
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
    
    token = graphene.String()
    
    @staticmethod
    def mutate(root, info, email, password):
        # Authenticate using email as username (since USERNAME_FIELD = 'email')
        user = authenticate(
            request=info.context,
            username=email,
            password=password
        )
        
        if not user:
            raise GraphQLError('Please enter valid credentials')
        
        if not user.is_active:
            raise GraphQLError('User account is disabled')
        
        # Create the token with custom payload including username
        now = datetime.datetime.utcnow()
        exp_time = now + settings.GRAPHQL_JWT['JWT_EXPIRATION_DELTA']
        
        payload = {
            'email': user.email,
            'username': user.username,  # Include username for middleware compatibility
            'user_id': str(user.pk),
            'exp': int(exp_time.timestamp()),
            'origIat': int(now.timestamp()),
        }
        
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        return CustomJSONWebToken(token=token)