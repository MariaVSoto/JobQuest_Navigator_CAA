"""
Debug authentication middleware to see what's happening with JWT.
"""

import graphene
from graphql import GraphQLError


class DebugAuthQuery(graphene.ObjectType):
    """Debug queries to check authentication status."""
    
    debug_auth_status = graphene.String()
    debug_user_info = graphene.String()
    debug_request_headers = graphene.List(graphene.String)
    
    def resolve_debug_auth_status(self, info):
        """Check authentication status without decorators."""
        user = info.context.user
        
        if not user:
            return "No user in context"
        
        if not hasattr(user, 'is_authenticated'):
            return f"User object has no is_authenticated: {type(user)}"
        
        if user.is_authenticated:
            return f"User authenticated: {user.username} (ID: {user.pk})"
        else:
            return f"User not authenticated: {user}"
    
    def resolve_debug_user_info(self, info):
        """Get detailed user information."""
        user = info.context.user
        
        if not user:
            return "No user in context"
        
        user_info = []
        user_info.append(f"Type: {type(user)}")
        user_info.append(f"Username: {getattr(user, 'username', 'N/A')}")
        user_info.append(f"Email: {getattr(user, 'email', 'N/A')}")
        user_info.append(f"Is authenticated: {getattr(user, 'is_authenticated', 'N/A')}")
        user_info.append(f"Is active: {getattr(user, 'is_active', 'N/A')}")
        user_info.append(f"PK: {getattr(user, 'pk', 'N/A')}")
        
        return " | ".join(user_info)
    
    def resolve_debug_request_headers(self, info):
        """Check request headers."""
        request = info.context
        headers = []
        
        # Check for Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', 'Not found')
        headers.append(f"Authorization: {auth_header}")
        
        # Check for other relevant headers
        for key in ['HTTP_CONTENT_TYPE', 'HTTP_USER_AGENT', 'REQUEST_METHOD']:
            value = request.META.get(key, 'Not found')
            headers.append(f"{key}: {value}")
        
        return headers