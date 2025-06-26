"""
GraphQL Security Decorators for JobQuest Navigator.

This module provides decorators for securing GraphQL resolvers and mutations
with authentication and authorization checks.
"""

from functools import wraps
from graphql import GraphQLError


def login_required(func):
    """
    Decorator for GraphQL resolvers that require user authentication.
    Raises a GraphQLError if the user is not authenticated.
    
    Usage:
        @login_required
        def resolve_my_profile(self, info):
            return info.context.user
    """
    @wraps(func)
    def wrapper(self, info, *args, **kwargs):
        user = info.context.user
        if not user or not user.is_authenticated:
            # Using GraphQLError provides a clean error message to the client.
            raise GraphQLError('Authentication is required to perform this action.')
        
        return func(self, info, *args, **kwargs)
    return wrapper


def mutation_login_required(mutate_func):
    """
    Decorator for GraphQL mutations that require user authentication.
    Returns a standard mutation error payload if the user is not authenticated,
    preserving the mutation's response structure.
    
    Usage:
        @mutation_login_required
        def mutate(self, info, **kwargs):
            user = info.context.user
            # Authentication is already verified by decorator
            ...
    """
    @wraps(mutate_func)
    def wrapper(self, info, **kwargs):
        user = info.context.user
        if not user or not user.is_authenticated:
            # self is the mutation instance, so self.__class__ is the mutation's class.
            # This returns the expected structure e.g. { success: false, errors: [...] }
            return self.__class__(
                success=False,
                errors=['Authentication is required to perform this action.']
            )
        
        return mutate_func(self, info, **kwargs)
    return wrapper


def staff_required(func):
    """
    Decorator for GraphQL resolvers that require staff privileges.
    Raises a GraphQLError if the user is not authenticated or not staff.
    
    Usage:
        @staff_required
        def resolve_admin_data(self, info):
            return AdminData.objects.all()
    """
    @wraps(func)
    def wrapper(self, info, *args, **kwargs):
        user = info.context.user
        if not user or not user.is_authenticated:
            raise GraphQLError('Authentication is required to perform this action.')
        
        if not user.is_staff:
            raise GraphQLError('Staff privileges are required to perform this action.')
        
        return func(self, info, *args, **kwargs)
    return wrapper


def owner_or_staff_required(owner_field='user'):
    """
    Decorator factory for GraphQL resolvers that require the user to be either
    the owner of the resource or have staff privileges.
    
    Args:
        owner_field (str): The field name on the object that contains the owner user.
    
    Usage:
        @owner_or_staff_required('user')
        def resolve_private_application(self, info, id):
            application = JobApplication.objects.get(pk=id)
            return application
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, info, *args, **kwargs):
            user = info.context.user
            if not user or not user.is_authenticated:
                raise GraphQLError('Authentication is required to perform this action.')
            
            # Get the result first
            result = func(self, info, *args, **kwargs)
            
            # Check ownership or staff status
            if result and hasattr(result, owner_field):
                owner = getattr(result, owner_field)
                if owner != user and not user.is_staff:
                    raise GraphQLError('You do not have permission to access this resource.')
            
            return result
        return wrapper
    return decorator