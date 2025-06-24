"""
Skills app URL configuration for Epic 4: Skills Analysis & Management.
"""

from django.urls import path
from . import views

app_name = 'skills'

urlpatterns = [
    # Skill management
    path('', views.SkillListView.as_view(), name='skill_list'),
    path('<uuid:pk>/', views.SkillDetailView.as_view(), name='skill_detail'),
    path('create/', views.SkillCreateView.as_view(), name='skill_create'),
    path('search/', views.SkillSearchView.as_view(), name='skill_search'),
    
    # Skill categories
    path('categories/', views.SkillCategoryListView.as_view(), name='skill_category_list'),
    path('categories/<uuid:pk>/', views.SkillCategoryDetailView.as_view(), name='skill_category_detail'),
    
    # User skills
    path('user/', views.UserSkillListView.as_view(), name='user_skill_list'),
    path('user/<uuid:pk>/', views.UserSkillDetailView.as_view(), name='user_skill_detail'),
    
    # Certifications
    path('certifications/', views.CertificationListView.as_view(), name='certification_list'),
    path('certifications/<uuid:pk>/', views.CertificationDetailView.as_view(), name='certification_detail'),
    
    # User certifications
    path('user-certifications/', views.UserCertificationListView.as_view(), name='user_certification_list'),
    path('user-certifications/<uuid:pk>/', views.UserCertificationDetailView.as_view(), name='user_certification_detail'),
    
    # Learning paths
    path('learning-paths/', views.LearningPathListView.as_view(), name='learning_path_list'),
    path('learning-paths/<uuid:pk>/', views.LearningPathDetailView.as_view(), name='learning_path_detail'),
    
    # User learning paths
    path('user-learning-paths/', views.UserLearningPathListView.as_view(), name='user_learning_path_list'),
    path('user-learning-paths/<uuid:pk>/', views.UserLearningPathDetailView.as_view(), name='user_learning_path_detail'),
    
    # Skill assessments
    path('assessments/', views.SkillAssessmentListView.as_view(), name='skill_assessment_list'),
    path('assessments/<uuid:pk>/', views.SkillAssessmentDetailView.as_view(), name='skill_assessment_detail'),
    
    # User skill assessments
    path('user-assessments/', views.UserSkillAssessmentListView.as_view(), name='user_skill_assessment_list'),
    path('user-assessments/<uuid:pk>/', views.UserSkillAssessmentDetailView.as_view(), name='user_skill_assessment_detail'),
] 