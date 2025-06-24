"""
Skills app URL configuration for Epic 4: Skills Analysis & Management.
Updated to use ViewSets with DRF Router for consistent API architecture.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import viewsets

# Create router and register ViewSets
router = DefaultRouter()
router.register(r'categories', viewsets.SkillCategoryViewSet, basename='skillcategory')
router.register(r'skills', viewsets.SkillViewSet, basename='skill')
router.register(r'user-skills', viewsets.UserSkillViewSet, basename='userskill')
router.register(r'certifications', viewsets.CertificationViewSet, basename='certification')
router.register(r'user-certifications', viewsets.UserCertificationViewSet, basename='usercertification')
router.register(r'learning-paths', viewsets.LearningPathViewSet, basename='learningpath')
router.register(r'user-learning-paths', viewsets.UserLearningPathViewSet, basename='userlearningpath')
router.register(r'assessments', viewsets.SkillAssessmentViewSet, basename='skillassessment')
router.register(r'user-assessments', viewsets.UserSkillAssessmentViewSet, basename='userskillassessment')

# Wire up our API using automatic URL routing
urlpatterns = [
    path('', include(router.urls)),
] 