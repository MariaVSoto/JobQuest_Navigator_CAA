"""
Jobs app models for Epic 1: Job Search & Geolocation Mapping.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from core.models import Company, Location

User = get_user_model()

# Job choices
JOB_TYPES = [
    ('full_time', 'Full Time'),
    ('part_time', 'Part Time'),
    ('contract', 'Contract'),
    ('freelance', 'Freelance'),
    ('internship', 'Internship'),
]

EXPERIENCE_LEVELS = [
    ('entry', 'Entry Level'),
    ('junior', 'Junior'),
    ('mid', 'Mid Level'),
    ('senior', 'Senior'),
    ('lead', 'Lead'),
    ('manager', 'Manager'),
]

CONTRACT_TYPES = [
    ('permanent', 'Permanent'),
    ('contract', 'Contract'),
    ('temporary', 'Temporary'),
    ('apprenticeship', 'Apprenticeship'),
    ('volunteer', 'Volunteer'),
]

REMOTE_TYPES = [
    ('on_site', 'On-site'),
    ('remote', 'Remote'),
    ('hybrid', 'Hybrid'),
]

SALARY_PERIODS = [
    ('hourly', 'Hourly'),
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
    ('yearly', 'Yearly'),
]

APPLICATION_STATUSES = [
    ('applied', 'Applied'),
    ('screening', 'Screening'),
    ('interview', 'Interview'),
    ('offer', 'Offer'),
    ('rejected', 'Rejected'),
    ('withdrawn', 'Withdrawn'),
]

SKILL_CATEGORIES = [
    ('programming', 'Programming'),
    ('framework', 'Framework'),
    ('database', 'Database'),
    ('cloud', 'Cloud'),
    ('devops', 'DevOps'),
    ('design', 'Design'),
    ('management', 'Management'),
    ('communication', 'Communication'),
    ('language', 'Language'),
    ('other', 'Other'),
]

PROFICIENCY_LEVELS = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
    ('expert', 'Expert'),
]


class Category(models.Model):
    """Job category model for classification."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100, unique=True)
    adzuna_tag = models.CharField(max_length=100, unique=True, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['adzuna_tag']),
        ]
    
    def __str__(self):
        return self.name


class Skill(models.Model):
    """Skill model for job requirements and user skills."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=50, choices=SKILL_CATEGORIES)
    description = models.TextField(blank=True)
    
    # Skill metadata
    is_technical = models.BooleanField(default=True)
    popularity_score = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['is_technical']),
        ]
    
    def __str__(self):
        return self.name


class Job(models.Model):
    """Job model for job listings."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    external_id = models.CharField(max_length=100, blank=True)  # From external APIs
    title = models.CharField(max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    description = models.TextField()
    requirements = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    
    # Salary information
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    salary_period = models.CharField(max_length=20, choices=SALARY_PERIODS, default='yearly')
    
    # Job details
    job_type = models.CharField(max_length=50, choices=JOB_TYPES, default='full_time')
    contract_type = models.CharField(max_length=50, choices=CONTRACT_TYPES, default='permanent')
    experience_level = models.CharField(max_length=50, choices=EXPERIENCE_LEVELS)
    remote_type = models.CharField(max_length=50, choices=REMOTE_TYPES, default='on_site')
    
    # External source information
    source = models.CharField(max_length=50, default='adzuna')  # adzuna, linkedin, etc.
    external_url = models.URLField(blank=True)
    
    # Status and dates
    is_active = models.BooleanField(default=True)
    posted_date = models.DateTimeField()
    expires_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['company']),
            models.Index(fields=['location']),
            models.Index(fields=['job_type']),
            models.Index(fields=['experience_level']),
            models.Index(fields=['posted_date']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"


class JobSkill(models.Model):
    """Skills required for jobs."""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='required_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    is_required = models.BooleanField(default=True)  # vs nice-to-have
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS, blank=True)
    
    class Meta:
        unique_together = ['job', 'skill']
    
    def __str__(self):
        return f"{self.job.title} - {self.skill.name}"


class JobApplication(models.Model):
    """User job applications."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    
    status = models.CharField(max_length=50, choices=APPLICATION_STATUSES, default='applied')
    applied_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Application tracking
    cover_letter = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['user', 'job']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['applied_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.job.title}"


class SavedJob(models.Model):
    """User saved jobs."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    saved_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['user', 'job']
        indexes = [
            models.Index(fields=['user', 'saved_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"


class JobAlert(models.Model):
    """User job alerts."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_alerts')
    name = models.CharField(max_length=200)
    
    # Search criteria
    keywords = models.CharField(max_length=500, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    radius = models.PositiveIntegerField(default=25)  # km
    job_type = models.CharField(max_length=50, choices=JOB_TYPES, blank=True)
    experience_level = models.CharField(max_length=50, choices=EXPERIENCE_LEVELS, blank=True)
    remote_type = models.CharField(max_length=50, choices=REMOTE_TYPES, blank=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Alert settings
    is_active = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    frequency = models.CharField(max_length=20, choices=[
        ('immediate', 'Immediate'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ], default='daily')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sent = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class UserSkill(models.Model):
    """User's skills and proficiency."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS)
    years_experience = models.PositiveIntegerField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'skill']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['proficiency_level']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.skill.name} ({self.proficiency_level})"
