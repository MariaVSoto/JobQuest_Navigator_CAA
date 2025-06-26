"""
AI Suggestions app models for Epic 3: AI-Powered Resume Optimization and Smart Recommendations.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()

# Suggestion types
SUGGESTION_TYPES = [
    ('resume_improvement', 'Resume Improvement'),
    ('job_match', 'Job Match Recommendation'),
    ('keyword_optimization', 'Keyword Optimization'),
    ('format_suggestion', 'Format Suggestion'),
    ('content_enhancement', 'Content Enhancement'),
    ('skill_highlight', 'Skill Highlighting'),
    ('experience_optimization', 'Experience Optimization'),
]

# Suggestion statuses
SUGGESTION_STATUSES = [
    ('pending', 'Pending Review'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
    ('partially_accepted', 'Partially Accepted'),
    ('expired', 'Expired'),
]

# Feedback types
FEEDBACK_TYPES = [
    ('helpful', 'Helpful'),
    ('not_helpful', 'Not Helpful'),
    ('irrelevant', 'Irrelevant'),
    ('excellent', 'Excellent'),
    ('needs_improvement', 'Needs Improvement'),
]

# AI models
AI_MODELS = [
    ('gpt-4', 'GPT-4'),
    ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
    ('custom-model', 'Custom Model'),
]


class SuggestionTemplate(models.Model):
    """Templates for different types of AI suggestions."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    suggestion_type = models.CharField(max_length=50, choices=SUGGESTION_TYPES)
    prompt_template = models.TextField(help_text="Template for AI prompt with placeholders")
    context_fields = models.JSONField(default=list, help_text="Required context fields for this template")
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    success_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_suggestion_templates'
        ordering = ['-usage_count', 'name']
        indexes = [
            models.Index(fields=['suggestion_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_suggestion_type_display()})"


class AISuggestion(models.Model):
    """AI-generated suggestions for resumes and job applications."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_suggestions')
    
    # Suggestion details
    suggestion_type = models.CharField(max_length=50, choices=SUGGESTION_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    suggestion_content = models.JSONField(help_text="Structured suggestion data")
    
    # AI metadata
    ai_model = models.CharField(max_length=50, choices=AI_MODELS, default='gpt-3.5-turbo')
    template = models.ForeignKey(
        SuggestionTemplate, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='generated_suggestions'
    )
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="AI confidence in this suggestion (0-1)"
    )
    processing_time = models.FloatField(null=True, blank=True, help_text="Time taken to generate (seconds)")
    
    # Context information
    context_data = models.JSONField(default=dict, help_text="Context used to generate suggestion")
    target_job_id = models.UUIDField(null=True, blank=True, help_text="Related job posting ID")
    target_resume_id = models.UUIDField(null=True, blank=True, help_text="Related resume ID")
    
    # Status and lifecycle
    status = models.CharField(max_length=20, choices=SUGGESTION_STATUSES, default='pending')
    priority = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium'
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # User interaction
    viewed_at = models.DateTimeField(null=True, blank=True)
    acted_on_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_suggestions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['suggestion_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['target_job_id']),
            models.Index(fields=['target_resume_id']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_viewed(self):
        """Mark suggestion as viewed."""
        if not self.viewed_at:
            self.viewed_at = timezone.now()
            self.save(update_fields=['viewed_at'])
    
    def mark_acted_on(self):
        """Mark suggestion as acted upon."""
        if not self.acted_on_at:
            self.acted_on_at = timezone.now()
            self.save(update_fields=['acted_on_at'])
    
    def is_expired(self):
        """Check if suggestion has expired."""
        return self.expires_at and timezone.now() > self.expires_at


class SuggestionFeedback(models.Model):
    """User feedback on AI suggestions."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    suggestion = models.ForeignKey(
        AISuggestion, 
        on_delete=models.CASCADE, 
        related_name='feedback'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Feedback details
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1-5 stars"
    )
    comments = models.TextField(blank=True)
    
    # Specific feedback categories
    accuracy_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    relevance_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    usefulness_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    
    # Implementation details
    implemented = models.BooleanField(default=False)
    implementation_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_suggestion_feedback'
        unique_together = ['suggestion', 'user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['feedback_type']),
            models.Index(fields=['rating']),
            models.Index(fields=['implemented']),
        ]
    
    def __str__(self):
        return f"Feedback for {self.suggestion.title} - {self.get_feedback_type_display()}"


class JobRecommendation(models.Model):
    """AI-generated job recommendations for users."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_recommendations')
    
    # Job details
    job_id = models.UUIDField(help_text="Related job posting ID")
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    
    # Recommendation metadata
    match_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="How well the job matches the user (0-1)"
    )
    recommendation_reason = models.TextField(help_text="Why this job was recommended")
    matching_skills = models.JSONField(default=list, help_text="Skills that match")
    missing_skills = models.JSONField(default=list, help_text="Skills user needs to develop")
    
    # AI metadata
    ai_model = models.CharField(max_length=50, choices=AI_MODELS, default='gpt-3.5-turbo')
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    # User interaction
    viewed = models.BooleanField(default=False)
    saved = models.BooleanField(default=False)
    applied = models.BooleanField(default=False)
    dismissed = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    viewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ai_job_recommendations'
        ordering = ['-match_score', '-created_at']
        unique_together = ['user', 'job_id']
        indexes = [
            models.Index(fields=['user', 'viewed']),
            models.Index(fields=['match_score']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.job_title} at {self.company_name} - {self.user.username}"
    
    def mark_viewed(self):
        """Mark recommendation as viewed."""
        if not self.viewed:
            self.viewed = True
            self.viewed_at = timezone.now()
            self.save(update_fields=['viewed', 'viewed_at'])


class ResumeJobMatch(models.Model):
    """AI analysis of how well a resume matches a specific job."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume_id = models.UUIDField(help_text="Resume ID being analyzed")
    job_id = models.UUIDField(help_text="Job ID being matched against")
    
    # Match analysis
    overall_match_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    skills_match_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    experience_match_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    keyword_match_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    # Detailed analysis
    matching_keywords = models.JSONField(default=list)
    missing_keywords = models.JSONField(default=list)
    suggested_improvements = models.JSONField(default=list)
    strength_areas = models.JSONField(default=list)
    weakness_areas = models.JSONField(default=list)
    
    # AI metadata
    ai_model = models.CharField(max_length=50, choices=AI_MODELS, default='gpt-3.5-turbo')
    analysis_summary = models.TextField()
    processing_time = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_resume_job_matches'
        unique_together = ['user', 'resume_id', 'job_id']
        ordering = ['-overall_match_score', '-created_at']
        indexes = [
            models.Index(fields=['user', 'resume_id']),
            models.Index(fields=['overall_match_score']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Resume-Job Match ({self.overall_match_score:.2f}) - {self.user.username}"


class AILearningData(models.Model):
    """Data collected to improve AI suggestions over time."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Source data
    data_type = models.CharField(
        max_length=50,
        choices=[
            ('suggestion_feedback', 'Suggestion Feedback'),
            ('user_behavior', 'User Behavior'),
            ('job_match_outcome', 'Job Match Outcome'),
            ('resume_update', 'Resume Update'),
        ]
    )
    
    # Training data
    input_data = models.JSONField(help_text="Input used for AI")
    output_data = models.JSONField(help_text="AI output")
    ground_truth = models.JSONField(null=True, blank=True, help_text="Actual user action/outcome")
    performance_score = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    # Metadata
    user_id = models.UUIDField(null=True, blank=True)
    model_version = models.CharField(max_length=50, default='1.0')
    is_training_data = models.BooleanField(default=False)
    is_validated = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_learning_data'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['data_type']),
            models.Index(fields=['is_training_data']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_data_type_display()} - {self.created_at.date()}"


class SuggestionBatch(models.Model):
    """Batch processing of AI suggestions."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='suggestion_batches')
    
    # Batch details
    batch_type = models.CharField(
        max_length=50,
        choices=[
            ('daily_suggestions', 'Daily Suggestions'),
            ('job_match_analysis', 'Job Match Analysis'),
            ('resume_optimization', 'Resume Optimization'),
            ('skill_recommendations', 'Skill Recommendations'),
        ]
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    
    # Processing metadata
    total_suggestions = models.PositiveIntegerField(default=0)
    successful_suggestions = models.PositiveIntegerField(default=0)
    failed_suggestions = models.PositiveIntegerField(default=0)
    processing_time = models.FloatField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ai_suggestion_batches'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['batch_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_batch_type_display()} - {self.user.username}"