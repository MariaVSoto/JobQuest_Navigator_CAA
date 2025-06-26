"""
Company Research app URL configuration for Epic 6: Company Research & Interview Preparation.
Modern DRF Router-based URLs with legacy compatibility.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, viewsets

# Create router and register viewsets
router = DefaultRouter()
router.register(r'company-research', viewsets.CompanyResearchViewSet, basename='companyresearch')
router.register(r'interview-preparation', viewsets.InterviewPreparationViewSet, basename='interviewpreparation')
router.register(r'interview-questions', viewsets.InterviewQuestionViewSet, basename='interviewquestion')
router.register(r'practice-sessions', viewsets.PracticeSessionViewSet, basename='practicesession')
router.register(r'company-insights', viewsets.CompanyInsightViewSet, basename='companyinsight')
router.register(r'company-news', viewsets.CompanyNewsViewSet, basename='companynews')

app_name = 'company_research'

urlpatterns = [
    # Modern ViewSets URLs
    path('', include(router.urls)),
    
    # Legacy compatibility URLs (redirecting to ViewSets)
    # Company research legacy support
    path('generate/', viewsets.CompanyResearchViewSet.as_view({'post': 'generate'}), name='generate_company_research'),
    path('saved/', viewsets.CompanyResearchViewSet.as_view({'get': 'saved'}), name='saved_research'),
    path('<uuid:pk>/save/', viewsets.CompanyResearchViewSet.as_view({'post': 'save'}), name='save_research'),
    path('<uuid:pk>/unsave/', viewsets.CompanyResearchViewSet.as_view({'delete': 'unsave'}), name='unsave_research'),
    
    # Interview preparation legacy support
    path('interview-prep/', viewsets.InterviewPreparationViewSet.as_view({'get': 'list', 'post': 'create'}), name='interview_prep_list'),
    path('interview-prep/<uuid:pk>/', viewsets.InterviewPreparationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='interview_prep_detail'),
    path('interview-prep/generate/', viewsets.InterviewPreparationViewSet.as_view({'post': 'generate'}), name='generate_interview_prep'),
    
    # Company insights legacy support
    path('insights/', viewsets.CompanyInsightViewSet.as_view({'get': 'list', 'post': 'create'}), name='company_insights'),
    path('insights/<uuid:pk>/', viewsets.CompanyInsightViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='company_insight_detail'),
    
    # Interview questions legacy support
    path('questions/', viewsets.InterviewQuestionViewSet.as_view({'get': 'list', 'post': 'create'}), name='interview_question_list'),
    path('questions/<uuid:pk>/', viewsets.InterviewQuestionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='interview_question_detail'),
    path('questions/generate/', viewsets.InterviewQuestionViewSet.as_view({'post': 'generate'}), name='generate_interview_questions'),
    
    # Practice sessions legacy support
    path('practice/', viewsets.PracticeSessionViewSet.as_view({'get': 'list', 'post': 'create'}), name='practice_session_list'),
    path('practice/<uuid:pk>/', viewsets.PracticeSessionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='practice_session_detail'),
    path('practice/start/', viewsets.PracticeSessionViewSet.as_view({'post': 'start'}), name='start_practice_session'),
    
    # Company news legacy support
    path('news/', viewsets.CompanyNewsViewSet.as_view({'get': 'list'}), name='company_news'),
    path('news/<uuid:pk>/', viewsets.CompanyNewsViewSet.as_view({'get': 'retrieve'}), name='company_news_detail'),
] 