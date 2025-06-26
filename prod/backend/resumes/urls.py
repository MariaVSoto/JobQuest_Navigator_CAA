"""
Resumes app URL configuration for Epic 2: Resume Management & Versioning.
Modern DRF Router-based URLs with legacy compatibility.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, viewsets

# Create router and register viewsets
router = DefaultRouter()
router.register(r'resume-templates', viewsets.ResumeTemplateViewSet, basename='resumetemplate')
router.register(r'resumes', viewsets.ResumeViewSet, basename='resume')
router.register(r'resume-versions', viewsets.ResumeVersionViewSet, basename='resumeversion')
router.register(r'resume-shares', viewsets.ResumeShareViewSet, basename='resumeshare')
router.register(r'resume-comments', viewsets.ResumeCommentViewSet, basename='resumecomment')
router.register(r'resume-exports', viewsets.ResumeExportViewSet, basename='resumeexport')

app_name = 'resumes'

urlpatterns = [
    # Modern ViewSets URLs
    path('', include(router.urls)),
    
    # Legacy compatibility URLs (redirecting to ViewSets)
    # Resume Templates legacy support
    path('templates/', viewsets.ResumeTemplateViewSet.as_view({'get': 'list'}), name='template-list'),
    path('templates/<uuid:pk>/', viewsets.ResumeTemplateViewSet.as_view({'get': 'retrieve'}), name='template-detail'),
    
    # Resume CRUD legacy support  
    path('create/', viewsets.ResumeViewSet.as_view({'post': 'create'}), name='resume-create'),
    path('<uuid:pk>/update/', viewsets.ResumeViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='resume-update'),
    path('<uuid:pk>/delete/', viewsets.ResumeViewSet.as_view({'delete': 'destroy'}), name='resume-delete'),
    
    # Resume Versions legacy support
    path('<uuid:resume_id>/versions/', viewsets.ResumeVersionViewSet.as_view({'get': 'by_resume', 'post': 'create'}), name='version-list'),
    path('<uuid:resume_id>/versions/<uuid:version_id>/', viewsets.ResumeVersionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='version-detail'),
    path('<uuid:resume_id>/versions/<uuid:version_id>/restore/', viewsets.ResumeVersionViewSet.as_view({'post': 'restore'}), name='version-restore'),
    
    # Resume Sharing legacy support
    path('<uuid:resume_id>/shares/', viewsets.ResumeShareViewSet.as_view({'get': 'by_resume', 'post': 'create'}), name='share-list'),
    path('<uuid:resume_id>/shares/<uuid:share_id>/', viewsets.ResumeShareViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='share-detail'),
    
    # Resume Comments legacy support
    path('<uuid:resume_id>/comments/', viewsets.ResumeCommentViewSet.as_view({'get': 'by_resume', 'post': 'create'}), name='comment-list'),
    path('<uuid:resume_id>/comments/<uuid:comment_id>/', viewsets.ResumeCommentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='comment-detail'),
    
    # Resume Exports legacy support
    path('<uuid:resume_id>/exports/', viewsets.ResumeExportViewSet.as_view({'get': 'by_resume', 'post': 'create'}), name='export-list'),
    path('<uuid:resume_id>/exports/<uuid:export_id>/download/', viewsets.ResumeExportViewSet.as_view({'get': 'download'}), name='export-download'),
    
    # Utility Endpoints legacy support
    path('<uuid:resume_id>/clone/', viewsets.ResumeViewSet.as_view({'post': 'clone'}), name='resume-clone'),
    path('<uuid:resume_id>/set-default/', viewsets.ResumeViewSet.as_view({'post': 'set_default'}), name='resume-set-default'),
    path('analytics/', viewsets.ResumeViewSet.as_view({'get': 'analytics'}), name='resume-analytics'),
] 