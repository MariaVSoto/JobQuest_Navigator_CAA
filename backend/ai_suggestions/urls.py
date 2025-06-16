"""
AI Suggestions app URL configuration for Epic 3: AI-Powered Resume Suggestions.
"""

from django.urls import path
from . import views

app_name = 'ai_suggestions'

urlpatterns = [
    # AI suggestion management
    path('', views.SuggestionListView.as_view(), name='suggestion_list'),
    path('<uuid:pk>/', views.SuggestionDetailView.as_view(), name='suggestion_detail'),
    
    # Resume analysis and suggestions
    path('analyze/', views.AnalyzeResumeView.as_view(), name='analyze_resume'),
    path('generate/', views.GenerateSuggestionsView.as_view(), name='generate_suggestions'),
    path('job-match/', views.JobMatchSuggestionsView.as_view(), name='job_match_suggestions'),
    
    # Suggestion interactions
    path('<uuid:pk>/accept/', views.AcceptSuggestionView.as_view(), name='accept_suggestion'),
    path('<uuid:pk>/reject/', views.RejectSuggestionView.as_view(), name='reject_suggestion'),
    path('<uuid:pk>/feedback/', views.SuggestionFeedbackView.as_view(), name='suggestion_feedback'),
    
    # Bulk operations
    path('bulk-accept/', views.BulkAcceptSuggestionsView.as_view(), name='bulk_accept_suggestions'),
    path('bulk-reject/', views.BulkRejectSuggestionsView.as_view(), name='bulk_reject_suggestions'),
    
    # AI model management
    path('models/', views.AIModelListView.as_view(), name='ai_model_list'),
    path('models/<uuid:pk>/', views.AIModelDetailView.as_view(), name='ai_model_detail'),
] 