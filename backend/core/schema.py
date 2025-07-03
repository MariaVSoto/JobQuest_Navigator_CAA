"""
GraphQL schema for core models (User, Location, Company).
"""

import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from django.db.models import Q
from graphql import GraphQLError

from .models import User, Location, Company
from .decorators import login_required, mutation_login_required

User = get_user_model()


class UserType(DjangoObjectType):
    """GraphQL type for User model."""
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 
            'full_name', 'date_of_birth', 'bio', 'phone_number',
            'current_job_title', 'years_of_experience', 'industry',
            'career_level', 'job_search_status', 'preferred_work_type',
            'date_joined', 'last_login'
        )


class LocationType(DjangoObjectType):
    """GraphQL type for Location model."""
    
    class Meta:
        model = Location
        fields = (
            'id', 'name', 'city', 'state', 'country', 'country_code',
            'latitude', 'longitude', 'postal_code', 'timezone',
            'google_place_id', 'google_formatted_address', 'full_address'
        )


class CompanyType(DjangoObjectType):
    """GraphQL type for Company model."""
    
    class Meta:
        model = Company
        fields = (
            'id', 'name', 'slug', 'description', 'website', 'logo_url',
            'industry', 'company_size', 'founded_year', 'headquarters',
            'email', 'phone', 'linkedin_url', 'twitter_handle',
            'glassdoor_rating', 'glassdoor_review_count'
        )


class UserQuery(graphene.ObjectType):
    """User-related queries."""
    
    # Single user queries
    me = graphene.Field(UserType)
    user = graphene.Field(UserType, id=graphene.ID())
    
    # List queries
    locations = graphene.List(LocationType)
    companies = graphene.List(CompanyType)
    
    # Search queries
    search_locations = graphene.List(
        LocationType,
        query=graphene.String(required=True),
        limit=graphene.Int(default_value=10)
    )
    
    search_companies = graphene.List(
        CompanyType,
        query=graphene.String(required=True),
        limit=graphene.Int(default_value=10)
    )

    @login_required
    def resolve_me(self, info):
        """Get current authenticated user."""
        return info.context.user

    @login_required
    def resolve_user(self, info, id):
        """Get user by ID, but only for the currently authenticated user."""
        current_user = info.context.user
        
        # CRITICAL: Prevent users from querying other users' data.
        if str(current_user.pk) != str(id):
            raise GraphQLError("You can only query your own user data.")

        try:
            # We already know the user exists and is the one making the request.
            return current_user
        except User.DoesNotExist:
            # This case is unlikely given the checks, but good practice.
            return None

    def resolve_locations(self, info):
        """Get all locations."""
        return Location.objects.all().order_by('name')

    def resolve_companies(self, info):
        """Get all companies."""
        return Company.objects.all().order_by('name')

    def resolve_search_locations(self, info, query, limit=10):
        """Search locations by query string."""
        return Location.objects.filter(
            Q(name__icontains=query) |
            Q(city__icontains=query) |
            Q(state__icontains=query) |
            Q(country__icontains=query)
        ).distinct()[:limit]

    def resolve_search_companies(self, info, query, limit=10):
        """Search companies by query string."""
        return Company.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(industry__icontains=query)
        ).distinct()[:limit]


class UpdateUserProfileMutation(graphene.Mutation):
    """Mutation to update user profile."""
    
    class Arguments:
        full_name = graphene.String()
        bio = graphene.String()
        phone_number = graphene.String()
        current_job_title = graphene.String()
        years_of_experience = graphene.Int()
        industry = graphene.String()
        career_level = graphene.String()
        job_search_status = graphene.String()
        preferred_work_type = graphene.String()

    user = graphene.Field(UserType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @mutation_login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        
        # Whitelist of fields that users are allowed to update
        UPDATABLE_FIELDS = {
            'full_name', 'bio', 'phone_number', 'current_job_title',
            'years_of_experience', 'industry', 'career_level',
            'job_search_status', 'preferred_work_type'
        }

        # Update user fields safely using whitelist
        for field, value in kwargs.items():
            if field in UPDATABLE_FIELDS and value is not None:
                setattr(user, field, value)

        from django.core.exceptions import ValidationError
        try:
            # Call full_clean() to trigger model validation
            user.full_clean()
            user.save()
            return UpdateUserProfileMutation(
                user=user,
                success=True,
                errors=[]
            )
        except ValidationError as e:
            # Convert Django's validation error dict to a list of strings
            errors = [msg for field_errors in e.message_dict.values() for msg in field_errors]
            return UpdateUserProfileMutation(success=False, errors=errors)
        except Exception as e:
            # Log unexpected exceptions for debugging (in production, use proper logging)
            # logger.error(f"Unexpected error in UpdateUserProfileMutation: {e}")
            return UpdateUserProfileMutation(
                success=False,
                errors=['An unexpected error occurred. Please try again.']
            )


class RegisterUserMutation(graphene.Mutation):
    """Mutation to register a new user."""
    
    class Arguments:
        email = graphene.String(required=True)
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        first_name = graphene.String()
        last_name = graphene.String()

    user = graphene.Field(UserType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, email, username, password, first_name=None, last_name=None):
        from django.contrib.auth import get_user_model
        from django.core.exceptions import ValidationError
        from django.contrib.auth.password_validation import validate_password
        
        User = get_user_model()
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return RegisterUserMutation(
                success=False, 
                errors=['User with this email already exists.']
            )
        
        if User.objects.filter(username=username).exists():
            return RegisterUserMutation(
                success=False, 
                errors=['User with this username already exists.']
            )
        
        try:
            # Validate password
            validate_password(password)
            
            # Create user
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password,
                first_name=first_name or '',
                last_name=last_name or ''
            )
            
            return RegisterUserMutation(
                user=user,
                success=True,
                errors=[]
            )
            
        except ValidationError as e:
            # Convert Django's validation error to a list of strings
            errors = [str(error) for error in e.messages] if hasattr(e, 'messages') else [str(e)]
            return RegisterUserMutation(success=False, errors=errors)
        except Exception as e:
            # Log unexpected exceptions for debugging
            return RegisterUserMutation(
                success=False,
                errors=['Registration failed. Please try again.']
            )


class UserMutation(graphene.ObjectType):
    """User-related mutations."""
    
    update_profile = UpdateUserProfileMutation.Field()
    register_user = RegisterUserMutation.Field()