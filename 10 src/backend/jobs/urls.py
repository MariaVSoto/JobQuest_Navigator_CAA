"""
Jobs app URL configuration for Epic 1: Job Search & Geolocation Mapping.
Updated to use ViewSets with DRF Router for consistent API architecture.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, viewsets

# Create router and register ViewSets
router = DefaultRouter()
router.register(r'jobs', viewsets.JobViewSet, basename='job')
router.register(r'saved-jobs', viewsets.SavedJobViewSet, basename='savedjob')
router.register(r'applications', viewsets.JobApplicationViewSet, basename='jobapplication')
router.register(r'alerts', viewsets.JobAlertViewSet, basename='jobalert')
router.register(r'skills', viewsets.SkillViewSet, basename='skill')
router.register(r'user-skills', viewsets.UserSkillViewSet, basename='userskill')

app_name = 'jobs'

urlpatterns = [
    # Include router URLs (modern ViewSets architecture)
    path('', include(router.urls)),
    
    # Legacy endpoints for backward compatibility (will be deprecated)
    # These endpoints map to old view classes for existing frontend integration
    path('legacy/list/', views.JobListView.as_view(), name='job_list_legacy'),
    path('legacy/<uuid:pk>/', views.JobDetailView.as_view(), name='job_detail_legacy'),
    path('legacy/search/', views.JobSearchView.as_view(), name='job_search_legacy'),
    path('legacy/create/', views.JobCreateView.as_view(), name='job_create_legacy'),
    path('legacy/<uuid:pk>/update/', views.JobUpdateView.as_view(), name='job_update_legacy'),
    
    # Legacy geolocation features
    path('legacy/nearby/', views.NearbyJobsView.as_view(), name='nearby_jobs_legacy'),
    path('legacy/map/', views.JobMapView.as_view(), name='job_map_legacy'),
    
    # Legacy user job interactions
    path('legacy/saved/', views.SavedJobsView.as_view(), name='saved_jobs_legacy'),
    path('legacy/<uuid:pk>/save/', views.SaveJobView.as_view(), name='save_job_legacy'),
    path('legacy/<uuid:pk>/unsave/', views.UnsaveJobView.as_view(), name='unsave_job_legacy'),
    path('legacy/<uuid:pk>/apply/', views.ApplyJobView.as_view(), name='apply_job_legacy'),
    
    # Legacy applications and alerts
    path('legacy/applications/', views.JobApplicationListView.as_view(), name='job_applications_legacy'),
    path('legacy/applications/<uuid:pk>/', views.JobApplicationDetailView.as_view(), name='job_application_detail_legacy'),
    path('legacy/alerts/', views.JobAlertListView.as_view(), name='job_alerts_legacy'),
    path('legacy/alerts/<uuid:pk>/', views.JobAlertDetailView.as_view(), name='job_alert_detail_legacy'),
    
    # Legacy skills endpoints
    path('legacy/skills/', views.SkillListView.as_view(), name='skills_legacy'),
    path('legacy/user-skills/', views.UserSkillListView.as_view(), name='user_skills_legacy'),
    path('legacy/user-skills/<uuid:pk>/', views.UserSkillDetailView.as_view(), name='user_skill_detail_legacy'),
]

# API Endpoint Documentation:
# 
# MODERN VIEWSET ENDPOINTS (Primary):
# GET /api/jobs/jobs/                          - List jobs with filtering
# POST /api/jobs/jobs/                         - Create job (admin only)
# GET /api/jobs/jobs/{id}/                     - Get job details
# PUT /api/jobs/jobs/{id}/                     - Update job (admin only)
# DELETE /api/jobs/jobs/{id}/                  - Delete job (admin only)
# GET /api/jobs/jobs/search/                   - Advanced job search
# GET /api/jobs/jobs/nearby/                   - Get nearby jobs
# GET /api/jobs/jobs/map/                      - Get jobs for map visualization
# POST /api/jobs/jobs/{id}/save/               - Save a job
# DELETE /api/jobs/jobs/{id}/unsave/           - Unsave a job
# POST /api/jobs/jobs/{id}/apply/              - Apply to a job
# 
# GET /api/jobs/saved-jobs/                    - List saved jobs
# GET /api/jobs/saved-jobs/{id}/               - Get saved job details
# 
# GET /api/jobs/applications/                  - List job applications
# POST /api/jobs/applications/                 - Create job application
# GET /api/jobs/applications/{id}/             - Get application details
# PUT /api/jobs/applications/{id}/             - Update application
# DELETE /api/jobs/applications/{id}/          - Delete application
# 
# GET /api/jobs/alerts/                        - List job alerts
# POST /api/jobs/alerts/                       - Create job alert
# GET /api/jobs/alerts/{id}/                   - Get alert details
# PUT /api/jobs/alerts/{id}/                   - Update alert
# DELETE /api/jobs/alerts/{id}/                - Delete alert
# 
# GET /api/jobs/skills/                        - List skills
# POST /api/jobs/skills/                       - Create skill
# GET /api/jobs/skills/{id}/                   - Get skill details
# PUT /api/jobs/skills/{id}/                   - Update skill
# DELETE /api/jobs/skills/{id}/                - Delete skill
# 
# GET /api/jobs/user-skills/                   - List user skills
# POST /api/jobs/user-skills/                  - Create user skill
# GET /api/jobs/user-skills/{id}/              - Get user skill details
# PUT /api/jobs/user-skills/{id}/              - Update user skill
# DELETE /api/jobs/user-skills/{id}/           - Delete user skill