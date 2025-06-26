"""
Simplified URL configuration for AI Suggestions app.
Provides essential endpoints with reduced complexity.
"""

from django.urls import path
from . import simple_views

app_name = 'ai_suggestions_simple'

urlpatterns = [
    # Core AI Suggestions
    path('suggestions/', simple_views.get_ai_suggestions, name='suggestions_list'),
    path('suggestions/generate/', simple_views.generate_resume_suggestions, name='generate_suggestions'),
    path('suggestions/<uuid:suggestion_id>/action/', simple_views.suggestion_action, name='suggestion_action'),
    
    # Job Recommendations
    path('recommendations/', simple_views.get_job_recommendations, name='recommendations_list'),
    path('recommendations/generate/', simple_views.generate_job_recommendations, name='generate_recommendations'),
    path('recommendations/<uuid:recommendation_id>/action/', simple_views.recommendation_action, name='recommendation_action'),
    
    # Analytics
    path('analytics/', simple_views.simple_analytics, name='analytics'),
]