"""
AI Suggestions app URL configuration for Epic 3: AI-Powered Resume Suggestions.
"""

from django.urls import path
from . import views

app_name = 'ai_suggestions'

urlpatterns = [
    # AI suggestion management
    path('', views.AISuggestionListView.as_view(), name='suggestion_list'),
    path('<uuid:pk>/', views.AISuggestionDetailView.as_view(), name='suggestion_detail'),
    path('create/', views.AISuggestionCreateView.as_view(), name='suggestion_create'),
    path('search/', views.AISuggestionSearchView.as_view(), name='suggestion_search'),
    
    # Suggestion templates
    path('templates/', views.SuggestionTemplateListView.as_view(), name='template_list'),
    path('templates/<uuid:pk>/', views.SuggestionTemplateDetailView.as_view(), name='template_detail'),
    
    # Resume optimization
    path('optimize-resume/', views.ResumeOptimizationView.as_view(), name='optimize_resume'),
    path('job-match-analysis/', views.JobMatchAnalysisView.as_view(), name='job_match_analysis'),
    
    # Suggestion actions
    path('<uuid:pk>/action/', views.SuggestionActionView.as_view(), name='suggestion_action'),
    path('bulk-action/', views.BulkSuggestionActionView.as_view(), name='bulk_suggestion_action'),
    
    # Job recommendations
    path('job-recommendations/', views.JobRecommendationListView.as_view(), name='job_recommendation_list'),
    path('job-recommendations/<uuid:pk>/', views.JobRecommendationDetailView.as_view(), name='job_recommendation_detail'),
    path('job-recommendations/<uuid:pk>/dismiss/', views.dismiss_job_recommendation, name='dismiss_job_recommendation'),
    path('job-recommendations/<uuid:pk>/save/', views.save_job_recommendation, name='save_job_recommendation'),
    
    # Feedback
    path('<uuid:suggestion_id>/feedback/', views.SuggestionFeedbackCreateView.as_view(), name='suggestion_feedback_create'),
    path('<uuid:suggestion_id>/feedback/list/', views.SuggestionFeedbackListView.as_view(), name='suggestion_feedback_list'),
    
    # Analytics and batch operations
    path('analytics/', views.ai_suggestions_analytics, name='ai_suggestions_analytics'),
    path('batches/', views.SuggestionBatchListView.as_view(), name='suggestion_batch_list'),
    path('batches/<uuid:pk>/', views.SuggestionBatchDetailView.as_view(), name='suggestion_batch_detail'),
    path('generate-daily/', views.generate_daily_suggestions, name='generate_daily_suggestions'),
] 