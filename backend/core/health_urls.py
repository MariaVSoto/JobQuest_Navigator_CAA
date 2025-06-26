"""
Health check URLs for monitoring and deployment.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.HealthCheckView.as_view(), name='health_check'),
    path('detailed/', views.DetailedHealthCheckView.as_view(), name='detailed_health_check'),
] 