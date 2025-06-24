"""
Certifications app URL configuration for Epic 4: Certification Roadmap.
"""

from django.urls import path
from . import views

app_name = 'certifications'

urlpatterns = [
    # Certification management
    path('', views.CertificationListView.as_view(), name='certification_list'),
    path('<uuid:pk>/', views.CertificationDetailView.as_view(), name='certification_detail'),
    path('providers/', views.CertificationProviderListView.as_view(), name='certification_provider_list'),
    
    # User certifications
    path('user/', views.UserCertificationListView.as_view(), name='user_certification_list'),
    path('user/add/', views.AddUserCertificationView.as_view(), name='add_user_certification'),
    path('user/<uuid:pk>/update/', views.UpdateUserCertificationView.as_view(), name='update_user_certification'),
    path('user/<uuid:pk>/remove/', views.RemoveUserCertificationView.as_view(), name='remove_user_certification'),
    
    # Certification roadmaps
    path('roadmaps/', views.CertificationRoadmapListView.as_view(), name='certification_roadmap_list'),
    path('roadmaps/<uuid:pk>/', views.CertificationRoadmapDetailView.as_view(), name='certification_roadmap_detail'),
    path('roadmaps/generate/', views.GenerateRoadmapView.as_view(), name='generate_roadmap'),
    
    # Certification recommendations
    path('recommendations/', views.CertificationRecommendationsView.as_view(), name='certification_recommendations'),
    path('career-path/', views.CareerPathCertificationsView.as_view(), name='career_path_certifications'),
    
    # Progress tracking
    path('progress/', views.CertificationProgressView.as_view(), name='certification_progress'),
    path('progress/<uuid:pk>/update/', views.UpdateProgressView.as_view(), name='update_progress'),
    
    # Study resources
    path('resources/', views.StudyResourceListView.as_view(), name='study_resource_list'),
    path('resources/<uuid:pk>/', views.StudyResourceDetailView.as_view(), name='study_resource_detail'),
] 