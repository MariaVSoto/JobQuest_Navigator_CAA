"""
Core app URL configuration.
Handles authentication, user management, and shared endpoints.
"""

from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

app_name = 'core'

# Authentication URLs
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

# User management URLs
user_patterns = [
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='update_profile'),
    path('preferences/', views.UserPreferencesView.as_view(), name='user_preferences'),
    path('activity/', views.ActivityLogListView.as_view(), name='user_activity'),
]

# Location URLs
location_patterns = [
    path('', views.LocationListView.as_view(), name='location_list'),
    path('<uuid:pk>/', views.LocationDetailView.as_view(), name='location_detail'),
    path('search/', views.LocationSearchView.as_view(), name='location_search'),
    path('geocode/', views.GeocodeView.as_view(), name='geocode'),
]

# Company URLs
company_patterns = [
    path('', views.CompanyListView.as_view(), name='company_list'),
    path('<uuid:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
    path('search/', views.CompanySearchView.as_view(), name='company_search'),
]

urlpatterns = [
    # Authentication endpoints
    path('', include(auth_patterns)),
    
    # User management
    path('user/', include(user_patterns)),
    
    # Shared resources
    path('locations/', include(location_patterns)),
    path('companies/', include(company_patterns)),
] 