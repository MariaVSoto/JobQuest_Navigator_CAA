"""
Jobs app URL configuration for Epic 1: Job Search & Geolocation Mapping.
"""

from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Job search and listing
    path('', views.JobListView.as_view(), name='job_list'),
    path('<uuid:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path('search/', views.JobSearchView.as_view(), name='job_search'),
    path('create/', views.JobCreateView.as_view(), name='job_create'),
    path('<uuid:pk>/update/', views.JobUpdateView.as_view(), name='job_update'),
    
    # Geolocation features
    path('nearby/', views.NearbyJobsView.as_view(), name='nearby_jobs'),
    path('map/', views.JobMapView.as_view(), name='job_map'),
    
    # User job interactions
    path('saved/', views.SavedJobsView.as_view(), name='saved_jobs'),
    path('<uuid:pk>/save/', views.SaveJobView.as_view(), name='save_job'),
    path('<uuid:pk>/unsave/', views.UnsaveJobView.as_view(), name='unsave_job'),
    path('<uuid:pk>/apply/', views.ApplyJobView.as_view(), name='apply_job'),
    
    # Job applications
    path('applications/', views.JobApplicationListView.as_view(), name='job_applications'),
    path('applications/<uuid:pk>/', views.JobApplicationDetailView.as_view(), name='job_application_detail'),
    
    # Job alerts
    path('alerts/', views.JobAlertListView.as_view(), name='job_alerts'),
    path('alerts/<uuid:pk>/', views.JobAlertDetailView.as_view(), name='job_alert_detail'),
    
    # Skills
    path('skills/', views.SkillListView.as_view(), name='skills'),
    path('user-skills/', views.UserSkillListView.as_view(), name='user_skills'),
    path('user-skills/<uuid:pk>/', views.UserSkillDetailView.as_view(), name='user_skill_detail'),
    
    # Function-based views for backward compatibility
    path('api/list/', views.JobListCBV.as_view(), name='job_list_func'),
    path('api/<uuid:pk>/', views.JobDetailCBV.as_view(), name='job_detail_func'),
    path('api/search/', views.JobSearchCBV.as_view(), name='job_search_func'),
    path('api/nearby/', views.NearbyJobsCBV.as_view(), name='nearby_jobs_func'),
    path('api/map/', views.JobMapCBV.as_view(), name='job_map_func'),
    path('api/saved/', views.SavedJobsCBV.as_view(), name='saved_jobs_func'),
    path('api/<uuid:pk>/save/', views.SaveJobCBV.as_view(), name='save_job_func'),
    path('api/<uuid:pk>/unsave/', views.UnsaveJobCBV.as_view(), name='unsave_job_func'),
    path('api/<uuid:pk>/apply/', views.ApplyJobCBV.as_view(), name='apply_job_func'),
    path('api/applications/', views.JobApplicationsCBV.as_view(), name='job_applications_func'),
    path('api/skills/', views.SkillsCBV.as_view(), name='skills_func'),
    path('api/user-skills/', views.UserSkillsCBV.as_view(), name='user_skills_func'),
] 