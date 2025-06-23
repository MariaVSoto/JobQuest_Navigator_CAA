"""
Resumes app URL configuration for Epic 2: Resume Management & Versioning.
"""

from django.urls import path
from . import views

app_name = 'resumes'

urlpatterns = [
    # Resume management
    path('', views.ResumeListView.as_view(), name='resume_list'),
    path('<uuid:pk>/', views.ResumeDetailView.as_view(), name='resume_detail'),
    path('create/', views.CreateResumeView.as_view(), name='create_resume'),
    path('<uuid:pk>/update/', views.UpdateResumeView.as_view(), name='update_resume'),
    path('<uuid:pk>/delete/', views.DeleteResumeView.as_view(), name='delete_resume'),
    
    # Resume versioning
    path('<uuid:pk>/versions/', views.ResumeVersionListView.as_view(), name='resume_version_list'),
    path('<uuid:pk>/versions/create/', views.CreateResumeVersionView.as_view(), name='create_resume_version'),
    path('versions/<uuid:pk>/', views.ResumeVersionDetailView.as_view(), name='resume_version_detail'),
    path('versions/<uuid:pk>/restore/', views.RestoreResumeVersionView.as_view(), name='restore_resume_version'),
    
    # Resume export/import
    path('<uuid:pk>/export/', views.ExportResumeView.as_view(), name='export_resume'),
    path('import/', views.ImportResumeView.as_view(), name='import_resume'),
    
    # Resume sharing
    path('<uuid:pk>/share/', views.ShareResumeView.as_view(), name='share_resume'),
    path('shared/<str:share_token>/', views.SharedResumeView.as_view(), name='shared_resume'),
    
    # Resume templates
    path('templates/', views.ResumeTemplateListView.as_view(), name='resume_template_list'),
    path('templates/<uuid:pk>/', views.ResumeTemplateDetailView.as_view(), name='resume_template_detail'),
] 