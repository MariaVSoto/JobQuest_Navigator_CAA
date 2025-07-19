"""
Epic 5: Job Application Tracking with Resume Used
Advanced application tracking system that links applications to specific resume versions,
provides comprehensive status management, and supports notification workflows.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from jobs.models import Job, JobApplication
from resumes.models import Resume, ResumeVersion

User = get_user_model()

# Extended application status choices
APPLICATION_STATUS_CHOICES = [
    ('applied', 'Applied'),
    ('screening', 'Application Screening'),
    ('phone_screening', 'Phone Screening'),
    ('technical_interview', 'Technical Interview'),
    ('behavioral_interview', 'Behavioral Interview'),
    ('final_interview', 'Final Interview'),
    ('reference_check', 'Reference Check'),
    ('offer_pending', 'Offer Pending'),
    ('offer_received', 'Offer Received'),
    ('offer_accepted', 'Offer Accepted'),
    ('offer_declined', 'Offer Declined'),
    ('rejected', 'Rejected'),
    ('withdrawn', 'Withdrawn'),
    ('on_hold', 'On Hold'),
]

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('urgent', 'Urgent'),
]

NOTIFICATION_TYPE_CHOICES = [
    ('status_update', 'Status Update'),
    ('interview_reminder', 'Interview Reminder'),
    ('follow_up_reminder', 'Follow-up Reminder'),
    ('deadline_reminder', 'Deadline Reminder'),
    ('custom', 'Custom'),
]

NOTIFICATION_METHOD_CHOICES = [
    ('email', 'Email'),
    ('in_app', 'In-App Notification'),
    ('both', 'Both Email and In-App'),
]


class ApplicationTracker(models.Model):
    """
    Enhanced job application tracking that extends the basic JobApplication model
    with resume versioning, detailed status tracking, and notification management.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tracked_applications')
    job_application = models.OneToOneField(
        JobApplication, 
        on_delete=models.CASCADE, 
        related_name='tracking_details'
    )
    
    # Resume version tracking
    resume_version = models.ForeignKey(
        ResumeVersion, 
        on_delete=models.PROTECT, 
        related_name='applications',
        help_text="The specific resume version used for this application"
    )
    
    # Enhanced status tracking
    status = models.CharField(max_length=50, choices=APPLICATION_STATUS_CHOICES, default='applied')
    previous_status = models.CharField(max_length=50, choices=APPLICATION_STATUS_CHOICES, blank=True)
    status_updated_at = models.DateTimeField(auto_now=True)
    
    # Priority and organization
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    is_favorite = models.BooleanField(default=False)
    
    # Application details
    application_source = models.CharField(max_length=100, blank=True, help_text="Where did you apply? (company website, LinkedIn, etc.)")
    cover_letter_used = models.TextField(blank=True)
    salary_expectation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Timeline tracking
    applied_date = models.DateTimeField(default=timezone.now)
    expected_response_date = models.DateField(null=True, blank=True)
    last_contact_date = models.DateField(null=True, blank=True)
    next_follow_up_date = models.DateField(null=True, blank=True)
    
    # Additional notes and tracking
    notes = models.TextField(blank=True, help_text="Personal notes about this application")
    contacts = models.TextField(blank=True, help_text="Contact person details (JSON format)")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'priority']),
            models.Index(fields=['applied_date']),
            models.Index(fields=['next_follow_up_date']),
            models.Index(fields=['is_favorite']),
        ]
        ordering = ['-applied_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.job_application.job.title} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Track status changes
        if self.pk:
            old_instance = ApplicationTracker.objects.get(pk=self.pk)
            if old_instance.status != self.status:
                self.previous_status = old_instance.status
                self.status_updated_at = timezone.now()
        super().save(*args, **kwargs)


class ApplicationStatusHistory(models.Model):
    """
    Track the complete history of status changes for each application.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    application_tracker = models.ForeignKey(
        ApplicationTracker, 
        on_delete=models.CASCADE, 
        related_name='status_history'
    )
    
    from_status = models.CharField(max_length=50, choices=APPLICATION_STATUS_CHOICES, blank=True)
    to_status = models.CharField(max_length=50, choices=APPLICATION_STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Notes about this status change")
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = 'Application status histories'
    
    def __str__(self):
        return f"{self.application_tracker} - {self.from_status} → {self.to_status}"


class ApplicationDocument(models.Model):
    """
    Track additional documents associated with applications
    (cover letters, portfolios, certifications, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    application_tracker = models.ForeignKey(
        ApplicationTracker, 
        on_delete=models.CASCADE, 
        related_name='documents'
    )
    
    document_type = models.CharField(max_length=50, choices=[
        ('cover_letter', 'Cover Letter'),
        ('portfolio', 'Portfolio'),
        ('certificate', 'Certificate'),
        ('transcript', 'Transcript'),
        ('reference', 'Reference Letter'),
        ('other', 'Other'),
    ])
    
    title = models.CharField(max_length=200)
    file_path = models.FileField(upload_to='application_documents/')
    description = models.TextField(blank=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['application_tracker', 'document_type']),
        ]
    
    def __str__(self):
        return f"{self.application_tracker} - {self.title}"


class ApplicationNotification(models.Model):
    """
    Manage notifications and reminders for application tracking.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    application_tracker = models.ForeignKey(
        ApplicationTracker, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Scheduling
    scheduled_for = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    
    # Delivery method
    notification_method = models.CharField(max_length=20, choices=NOTIFICATION_METHOD_CHOICES, default='in_app')
    
    # User interaction
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['application_tracker', 'is_sent']),
            models.Index(fields=['scheduled_for']),
            models.Index(fields=['is_read']),
        ]
        ordering = ['-scheduled_for']
    
    def __str__(self):
        return f"{self.title} - {self.application_tracker}"


class ApplicationInterview(models.Model):
    """
    Track interview details and scheduling for applications.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    application_tracker = models.ForeignKey(
        ApplicationTracker, 
        on_delete=models.CASCADE, 
        related_name='interviews'
    )
    
    interview_type = models.CharField(max_length=50, choices=[
        ('phone', 'Phone Interview'),
        ('video', 'Video Interview'),
        ('in_person', 'In-Person Interview'),
        ('technical', 'Technical Interview'),
        ('behavioral', 'Behavioral Interview'),
        ('panel', 'Panel Interview'),
        ('group', 'Group Interview'),
        ('final', 'Final Interview'),
    ])
    
    scheduled_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    location = models.CharField(max_length=500, blank=True)
    meeting_link = models.URLField(blank=True)
    
    # Interview contacts
    interviewer_name = models.CharField(max_length=200, blank=True)
    interviewer_title = models.CharField(max_length=200, blank=True)
    interviewer_email = models.EmailField(blank=True)
    
    # Preparation and notes
    preparation_notes = models.TextField(blank=True)
    post_interview_notes = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
        ('no_show', 'No Show'),
    ], default='scheduled')
    
    # Feedback
    self_rating = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text="Rate your performance 1-10"
    )
    feedback_received = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['application_tracker', 'status']),
            models.Index(fields=['scheduled_date']),
        ]
        ordering = ['scheduled_date']
    
    def __str__(self):
        return f"{self.application_tracker} - {self.interview_type} on {self.scheduled_date.date()}"


class ApplicationMetrics(models.Model):
    """
    Track application metrics and analytics for user insights.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='application_metrics')
    
    # Time period
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Application statistics
    total_applications = models.PositiveIntegerField(default=0)
    applications_by_status = models.JSONField(default=dict)
    
    # Response rates
    response_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    interview_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    offer_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Time to response analytics
    avg_time_to_response_days = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    avg_time_to_interview_days = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Resume version performance
    most_successful_resume = models.ForeignKey(
        ResumeVersion, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='performance_metrics'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'period_start', 'period_end']),
        ]
        unique_together = ['user', 'period_start', 'period_end']
    
    def __str__(self):
        return f"{self.user.username} metrics - {self.period_start} to {self.period_end}"