"""
Company Research app URL configuration for Epic 6: Company Research & Interview Preparation.
"""

from django.urls import path
from . import views

app_name = 'company_research'

urlpatterns = [
    # Company research
    path('', views.CompanyResearchListView.as_view(), name='company_research_list'),
    path('<uuid:pk>/', views.CompanyResearchDetailView.as_view(), name='company_research_detail'),
    path('generate/', views.GenerateCompanyResearchView.as_view(), name='generate_company_research'),
    
    # Interview preparation
    path('interview-prep/', views.InterviewPrepListView.as_view(), name='interview_prep_list'),
    path('interview-prep/<uuid:pk>/', views.InterviewPrepDetailView.as_view(), name='interview_prep_detail'),
    path('interview-prep/generate/', views.GenerateInterviewPrepView.as_view(), name='generate_interview_prep'),
    
    # Company insights
    path('insights/', views.CompanyInsightsView.as_view(), name='company_insights'),
    path('insights/<uuid:pk>/', views.CompanyInsightDetailView.as_view(), name='company_insight_detail'),
    
    # Interview questions
    path('questions/', views.InterviewQuestionListView.as_view(), name='interview_question_list'),
    path('questions/<uuid:pk>/', views.InterviewQuestionDetailView.as_view(), name='interview_question_detail'),
    path('questions/generate/', views.GenerateInterviewQuestionsView.as_view(), name='generate_interview_questions'),
    
    # Practice sessions
    path('practice/', views.PracticeSessionListView.as_view(), name='practice_session_list'),
    path('practice/<uuid:pk>/', views.PracticeSessionDetailView.as_view(), name='practice_session_detail'),
    path('practice/start/', views.StartPracticeSessionView.as_view(), name='start_practice_session'),
    
    # Company news and updates
    path('news/', views.CompanyNewsView.as_view(), name='company_news'),
    path('news/<uuid:pk>/', views.CompanyNewsDetailView.as_view(), name='company_news_detail'),
    
    # Saved research
    path('saved/', views.SavedResearchView.as_view(), name='saved_research'),
    path('<uuid:pk>/save/', views.SaveResearchView.as_view(), name='save_research'),
    path('<uuid:pk>/unsave/', views.UnsaveResearchView.as_view(), name='unsave_research'),
] 