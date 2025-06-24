"""
Epic 5: Job Application Tracking - URL Configuration
URL patterns for comprehensive application tracking API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'applications', views.ApplicationTrackerViewSet, basename='applicationtracker')
router.register(r'interviews', views.ApplicationInterviewViewSet, basename='applicationinterview')
router.register(r'notifications', views.ApplicationNotificationViewSet, basename='applicationnotification')
router.register(r'documents', views.ApplicationDocumentViewSet, basename='applicationdocument')

app_name = 'application_tracking'

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Additional custom endpoints
    path('applications/<uuid:application_id>/history/', 
         views.ApplicationStatusHistoryListView.as_view(), 
         name='application-status-history'),
    
    path('metrics/', 
         views.ApplicationMetricsListView.as_view(), 
         name='application-metrics'),
    
    # API endpoints for specific functionalities
    # Dashboard: GET /api/application-tracking/applications/dashboard/
    # Analytics: GET /api/application-tracking/applications/analytics/
    # Status Update: POST /api/application-tracking/applications/{id}/update_status/
    # Bulk Update: POST /api/application-tracking/applications/bulk_status_update/
    # Upcoming Interviews: GET /api/application-tracking/interviews/upcoming/
    # Mark Notification Read: POST /api/application-tracking/notifications/{id}/mark_read/
    # Mark All Read: POST /api/application-tracking/notifications/mark_all_read/
]