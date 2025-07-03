"""
JobQuest Navigator - Main URL Configuration
Includes all Epic apps and core functionality with API versioning.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from . import views

# Authentication URLs (moved from previous core-only URLs)
auth_patterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('password/change/', views.ChangePasswordView.as_view(), name='change_password'),
    path('password/reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]

# User management URLs (moved from previous core-only URLs)
user_patterns = [
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='update_profile'),
    path('preferences/', views.UserPreferencesView.as_view(), name='user_preferences'),
    path('activity/', views.ActivityLogListView.as_view(), name='user_activity'),
]

# Location URLs (moved from previous core-only URLs)
location_patterns = [
    path('', views.LocationListView.as_view(), name='location_list'),
    path('<uuid:pk>/', views.LocationDetailView.as_view(), name='location_detail'),
    path('search/', views.LocationSearchView.as_view(), name='location_search'),
    path('geocode/', views.GeocodeView.as_view(), name='geocode'),
]

# Company URLs (moved from previous core-only URLs)
company_patterns = [
    path('', views.CompanyListView.as_view(), name='company_list'),
    path('<uuid:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
    path('search/', views.CompanySearchView.as_view(), name='company_search'),
]

# Main URL patterns including all Epic applications
urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # GraphQL API
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),
    
    # API Documentation and Health Checks
    path('health/', include('core.health_urls')),
    
    # Authentication & Core User Management
    path('api/auth/', include(auth_patterns)),
    path('api/user/', include(user_patterns)),
    path('api/locations/', include(location_patterns)),
    path('api/companies/', include(company_patterns)),
    
    # Epic 1: Geolocation-Based Job Mapping (Jobs)
    path('api/jobs/', include('jobs.urls')),
    
    # Epic 2: Automated Resume Versioning System
    path('api/resumes/', include('resumes.urls')),
    
    # Epic 3: AI-Powered Resume Optimization and Smart Recommendations
    path('api/ai-suggestions/', include('ai_suggestions.urls')),
    
    # Epic 4: Dynamic Certification Roadmap with Market Demand Alerts (unified in skills module)
    path('api/skills/', include('skills.urls')),
    
    # Epic 5: Job Application Tracking with Resume Used
    path('api/application-tracking/', include('application_tracking.urls')),
    
    # Epic 6: AI-Driven Company Research and Interview Prep Module
    path('api/company-research/', include('company_research.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Add debug toolbar only if it's available
    try:
        import debug_toolbar
        urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    except ImportError:
        pass