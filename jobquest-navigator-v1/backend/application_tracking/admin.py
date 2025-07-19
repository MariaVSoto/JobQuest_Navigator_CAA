"""
Epic 5: Job Application Tracking - Django Admin Configuration
Comprehensive admin interface for application tracking models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    ApplicationTracker, ApplicationStatusHistory, ApplicationDocument,
    ApplicationNotification, ApplicationInterview, ApplicationMetrics
)


@admin.register(ApplicationTracker)
class ApplicationTrackerAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'job_title', 'company_name', 'status', 'priority', 
        'is_favorite', 'applied_date', 'next_follow_up_date'
    ]
    list_filter = [
        'status', 'priority', 'is_favorite', 'applied_date', 
        'application_source'
    ]
    search_fields = [
        'user__username', 'user__email', 
        'job_application__job__title', 
        'job_application__job__company__name'
    ]
    readonly_fields = [
        'id', 'previous_status', 'status_updated_at', 
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        (None, {
            'fields': ('user', 'job_application', 'resume_version')
        }),
        ('Status & Priority', {
            'fields': ('status', 'previous_status', 'status_updated_at', 'priority', 'is_favorite')
        }),
        ('Application Details', {
            'fields': ('application_source', 'cover_letter_used', 'salary_expectation')
        }),
        ('Timeline', {
            'fields': ('applied_date', 'expected_response_date', 'last_contact_date', 'next_follow_up_date')
        }),
        ('Notes & Contacts', {
            'fields': ('notes', 'contacts')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def job_title(self, obj):
        return obj.job_application.job.title
    job_title.short_description = 'Job Title'
    
    def company_name(self, obj):
        return obj.job_application.job.company.name
    company_name.short_description = 'Company'


@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'application_tracker', 'from_status', 'to_status', 
        'changed_at', 'has_notes'
    ]
    list_filter = ['from_status', 'to_status', 'changed_at']
    search_fields = [
        'application_tracker__user__username',
        'application_tracker__job_application__job__title'
    ]
    readonly_fields = ['changed_at']
    
    def has_notes(self, obj):
        return bool(obj.notes)
    has_notes.boolean = True
    has_notes.short_description = 'Has Notes'


@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'application_tracker', 'document_type', 
        'uploaded_at', 'file_link'
    ]
    list_filter = ['document_type', 'uploaded_at']
    search_fields = [
        'title', 'application_tracker__user__username',
        'application_tracker__job_application__job__title'
    ]
    readonly_fields = ['uploaded_at']
    
    def file_link(self, obj):
        if obj.file_path:
            return format_html(
                '<a href="{}" target="_blank">Download</a>',
                obj.file_path.url
            )
        return "No file"
    file_link.short_description = 'File'


@admin.register(ApplicationNotification)
class ApplicationNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'application_tracker', 'notification_type', 
        'scheduled_for', 'is_sent', 'is_read'
    ]
    list_filter = [
        'notification_type', 'is_sent', 'is_read', 
        'notification_method', 'scheduled_for'
    ]
    search_fields = [
        'title', 'message', 
        'application_tracker__user__username'
    ]
    readonly_fields = ['sent_at', 'read_at', 'created_at']
    
    actions = ['mark_as_sent', 'mark_as_read']
    
    def mark_as_sent(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(is_sent=True, sent_at=timezone.now())
        self.message_user(request, f'{count} notifications marked as sent.')
    mark_as_sent.short_description = 'Mark selected notifications as sent'
    
    def mark_as_read(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'{count} notifications marked as read.')
    mark_as_read.short_description = 'Mark selected notifications as read'


@admin.register(ApplicationInterview)
class ApplicationInterviewAdmin(admin.ModelAdmin):
    list_display = [
        'application_tracker', 'interview_type', 'scheduled_date', 
        'status', 'interviewer_name', 'self_rating'
    ]
    list_filter = [
        'interview_type', 'status', 'scheduled_date', 'self_rating'
    ]
    search_fields = [
        'application_tracker__user__username',
        'application_tracker__job_application__job__title',
        'interviewer_name', 'interviewer_email'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('application_tracker', 'interview_type', 'status')
        }),
        ('Scheduling', {
            'fields': ('scheduled_date', 'duration_minutes', 'location', 'meeting_link')
        }),
        ('Interviewer Details', {
            'fields': ('interviewer_name', 'interviewer_title', 'interviewer_email')
        }),
        ('Preparation & Notes', {
            'fields': ('preparation_notes', 'post_interview_notes')
        }),
        ('Feedback', {
            'fields': ('self_rating', 'feedback_received')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ApplicationMetrics)
class ApplicationMetricsAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'period_start', 'period_end', 'total_applications',
        'response_rate', 'interview_rate', 'offer_rate'
    ]
    list_filter = ['period_start', 'period_end']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'period_start', 'period_end')
        }),
        ('Application Statistics', {
            'fields': ('total_applications', 'applications_by_status')
        }),
        ('Success Rates', {
            'fields': ('response_rate', 'interview_rate', 'offer_rate')
        }),
        ('Time Analytics', {
            'fields': ('avg_time_to_response_days', 'avg_time_to_interview_days')
        }),
        ('Resume Performance', {
            'fields': ('most_successful_resume',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )