"""
Skills app URL configuration for Epic 4: Skills Analysis & Management.
"""

from django.urls import path
from . import views

app_name = 'skills'

urlpatterns = [
    # Skill management
    path('', views.SkillListView.as_view(), name='skill_list'),
    path('<uuid:pk>/', views.SkillDetailView.as_view(), name='skill_detail'),
    path('categories/', views.SkillCategoryListView.as_view(), name='skill_category_list'),
    
    # User skills
    path('user/', views.UserSkillListView.as_view(), name='user_skill_list'),
    path('user/add/', views.AddUserSkillView.as_view(), name='add_user_skill'),
    path('user/<uuid:pk>/update/', views.UpdateUserSkillView.as_view(), name='update_user_skill'),
    path('user/<uuid:pk>/remove/', views.RemoveUserSkillView.as_view(), name='remove_user_skill'),
    
    # Skill analysis
    path('analyze/', views.AnalyzeSkillsView.as_view(), name='analyze_skills'),
    path('gap-analysis/', views.SkillGapAnalysisView.as_view(), name='skill_gap_analysis'),
    path('recommendations/', views.SkillRecommendationsView.as_view(), name='skill_recommendations'),
    
    # Skill extraction from resume/job
    path('extract/resume/', views.ExtractSkillsFromResumeView.as_view(), name='extract_skills_resume'),
    path('extract/job/', views.ExtractSkillsFromJobView.as_view(), name='extract_skills_job'),
    
    # Skill trends and market data
    path('trends/', views.SkillTrendsView.as_view(), name='skill_trends'),
    path('market-demand/', views.SkillMarketDemandView.as_view(), name='skill_market_demand'),
] 