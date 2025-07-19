"""
Custom permissions for JobQuest Navigator Backend.

This module contains custom permission classes for role-based access control
and feature-specific permissions across all epics.
"""

from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsOwner(BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Only allow access to the owner of the object
        return obj.user == request.user


class IsProfileOwner(BasePermission):
    """
    Custom permission for user profile access.
    """
    
    def has_object_permission(self, request, view, obj):
        # Only allow users to access their own profile
        return obj == request.user


class CanAccessEpic1(BasePermission):
    """
    Permission for Epic 1 - Job Mapping features.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if user has access to job mapping features
        # This could be based on subscription, user type, etc.
        return True  # For now, all authenticated users have access


class CanAccessEpic2(BasePermission):
    """
    Permission for Epic 2 - Resume Management features.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if user has access to resume management features
        return True  # For now, all authenticated users have access


class CanAccessEpic3(BasePermission):
    """
    Permission for Epic 3 - Resume Feedback features.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if user has access to AI feedback features
        # This might require a premium subscription
        return True  # For now, all authenticated users have access


class CanAccessEpic4(BasePermission):
    """
    Permission for Epic 4 - Certification Roadmap features.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if user has access to certification features
        return True  # For now, all authenticated users have access


class CanAccessEpic6(BasePermission):
    """
    Permission for Epic 6 - Company Research features.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if user has access to company research features
        return True  # For now, all authenticated users have access


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admins to edit, but allow read access to all.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to admin users
        return request.user.is_authenticated and request.user.is_staff


class CanManageCompanies(BasePermission):
    """
    Permission for managing company data.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only staff users can manage company data
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.is_staff


class CanManageLocations(BasePermission):
    """
    Permission for managing location data.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only staff users can manage location data
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.is_staff


class HasValidSubscription(BasePermission):
    """
    Permission for premium features requiring valid subscription.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if user has valid subscription
        # This would integrate with a subscription system
        # For now, return True for all authenticated users
        return True


class RateLimitPermission(BasePermission):
    """
    Permission for rate limiting API access.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Implement rate limiting logic here
        # This could check against a cache or database
        # For now, allow all requests
        return True


class CanAccessAIFeatures(BasePermission):
    """
    Permission for AI-powered features.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if user can access AI features
        # This might require specific permissions or subscription
        user_preferences = getattr(request.user, 'preferences', None)
        if user_preferences:
            return user_preferences.enable_ai_suggestions
        
        return True  # Default to allowing AI features


class CanModifyUserData(BasePermission):
    """
    Permission for modifying user-specific data.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Check if the object belongs to the user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        # If no user relationship, allow access
        return True


class IsActiveUser(BasePermission):
    """
    Permission to check if user account is active.
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.is_active
        )


class CanAccessAnalytics(BasePermission):
    """
    Permission for accessing analytics and reporting features.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only staff or users with analytics permission can access
        return request.user.is_staff or getattr(request.user, 'can_access_analytics', False)


# Composite permissions for common use cases
class AuthenticatedAndActive(BasePermission):
    """
    Composite permission for authenticated and active users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.is_active
        )


class AuthenticatedOwnerOrReadOnly(BasePermission):
    """
    Composite permission for authenticated users who own the object or read-only access.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for owners
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False 