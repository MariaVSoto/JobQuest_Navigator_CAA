"""
Core serializers for JobQuest Navigator Backend.

This module contains DRF serializers for authentication, user management,
and shared models across all epics.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Location, Company, UserPreference, ActivityLog


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'full_name', 'phone_number', 'current_job_title',
            'years_of_experience', 'industry', 'career_level'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value
    
    def validate_username(self, value):
        """Validate username uniqueness."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("User with this username already exists.")
        return value
    
    def create(self, validated_data):
        """Create new user with encrypted password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Create default user preferences
        UserPreference.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate user credentials."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Try to authenticate with email as username
            user = authenticate(username=email, password=password)
            
            if not user:
                # Try to find user by email and authenticate with username
                try:
                    user_obj = User.objects.get(email=email)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError("Invalid email or password.")
        else:
            raise serializers.ValidationError("Must include email and password.")


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information.
    """
    current_location = serializers.StringRelatedField(read_only=True)
    preferred_locations = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'full_name', 'date_of_birth',
            'profile_picture', 'bio', 'phone_number', 'current_location',
            'preferred_locations', 'current_job_title', 'years_of_experience',
            'industry', 'career_level', 'job_search_status',
            'salary_expectation_min', 'salary_expectation_max',
            'preferred_work_type', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'email', 'date_joined', 'last_login']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    """
    current_location_id = serializers.UUIDField(write_only=True, required=False)
    preferred_location_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = User
        fields = [
            'full_name', 'date_of_birth', 'profile_picture', 'bio',
            'phone_number', 'current_job_title', 'years_of_experience',
            'industry', 'career_level', 'job_search_status',
            'salary_expectation_min', 'salary_expectation_max',
            'preferred_work_type', 'current_location_id', 'preferred_location_ids'
        ]
    
    def update(self, instance, validated_data):
        """Update user profile with location handling."""
        # Handle current location
        current_location_id = validated_data.pop('current_location_id', None)
        if current_location_id:
            try:
                location = Location.objects.get(id=current_location_id)
                instance.current_location = location
            except Location.DoesNotExist:
                raise serializers.ValidationError("Invalid current location ID.")
        
        # Handle preferred locations
        preferred_location_ids = validated_data.pop('preferred_location_ids', None)
        if preferred_location_ids is not None:
            try:
                locations = Location.objects.filter(id__in=preferred_location_ids)
                if len(locations) != len(preferred_location_ids):
                    raise serializers.ValidationError("One or more preferred location IDs are invalid.")
                instance.preferred_locations.set(locations)
            except Exception:
                raise serializers.ValidationError("Error updating preferred locations.")
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate new password confirmation."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs
    
    def save(self):
        """Update user password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for password reset request.
    """
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validate email exists."""
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation.
    """
    token = serializers.CharField()
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate new password confirmation."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs


class LocationSerializer(serializers.ModelSerializer):
    """
    Serializer for location data.
    """
    full_address = serializers.ReadOnlyField()
    
    class Meta:
        model = Location
        fields = [
            'id', 'name', 'city', 'state', 'country', 'country_code',
            'latitude', 'longitude', 'postal_code', 'timezone',
            'google_place_id', 'google_formatted_address', 'full_address'
        ]


class LocationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating location data.
    """
    class Meta:
        model = Location
        fields = [
            'name', 'city', 'state', 'country', 'country_code',
            'latitude', 'longitude', 'postal_code', 'timezone',
            'google_place_id', 'google_formatted_address'
        ]
    
    def validate(self, attrs):
        """Validate location uniqueness."""
        city = attrs.get('city')
        state = attrs.get('state', '')
        country = attrs.get('country')
        
        if Location.objects.filter(city=city, state=state, country=country).exists():
            raise serializers.ValidationError("Location already exists.")
        
        return attrs


class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer for company data.
    """
    headquarters = LocationSerializer(read_only=True)
    locations = LocationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'slug', 'description', 'website', 'logo_url',
            'industry', 'company_size', 'founded_year', 'headquarters',
            'locations', 'email', 'phone', 'linkedin_url', 'twitter_handle',
            'glassdoor_id', 'glassdoor_rating', 'glassdoor_review_count',
            'adzuna_company_id', 'last_research_update'
        ]


class CompanyCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating company data.
    """
    headquarters_id = serializers.UUIDField(write_only=True, required=False)
    location_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Company
        fields = [
            'name', 'description', 'website', 'logo_url', 'industry',
            'company_size', 'founded_year', 'email', 'phone',
            'linkedin_url', 'twitter_handle', 'glassdoor_id',
            'adzuna_company_id', 'headquarters_id', 'location_ids'
        ]
    
    def create(self, validated_data):
        """Create company with location relationships."""
        headquarters_id = validated_data.pop('headquarters_id', None)
        location_ids = validated_data.pop('location_ids', [])
        
        company = Company.objects.create(**validated_data)
        
        # Set headquarters
        if headquarters_id:
            try:
                headquarters = Location.objects.get(id=headquarters_id)
                company.headquarters = headquarters
                company.save()
            except Location.DoesNotExist:
                pass
        
        # Set locations
        if location_ids:
            try:
                locations = Location.objects.filter(id__in=location_ids)
                company.locations.set(locations)
            except Exception:
                pass
        
        return company


class UserPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for user preferences.
    """
    class Meta:
        model = UserPreference
        fields = [
            'job_alert_frequency', 'max_commute_distance', 'auto_save_resume',
            'resume_privacy_level', 'enable_ai_suggestions', 'ai_suggestion_frequency',
            'email_notifications', 'push_notifications', 'sms_notifications',
            'profile_visibility', 'theme', 'language', 'timezone'
        ]


class ActivityLogSerializer(serializers.ModelSerializer):
    """
    Serializer for activity logs.
    """
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = [
            'id', 'user', 'action', 'description', 'epic',
            'ip_address', 'user_agent', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class TokenSerializer(serializers.Serializer):
    """
    Serializer for JWT token response.
    """
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserProfileSerializer()
    
    @classmethod
    def get_token_for_user(cls, user):
        """Generate JWT tokens for user."""
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserProfileSerializer(user).data
        } 