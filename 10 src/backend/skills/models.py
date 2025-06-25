"""
Skills app models for Epic 4: Skills Analysis and Certification Roadmaps.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()

# Skill categories
SKILL_CATEGORIES = [
    ('technical', 'Technical Skills'),
    ('soft', 'Soft Skills'),
    ('language', 'Language Skills'),
    ('management', 'Management Skills'),
    ('design', 'Design Skills'),
    ('data', 'Data Skills'),
    ('marketing', 'Marketing Skills'),
    ('finance', 'Finance Skills'),
    ('healthcare', 'Healthcare Skills'),
    ('education', 'Education Skills'),
    ('other', 'Other'),
]

# Proficiency levels
PROFICIENCY_LEVELS = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
    ('expert', 'Expert'),
]

# Certification statuses
CERTIFICATION_STATUSES = [
    ('active', 'Active'),
    ('expired', 'Expired'),
    ('in_progress', 'In Progress'),
    ('planned', 'Planned'),
]

# Learning path statuses
LEARNING_PATH_STATUSES = [
    ('not_started', 'Not Started'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('paused', 'Paused'),
]

# Skill demand levels
DEMAND_LEVELS = [
    ('very_low', 'Very Low'),
    ('low', 'Low'),
    ('moderate', 'Moderate'),
    ('high', 'High'),
    ('very_high', 'Very High'),
]


class SkillCategory(models.Model):
    """Skill categories for organizing skills."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class or code")
    color = models.CharField(max_length=7, default="#007bff", help_text="Hex color code")
    parent_category = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'skill_categories'
        ordering = ['name']
        verbose_name_plural = 'Skill Categories'
    
    def __str__(self):
        return self.name


class Skill(models.Model):
    """Individual skills that can be associated with users and jobs."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name='skills')
    description = models.TextField(blank=True)
    aliases = models.JSONField(
        default=list, 
        help_text="Alternative names or spellings for this skill"
    )
    
    # Market data
    market_demand = models.CharField(
        max_length=20, 
        choices=DEMAND_LEVELS, 
        default='moderate'
    )
    average_salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Average salary associated with this skill"
    )
    growth_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(-100.0), MaxValueValidator(100.0)],
        help_text="Annual growth rate percentage"
    )
    
    # Learning resources
    learning_time_hours = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Estimated hours to achieve proficiency"
    )
    difficulty_level = models.CharField(
        max_length=20,
        choices=PROFICIENCY_LEVELS,
        default='intermediate'
    )
    prerequisites = models.ManyToManyField(
        'self', 
        blank=True, 
        symmetrical=False,
        related_name='dependent_skills'
    )
    
    # Metadata
    is_trending = models.BooleanField(default=False)
    is_technical = models.BooleanField(default=True)
    popularity_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Popularity score from 0-100"
    )
    usage_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'skills'
        ordering = ['-popularity_score', 'name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['market_demand']),
            models.Index(fields=['is_trending']),
            models.Index(fields=['popularity_score']),
        ]
    
    def __str__(self):
        return self.name
    
    def increment_usage(self):
        """Increment usage count for popularity tracking."""
        self.usage_count = models.F('usage_count') + 1
        self.save(update_fields=['usage_count'])


class UserSkill(models.Model):
    """Skills associated with a user and their proficiency level."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='user_skills')
    
    # Proficiency data
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS)
    years_experience = models.PositiveIntegerField(default=0)
    self_assessed_level = models.CharField(
        max_length=20, 
        choices=PROFICIENCY_LEVELS,
        help_text="User's self-assessment"
    )
    
    # Verification and evidence
    is_verified = models.BooleanField(default=False)
    verification_source = models.CharField(max_length=200, blank=True)
    evidence_url = models.URLField(blank=True, help_text="Link to portfolio, certification, etc.")
    
    # Learning progress
    learning_progress = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Learning progress percentage"
    )
    target_proficiency = models.CharField(
        max_length=20,
        choices=PROFICIENCY_LEVELS,
        blank=True,
        help_text="Target proficiency level"
    )
    
    # Usage tracking
    last_used = models.DateField(null=True, blank=True)
    frequency_of_use = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('occasionally', 'Occasionally'),
            ('rarely', 'Rarely'),
        ],
        default='occasionally'
    )
    
    # Metadata
    source = models.CharField(
        max_length=50,
        choices=[
            ('manual', 'Manually Added'),
            ('resume_extracted', 'Extracted from Resume'),
            ('linkedin_imported', 'Imported from LinkedIn'),
            ('assessment', 'From Skill Assessment'),
            ('ai_suggested', 'AI Suggested'),
        ],
        default='manual'
    )
    confidence_score = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Confidence in skill accuracy (0-1)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_skills'
        unique_together = ['user', 'skill']
        ordering = ['-proficiency_level', '-years_experience', 'skill__name']
        indexes = [
            models.Index(fields=['user', 'proficiency_level']),
            models.Index(fields=['skill', 'proficiency_level']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['last_used']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.skill.name} ({self.proficiency_level})"


class Certification(models.Model):
    """Professional certifications and their details."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Certification details
    skill_categories = models.ManyToManyField(SkillCategory, related_name='certifications')
    related_skills = models.ManyToManyField(Skill, blank=True, related_name='certifications')
    difficulty_level = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS)
    
    # Requirements
    prerequisites = models.JSONField(
        default=list,
        help_text="List of prerequisites for this certification"
    )
    exam_format = models.CharField(max_length=100, blank=True)
    exam_duration_hours = models.PositiveIntegerField(null=True, blank=True)
    
    # Validity
    is_lifetime = models.BooleanField(default=False)
    validity_years = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Years before certification expires"
    )
    
    # Costs and preparation
    cost_usd = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    preparation_time_hours = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Recommended preparation time"
    )
    pass_rate = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Pass rate percentage"
    )
    
    # Market value
    salary_boost_percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Average salary increase percentage"
    )
    market_demand = models.CharField(max_length=20, choices=DEMAND_LEVELS, default='moderate')
    
    # External links
    official_url = models.URLField(blank=True)
    study_guide_url = models.URLField(blank=True)
    practice_exam_url = models.URLField(blank=True)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    popularity_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'certifications'
        ordering = ['-popularity_score', 'name']
        indexes = [
            models.Index(fields=['issuing_organization']),
            models.Index(fields=['difficulty_level']),
            models.Index(fields=['market_demand']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.issuing_organization})"


class UserCertification(models.Model):
    """Certifications earned or pursued by users."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certifications')
    certification = models.ForeignKey(Certification, on_delete=models.CASCADE)
    
    # Status and dates
    status = models.CharField(max_length=20, choices=CERTIFICATION_STATUSES)
    earned_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    # Verification
    credential_id = models.CharField(max_length=100, blank=True)
    credential_url = models.URLField(blank=True)
    verification_url = models.URLField(blank=True)
    is_verified = models.BooleanField(default=False)
    
    # Progress tracking (for in-progress certifications)
    study_progress = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Study progress percentage"
    )
    target_completion_date = models.DateField(null=True, blank=True)
    
    # Performance data
    exam_score = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    attempt_number = models.PositiveIntegerField(default=1)
    
    # Investment tracking
    cost_paid = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    study_hours = models.PositiveIntegerField(default=0)
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_certifications'
        unique_together = ['user', 'certification']
        ordering = ['-earned_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'expiry_date']),
            models.Index(fields=['earned_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.certification.name} ({self.status})"
    
    def is_expired(self):
        """Check if certification has expired."""
        if self.expiry_date and self.status == 'active':
            return timezone.now().date() > self.expiry_date
        return False


class LearningPath(models.Model):
    """Structured learning paths for skill development."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    target_role = models.CharField(max_length=100, blank=True)
    
    # Path configuration
    target_skills = models.ManyToManyField(Skill, related_name='learning_paths')
    recommended_certifications = models.ManyToManyField(
        Certification, 
        blank=True,
        related_name='learning_paths'
    )
    difficulty_level = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS)
    
    # Timeline
    estimated_duration_weeks = models.PositiveIntegerField(
        help_text="Estimated completion time in weeks"
    )
    hours_per_week = models.PositiveIntegerField(
        default=10,
        help_text="Recommended study hours per week"
    )
    
    # Prerequisites
    prerequisite_skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='dependent_learning_paths'
    )
    
    # Outcome expectations
    career_outcomes = models.JSONField(
        default=list,
        help_text="Expected career outcomes from completing this path"
    )
    salary_range_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    salary_range_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Content
    learning_resources = models.JSONField(
        default=list,
        help_text="List of learning resources, courses, books, etc."
    )
    milestones = models.JSONField(
        default=list,
        help_text="Key milestones and checkpoints"
    )
    
    # Metadata
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    popularity_score = models.FloatField(default=0.0)
    success_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Percentage of users who complete this path"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_learning_paths'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_paths'
        ordering = ['-popularity_score', 'name']
        indexes = [
            models.Index(fields=['difficulty_level']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['target_role']),
        ]
    
    def __str__(self):
        return self.name


class UserLearningPath(models.Model):
    """User's progress through a learning path."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_paths')
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    
    # Progress tracking
    status = models.CharField(max_length=20, choices=LEARNING_PATH_STATUSES, default='not_started')
    progress_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    current_milestone = models.PositiveIntegerField(default=0)
    
    # Timeline
    started_date = models.DateField(null=True, blank=True)
    target_completion_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    estimated_hours_remaining = models.PositiveIntegerField(default=0)
    
    # Activity tracking
    total_study_hours = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    weekly_hours_goal = models.PositiveIntegerField(default=10)
    
    # Outcomes
    skills_acquired = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='acquired_through_paths'
    )
    certifications_earned = models.ManyToManyField(
        UserCertification,
        blank=True,
        related_name='learning_paths'
    )
    
    # Feedback
    difficulty_rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    satisfaction_rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    feedback_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_learning_paths'
        unique_together = ['user', 'learning_path']
        ordering = ['-started_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'progress_percentage']),
            models.Index(fields=['last_activity_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.learning_path.name} ({self.status})"
    
    def update_progress(self, hours_studied=0):
        """Update learning path progress."""
        if hours_studied > 0:
            self.total_study_hours += hours_studied
            self.last_activity_date = timezone.now().date()
            
            # Calculate progress based on hours studied vs estimated duration
            total_estimated_hours = (
                self.learning_path.estimated_duration_weeks * 
                self.learning_path.hours_per_week
            )
            if total_estimated_hours > 0:
                self.progress_percentage = min(
                    100,
                    int((self.total_study_hours / total_estimated_hours) * 100)
                )
            
            self.save()


class SkillAssessment(models.Model):
    """Skill assessments to measure proficiency."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='assessments')
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Assessment configuration
    assessment_type = models.CharField(
        max_length=50,
        choices=[
            ('multiple_choice', 'Multiple Choice'),
            ('coding_challenge', 'Coding Challenge'),
            ('project_based', 'Project Based'),
            ('peer_review', 'Peer Review'),
            ('self_assessment', 'Self Assessment'),
        ]
    )
    difficulty_level = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS)
    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Scoring
    max_score = models.PositiveIntegerField(default=100)
    passing_score = models.PositiveIntegerField(default=70)
    
    # Content
    questions = models.JSONField(
        default=list,
        help_text="Assessment questions and answers"
    )
    
    # Metadata
    is_active = models.BooleanField(default=True)
    is_certified = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_assessments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'skill_assessments'
        ordering = ['skill__name', 'difficulty_level']
        indexes = [
            models.Index(fields=['skill', 'difficulty_level']),
            models.Index(fields=['assessment_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.skill.name} - {self.name}"


class UserSkillAssessment(models.Model):
    """User's attempts at skill assessments."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skill_assessments')
    assessment = models.ForeignKey(SkillAssessment, on_delete=models.CASCADE)
    
    # Attempt details
    attempt_number = models.PositiveIntegerField(default=1)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Results
    score = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    passed = models.BooleanField(default=False)
    
    # Performance data
    time_taken_minutes = models.PositiveIntegerField(null=True, blank=True)
    answers = models.JSONField(
        default=dict,
        help_text="User's answers to assessment questions"
    )
    detailed_results = models.JSONField(
        default=dict,
        help_text="Detailed breakdown of performance"
    )
    
    # Recommendations
    recommended_proficiency = models.CharField(
        max_length=20,
        choices=PROFICIENCY_LEVELS,
        blank=True
    )
    improvement_areas = models.JSONField(
        default=list,
        help_text="Areas identified for improvement"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_skill_assessments'
        ordering = ['-completed_at', '-started_at']
        indexes = [
            models.Index(fields=['user', 'assessment']),
            models.Index(fields=['passed', 'score']),
            models.Index(fields=['completed_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.assessment.name} (Attempt {self.attempt_number})"
    
    def calculate_percentage(self):
        """Calculate score percentage."""
        if self.assessment.max_score > 0:
            self.percentage = (self.score / self.assessment.max_score) * 100
            self.passed = self.percentage >= self.assessment.passing_score
        else:
            self.percentage = 0.0
            self.passed = False