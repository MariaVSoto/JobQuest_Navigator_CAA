from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Resume, JobDescription, Suggestion, Feedback
from .serializers import (
    ResumeSerializer,
    JobDescriptionSerializer,
    SuggestionSerializer,
    FeedbackSerializer
)
from .services.ai_service import AIService

class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

class JobDescriptionViewSet(viewsets.ModelViewSet):
    queryset = JobDescription.objects.all()
    serializer_class = JobDescriptionSerializer

class SuggestionViewSet(viewsets.ModelViewSet):
    queryset = Suggestion.objects.all()
    serializer_class = SuggestionSerializer

    @action(detail=False, methods=['post'])
    def analyze(self, request):
        resume_id = request.data.get('resumeId')
        job_id = request.data.get('jobId')

        if not resume_id or not job_id:
            return Response(
                {'error': 'resumeId and jobId are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        resume = get_object_or_404(Resume, id=resume_id)
        job = get_object_or_404(JobDescription, id=job_id)

        ai_service = AIService()
        suggestions = ai_service.generate_suggestions(resume.content, job.description)

        suggestion = Suggestion.objects.create(
            resume=resume,
            job=job,
            content=suggestions
        )

        return Response(SuggestionSerializer(suggestion).data)

    @action(detail=True, methods=['get'])
    def feedback(self, request, pk=None):
        suggestion = self.get_object()
        feedback = Feedback.objects.filter(suggestion=suggestion)
        return Response(FeedbackSerializer(feedback, many=True).data)

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def perform_create(self, serializer):
        suggestion_id = self.request.data.get('suggestionId')
        suggestion = get_object_or_404(Suggestion, id=suggestion_id)
        serializer.save(
            user=self.request.user,
            suggestion=suggestion
        ) 