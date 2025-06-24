"""
Simplified AI Suggestions views for Phase 2 MVP.
Focuses on core functionality with reduced complexity.
"""

import time
import json
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from .models import AISuggestion, SuggestionFeedback, JobRecommendation


class SimplePagination(PageNumberPagination):
    """Simple pagination for AI suggestions."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class SimpleAISuggestionSerializer:
    """Simplified serializer for AI suggestions."""
    
    @staticmethod
    def serialize(suggestion):
        return {
            'id': str(suggestion.id),
            'type': suggestion.suggestion_type,
            'title': suggestion.title,
            'description': suggestion.description,
            'content': suggestion.suggestion_content,
            'confidence': suggestion.confidence_score,
            'status': suggestion.status,
            'priority': suggestion.priority,
            'created_at': suggestion.created_at.isoformat(),
            'viewed': suggestion.viewed_at is not None,
            'acted_on': suggestion.acted_on_at is not None,
        }
    
    @staticmethod
    def serialize_many(suggestions):
        return [SimpleAISuggestionSerializer.serialize(s) for s in suggestions]


class SimpleJobRecommendationSerializer:
    """Simplified serializer for job recommendations."""
    
    @staticmethod
    def serialize(recommendation):
        return {
            'id': str(recommendation.id),
            'job_id': str(recommendation.job_id),
            'job_title': recommendation.job_title,
            'company_name': recommendation.company_name,
            'match_score': recommendation.match_score,
            'reason': recommendation.recommendation_reason,
            'matching_skills': recommendation.matching_skills,
            'missing_skills': recommendation.missing_skills,
            'viewed': recommendation.viewed,
            'saved': recommendation.saved,
            'created_at': recommendation.created_at.isoformat(),
        }
    
    @staticmethod
    def serialize_many(recommendations):
        return [SimpleJobRecommendationSerializer.serialize(r) for r in recommendations]


# Simplified Views

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_ai_suggestions(request):
    """Get user's AI suggestions with simple filtering."""
    user = request.user
    
    # Get query parameters
    suggestion_type = request.GET.get('type')
    status_filter = request.GET.get('status')
    limit = min(int(request.GET.get('limit', 10)), 50)
    
    # Build query
    queryset = AISuggestion.objects.filter(user=user)
    
    if suggestion_type:
        queryset = queryset.filter(suggestion_type=suggestion_type)
    
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    # Get suggestions
    suggestions = queryset.order_by('-created_at')[:limit]
    
    return Response({
        'suggestions': SimpleAISuggestionSerializer.serialize_many(suggestions),
        'total_count': queryset.count()
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_resume_suggestions(request):
    """Generate simple AI suggestions for resume improvement."""
    user = request.user
    resume_id = request.data.get('resume_id')
    
    if not resume_id:
        return Response(
            {'error': 'resume_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Simple suggestion generation
    suggestions_data = [
        {
            'type': 'keyword_optimization',
            'title': 'Add Relevant Keywords',
            'description': 'Include industry-specific keywords to improve ATS compatibility.',
            'content': {
                'suggestion': 'Add these keywords to your resume',
                'keywords': ['Python', 'Django', 'REST API', 'PostgreSQL', 'React'],
                'sections': ['Skills', 'Experience']
            },
            'confidence': 0.85,
            'priority': 'high'
        },
        {
            'type': 'content_enhancement',
            'title': 'Quantify Achievements',
            'description': 'Add numbers and metrics to your accomplishments.',
            'content': {
                'suggestion': 'Replace vague descriptions with quantified achievements',
                'examples': [
                    'Improved system performance by 25%',
                    'Managed a team of 5 developers',
                    'Reduced bug reports by 40%'
                ]
            },
            'confidence': 0.78,
            'priority': 'medium'
        },
        {
            'type': 'skill_highlight',
            'title': 'Highlight Technical Skills',
            'description': 'Emphasize your most relevant technical abilities.',
            'content': {
                'suggestion': 'Move technical skills to a prominent section',
                'skills_to_highlight': ['Programming Languages', 'Frameworks', 'Databases'],
                'recommended_format': 'Skills matrix or bullet points'
            },
            'confidence': 0.72,
            'priority': 'medium'
        }
    ]
    
    # Create suggestions
    created_suggestions = []
    for data in suggestions_data:
        suggestion = AISuggestion.objects.create(
            user=user,
            suggestion_type=data['type'],
            title=data['title'],
            description=data['description'],
            suggestion_content=data['content'],
            ai_model='gpt-3.5-turbo',
            confidence_score=data['confidence'],
            target_resume_id=resume_id,
            priority=data['priority'],
            expires_at=timezone.now() + timedelta(days=30)
        )
        created_suggestions.append(suggestion)
    
    return Response({
        'message': f'{len(created_suggestions)} suggestions generated',
        'suggestions': SimpleAISuggestionSerializer.serialize_many(created_suggestions)
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_job_recommendations(request):
    """Generate simple job recommendations for user."""
    user = request.user
    
    # Mock job recommendations based on user profile
    recommendations_data = [
        {
            'job_id': '550e8400-e29b-41d4-a716-446655440001',
            'job_title': 'Senior Software Engineer',
            'company_name': 'TechCorp Solutions',
            'match_score': 0.85,
            'reason': 'Strong match based on your Python and Django experience',
            'matching_skills': ['Python', 'Django', 'REST API', 'PostgreSQL'],
            'missing_skills': ['Docker', 'Kubernetes']
        },
        {
            'job_id': '550e8400-e29b-41d4-a716-446655440002',
            'job_title': 'Full Stack Developer',
            'company_name': 'Innovation Labs',
            'match_score': 0.78,
            'reason': 'Good fit for your full-stack development skills',
            'matching_skills': ['JavaScript', 'React', 'Node.js', 'MongoDB'],
            'missing_skills': ['Vue.js', 'TypeScript']
        },
        {
            'job_id': '550e8400-e29b-41d4-a716-446655440003',
            'job_title': 'Backend Developer',
            'company_name': 'DataFlow Inc',
            'match_score': 0.72,
            'reason': 'Matches your backend development expertise',
            'matching_skills': ['Python', 'FastAPI', 'SQL', 'Redis'],
            'missing_skills': ['Microservices', 'AWS']
        }
    ]
    
    # Create recommendations (avoid duplicates)
    created_recommendations = []
    for data in recommendations_data:
        recommendation, created = JobRecommendation.objects.get_or_create(
            user=user,
            job_id=data['job_id'],
            defaults={
                'job_title': data['job_title'],
                'company_name': data['company_name'],
                'match_score': data['match_score'],
                'recommendation_reason': data['reason'],
                'matching_skills': data['matching_skills'],
                'missing_skills': data['missing_skills'],
                'ai_model': 'gpt-3.5-turbo',
                'confidence_score': data['match_score']
            }
        )
        if created:
            created_recommendations.append(recommendation)
    
    return Response({
        'message': f'{len(created_recommendations)} new recommendations generated',
        'recommendations': SimpleJobRecommendationSerializer.serialize_many(created_recommendations)
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_job_recommendations(request):
    """Get user's job recommendations."""
    user = request.user
    limit = min(int(request.GET.get('limit', 10)), 20)
    
    recommendations = JobRecommendation.objects.filter(
        user=user,
        dismissed=False
    ).order_by('-match_score', '-created_at')[:limit]
    
    return Response({
        'recommendations': SimpleJobRecommendationSerializer.serialize_many(recommendations),
        'total_count': JobRecommendation.objects.filter(user=user, dismissed=False).count()
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def suggestion_action(request, suggestion_id):
    """Handle suggestion actions (accept/reject)."""
    user = request.user
    action = request.data.get('action')
    notes = request.data.get('notes', '')
    
    if action not in ['accept', 'reject', 'viewed']:
        return Response(
            {'error': 'Invalid action. Must be accept, reject, or viewed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        suggestion = AISuggestion.objects.get(id=suggestion_id, user=user)
    except AISuggestion.DoesNotExist:
        return Response(
            {'error': 'Suggestion not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Update suggestion
    if action == 'viewed':
        suggestion.mark_viewed()
    elif action == 'accept':
        suggestion.status = 'accepted'
        suggestion.mark_acted_on()
        suggestion.save()
        
        # Create simple feedback
        SuggestionFeedback.objects.get_or_create(
            suggestion=suggestion,
            user=user,
            defaults={
                'feedback_type': 'helpful',
                'rating': 5,
                'comments': notes,
                'implemented': True
            }
        )
    elif action == 'reject':
        suggestion.status = 'rejected'
        suggestion.mark_acted_on()
        suggestion.save()
        
        # Create simple feedback
        SuggestionFeedback.objects.get_or_create(
            suggestion=suggestion,
            user=user,
            defaults={
                'feedback_type': 'not_helpful',
                'rating': 2,
                'comments': notes,
                'implemented': False
            }
        )
    
    return Response({
        'message': f'Suggestion {action}ed successfully',
        'suggestion': SimpleAISuggestionSerializer.serialize(suggestion)
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def recommendation_action(request, recommendation_id):
    """Handle recommendation actions (save/dismiss)."""
    user = request.user
    action = request.data.get('action')
    
    if action not in ['save', 'dismiss', 'viewed']:
        return Response(
            {'error': 'Invalid action. Must be save, dismiss, or viewed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        recommendation = JobRecommendation.objects.get(id=recommendation_id, user=user)
    except JobRecommendation.DoesNotExist:
        return Response(
            {'error': 'Recommendation not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Update recommendation
    if action == 'viewed':
        recommendation.mark_viewed()
    elif action == 'save':
        recommendation.saved = True
        recommendation.mark_viewed()
        recommendation.save()
    elif action == 'dismiss':
        recommendation.dismissed = True
        recommendation.mark_viewed()
        recommendation.save()
    
    return Response({
        'message': f'Recommendation {action}ed successfully',
        'recommendation': SimpleJobRecommendationSerializer.serialize(recommendation)
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def simple_analytics(request):
    """Get simple analytics for user's AI suggestions."""
    user = request.user
    
    suggestions = AISuggestion.objects.filter(user=user)
    recommendations = JobRecommendation.objects.filter(user=user)
    
    # Basic counts
    total_suggestions = suggestions.count()
    pending_suggestions = suggestions.filter(status='pending').count()
    accepted_suggestions = suggestions.filter(status='accepted').count()
    
    total_recommendations = recommendations.count()
    saved_recommendations = recommendations.filter(saved=True).count()
    
    # Recent activity
    recent_suggestions = suggestions.order_by('-created_at')[:5]
    recent_recommendations = recommendations.order_by('-created_at')[:5]
    
    return Response({
        'suggestions': {
            'total': total_suggestions,
            'pending': pending_suggestions,
            'accepted': accepted_suggestions,
            'recent': SimpleAISuggestionSerializer.serialize_many(recent_suggestions)
        },
        'recommendations': {
            'total': total_recommendations,
            'saved': saved_recommendations,
            'recent': SimpleJobRecommendationSerializer.serialize_many(recent_recommendations)
        }
    })