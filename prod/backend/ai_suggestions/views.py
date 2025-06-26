"""
AI Suggestions app views for Epic 3: AI-Powered Resume Optimization and Smart Recommendations.
"""

import time
import json
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from core.permissions import AuthenticatedAndActive
from .models import (
    SuggestionTemplate, AISuggestion, SuggestionFeedback, JobRecommendation,
    ResumeJobMatch, AILearningData, SuggestionBatch
)
from .serializers import (
    SuggestionTemplateSerializer, AISuggestionSerializer, AISuggestionCreateSerializer,
    SuggestionFeedbackSerializer, JobRecommendationSerializer, ResumeJobMatchSerializer,
    SuggestionBatchSerializer, AISuggestionAnalyticsSerializer, JobMatchAnalysisSerializer,
    ResumeOptimizationRequestSerializer, SuggestionActionSerializer, BulkSuggestionActionSerializer,
    SuggestionSearchSerializer
)


class AISuggestionPagination(PageNumberPagination):
    """Custom pagination for AI suggestions."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# Suggestion Template Views
class SuggestionTemplateListView(generics.ListAPIView):
    """List all available suggestion templates."""
    serializer_class = SuggestionTemplateSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'suggestion_type']
    
    def get_queryset(self):
        queryset = SuggestionTemplate.objects.filter(is_active=True)
        suggestion_type = self.request.query_params.get('suggestion_type')
        if suggestion_type:
            queryset = queryset.filter(suggestion_type=suggestion_type)
        return queryset.order_by('-usage_count', 'name')


class SuggestionTemplateDetailView(generics.RetrieveAPIView):
    """Get detailed information about a specific template."""
    queryset = SuggestionTemplate.objects.filter(is_active=True)
    serializer_class = SuggestionTemplateSerializer
    permission_classes = [permissions.AllowAny]


# AI Suggestions CRUD Views
class AISuggestionListView(generics.ListAPIView):
    """List user's AI suggestions with filtering and search."""
    serializer_class = AISuggestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = AISuggestionPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'confidence_score', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = AISuggestion.objects.filter(user=self.request.user).select_related(
            'template'
        ).prefetch_related('feedback')
        
        # Apply custom filters
        queryset = self._apply_filters(queryset)
        return queryset
    
    def _apply_filters(self, queryset):
        """Apply custom filters to queryset."""
        # Suggestion type filter
        suggestion_type = self.request.query_params.get('suggestion_type')
        if suggestion_type:
            queryset = queryset.filter(suggestion_type=suggestion_type)
        
        # Status filter
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Priority filter
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Confidence score range
        confidence_min = self.request.query_params.get('confidence_min')
        if confidence_min:
            try:
                queryset = queryset.filter(confidence_score__gte=float(confidence_min))
            except ValueError:
                pass
        
        confidence_max = self.request.query_params.get('confidence_max')
        if confidence_max:
            try:
                queryset = queryset.filter(confidence_score__lte=float(confidence_max))
            except ValueError:
                pass
        
        # Target job/resume filters
        target_job_id = self.request.query_params.get('target_job_id')
        if target_job_id:
            queryset = queryset.filter(target_job_id=target_job_id)
        
        target_resume_id = self.request.query_params.get('target_resume_id')
        if target_resume_id:
            queryset = queryset.filter(target_resume_id=target_resume_id)
        
        # Date range filters
        created_after = self.request.query_params.get('created_after')
        if created_after:
            try:
                date = datetime.fromisoformat(created_after.replace('Z', '+00:00'))
                queryset = queryset.filter(created_at__gte=date)
            except ValueError:
                pass
        
        created_before = self.request.query_params.get('created_before')
        if created_before:
            try:
                date = datetime.fromisoformat(created_before.replace('Z', '+00:00'))
                queryset = queryset.filter(created_at__lte=date)
            except ValueError:
                pass
        
        # Has feedback filter
        has_feedback = self.request.query_params.get('has_feedback')
        if has_feedback:
            if has_feedback.lower() == 'true':
                queryset = queryset.filter(feedback__isnull=False)
            else:
                queryset = queryset.filter(feedback__isnull=True)
        
        return queryset.distinct()


class AISuggestionDetailView(generics.RetrieveAPIView):
    """Get detailed information about a specific AI suggestion."""
    serializer_class = AISuggestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AISuggestion.objects.filter(user=self.request.user).select_related(
            'template'
        ).prefetch_related('feedback')
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Mark as viewed
        instance.mark_viewed()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class AISuggestionCreateView(generics.CreateAPIView):
    """Create a new AI suggestion (typically used by AI services)."""
    serializer_class = AISuggestionCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AISuggestionSearchView(APIView):
    """Advanced search for AI suggestions."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Search suggestions with advanced filters."""
        serializer = SuggestionSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        queryset = AISuggestion.objects.filter(user=request.user).select_related(
            'template'
        ).prefetch_related('feedback')
        
        # Apply search filters
        queryset = self._apply_search_filters(queryset, data)
        
        # Paginate results
        paginator = AISuggestionPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = AISuggestionSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        
        serializer = AISuggestionSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    def _apply_search_filters(self, queryset, data):
        """Apply search filters to queryset."""
        # Basic filters
        for field in ['suggestion_type', 'status', 'priority', 'target_job_id', 'target_resume_id']:
            value = data.get(field)
            if value:
                queryset = queryset.filter(**{field: value})
        
        # Confidence range
        confidence_min = data.get('confidence_min')
        confidence_max = data.get('confidence_max')
        if confidence_min is not None:
            queryset = queryset.filter(confidence_score__gte=confidence_min)
        if confidence_max is not None:
            queryset = queryset.filter(confidence_score__lte=confidence_max)
        
        # Date range
        created_after = data.get('created_after')
        created_before = data.get('created_before')
        if created_after:
            queryset = queryset.filter(created_at__gte=created_after)
        if created_before:
            queryset = queryset.filter(created_at__lte=created_before)
        
        # Has feedback
        has_feedback = data.get('has_feedback')
        if has_feedback is not None:
            if has_feedback:
                queryset = queryset.filter(feedback__isnull=False)
            else:
                queryset = queryset.filter(feedback__isnull=True)
        
        # Text search
        search = data.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(suggestion_content__icontains=search)
            )
        
        return queryset.distinct()


# Suggestion Actions
class SuggestionActionView(APIView):
    """Handle suggestion actions (accept/reject/partially accept)."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """Process suggestion action."""
        try:
            suggestion = AISuggestion.objects.get(id=pk, user=request.user)
        except AISuggestion.DoesNotExist:
            return Response(
                {"error": "Suggestion not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = SuggestionActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        action = data['action']
        notes = data.get('notes', '')
        implementation_details = data.get('implementation_details')
        
        # Update suggestion status
        if action == 'accept':
            suggestion.status = 'accepted'
        elif action == 'reject':
            suggestion.status = 'rejected'
        elif action == 'partially_accept':
            suggestion.status = 'partially_accepted'
        
        suggestion.mark_acted_on()
        suggestion.save()
        
        # Create feedback entry
        SuggestionFeedback.objects.create(
            suggestion=suggestion,
            user=request.user,
            feedback_type='helpful' if action in ['accept', 'partially_accept'] else 'not_helpful',
            rating=5 if action == 'accept' else 3 if action == 'partially_accept' else 1,
            comments=notes,
            implemented=action in ['accept', 'partially_accept'],
            implementation_notes=json.dumps(implementation_details) if implementation_details else ''
        )
        
        return Response({
            'message': f'Suggestion {action}ed successfully',
            'status': suggestion.status
        })


class BulkSuggestionActionView(APIView):
    """Handle bulk suggestion actions."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Process bulk suggestion actions."""
        serializer = BulkSuggestionActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        suggestion_ids = data['suggestion_ids']
        action = data['action']
        notes = data.get('notes', '')
        
        # Get suggestions
        suggestions = AISuggestion.objects.filter(
            id__in=suggestion_ids,
            user=request.user
        )
        
        if not suggestions.exists():
            return Response(
                {"error": "No valid suggestions found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        updated_count = 0
        for suggestion in suggestions:
            if action == 'accept':
                suggestion.status = 'accepted'
                feedback_type = 'helpful'
                rating = 5
                implemented = True
            elif action == 'reject':
                suggestion.status = 'rejected'
                feedback_type = 'not_helpful'
                rating = 1
                implemented = False
            elif action == 'mark_viewed':
                suggestion.mark_viewed()
                updated_count += 1
                continue
            
            suggestion.mark_acted_on()
            suggestion.save()
            
            # Create feedback
            SuggestionFeedback.objects.get_or_create(
                suggestion=suggestion,
                user=request.user,
                defaults={
                    'feedback_type': feedback_type,
                    'rating': rating,
                    'comments': notes,
                    'implemented': implemented
                }
            )
            updated_count += 1
        
        return Response({
            'message': f'{updated_count} suggestions processed successfully',
            'action': action,
            'processed_count': updated_count
        })


# Resume Optimization Views
class ResumeOptimizationView(APIView):
    """Generate AI suggestions for resume optimization."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Generate optimization suggestions for a resume."""
        serializer = ResumeOptimizationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        resume_id = data['resume_id']
        target_job_id = data.get('target_job_id')
        optimization_focus = data.get('optimization_focus', ['keywords', 'content'])
        priority = data.get('priority', 'medium')
        
        # Simulate AI processing time
        start_time = time.time()
        
        # Create batch processing record
        batch = SuggestionBatch.objects.create(
            user=request.user,
            batch_type='resume_optimization',
            status='processing'
        )
        batch.started_at = timezone.now()
        batch.save()
        
        try:
            suggestions_created = []
            
            # Generate different types of suggestions based on focus areas
            for focus in optimization_focus:
                suggestion_data = self._generate_suggestion_for_focus(
                    focus, resume_id, target_job_id, priority
                )
                
                suggestion = AISuggestion.objects.create(
                    user=request.user,
                    suggestion_type=suggestion_data['type'],
                    title=suggestion_data['title'],
                    description=suggestion_data['description'],
                    suggestion_content=suggestion_data['content'],
                    ai_model='gpt-3.5-turbo',
                    confidence_score=suggestion_data['confidence'],
                    processing_time=time.time() - start_time,
                    target_resume_id=resume_id,
                    target_job_id=target_job_id,
                    priority=priority,
                    expires_at=timezone.now() + timedelta(days=30)
                )
                suggestions_created.append(suggestion)
            
            # Update batch status
            batch.status = 'completed'
            batch.completed_at = timezone.now()
            batch.total_suggestions = len(suggestions_created)
            batch.successful_suggestions = len(suggestions_created)
            batch.processing_time = time.time() - start_time
            batch.save()
            
            # Serialize suggestions
            serializer = AISuggestionSerializer(
                suggestions_created, many=True, context={'request': request}
            )
            
            return Response({
                'message': f'{len(suggestions_created)} optimization suggestions generated',
                'batch_id': str(batch.id),
                'suggestions': serializer.data,
                'processing_time': batch.processing_time
            })
            
        except Exception as e:
            # Update batch status on error
            batch.status = 'failed'
            batch.error_message = str(e)
            batch.completed_at = timezone.now()
            batch.processing_time = time.time() - start_time
            batch.save()
            
            return Response(
                {"error": "Failed to generate suggestions", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_suggestion_for_focus(self, focus, resume_id, target_job_id, priority):
        """Generate suggestion based on optimization focus."""
        if focus == 'keywords':
            return {
                'type': 'keyword_optimization',
                'title': 'Optimize Resume Keywords',
                'description': 'Add industry-specific keywords to improve ATS compatibility.',
                'content': {
                    'suggestion': 'Add these relevant keywords to your resume',
                    'reasoning': 'These keywords are commonly found in similar job postings',
                    'keywords': ['Python', 'Django', 'REST API', 'PostgreSQL', 'Docker'],
                    'sections_to_update': ['Skills', 'Experience', 'Summary']
                },
                'confidence': 0.85
            }
        elif focus == 'content':
            return {
                'type': 'content_enhancement',
                'title': 'Enhance Resume Content',
                'description': 'Improve content structure and impact statements.',
                'content': {
                    'suggestion': 'Rewrite experience bullets with quantified achievements',
                    'reasoning': 'Quantified achievements demonstrate measurable impact',
                    'improvements': [
                        'Use action verbs to start bullet points',
                        'Include specific metrics and numbers',
                        'Focus on achievements rather than responsibilities'
                    ]
                },
                'confidence': 0.78
            }
        elif focus == 'formatting':
            return {
                'type': 'format_suggestion',
                'title': 'Improve Resume Format',
                'description': 'Optimize layout and formatting for better readability.',
                'content': {
                    'suggestion': 'Adjust formatting for better visual hierarchy',
                    'reasoning': 'Well-formatted resumes are easier to scan and read',
                    'changes': [
                        'Use consistent font sizes and styles',
                        'Improve whitespace and margins',
                        'Organize sections logically'
                    ]
                },
                'confidence': 0.72
            }
        elif focus == 'skills':
            return {
                'type': 'skill_highlight',
                'title': 'Highlight Relevant Skills',
                'description': 'Emphasize skills that match job requirements.',
                'content': {
                    'suggestion': 'Promote these skills based on job matching',
                    'reasoning': 'These skills are highly valued for target positions',
                    'skills_to_highlight': ['Leadership', 'Project Management', 'Data Analysis'],
                    'skills_to_add': ['Agile Methodology', 'Cloud Computing']
                },
                'confidence': 0.80
            }
        else:  # experience
            return {
                'type': 'experience_optimization',
                'title': 'Optimize Experience Section',
                'description': 'Enhance work experience descriptions and relevance.',
                'content': {
                    'suggestion': 'Reorganize and enhance experience descriptions',
                    'reasoning': 'Better structured experience section shows career progression',
                    'improvements': [
                        'Lead with most relevant experiences',
                        'Use industry-specific terminology',
                        'Highlight transferable skills'
                    ]
                },
                'confidence': 0.76
            }


# Job Matching Views
class JobMatchAnalysisView(APIView):
    """Analyze how well a resume matches a job posting."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Analyze resume-job match."""
        serializer = JobMatchAnalysisSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        resume_id = data['resume_id']
        job_id = data['job_id']
        analysis_type = data.get('analysis_type', 'basic')
        include_suggestions = data.get('include_suggestions', True)
        
        start_time = time.time()
        
        # Check if analysis already exists
        existing_match = ResumeJobMatch.objects.filter(
            user=request.user,
            resume_id=resume_id,
            job_id=job_id
        ).first()
        
        if existing_match:
            # Update existing analysis
            match_analysis = existing_match
        else:
            # Create new analysis with mock data
            match_analysis = ResumeJobMatch.objects.create(
                user=request.user,
                resume_id=resume_id,
                job_id=job_id,
                overall_match_score=0.75,
                skills_match_score=0.80,
                experience_match_score=0.70,
                keyword_match_score=0.72,
                matching_keywords=['Python', 'Django', 'REST API', 'PostgreSQL'],
                missing_keywords=['Docker', 'Kubernetes', 'Redis'],
                suggested_improvements=[
                    'Add Docker experience to skills section',
                    'Include cloud deployment projects',
                    'Emphasize API development experience'
                ],
                strength_areas=['Technical Skills', 'Backend Development', 'Database Design'],
                weakness_areas=['DevOps', 'Frontend Development', 'Cloud Services'],
                ai_model='gpt-3.5-turbo',
                analysis_summary='Strong technical match with room for improvement in DevOps skills.',
                processing_time=time.time() - start_time
            )
        
        response_data = {
            'match_analysis': ResumeJobMatchSerializer(match_analysis).data,
            'processing_time': match_analysis.processing_time
        }
        
        # Generate suggestions if requested
        if include_suggestions:
            suggestions = self._generate_match_improvement_suggestions(
                match_analysis, analysis_type
            )
            response_data['improvement_suggestions'] = AISuggestionSerializer(
                suggestions, many=True, context={'request': request}
            ).data
        
        return Response(response_data)
    
    def _generate_match_improvement_suggestions(self, match_analysis, analysis_type):
        """Generate suggestions to improve job match score."""
        suggestions = []
        
        # Generate suggestions based on missing keywords
        if match_analysis.missing_keywords:
            suggestion = AISuggestion.objects.create(
                user=match_analysis.user,
                suggestion_type='keyword_optimization',
                title='Add Missing Keywords',
                description='Include these keywords to improve job match score.',
                suggestion_content={
                    'suggestion': 'Add the following keywords to your resume',
                    'reasoning': 'These keywords are required for the target job but missing from your resume',
                    'keywords': match_analysis.missing_keywords,
                    'expected_improvement': '15-20% increase in match score'
                },
                ai_model='gpt-3.5-turbo',
                confidence_score=0.85,
                target_resume_id=match_analysis.resume_id,
                target_job_id=match_analysis.job_id,
                priority='high',
                expires_at=timezone.now() + timedelta(days=14)
            )
            suggestions.append(suggestion)
        
        # Generate suggestions for weakness areas
        for weakness in match_analysis.weakness_areas[:2]:  # Limit to top 2
            suggestion = AISuggestion.objects.create(
                user=match_analysis.user,
                suggestion_type='skill_highlight',
                title=f'Strengthen {weakness} Skills',
                description=f'Improve your {weakness.lower()} profile to better match job requirements.',
                suggestion_content={
                    'suggestion': f'Enhance your {weakness.lower()} experience presentation',
                    'reasoning': f'{weakness} was identified as a weak area in your profile',
                    'focus_area': weakness,
                    'recommended_actions': [
                        f'Add relevant {weakness.lower()} projects',
                        f'Include {weakness.lower()} tools and technologies',
                        f'Quantify {weakness.lower()} achievements'
                    ]
                },
                ai_model='gpt-3.5-turbo',
                confidence_score=0.75,
                target_resume_id=match_analysis.resume_id,
                target_job_id=match_analysis.job_id,
                priority='medium',
                expires_at=timezone.now() + timedelta(days=21)
            )
            suggestions.append(suggestion)
        
        return suggestions


# Job Recommendations Views
class JobRecommendationListView(generics.ListAPIView):
    """List AI-generated job recommendations for the user."""
    serializer_class = JobRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = AISuggestionPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['match_score', 'created_at']
    ordering = ['-match_score', '-created_at']
    
    def get_queryset(self):
        return JobRecommendation.objects.filter(
            user=self.request.user,
            dismissed=False
        )


class JobRecommendationDetailView(generics.RetrieveAPIView):
    """Get detailed information about a job recommendation."""
    serializer_class = JobRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return JobRecommendation.objects.filter(user=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Mark as viewed
        instance.mark_viewed()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# Feedback Views
class SuggestionFeedbackCreateView(generics.CreateAPIView):
    """Create feedback for a suggestion."""
    serializer_class = SuggestionFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        suggestion_id = self.kwargs.get('suggestion_id')
        suggestion = get_object_or_404(
            AISuggestion, id=suggestion_id, user=self.request.user
        )
        serializer.save(suggestion=suggestion, user=self.request.user)


class SuggestionFeedbackListView(generics.ListAPIView):
    """List feedback for a suggestion."""
    serializer_class = SuggestionFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        suggestion_id = self.kwargs.get('suggestion_id')
        suggestion = get_object_or_404(
            AISuggestion, id=suggestion_id, user=self.request.user
        )
        return suggestion.feedback.all()


# Analytics Views
class AISuggestionsAnalyticsView(APIView):
    """CBV version of ai_suggestions_analytics (was FBV)"""
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        user_suggestions = AISuggestion.objects.filter(user=request.user)
        total_suggestions = user_suggestions.count()
        suggestions_by_type = dict(
            user_suggestions.values('suggestion_type').annotate(
                count=Count('id')
            ).values_list('suggestion_type', 'count')
        )
        suggestions_by_status = dict(
            user_suggestions.values('status').annotate(
                count=Count('id')
            ).values_list('status', 'count')
        )
        avg_confidence = user_suggestions.aggregate(
            avg=Avg('confidence_score')
        )['avg'] or 0.0
        avg_processing_time = user_suggestions.filter(
            processing_time__isnull=False
        ).aggregate(avg=Avg('processing_time'))['avg'] or 0.0
        viewed_suggestions = user_suggestions.filter(viewed_at__isnull=False).count()
        acted_suggestions = user_suggestions.filter(acted_on_at__isnull=False).count()
        user_engagement_rate = (viewed_suggestions / total_suggestions) if total_suggestions > 0 else 0.0
        implementation_rate = (acted_suggestions / total_suggestions) if total_suggestions > 0 else 0.0
        recent_suggestions = user_suggestions.order_by('-created_at')[:10]
        recent_suggestions_data = AISuggestionSerializer(
            recent_suggestions, many=True, context={'request': request}
        ).data
        analytics_data = {
            'total_suggestions': total_suggestions,
            'suggestions_by_type': suggestions_by_type,
            'suggestions_by_status': suggestions_by_status,
            'average_confidence_score': round(avg_confidence, 2),
            'average_processing_time': round(avg_processing_time, 2),
            'user_engagement_rate': round(user_engagement_rate, 2),
            'implementation_rate': round(implementation_rate, 2),
            'recent_suggestions': recent_suggestions_data
        }
        serializer = AISuggestionAnalyticsSerializer(data=analytics_data)
        if serializer.is_valid():
            return Response(serializer.data)
        else:
            return Response(analytics_data)


# Batch Processing Views
class SuggestionBatchListView(generics.ListAPIView):
    """List user's suggestion batches."""
    serializer_class = SuggestionBatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['-created_at']
    
    def get_queryset(self):
        return SuggestionBatch.objects.filter(user=self.request.user)


class SuggestionBatchDetailView(generics.RetrieveAPIView):
    """Get details of a suggestion batch."""
    serializer_class = SuggestionBatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SuggestionBatch.objects.filter(user=self.request.user)


# Utility Functions
class GenerateDailySuggestionsView(APIView):
    """CBV version of generate_daily_suggestions (was FBV)"""
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        user = request.user
        batch = SuggestionBatch.objects.create(
            user=user,
            batch_type='daily_suggestions',
            status='processing'
        )
        batch.started_at = timezone.now()
        batch.save()
        try:
            suggestions_created = []
            start_time = time.time()
            suggestion_types = [
                ('resume_improvement', 'Daily Resume Tip'),
                ('job_match', 'New Job Matches'),
                ('skill_highlight', 'Skill Enhancement')
            ]
            for suggestion_type, title_prefix in suggestion_types:
                suggestion = AISuggestion.objects.create(
                    user=user,
                    suggestion_type=suggestion_type,
                    title=f'{title_prefix} - {timezone.now().strftime("%Y-%m-%d")}',
                    description=f'Daily {suggestion_type.replace("_", " ")} suggestion',
                    suggestion_content={
                        'suggestion': f'Daily tip for {suggestion_type.replace("_", " ")}',
                        'reasoning': 'Generated as part of daily suggestions',
                        'daily_tip': True
                    },
                    ai_model='gpt-3.5-turbo',
                    confidence_score=0.7,
                    processing_time=time.time() - start_time,
                    priority='low',
                    expires_at=timezone.now() + timedelta(days=7)
                )
                suggestions_created.append(suggestion)
            batch.status = 'completed'
            batch.completed_at = timezone.now()
            batch.total_suggestions = len(suggestions_created)
            batch.successful_suggestions = len(suggestions_created)
            batch.processing_time = time.time() - start_time
            batch.save()
            return Response({
                'message': f'{len(suggestions_created)} daily suggestions generated',
                'batch_id': str(batch.id),
                'suggestions_count': len(suggestions_created)
            })
        except Exception as e:
            batch.status = 'failed'
            batch.error_message = str(e)
            batch.completed_at = timezone.now()
            batch.save()
            return Response(
                {"error": "Failed to generate daily suggestions", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DismissJobRecommendationView(APIView):
    """CBV version of dismiss_job_recommendation (was FBV)"""
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, recommendation_id):
        try:
            recommendation = JobRecommendation.objects.get(
                id=recommendation_id, user=request.user
            )
            recommendation.dismissed = True
            recommendation.save()
            return Response({'message': 'Job recommendation dismissed'})
        except JobRecommendation.DoesNotExist:
            return Response(
                {"error": "Job recommendation not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class SaveJobRecommendationView(APIView):
    """CBV version of save_job_recommendation (was FBV)"""
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, recommendation_id):
        try:
            recommendation = JobRecommendation.objects.get(
                id=recommendation_id, user=request.user
            )
            recommendation.saved = True
            recommendation.save()
            return Response({'message': 'Job recommendation saved'})
        except JobRecommendation.DoesNotExist:
            return Response(
                {"error": "Job recommendation not found"},
                status=status.HTTP_404_NOT_FOUND
            )