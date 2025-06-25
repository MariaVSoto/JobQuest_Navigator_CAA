"""
Skills app URL configuration for Epic 4: Skills Analysis & Management.
Updated to use ViewSets with DRF Router for consistent API architecture with legacy compatibility.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import viewsets, views

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

app_name = 'skills'

# Wire up our API using automatic URL routing
urlpatterns = [
    # ViewSets Router URLs (Primary API endpoints)
    path('', include(router.urls)),
    
    # Legacy endpoints for backward compatibility (will be deprecated)
    # These map to the ViewSets actions using the same URLs
    path('legacy/skill-gap-analysis/', views.skill_gap_analysis, name='skill_gap_analysis_legacy'),
    path('legacy/skill-trends/', views.skill_trends, name='skill_trends_legacy'),
    path('legacy/skill-recommendations/', views.skill_recommendations, name='skill_recommendations_legacy'),
    path('legacy/extract-skills-from-text/', views.extract_skills_from_text, name='extract_skills_from_text_legacy'),
    path('legacy/learning-progress/<uuid:learning_path_id>/', views.update_learning_progress, name='update_learning_progress_legacy'),
    path('legacy/certification-plan/', views.create_certification_plan, name='create_certification_plan_legacy'),
    path('legacy/user-skills-analytics/', views.user_skills_analytics, name='user_skills_analytics_legacy'),
    path('legacy/skill-assessment/<uuid:assessment_id>/', views.take_skill_assessment, name='take_skill_assessment_legacy'),
    path('legacy/skill-market-demand/', views.skill_market_demand, name='skill_market_demand_legacy'),
    
    # Modern ViewSets endpoints documentation:
    # GET /api/skills/skills/trending/ - Get trending skills
    # POST /api/skills/skills/extract_from_text/ - Extract skills from text
    # GET /api/skills/skills/market_demand/ - Get market demand data
    # GET /api/skills/user-skills/gap_analysis/?role=<role> - Skill gap analysis
    # GET /api/skills/user-skills/recommendations/ - Skill recommendations
    # GET /api/skills/user-skills/analytics/ - User skills analytics
    # POST /api/skills/certifications/generate_plan/ - Generate certification plan
    # GET /api/skills/user-certifications/progress/ - Certification progress
    # POST /api/skills/user-learning-paths/{id}/update_progress/ - Update learning progress
    # GET /api/skills/user-assessments/analytics/ - Assessment analytics
    # POST /api/skills/user-assessments/{id}/take_assessment/ - Take assessment
] 