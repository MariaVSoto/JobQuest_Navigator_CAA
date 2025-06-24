"""
JobQuest Navigator Backend URL Configuration

This configuration provides unified API routing for all epics:
- Epic 1: Job Search & Geolocation Mapping
- Epic 2: Resume Management & Versioning  
- Epic 3: AI-Powered Resume Suggestions
- Epic 4: Skills Analysis & Certification Roadmap
- Epic 6: Company Research & Interview Preparation
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

# API v1 URL patterns
api_v1_patterns = [
    # Authentication endpoints
    path('auth/', include('core.urls')),
    
    # Epic 1: Job Search & Geolocation
    path('jobs/', include('jobs.urls')),
    
    # Epic 2: Resume Management
    path('resumes/', include('resumes.urls')),
    
    # Epic 3: AI Suggestions
    path('ai-suggestions/', include('ai_suggestions.urls')),
    path('ai-simple/', include('ai_suggestions.simple_urls')),
    
    # Epic 4: Skills & Certifications
    path('skills/', include('skills.urls')),
    path('certifications/', include('certifications.urls')),
    
    # Epic 6: Company Research
    path('company-research/', include('company_research.urls')),
]

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # GraphQL endpoint
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1 endpoints
    path('api/v1/', include(api_v1_patterns)),
    
    # Health check endpoint
    path('health/', include('core.health_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'
