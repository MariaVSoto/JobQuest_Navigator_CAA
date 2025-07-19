"""
AI Suggestions app URL configuration for Epic 3: AI-Powered Resume Suggestions.
Updated to use ViewSets with DRF Router for consistent API architecture with legacy compatibility.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import viewsets, views

# Create router and register ViewSets
router = DefaultRouter()
router.register(r'templates', viewsets.SuggestionTemplateViewSet, basename='suggestiontemplate')
router.register(r'suggestions', viewsets.AISuggestionViewSet, basename='aisuggestion')
router.register(r'job-recommendations', viewsets.JobRecommendationViewSet, basename='jobrecommendation')
router.register(r'batches', viewsets.SuggestionBatchViewSet, basename='suggestionbatch')

app_name = 'ai_suggestions'

# Wire up our API using automatic URL routing
urlpatterns = [
    # ViewSets Router URLs (Primary API endpoints)
    path('', include(router.urls)),
    
    # Nested feedback endpoints (manual routing since we don't have nested router)
    path('suggestions/<uuid:suggestion_pk>/feedback/', viewsets.SuggestionFeedbackViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='suggestion-feedback-list'),
    path('suggestions/<uuid:suggestion_pk>/feedback/<uuid:pk>/', viewsets.SuggestionFeedbackViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='suggestion-feedback-detail'),
    
    # Legacy endpoints for backward compatibility (will be deprecated)
    # These map to the ViewSets actions using the same URLs
    path('legacy/', views.AISuggestionListView.as_view(), name='suggestion_list_legacy'),
    path('legacy/<uuid:pk>/', views.AISuggestionDetailView.as_view(), name='suggestion_detail_legacy'),
    path('legacy/create/', views.AISuggestionCreateView.as_view(), name='suggestion_create_legacy'),
    path('legacy/search/', views.AISuggestionSearchView.as_view(), name='suggestion_search_legacy'),
    path('legacy/templates/', views.SuggestionTemplateListView.as_view(), name='template_list_legacy'),
    path('legacy/templates/<uuid:pk>/', views.SuggestionTemplateDetailView.as_view(), name='template_detail_legacy'),
    path('legacy/optimize-resume/', views.ResumeOptimizationView.as_view(), name='optimize_resume_legacy'),
    path('legacy/job-match-analysis/', views.JobMatchAnalysisView.as_view(), name='job_match_analysis_legacy'),
    path('legacy/<uuid:pk>/action/', views.SuggestionActionView.as_view(), name='suggestion_action_legacy'),
    path('legacy/bulk-action/', views.BulkSuggestionActionView.as_view(), name='bulk_suggestion_action_legacy'),
    path('legacy/job-recommendations/', views.JobRecommendationListView.as_view(), name='job_recommendation_list_legacy'),
    path('legacy/job-recommendations/<uuid:pk>/', views.JobRecommendationDetailView.as_view(), name='job_recommendation_detail_legacy'),
    path('legacy/job-recommendations/<uuid:pk>/dismiss/', views.DismissJobRecommendationView.as_view(), name='dismiss_job_recommendation_legacy'),
    path('legacy/job-recommendations/<uuid:pk>/save/', views.SaveJobRecommendationView.as_view(), name='save_job_recommendation_legacy'),
    path('legacy/<uuid:suggestion_id>/feedback/', views.SuggestionFeedbackCreateView.as_view(), name='suggestion_feedback_create_legacy'),
    path('legacy/<uuid:suggestion_id>/feedback/list/', views.SuggestionFeedbackListView.as_view(), name='suggestion_feedback_list_legacy'),
    path('legacy/analytics/', views.AISuggestionsAnalyticsView.as_view(), name='ai_suggestions_analytics_legacy'),
    path('legacy/batches/', views.SuggestionBatchListView.as_view(), name='suggestion_batch_list_legacy'),
    path('legacy/batches/<uuid:pk>/', views.SuggestionBatchDetailView.as_view(), name='suggestion_batch_detail_legacy'),
    path('legacy/generate-daily/', views.GenerateDailySuggestionsView.as_view(), name='generate_daily_suggestions_legacy'),
    
    # Modern ViewSets endpoints documentation:
    # GET /api/ai-suggestions/templates/ - List suggestion templates
    # GET /api/ai-suggestions/templates/{id}/ - Get specific template
    # GET /api/ai-suggestions/templates/popular/ - Popular templates
    # GET /api/ai-suggestions/templates/by_type/?type=<type> - Templates by type
    # 
    # GET /api/ai-suggestions/suggestions/ - List user's suggestions
    # POST /api/ai-suggestions/suggestions/ - Create suggestion
    # GET /api/ai-suggestions/suggestions/{id}/ - Get specific suggestion (marks as viewed)
    # PUT /api/ai-suggestions/suggestions/{id}/ - Update suggestion
    # DELETE /api/ai-suggestions/suggestions/{id}/ - Delete suggestion
    # GET /api/ai-suggestions/suggestions/search/ - Advanced search
    # POST /api/ai-suggestions/suggestions/{id}/action/ - Accept/reject suggestion
    # POST /api/ai-suggestions/suggestions/bulk_action/ - Bulk actions
    # POST /api/ai-suggestions/suggestions/optimize_resume/ - Generate resume optimization
    # POST /api/ai-suggestions/suggestions/analyze_job_match/ - Analyze job match
    # GET /api/ai-suggestions/suggestions/analytics/ - User analytics
    # POST /api/ai-suggestions/suggestions/generate_daily/ - Generate daily suggestions
    # 
    # GET /api/ai-suggestions/job-recommendations/ - List job recommendations
    # GET /api/ai-suggestions/job-recommendations/{id}/ - Get specific recommendation (marks as viewed)
    # POST /api/ai-suggestions/job-recommendations/{id}/dismiss/ - Dismiss recommendation
    # POST /api/ai-suggestions/job-recommendations/{id}/save/ - Save recommendation
    # GET /api/ai-suggestions/job-recommendations/active/ - Active recommendations
    # GET /api/ai-suggestions/job-recommendations/saved/ - Saved recommendations
    # 
    # GET /api/ai-suggestions/suggestions/{suggestion_id}/feedback/ - List feedback for suggestion
    # POST /api/ai-suggestions/suggestions/{suggestion_id}/feedback/ - Create feedback
    # GET /api/ai-suggestions/suggestions/{suggestion_id}/feedback/{id}/ - Get specific feedback
    # PUT /api/ai-suggestions/suggestions/{suggestion_id}/feedback/{id}/ - Update feedback
    # DELETE /api/ai-suggestions/suggestions/{suggestion_id}/feedback/{id}/ - Delete feedback
    # 
    # GET /api/ai-suggestions/batches/ - List suggestion batches
    # GET /api/ai-suggestions/batches/{id}/ - Get specific batch
    # GET /api/ai-suggestions/batches/recent/ - Recent batches
    # GET /api/ai-suggestions/batches/by_type/?type=<type> - Batches by type
] 