"""
Resumes app URL configuration for Epic 2: Resume Management & Versioning.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'resumes'

urlpatterns = [
    # Resume Templates
    path('templates/', views.ResumeTemplateListView.as_view(), name='template-list'),
    path('templates/<uuid:pk>/', views.ResumeTemplateDetailView.as_view(), name='template-detail'),
    
    # Resume CRUD
    path('', views.ResumeListView.as_view(), name='resume-list'),
    path('create/', views.ResumeCreateView.as_view(), name='resume-create'),
    path('<uuid:pk>/', views.ResumeDetailView.as_view(), name='resume-detail'),
    path('<uuid:pk>/update/', views.ResumeUpdateView.as_view(), name='resume-update'),
    path('<uuid:pk>/delete/', views.ResumeDeleteView.as_view(), name='resume-delete'),
    
    # Resume Versions
    path('<uuid:resume_id>/versions/', views.ResumeVersionListView.as_view(), name='version-list'),
    path('<uuid:resume_id>/versions/<uuid:version_id>/', views.ResumeVersionDetailView.as_view(), name='version-detail'),
    path('<uuid:resume_id>/versions/<uuid:version_id>/restore/', views.restore_resume_version, name='version-restore'),
    
    # Resume Sharing
    path('<uuid:resume_id>/shares/', views.ResumeShareListView.as_view(), name='share-list'),
    path('<uuid:resume_id>/shares/<uuid:share_id>/', views.ResumeShareDetailView.as_view(), name='share-detail'),
    
    # Resume Comments
    path('<uuid:resume_id>/comments/', views.ResumeCommentListView.as_view(), name='comment-list'),
    path('<uuid:resume_id>/comments/<uuid:comment_id>/', views.ResumeCommentDetailView.as_view(), name='comment-detail'),
    
    # Resume Exports
    path('<uuid:resume_id>/exports/', views.ResumeExportListView.as_view(), name='export-list'),
    path('<uuid:resume_id>/exports/<uuid:export_id>/download/', views.download_resume_export, name='export-download'),
    
    # Resume Skills
    path('<uuid:resume_id>/skills/', views.ResumeSkillMatchListView.as_view(), name='skill-match-list'),
    
    # Utility Endpoints
    path('<uuid:resume_id>/clone/', views.clone_resume, name='resume-clone'),
    path('<uuid:resume_id>/set-default/', views.set_default_resume, name='resume-set-default'),
    path('analytics/', views.resume_analytics, name='resume-analytics'),
] 