"""
Core models for JobQuest Navigator Backend.

This module contains shared models used across all epics:
- Custom User model with extended profile information
- Location models for geolocation features
- Company models for job and research features
- Base models with common fields and behaviors
"""

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class BaseModel(models.Model):
    """
    Abstract base model with common fields for all entities.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Supports all epic requirements with profile information.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    
    # Profile Information
    full_name = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Location Information
    current_location = models.ForeignKey(
        'Location', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='users_current'
    )
    preferred_locations = models.ManyToManyField(
        'Location',
        blank=True,
        related_name='users_preferred'
    )
    
    # Career Information
    current_job_title = models.CharField(max_length=200, blank=True)
    years_of_experience = models.PositiveIntegerField(null=True, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    career_level = models.CharField(
        max_length=20,
        choices=[
            ('entry', 'Entry Level'),
            ('junior', 'Junior'),
            ('mid', 'Mid Level'),
            ('senior', 'Senior'),
            ('lead', 'Lead'),
            ('manager', 'Manager'),
            ('director', 'Director'),
            ('executive', 'Executive'),
        ],
        blank=True
    )
    
    # Preferences
    job_search_status = models.CharField(
        max_length=20,
        choices=[
            ('not_looking', 'Not Looking'),
            ('casually_looking', 'Casually Looking'),
            ('actively_looking', 'Actively Looking'),
            ('open_to_offers', 'Open to Offers'),
        ],
        default='not_looking'
    )
    salary_expectation_min = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    salary_expectation_max = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    preferred_work_type = models.CharField(
        max_length=20,
        choices=[
            ('remote', 'Remote'),
            ('hybrid', 'Hybrid'),
            ('onsite', 'On-site'),
            ('flexible', 'Flexible'),
        ],
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['job_search_status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.full_name or self.username} ({self.email})"

    @property
    def display_name(self):
        return self.full_name or self.username

    def get_active_resume(self):
        """Get the user's currently active resume."""
        return self.resumes.filter(is_active=True).first()


class Location(BaseModel):
    """
    Location model for geolocation features across epics.
    Supports cities, states, countries with coordinates.
    """
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2)  # ISO 3166-1 alpha-2
    
    # Coordinates for mapping
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    # Additional location data
    postal_code = models.CharField(max_length=20, blank=True)
    timezone = models.CharField(max_length=50, blank=True)
    
    # Google Places API data
    google_place_id = models.CharField(max_length=200, blank=True, unique=True)
    google_formatted_address = models.TextField(blank=True)

    class Meta:
        db_table = 'locations'
        unique_together = ['city', 'state', 'country']
        indexes = [
            models.Index(fields=['city', 'country']),
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['google_place_id']),
        ]

    def __str__(self):
        if self.state:
            return f"{self.city}, {self.state}, {self.country}"
        return f"{self.city}, {self.country}"

    @property
    def full_address(self):
        return self.google_formatted_address or str(self)


class Company(BaseModel):
    """
    Company model for job postings and company research.
    Supports Epic 1 (jobs) and Epic 6 (company research).
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    
    # Basic Information
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)
    
    # Company Details
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(
        max_length=20,
        choices=[
            ('startup', '1-10 employees'),
            ('small', '11-50 employees'),
            ('medium', '51-200 employees'),
            ('large', '201-1000 employees'),
            ('enterprise', '1000+ employees'),
        ],
        blank=True
    )
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    
    # Location Information
    headquarters = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headquartered_companies'
    )
    locations = models.ManyToManyField(
        Location,
        blank=True,
        related_name='companies'
    )
    
    # Contact Information
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Social Media & External IDs
    linkedin_url = models.URLField(blank=True)
    twitter_handle = models.CharField(max_length=50, blank=True)
    glassdoor_id = models.CharField(max_length=50, blank=True)
    
    # Ratings & Reviews (aggregated data)
    glassdoor_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        null=True, 
        blank=True
    )
    glassdoor_review_count = models.PositiveIntegerField(default=0)
    
    # Job Board Integration
    adzuna_company_id = models.CharField(max_length=100, blank=True)
    
    # Research Data (Epic 6)
    last_research_update = models.DateTimeField(null=True, blank=True)
    research_data = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'companies'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
            models.Index(fields=['industry']),
            models.Index(fields=['company_size']),
        ]

    def __str__(self):
        return self.name

    def update_research_timestamp(self):
        """Update the last research timestamp."""
        self.last_research_update = timezone.now()
        self.save(update_fields=['last_research_update'])


class UserPreference(BaseModel):
    """
    User preferences for personalization across all epics.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='preferences'
    )
    
    # Job Search Preferences (Epic 1)
    job_alert_frequency = models.CharField(
        max_length=20,
        choices=[
            ('never', 'Never'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='weekly'
    )
    max_commute_distance = models.PositiveIntegerField(
        default=25,
        help_text="Maximum commute distance in miles"
    )
    
    # Resume Preferences (Epic 2)
    auto_save_resume = models.BooleanField(default=True)
    resume_privacy_level = models.CharField(
        max_length=20,
        choices=[
            ('private', 'Private'),
            ('public', 'Public'),
            ('recruiters_only', 'Recruiters Only'),
        ],
        default='private'
    )
    
    # AI Suggestions Preferences (Epic 3)
    enable_ai_suggestions = models.BooleanField(default=True)
    ai_suggestion_frequency = models.CharField(
        max_length=20,
        choices=[
            ('real_time', 'Real-time'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
        ],
        default='daily'
    )
    
    # Notification Preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Privacy Settings
    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ('private', 'Private'),
            ('public', 'Public'),
            ('connections_only', 'Connections Only'),
        ],
        default='private'
    )
    
    # Theme and UI Preferences
    theme = models.CharField(
        max_length=10,
        choices=[
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('auto', 'Auto'),
        ],
        default='auto'
    )
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')

    class Meta:
        db_table = 'user_preferences'

    def __str__(self):
        return f"Preferences for {self.user.display_name}"


class ActivityLog(BaseModel):
    """
    Activity log for tracking user actions across all epics.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activity_logs'
    )
    
    action = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Context information
    epic = models.CharField(
        max_length=20,
        choices=[
            ('core', 'Core'),
            ('jobs', 'Job Search'),
            ('resumes', 'Resume Management'),
            ('ai_suggestions', 'AI Suggestions'),
            ('skills', 'Skills Analysis'),
            ('certifications', 'Certifications'),
            ('company_research', 'Company Research'),
        ]
    )
    
    # Technical details
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Additional context data
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'activity_logs'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action']),
            models.Index(fields=['epic']),
        ]

    def __str__(self):
        return f"{self.user.display_name} - {self.action} ({self.created_at})"
