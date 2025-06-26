"""
Skills app legacy views for Epic 4: Skills Analysis and Certification Roadmaps.
Note: These views are deprecated and maintained only for backward compatibility.
New implementations use the ViewSets in viewsets.py
"""

import time
import re
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, F, Sum
from django.utils import timezone
from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from core.permissions import AuthenticatedAndActive
from .models import (
    SkillCategory, Skill, UserSkill, Certification, UserCertification,
    LearningPath, UserLearningPath, SkillAssessment, UserSkillAssessment
)
from .serializers import (
    SkillCategorySerializer, SkillSerializer, SkillCreateSerializer,
    UserSkillSerializer, UserSkillUpdateSerializer, CertificationSerializer,
    UserCertificationSerializer, LearningPathSerializer, UserLearningPathSerializer,
    SkillAssessmentSerializer, UserSkillAssessmentSerializer, SkillSearchSerializer,
    SkillGapAnalysisSerializer, SkillTrendSerializer, SkillRecommendationSerializer,
    LearningProgressSerializer, SkillExtractionSerializer, SkillExtractionResultSerializer,
    CertificationPlanSerializer, CertificationPlanResultSerializer
)

# Note: Most views have been consolidated into ViewSets for better API architecture.
# These remaining views provide legacy endpoints for backward compatibility.


# Note: Traditional view classes have been migrated to ViewSets for consistency.
# Only function-based views remain for legacy endpoint compatibility.

# Legacy function-based views for backward compatibility
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def skill_gap_analysis(request):
    """Analyze skill gaps for a target role."""
    target_role = request.query_params.get('target_role')
    if not target_role:
        return Response(
            {"error": "target_role parameter is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = request.user
    
    # Get user's current skills
    user_skills = UserSkill.objects.filter(user=user).select_related('skill')
    user_skill_names = [us.skill.name.lower() for us in user_skills]
    
    # Mock required skills for the target role (in a real implementation, this would come from a job skills database)
    required_skills_map = {
        'software developer': [
            'Python', 'JavaScript', 'React', 'SQL', 'Git', 'REST APIs',
            'HTML/CSS', 'Node.js', 'Docker', 'AWS'
        ],
        'data scientist': [
            'Python', 'R', 'SQL', 'Machine Learning', 'Statistics',
            'Pandas', 'NumPy', 'Matplotlib', 'Jupyter', 'TensorFlow'
        ],
        'product manager': [
            'Agile', 'Scrum', 'Product Strategy', 'User Research', 'Analytics',
            'Roadmapping', 'Stakeholder Management', 'A/B Testing'
        ],
        'devops engineer': [
            'Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Linux', 'Python',
            'Terraform', 'Monitoring', 'Security', 'Git'
        ]
    }
    
    required_skill_names = required_skills_map.get(
        target_role.lower(),
        ['Python', 'JavaScript', 'SQL', 'Communication', 'Problem Solving']  # Default skills
    )
    
    # Find required skills in database
    required_skills = Skill.objects.filter(
        name__in=required_skill_names
    ).select_related('category')
    
    # Find missing skills
    missing_skill_names = [
        skill_name for skill_name in required_skill_names
        if skill_name.lower() not in user_skill_names
    ]
    
    missing_skills = Skill.objects.filter(
        name__in=missing_skill_names
    ).select_related('category')
    
    # Calculate skill gaps (skills user has but at lower proficiency)
    skill_gaps = []
    proficiency_scores = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}
    target_proficiency = 3  # Advanced level expected for role
    
    for user_skill in user_skills:
        if user_skill.skill.name in required_skill_names:
            current_score = proficiency_scores.get(user_skill.proficiency_level, 1)
            if current_score < target_proficiency:
                skill_gaps.append({
                    'skill': SkillSerializer(user_skill.skill, context={'request': request}).data,
                    'current_level': user_skill.proficiency_level,
                    'target_level': 'advanced',
                    'gap_score': target_proficiency - current_score
                })
    
    # Find recommended learning paths
    recommended_paths = LearningPath.objects.filter(
        Q(target_role__icontains=target_role) |
        Q(target_skills__in=missing_skills)
    ).filter(is_active=True).distinct()[:5]
    
    # Find recommended certifications
    recommended_certs = Certification.objects.filter(
        Q(related_skills__in=missing_skills) |
        Q(name__icontains=target_role)
    ).filter(is_active=True).distinct()[:5]
    
    # Calculate overall readiness score
    total_required = len(required_skill_names)
    skills_met = len(required_skill_names) - len(missing_skill_names)
    overall_readiness_score = (skills_met / total_required) * 100 if total_required > 0 else 0
    
    analysis_data = {
        'target_role': target_role,
        'user_skills': UserSkillSerializer(user_skills, many=True, context={'request': request}).data,
        'required_skills': SkillSerializer(required_skills, many=True, context={'request': request}).data,
        'missing_skills': SkillSerializer(missing_skills, many=True, context={'request': request}).data,
        'skill_gaps': skill_gaps,
        'recommended_learning_paths': LearningPathSerializer(
            recommended_paths, many=True, context={'request': request}
        ).data,
        'recommended_certifications': CertificationSerializer(
            recommended_certs, many=True, context={'request': request}
        ).data,
        'overall_readiness_score': round(overall_readiness_score, 1)
    }
    
    return Response(analysis_data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def skill_trends(request):
    """Get skill trends and market data."""
    # Mock trending skills data
    trending_skills = Skill.objects.filter(is_trending=True)[:20]
    
    trends_data = []
    for skill in trending_skills:
        trends_data.append({
            'skill': SkillSerializer(skill, context={'request': request}).data,
            'trend_direction': 'up',
            'growth_percentage': skill.growth_rate,
            'demand_change': skill.market_demand,
            'salary_change': 15.0,  # Mock data
            'period': '2024'
        })
    
    return Response(trends_data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def skill_recommendations(request):
    """Get personalized skill recommendations for the user."""
    user = request.user
    
    # Get user's current skills and proficiency levels
    user_skills = UserSkill.objects.filter(user=user).select_related('skill__category')
    user_skill_categories = [us.skill.category for us in user_skills]
    
    # Find skills in similar categories that user doesn't have
    recommended_skills = Skill.objects.filter(
        category__in=user_skill_categories
    ).exclude(
        id__in=user_skills.values_list('skill_id', flat=True)
    ).filter(
        market_demand__in=['high', 'very_high']
    ).order_by('-popularity_score')[:10]
    
    recommendations = []
    for skill in recommended_skills:
        recommendations.append({
            'skill': SkillSerializer(skill, context={'request': request}).data,
            'recommendation_reason': f'Popular skill in {skill.category.name} category',
            'relevance_score': 0.8,
            'priority': 'medium',
            'learning_time_estimate': skill.learning_time_hours or 40,
            'career_impact': 'Enhances expertise in your field'
        })
    
    return Response(recommendations)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def extract_skills_from_text(request):
    """Extract skills from resume or job description text."""
    serializer = SkillExtractionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    text = data['text']
    extraction_type = data['extraction_type']
    confidence_threshold = data['confidence_threshold']
    
    start_time = time.time()
    
    # Simple skill extraction using keyword matching
    # In a real implementation, this would use NLP models
    all_skills = Skill.objects.all()
    extracted_skills = []
    confidence_scores = {}
    
    text_lower = text.lower()
    
    for skill in all_skills:
        # Check skill name and aliases
        skill_terms = [skill.name.lower()] + [alias.lower() for alias in skill.aliases]
        
        for term in skill_terms:
            if term in text_lower:
                # Calculate confidence based on context and frequency
                occurrences = text_lower.count(term)
                confidence = min(1.0, 0.6 + (occurrences * 0.1))
                
                if confidence >= confidence_threshold:
                    extracted_skills.append({
                        'skill_id': str(skill.id),
                        'skill_name': skill.name,
                        'category': skill.category.name,
                        'occurrences': occurrences,
                        'context_matches': [
                            text[max(0, text_lower.find(term) - 50):text_lower.find(term) + len(term) + 50]
                        ]
                    })
                    confidence_scores[skill.name] = confidence
                break
    
    # Remove duplicates and sort by confidence
    unique_skills = {}
    for skill_data in extracted_skills:
        skill_name = skill_data['skill_name']
        if skill_name not in unique_skills or confidence_scores[skill_name] > confidence_scores.get(skill_name, 0):
            unique_skills[skill_name] = skill_data
    
    extracted_skills = list(unique_skills.values())
    extracted_skills.sort(key=lambda x: confidence_scores[x['skill_name']], reverse=True)
    
    # Generate suggestions
    suggestions = []
    if extraction_type == 'resume':
        suggestions = [
            "Consider adding proficiency levels for each skill",
            "Include years of experience with each skill",
            "Add specific tools and technologies used"
        ]
    elif extraction_type == 'job_description':
        suggestions = [
            "These skills appear to be requirements for the role",
            "Consider learning missing skills for better job match",
            "Look for similar roles that match your current skills"
        ]
    
    processing_time = time.time() - start_time
    
    result_data = {
        'extracted_skills': extracted_skills,
        'confidence_scores': confidence_scores,
        'processing_time': round(processing_time, 2),
        'suggestions': suggestions
    }
    
    return Response(result_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_learning_progress(request, learning_path_id):
    """Update progress for a learning path."""
    try:
        user_path = UserLearningPath.objects.get(
            learning_path_id=learning_path_id,
            user=request.user
        )
    except UserLearningPath.DoesNotExist:
        return Response(
            {"error": "Learning path enrollment not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = LearningProgressSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    hours_studied = data['hours_studied']
    milestone_completed = data.get('milestone_completed')
    notes = data.get('notes', '')
    difficulty_rating = data.get('difficulty_rating')
    
    # Update progress
    user_path.update_progress(hours_studied)
    
    # Update milestone if provided
    if milestone_completed is not None:
        user_path.current_milestone = milestone_completed
    
    # Update ratings if provided
    if difficulty_rating:
        user_path.difficulty_rating = difficulty_rating
    
    # Add notes
    if notes:
        if user_path.feedback_notes:
            user_path.feedback_notes += f"\n\n{timezone.now().strftime('%Y-%m-%d')}: {notes}"
        else:
            user_path.feedback_notes = f"{timezone.now().strftime('%Y-%m-%d')}: {notes}"
    
    user_path.save()
    
    return Response({
        'message': 'Progress updated successfully',
        'current_progress': user_path.progress_percentage,
        'total_hours': user_path.total_study_hours,
        'current_milestone': user_path.current_milestone
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_certification_plan(request):
    """Create a personalized certification plan."""
    serializer = CertificationPlanSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    target_role = data['target_role']
    timeline_months = data['timeline_months']
    budget_usd = data.get('budget_usd')
    current_skill_ids = data.get('current_skills', [])
    preferred_difficulty = data.get('preferred_difficulty')
    
    # Get user's current skills
    current_skills = Skill.objects.filter(id__in=current_skill_ids)
    
    # Find relevant certifications for the target role
    relevant_certs = Certification.objects.filter(
        Q(name__icontains=target_role) |
        Q(related_skills__name__icontains=target_role)
    ).filter(is_active=True).distinct()
    
    # Filter by difficulty if specified
    if preferred_difficulty:
        relevant_certs = relevant_certs.filter(difficulty_level=preferred_difficulty)
    
    # Filter by budget if specified
    if budget_usd:
        relevant_certs = relevant_certs.filter(
            Q(cost_usd__lte=budget_usd) | Q(cost_usd__isnull=True)
        )
    
    # Order by popularity and market demand
    recommended_certs = relevant_certs.order_by('-popularity_score', '-market_demand')[:5]
    
    # Create timeline
    timeline = []
    total_cost = 0
    total_study_hours = 0
    current_month = 0
    
    for cert in recommended_certs:
        if current_month >= timeline_months:
            break
        
        prep_time_months = (cert.preparation_time_hours or 120) // 40  # Assuming 40 hours per month
        prep_time_months = max(1, min(prep_time_months, timeline_months - current_month))
        
        timeline.append({
            'certification': CertificationSerializer(cert, context={'request': request}).data,
            'start_month': current_month + 1,
            'end_month': current_month + prep_time_months,
            'estimated_hours': cert.preparation_time_hours or 120,
            'cost': float(cert.cost_usd) if cert.cost_usd else 0
        })
        
        total_cost += float(cert.cost_usd) if cert.cost_usd else 0
        total_study_hours += cert.preparation_time_hours or 120
        current_month += prep_time_months
    
    # Expected outcomes
    expected_outcomes = [
        f"Enhanced expertise in {target_role}",
        "Increased market competitiveness",
        "Potential salary increase of 15-25%",
        "Expanded career opportunities",
        "Industry recognition and credibility"
    ]
    
    # Prerequisites analysis
    prerequisites_analysis = {
        'missing_prerequisites': [],
        'recommended_preparation': [],
        'skill_readiness_score': 0.8  # Mock score
    }
    
    plan_data = {
        'recommended_certifications': CertificationSerializer(
            recommended_certs, many=True, context={'request': request}
        ).data,
        'learning_timeline': timeline,
        'total_cost': total_cost,
        'total_study_hours': total_study_hours,
        'expected_outcomes': expected_outcomes,
        'prerequisites_analysis': prerequisites_analysis
    }
    
    return Response(plan_data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_skills_analytics(request):
    """Get analytics for user's skills."""
    user = request.user
    user_skills = UserSkill.objects.filter(user=user).select_related('skill__category')
    
    # Skills by category
    skills_by_category = {}
    for user_skill in user_skills:
        category = user_skill.skill.category.name
        if category not in skills_by_category:
            skills_by_category[category] = 0
        skills_by_category[category] += 1
    
    # Skills by proficiency
    skills_by_proficiency = {}
    for user_skill in user_skills:
        proficiency = user_skill.proficiency_level
        if proficiency not in skills_by_proficiency:
            skills_by_proficiency[proficiency] = 0
        skills_by_proficiency[proficiency] += 1
    
    # Skills verification rate
    verified_skills = user_skills.filter(is_verified=True).count()
    verification_rate = (verified_skills / user_skills.count()) * 100 if user_skills.count() > 0 else 0
    
    # Market value estimation
    total_market_value = 0
    for user_skill in user_skills:
        if user_skill.skill.average_salary:
            total_market_value += float(user_skill.skill.average_salary)
    
    average_market_value = total_market_value / user_skills.count() if user_skills.count() > 0 else 0
    
    analytics = {
        'total_skills': user_skills.count(),
        'skills_by_category': skills_by_category,
        'skills_by_proficiency': skills_by_proficiency,
        'verification_rate': round(verification_rate, 1),
        'average_market_value': round(average_market_value, 2),
        'trending_skills_owned': user_skills.filter(skill__is_trending=True).count(),
        'high_demand_skills': user_skills.filter(
            skill__market_demand__in=['high', 'very_high']
        ).count()
    }
    
    return Response(analytics)


# Additional legacy function views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def take_skill_assessment(request, assessment_id):
    """Start or submit a skill assessment."""
    try:
        assessment = SkillAssessment.objects.get(id=assessment_id, is_active=True)
    except SkillAssessment.DoesNotExist:
        return Response(
            {"error": "Assessment not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Create or get existing attempt
    user_assessment, created = UserSkillAssessment.objects.get_or_create(
        user=request.user,
        assessment=assessment,
        completed_at__isnull=True,
        defaults={'assessment': assessment}
    )
    
    if request.method == 'POST':
        # Submit assessment
        answers = request.data.get('answers', {})
        
        # Calculate score (simplified scoring)
        total_questions = len(assessment.questions)
        correct_answers = 0
        
        for question_id, user_answer in answers.items():
            # Mock scoring logic
            if user_answer:  # Assume any answer is correct for demo
                correct_answers += 1
        
        score = (correct_answers / total_questions) * assessment.max_score if total_questions > 0 else 0
        
        # Update assessment attempt
        user_assessment.answers = answers
        user_assessment.score = score
        user_assessment.completed_at = timezone.now()
        user_assessment.calculate_percentage()
        
        # Set time taken
        time_taken = (timezone.now() - user_assessment.started_at).total_seconds() / 60
        user_assessment.time_taken_minutes = int(time_taken)
        
        # Generate recommendations
        if user_assessment.passed:
            user_assessment.recommended_proficiency = assessment.difficulty_level
        else:
            proficiency_levels = ['beginner', 'intermediate', 'advanced', 'expert']
            current_index = proficiency_levels.index(assessment.difficulty_level)
            if current_index > 0:
                user_assessment.recommended_proficiency = proficiency_levels[current_index - 1]
            else:
                user_assessment.recommended_proficiency = 'beginner'
        
        user_assessment.improvement_areas = ['Practice more with similar questions', 'Review fundamentals']
        user_assessment.save()
        
        return Response({
            'message': 'Assessment completed',
            'score': user_assessment.score,
            'percentage': user_assessment.percentage,
            'passed': user_assessment.passed,
            'recommended_proficiency': user_assessment.recommended_proficiency
        })
    
    else:
        # Return assessment questions for taking
        return Response({
            'assessment': SkillAssessmentSerializer(assessment, context={'request': request}).data,
            'attempt_id': str(user_assessment.id),
            'questions': assessment.questions
        })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def skill_market_demand(request):
    """Get market demand data for skills."""
    # Get skills with market data
    skills_with_demand = Skill.objects.exclude(
        market_demand='moderate'
    ).order_by('-popularity_score')[:20]
    
    demand_data = []
    for skill in skills_with_demand:
        demand_data.append({
            'skill': SkillSerializer(skill, context={'request': request}).data,
            'demand_level': skill.market_demand,
            'growth_rate': skill.growth_rate,
            'average_salary': float(skill.average_salary) if skill.average_salary else None,
            'job_postings_count': skill.usage_count,  # Mock data
            'learning_difficulty': skill.difficulty_level
        })
    
    return Response(demand_data)