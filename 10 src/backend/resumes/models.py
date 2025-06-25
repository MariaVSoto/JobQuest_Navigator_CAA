import uuid
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class ResumeTemplate(models.Model):
    """Resume templates for different industries and roles"""
    TEMPLATE_CATEGORIES = [
        ('tech', 'Technology'),
        ('business', 'Business'),
        ('creative', 'Creative'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('finance', 'Finance'),
        ('marketing', 'Marketing'),
        ('sales', 'Sales'),
        ('general', 'General'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=TEMPLATE_CATEGORIES)
    description = models.TextField()
    template_data = models.JSONField(help_text="Template structure and styling")
    preview_image = models.ImageField(upload_to='resume_templates/', null=True, blank=True)
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resumes_template'
        ordering = ['-usage_count', 'name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_premium']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Resume(models.Model):
    """Main resume model with versioning support"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=200)
    template = models.ForeignKey(ResumeTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_default = models.BooleanField(default=False)
    
    # Personal Information
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    
    # Professional Summary
    professional_summary = models.TextField(blank=True)
    
    # Resume Data (JSON structure for flexibility)
    resume_data = models.JSONField(default=dict, help_text="Complete resume data structure")
    
    # Metadata
    target_role = models.CharField(max_length=100, blank=True)
    target_industry = models.CharField(max_length=50, blank=True)
    keywords = models.TextField(blank=True, help_text="Comma-separated keywords")
    
    # Tracking
    view_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    last_modified_section = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resumes_resume'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['target_role']),
            models.Index(fields=['target_industry']),
            models.Index(fields=['is_default']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Ensure only one default resume per user
        if self.is_default:
            Resume.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class ResumeVersion(models.Model):
    """Version history for resume changes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    resume_data = models.JSONField()
    change_summary = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'resumes_version'
        ordering = ['-version_number']
        unique_together = ['resume', 'version_number']
        indexes = [
            models.Index(fields=['resume', 'version_number']),
        ]
    
    def __str__(self):
        return f"{self.resume.title} v{self.version_number}"


class ResumeSkillMatch(models.Model):
    """Skills extracted from resume and their relevance to target roles"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skill_matches')
    skill_name = models.CharField(max_length=100)
    skill_category = models.CharField(max_length=50, blank=True)
    
    # Match details
    relevance_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    is_primary_skill = models.BooleanField(default=False)
    years_of_experience = models.PositiveIntegerField(null=True, blank=True)
    proficiency_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('expert', 'Expert'),
        ],
        blank=True
    )
    
    # Context information
    found_in_section = models.CharField(max_length=50, blank=True)
    context_snippet = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'resumes_skill_match'
        unique_together = ['resume', 'skill_name']
        ordering = ['-relevance_score', 'skill_name']
        indexes = [
            models.Index(fields=['resume', 'relevance_score']),
            models.Index(fields=['skill_category']),
        ]
    
    def __str__(self):
        return f"{self.skill_name} - {self.resume.title}"


class ResumeShare(models.Model):
    """Sharing and collaboration for resumes"""
    PERMISSION_LEVELS = [
        ('view', 'View Only'),
        ('comment', 'View & Comment'),
        ('edit', 'View & Edit'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shared_resumes')
    shared_with_email = models.EmailField()
    permission_level = models.CharField(max_length=10, choices=PERMISSION_LEVELS, default='view')
    
    # Sharing settings
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    share_token = models.CharField(max_length=64, unique=True)
    
    # Access tracking
    access_count = models.PositiveIntegerField(default=0)
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'resumes_share'
        unique_together = ['resume', 'shared_with_email']
        indexes = [
            models.Index(fields=['share_token']),
            models.Index(fields=['shared_with_email']),
        ]
    
    def __str__(self):
        return f"{self.resume.title} shared with {self.shared_with_email}"
    
    def save(self, *args, **kwargs):
        if not self.share_token:
            self.share_token = uuid.uuid4().hex
        super().save(*args, **kwargs)


class ResumeComment(models.Model):
    """Comments and feedback on resumes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='comments')
    author_email = models.EmailField()
    author_name = models.CharField(max_length=100, blank=True)
    
    # Comment content
    section = models.CharField(max_length=50, blank=True)
    content = models.TextField()
    is_resolved = models.BooleanField(default=False)
    
    # Threading support
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resumes_comment'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['resume', 'created_at']),
            models.Index(fields=['author_email']),
        ]
    
    def __str__(self):
        return f"Comment on {self.resume.title} by {self.author_email}"


class ResumeExport(models.Model):
    """Resume export history and formats"""
    EXPORT_FORMATS = [
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
        ('html', 'HTML'),
        ('txt', 'Plain Text'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='exports')
    format = models.CharField(max_length=10, choices=EXPORT_FORMATS)
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)  # in bytes
    download_count = models.PositiveIntegerField(default=0)
    
    # Export settings
    include_photo = models.BooleanField(default=True)
    include_references = models.BooleanField(default=True)
    custom_styling = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_downloaded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'resumes_export'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['resume', 'format']),
        ]
    
    def __str__(self):
        return f"{self.resume.title} - {self.get_format_display()}"
