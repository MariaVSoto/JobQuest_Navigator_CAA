"""
Epic 5: Job Application Tracking - DRF Serializers
Comprehensive serializers for application tracking system with resume versioning,
status management, notifications, and analytics.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    ApplicationTracker, ApplicationStatusHistory, ApplicationDocument,
    ApplicationNotification, ApplicationInterview, ApplicationMetrics
)
from jobs.models import Job, JobApplication
from resumes.models import Resume, ResumeVersion
from core.models import User

User = get_user_model()


class ApplicationTrackerListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing applications with basic info.
    """
    job_title = serializers.CharField(source='job_application.job.title', read_only=True)
    company_name = serializers.CharField(source='job_application.job.company.name', read_only=True)
    resume_name = serializers.CharField(source='resume_version.resume.name', read_only=True)
    days_since_applied = serializers.SerializerMethodField()
    
    class Meta:
        model = ApplicationTracker
        fields = [
            'id', 'status', 'priority', 'is_favorite', 'applied_date',
            'job_title', 'company_name', 'resume_name', 'days_since_applied'
        ]
    
    def get_days_since_applied(self, obj):
        from django.utils import timezone
        return (timezone.now().date() - obj.applied_date.date()).days


class ApplicationTrackerDetailSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for detailed application view.
    """
    job_application = serializers.PrimaryKeyRelatedField(
        queryset=JobApplication.objects.all()
    )
    resume_version = serializers.PrimaryKeyRelatedField(
        queryset=ResumeVersion.objects.all()
    )
    
    # Read-only nested data
    job_details = serializers.SerializerMethodField()
    resume_details = serializers.SerializerMethodField()
    status_history = serializers.SerializerMethodField()
    upcoming_interviews = serializers.SerializerMethodField()
    unread_notifications = serializers.SerializerMethodField()
    
    class Meta:
        model = ApplicationTracker
        fields = [
            'id', 'user', 'job_application', 'resume_version', 'status', 
            'previous_status', 'status_updated_at', 'priority', 'is_favorite',
            'application_source', 'cover_letter_used', 'salary_expectation',
            'applied_date', 'expected_response_date', 'last_contact_date',
            'next_follow_up_date', 'notes', 'contacts', 'created_at', 'updated_at',
            'job_details', 'resume_details', 'status_history', 
            'upcoming_interviews', 'unread_notifications'
        ]
        read_only_fields = ['user', 'previous_status', 'status_updated_at']
    
    def get_job_details(self, obj):
        job = obj.job_application.job
        return {
            'id': job.id,
            'title': job.title,
            'company': job.company.name,
            'location': f"{job.location.city}, {job.location.state}",
            'job_type': job.job_type,
            'experience_level': job.experience_level,
            'external_url': job.external_url,
        }
    
    def get_resume_details(self, obj):
        resume_version = obj.resume_version
        return {
            'id': resume_version.id,
            'resume_name': resume_version.resume.name,
            'version_number': resume_version.version_number,
            'file_name': resume_version.file_name,
            'created_at': resume_version.created_at,
        }
    
    def get_status_history(self, obj):
        history = obj.status_history.all()[:5]  # Last 5 status changes
        return ApplicationStatusHistorySerializer(history, many=True).data
    
    def get_upcoming_interviews(self, obj):
        from django.utils import timezone
        interviews = obj.interviews.filter(
            scheduled_date__gte=timezone.now(),
            status='scheduled'
        ).order_by('scheduled_date')[:3]
        return ApplicationInterviewSerializer(interviews, many=True).data
    
    def get_unread_notifications(self, obj):
        notifications = obj.notifications.filter(is_read=False)[:5]
        return ApplicationNotificationSerializer(notifications, many=True).data


class ApplicationTrackerCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new application trackers.
    """
    job_application = serializers.PrimaryKeyRelatedField(
        queryset=JobApplication.objects.all()
    )
    resume_version = serializers.PrimaryKeyRelatedField(
        queryset=ResumeVersion.objects.all()
    )
    
    class Meta:
        model = ApplicationTracker
        fields = [
            'job_application', 'resume_version', 'priority', 'application_source',
            'cover_letter_used', 'salary_expectation', 'expected_response_date',
            'notes'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for application status history tracking.
    """
    time_since_change = serializers.SerializerMethodField()
    
    class Meta:
        model = ApplicationStatusHistory
        fields = [
            'id', 'from_status', 'to_status', 'changed_at', 'notes', 'time_since_change'
        ]
        read_only_fields = ['changed_at']
    
    def get_time_since_change(self, obj):
        from django.utils import timezone
        delta = timezone.now() - obj.changed_at
        if delta.days > 0:
            return f"{delta.days} days ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hours ago"
        else:
            minutes = delta.seconds // 60
            return f"{minutes} minutes ago"


class ApplicationDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for application documents.
    """
    file_size = serializers.SerializerMethodField()
    
    class Meta:
        model = ApplicationDocument
        fields = [
            'id', 'application_tracker', 'document_type', 'title', 
            'file_path', 'description', 'uploaded_at', 'file_size'
        ]
        read_only_fields = ['uploaded_at']
    
    def get_file_size(self, obj):
        if obj.file_path:
            return obj.file_path.size
        return None


class ApplicationNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for application notifications and reminders.
    """
    time_until_scheduled = serializers.SerializerMethodField()
    
    class Meta:
        model = ApplicationNotification
        fields = [
            'id', 'application_tracker', 'notification_type', 'title', 'message',
            'scheduled_for', 'sent_at', 'is_sent', 'notification_method',
            'is_read', 'read_at', 'created_at', 'time_until_scheduled'
        ]
        read_only_fields = ['sent_at', 'is_sent', 'created_at']
    
    def get_time_until_scheduled(self, obj):
        from django.utils import timezone
        if obj.scheduled_for > timezone.now():
            delta = obj.scheduled_for - timezone.now()
            if delta.days > 0:
                return f"in {delta.days} days"
            elif delta.seconds > 3600:
                hours = delta.seconds // 3600
                return f"in {hours} hours"
            else:
                minutes = delta.seconds // 60
                return f"in {minutes} minutes"
        return "overdue"


class ApplicationInterviewSerializer(serializers.ModelSerializer):
    """
    Serializer for interview tracking and management.
    """
    time_until_interview = serializers.SerializerMethodField()
    
    class Meta:
        model = ApplicationInterview
        fields = [
            'id', 'application_tracker', 'interview_type', 'scheduled_date',
            'duration_minutes', 'location', 'meeting_link', 'interviewer_name',
            'interviewer_title', 'interviewer_email', 'preparation_notes',
            'post_interview_notes', 'status', 'self_rating', 'feedback_received',
            'created_at', 'updated_at', 'time_until_interview'
        ]
    
    def get_time_until_interview(self, obj):
        from django.utils import timezone
        if obj.scheduled_date > timezone.now():
            delta = obj.scheduled_date - timezone.now()
            if delta.days > 0:
                return f"in {delta.days} days"
            elif delta.seconds > 3600:
                hours = delta.seconds // 3600
                return f"in {hours} hours"
            else:
                minutes = delta.seconds // 60
                return f"in {minutes} minutes"
        return "past"


class ApplicationMetricsSerializer(serializers.ModelSerializer):
    """
    Serializer for application analytics and insights.
    """
    period_duration_days = serializers.SerializerMethodField()
    
    class Meta:
        model = ApplicationMetrics
        fields = [
            'id', 'user', 'period_start', 'period_end', 'total_applications',
            'applications_by_status', 'response_rate', 'interview_rate', 'offer_rate',
            'avg_time_to_response_days', 'avg_time_to_interview_days',
            'most_successful_resume', 'created_at', 'updated_at', 'period_duration_days'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def get_period_duration_days(self, obj):
        return (obj.period_end - obj.period_start).days


class ApplicationDashboardSerializer(serializers.Serializer):
    """
    Serializer for application dashboard summary data.
    """
    total_applications = serializers.IntegerField()
    applications_by_status = serializers.DictField()
    recent_applications = ApplicationTrackerListSerializer(many=True)
    upcoming_interviews = ApplicationInterviewSerializer(many=True)
    pending_follow_ups = ApplicationTrackerListSerializer(many=True)
    unread_notifications_count = serializers.IntegerField()
    response_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    average_time_to_response = serializers.DecimalField(max_digits=5, decimal_places=2)


class BulkStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer for bulk status updates on multiple applications.
    """
    application_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False
    )
    new_status = serializers.ChoiceField(
        choices=ApplicationTracker._meta.get_field('status').choices
    )
    notes = serializers.CharField(required=False, allow_blank=True)