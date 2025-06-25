"""
Views for Epic 6: Company Research & Interview Preparation.
Provides comprehensive company research and interview preparation functionality.
"""

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, permissions, generics, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from core.models import Company
from .models import (
    CompanyResearch, InterviewPreparation, InterviewQuestion,
    PracticeSession, CompanyInsight, SavedResearch, CompanyNews
)
from .serializers import (
    CompanyResearchSerializer, CompanyResearchSummarySerializer,
    InterviewPreparationSerializer, InterviewQuestionSerializer,
    InterviewQuestionListSerializer, PracticeSessionSerializer,
    CompanyInsightSerializer, SavedResearchSerializer, CompanyNewsSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CompanyResearchListView(generics.ListCreateAPIView):
    """
    List all company research for authenticated user or create new research.
    """
    serializer_class = CompanyResearchSummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_saved', 'company__industry']
    search_fields = ['title', 'company__name', 'overview']
    ordering_fields = ['research_date', 'confidence_score', 'updated_at']
    ordering = ['-research_date']

    def get_queryset(self):
        return CompanyResearch.objects.filter(user=self.request.user).select_related('company')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CompanyResearchSerializer
        return CompanyResearchSummarySerializer


class CompanyResearchDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a specific company research.
    """
    serializer_class = CompanyResearchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CompanyResearch.objects.filter(user=self.request.user).select_related('company')


class GenerateCompanyResearchView(APIView):
    """
    Generate AI-powered company research for a specific company.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        company_id = request.data.get('company_id')
        if not company_id:
            return Response(
                {'error': 'company_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response(
                {'error': 'Company not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if research already exists
        existing_research = CompanyResearch.objects.filter(
            company=company, 
            user=request.user
        ).first()

        if existing_research:
            return Response(
                {
                    'message': 'Research already exists for this company',
                    'research_id': existing_research.id
                },
                status=status.HTTP_200_OK
            )

        # Generate research data (simplified for MVP)
        research_data = {
            'company_id': company_id,
            'title': f"Research Report: {company.name}",
            'overview': f"Comprehensive research analysis for {company.name}, a leading company in the {company.industry} industry.",
            'culture_analysis': f"Company culture analysis for {company.name} indicates a focus on innovation, collaboration, and employee growth.",
            'recent_news': f"Recent developments at {company.name} include expansion plans and new product launches.",
            'financial_highlights': f"Financial performance shows steady growth and strong market position.",
            'growth_prospects': f"Future outlook for {company.name} remains positive with opportunities in emerging markets.",
            'confidence_score': 0.85
        }

        serializer = CompanyResearchSerializer(
            data=research_data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            research = serializer.save()
            return Response(
                CompanyResearchSerializer(research).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InterviewPrepListView(generics.ListCreateAPIView):
    """
    List all interview preparations for authenticated user.
    """
    serializer_class = InterviewPreparationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['preparation_status']
    search_fields = ['position_title', 'company_research__company__name']

    def get_queryset(self):
        return InterviewPreparation.objects.filter(
            company_research__user=self.request.user
        ).select_related('company_research__company')


class InterviewPrepDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a specific interview preparation.
    """
    serializer_class = InterviewPreparationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return InterviewPreparation.objects.filter(
            company_research__user=self.request.user
        ).select_related('company_research__company')


class GenerateInterviewPrepView(APIView):
    """
    Generate interview preparation materials for a company research.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        research_id = request.data.get('research_id')
        position_title = request.data.get('position_title', '')

        if not research_id:
            return Response(
                {'error': 'research_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            research = CompanyResearch.objects.get(
                id=research_id, 
                user=request.user
            )
        except CompanyResearch.DoesNotExist:
            return Response(
                {'error': 'Company research not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Generate interview preparation data
        prep_data = {
            'company_research': research.id,
            'position_title': position_title,
            'key_talking_points': f"Key points to discuss when interviewing at {research.company.name}",
            'company_specific_prep': f"Specific preparation notes for {research.company.name}",
            'technical_focus_areas': f"Technical areas to focus on for {position_title} role",
            'behavioral_scenarios': f"Common behavioral scenarios at {research.company.name}",
        }

        serializer = InterviewPreparationSerializer(data=prep_data)
        
        if serializer.is_valid():
            prep = serializer.save()
            return Response(
                InterviewPreparationSerializer(prep).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyInsightsView(generics.ListCreateAPIView):
    """
    List company insights or create new insights.
    """
    serializer_class = CompanyInsightSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['insight_type', 'company']
    search_fields = ['title', 'content', 'company__name']

    def get_queryset(self):
        return CompanyInsight.objects.all().select_related('company')


class CompanyInsightDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a specific company insight.
    """
    serializer_class = CompanyInsightSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CompanyInsight.objects.all().select_related('company')


class InterviewQuestionListView(generics.ListCreateAPIView):
    """
    List interview questions with filtering options.
    """
    serializer_class = InterviewQuestionListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['question_type', 'difficulty', 'company']
    search_fields = ['question_text', 'position_type']

    def get_queryset(self):
        return InterviewQuestion.objects.all().select_related('company')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return InterviewQuestionSerializer
        return InterviewQuestionListSerializer


class InterviewQuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a specific interview question.
    """
    serializer_class = InterviewQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = InterviewQuestion.objects.all().select_related('company')


class GenerateInterviewQuestionsView(APIView):
    """
    Generate AI-powered interview questions for a specific role/company.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        question_type = request.data.get('question_type', 'general')
        difficulty = request.data.get('difficulty', 'medium')
        company_id = request.data.get('company_id')
        position_type = request.data.get('position_type', '')

        # Generate sample questions (would be AI-powered in production)
        sample_questions = {
            'general': [
                "Tell me about yourself and your career journey.",
                "Why are you interested in this position?",
                "What are your greatest strengths and weaknesses?"
            ],
            'technical': [
                "Explain your approach to solving complex technical problems.",
                "How do you stay updated with new technologies?",
                "Describe a challenging technical project you've worked on."
            ],
            'behavioral': [
                "Tell me about a time you had to work under pressure.",
                "Describe a situation where you had to collaborate with a difficult team member.",
                "Give an example of when you had to learn something new quickly."
            ]
        }

        questions_data = []
        for question_text in sample_questions.get(question_type, []):
            question_data = {
                'question_text': question_text,
                'question_type': question_type,
                'difficulty': difficulty,
                'position_type': position_type
            }
            if company_id:
                question_data['company_id'] = company_id

            questions_data.append(question_data)

        serializer = InterviewQuestionSerializer(data=questions_data, many=True)
        
        if serializer.is_valid():
            questions = serializer.save()
            return Response(
                InterviewQuestionSerializer(questions, many=True).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PracticeSessionListView(generics.ListCreateAPIView):
    """
    List practice sessions for authenticated user.
    """
    serializer_class = PracticeSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['session_type', 'completion_status', 'company']
    search_fields = ['notes']

    def get_queryset(self):
        return PracticeSession.objects.filter(user=self.request.user).select_related('company')


class PracticeSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a specific practice session.
    """
    serializer_class = PracticeSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PracticeSession.objects.filter(user=self.request.user).select_related('company')


class StartPracticeSessionView(APIView):
    """
    Start a new practice session with initial setup.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        session_type = request.data.get('session_type')
        company_id = request.data.get('company_id')

        if not session_type:
            return Response(
                {'error': 'session_type is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        session_data = {
            'session_type': session_type,
            'completion_status': 'in_progress',
            'session_data': {
                'start_time': timezone.now().isoformat(),
                'questions': [],
                'responses': []
            }
        }

        if company_id:
            session_data['company_id'] = company_id

        serializer = PracticeSessionSerializer(
            data=session_data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            session = serializer.save()
            return Response(
                PracticeSessionSerializer(session).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyNewsView(generics.ListCreateAPIView):
    """
    List company news articles.
    """
    serializer_class = CompanyNewsSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['company', 'source']
    search_fields = ['title', 'summary', 'company__name']

    def get_queryset(self):
        return CompanyNews.objects.all().select_related('company')


class CompanyNewsDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific news article.
    """
    serializer_class = CompanyNewsSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CompanyNews.objects.all().select_related('company')


class SavedResearchView(generics.ListAPIView):
    """
    List saved research for authenticated user.
    """
    serializer_class = SavedResearchSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return SavedResearch.objects.filter(user=self.request.user).select_related(
            'company_research__company'
        )


class SaveResearchView(APIView):
    """
    Save a company research item.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            research = CompanyResearch.objects.get(id=pk, user=request.user)
        except CompanyResearch.DoesNotExist:
            return Response(
                {'error': 'Company research not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        saved_research, created = SavedResearch.objects.get_or_create(
            user=request.user,
            company_research=research,
            defaults={
                'notes': request.data.get('notes', ''),
                'tags': request.data.get('tags', [])
            }
        )

        # Also mark the research as saved
        research.is_saved = True
        research.save(update_fields=['is_saved'])

        if created:
            return Response(
                SavedResearchSerializer(saved_research).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': 'Research already saved'},
                status=status.HTTP_200_OK
            )


class UnsaveResearchView(APIView):
    """
    Unsave a company research item.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            research = CompanyResearch.objects.get(id=pk, user=request.user)
            saved_research = SavedResearch.objects.get(
                user=request.user,
                company_research=research
            )
            saved_research.delete()
            
            # Mark research as unsaved
            research.is_saved = False
            research.save(update_fields=['is_saved'])
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (CompanyResearch.DoesNotExist, SavedResearch.DoesNotExist):
            return Response(
                {'error': 'Saved research not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
