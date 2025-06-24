"""
Epic 5: Job Application Tracking - DRF API Views
Comprehensive API views for application tracking system with resume versioning,
status management, notifications, analytics, and dashboard functionality.
"""

from django.shortcuts import render
from django.db.models import Q, Count, Avg
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction

from .models import (
    ApplicationTracker, ApplicationStatusHistory, ApplicationDocument,
    ApplicationNotification, ApplicationInterview, ApplicationMetrics
)
from .serializers import (
    ApplicationTrackerListSerializer, ApplicationTrackerDetailSerializer,
    ApplicationTrackerCreateSerializer, ApplicationStatusHistorySerializer,
    ApplicationDocumentSerializer, ApplicationNotificationSerializer,
    ApplicationInterviewSerializer, ApplicationMetricsSerializer,
    ApplicationDashboardSerializer, BulkStatusUpdateSerializer
)


class ApplicationTrackerPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ApplicationTrackerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing application tracking with comprehensive filtering,
    status updates, and analytics.
    """
    permission_classes = [IsAuthenticated]
    pagination_class = ApplicationTrackerPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'priority', 'is_favorite']
    
    def get_queryset(self):
        return ApplicationTracker.objects.filter(
            user=self.request.user
        ).select_related(
            'job_application__job__company',
            'resume_version__resume'
        ).prefetch_related(
            'status_history',
            'interviews',
            'notifications'
        ).order_by('-applied_date')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ApplicationTrackerListSerializer
        elif self.action == 'create':
            return ApplicationTrackerCreateSerializer
        return ApplicationTrackerDetailSerializer
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Get dashboard summary with key metrics and recent activity.
        """
        user_applications = self.get_queryset()
        
        # Basic statistics
        total_applications = user_applications.count()
        applications_by_status = dict(
            user_applications.values('status').annotate(
                count=Count('id')
            ).values_list('status', 'count')
        )
        
        # Recent applications (last 10)
        recent_applications = user_applications[:10]
        
        # Upcoming interviews (next 5)
        upcoming_interviews = ApplicationInterview.objects.filter(
            application_tracker__user=request.user,
            scheduled_date__gte=timezone.now(),
            status='scheduled'
        ).order_by('scheduled_date')[:5]
        
        # Pending follow-ups (applications needing follow-up in next 7 days)
        next_week = timezone.now().date() + timezone.timedelta(days=7)
        pending_follow_ups = user_applications.filter(
            next_follow_up_date__lte=next_week,
            status__in=['applied', 'screening', 'interview']
        )[:5]
        
        # Unread notifications count
        unread_notifications_count = ApplicationNotification.objects.filter(
            application_tracker__user=request.user,
            is_read=False
        ).count()
        
        # Response rate calculation
        total_with_responses = user_applications.exclude(
            status__in=['applied', 'withdrawn']
        ).count()
        response_rate = (total_with_responses / total_applications * 100) if total_applications > 0 else 0
        
        # Average time to response
        responded_applications = user_applications.exclude(
            status='applied',
            status_updated_at__isnull=True
        )
        avg_response_time = 0
        if responded_applications.exists():
            total_response_time = sum(
                (app.status_updated_at.date() - app.applied_date.date()).days
                for app in responded_applications
                if app.status_updated_at
            )
            avg_response_time = total_response_time / responded_applications.count()
        
        dashboard_data = {
            'total_applications': total_applications,
            'applications_by_status': applications_by_status,
            'recent_applications': ApplicationTrackerListSerializer(recent_applications, many=True).data,
            'upcoming_interviews': ApplicationInterviewSerializer(upcoming_interviews, many=True).data,
            'pending_follow_ups': ApplicationTrackerListSerializer(pending_follow_ups, many=True).data,
            'unread_notifications_count': unread_notifications_count,
            'response_rate': round(response_rate, 2),
            'average_time_to_response': round(avg_response_time, 1)
        }
        
        serializer = ApplicationDashboardSerializer(dashboard_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update application status with automatic history tracking.
        """
        application = self.get_object()
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if not new_status:
            return Response(
                {'error': 'Status is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = application.status
        
        with transaction.atomic():
            # Update application status
            application.status = new_status
            application.save()
            
            # Create status history entry
            ApplicationStatusHistory.objects.create(
                application_tracker=application,
                from_status=old_status,
                to_status=new_status,
                notes=notes
            )
            
            # Create notification for significant status changes
            if new_status in ['interview', 'offer_received', 'rejected']:
                ApplicationNotification.objects.create(
                    application_tracker=application,
                    notification_type='status_update',
                    title=f'Application Status Updated',
                    message=f'Your application for {application.job_application.job.title} has been updated to {new_status}',
                    scheduled_for=timezone.now(),
                    notification_method='in_app'
                )
        
        return Response(
            ApplicationTrackerDetailSerializer(application).data
        )
    
    @action(detail=False, methods=['post'])
    def bulk_status_update(self, request):
        """
        Update status for multiple applications at once.
        """
        serializer = BulkStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            application_ids = serializer.validated_data['application_ids']
            new_status = serializer.validated_data['new_status']
            notes = serializer.validated_data.get('notes', '')
            
            applications = ApplicationTracker.objects.filter(
                id__in=application_ids,
                user=request.user
            )
            
            with transaction.atomic():
                for application in applications:
                    old_status = application.status
                    application.status = new_status
                    application.save()
                    
                    # Create status history
                    ApplicationStatusHistory.objects.create(
                        application_tracker=application,
                        from_status=old_status,
                        to_status=new_status,
                        notes=notes
                    )
            
            return Response({
                'message': f'Updated {applications.count()} applications to {new_status}',
                'updated_count': applications.count()
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """
        Get detailed analytics for user applications.
        """
        user_applications = self.get_queryset()
        
        # Time period (default: last 3 months)
        end_date = timezone.now().date()
        start_date = end_date - timezone.timedelta(days=90)
        
        period_applications = user_applications.filter(
            applied_date__date__gte=start_date,
            applied_date__date__lte=end_date
        )
        
        analytics_data = {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'total_applications': period_applications.count()
            },
            'status_breakdown': dict(
                period_applications.values('status').annotate(
                    count=Count('id')
                ).values_list('status', 'count')
            ),
            'application_sources': dict(
                period_applications.exclude(
                    application_source=''
                ).values('application_source').annotate(
                    count=Count('id')
                ).values_list('application_source', 'count')
            ),
            'priority_distribution': dict(
                period_applications.values('priority').annotate(
                    count=Count('id')
                ).values_list('priority', 'count')
            ),
            'interview_success_rate': self._calculate_interview_rate(period_applications),
            'monthly_application_trend': self._get_monthly_trend(period_applications)
        }
        
        return Response(analytics_data)
    
    def _calculate_interview_rate(self, applications):
        """Calculate percentage of applications that led to interviews."""
        total = applications.count()
        if total == 0:
            return 0
        
        with_interviews = applications.filter(
            status__in=['interview', 'technical_interview', 'behavioral_interview', 
                       'final_interview', 'offer_pending', 'offer_received', 'offer_accepted']
        ).count()
        
        return round((with_interviews / total) * 100, 2)
    
    def _get_monthly_trend(self, applications):
        """Get application count by month for trend analysis."""
        from django.db.models import TruncMonth
        
        monthly_data = applications.annotate(
            month=TruncMonth('applied_date')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        return [
            {
                'month': item['month'].strftime('%Y-%m'),
                'count': item['count']
            }
            for item in monthly_data
        ]


class ApplicationInterviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing interview scheduling and tracking.
    """
    serializer_class = ApplicationInterviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ApplicationInterview.objects.filter(
            application_tracker__user=self.request.user
        ).select_related('application_tracker__job_application__job')
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming interviews."""
        upcoming_interviews = self.get_queryset().filter(
            scheduled_date__gte=timezone.now(),
            status='scheduled'
        ).order_by('scheduled_date')
        
        serializer = self.get_serializer(upcoming_interviews, many=True)
        return Response(serializer.data)


class ApplicationNotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications and reminders.
    """
    serializer_class = ApplicationNotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ApplicationNotification.objects.filter(
            application_tracker__user=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read."""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        return Response({'status': 'marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        unread_notifications = self.get_queryset().filter(is_read=False)
        count = unread_notifications.update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            'message': f'Marked {count} notifications as read',
            'count': count
        })


class ApplicationDocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing application documents.
    """
    serializer_class = ApplicationDocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ApplicationDocument.objects.filter(
            application_tracker__user=self.request.user
        )


class ApplicationStatusHistoryListView(generics.ListAPIView):
    """
    List view for application status history.
    """
    serializer_class = ApplicationStatusHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        application_id = self.kwargs.get('application_id')
        return ApplicationStatusHistory.objects.filter(
            application_tracker_id=application_id,
            application_tracker__user=self.request.user
        ).order_by('-changed_at')


class ApplicationMetricsListView(generics.ListCreateAPIView):
    """
    List and create view for application metrics.
    """
    serializer_class = ApplicationMetricsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ApplicationMetrics.objects.filter(
            user=self.request.user
        ).order_by('-period_end')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)