"""
Skills app ViewSets for Epic 4: Skills Analysis and Certification Roadmaps.
Modern ViewSet-based API architecture aligned with Epic 5 standards.
"""

from django.db.models import Q, Count, Avg, F, Sum, Max
from django.utils import timezone
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
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


class SkillsPagination(PageNumberPagination):
    """Custom pagination for skills endpoints."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class SkillCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing skill categories.
    Provides CRUD operations and search functionality.
    """
    serializer_class = SkillCategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = SkillsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['is_active']
    
    def get_queryset(self):
        return SkillCategory.objects.filter(is_active=True).order_by('name')
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular skill categories with skill counts."""
        categories = self.get_queryset().annotate(
            skill_count=Count('skills')
        ).filter(skill_count__gt=0).order_by('-skill_count')[:10]
        
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


class SkillViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing skills.
    Provides CRUD operations, search, and analytics.
    """
    permission_classes = [permissions.AllowAny]
    pagination_class = SkillsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    filterset_fields = ['category', 'skill_type', 'difficulty_level']
    ordering_fields = ['name', 'created_at', 'demand_score']
    ordering = ['name']
    
    def get_queryset(self):
        return Skill.objects.select_related('category').filter(is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SkillCreateSerializer
        return SkillSerializer
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending skills based on demand and recent activity."""
        skills = self.get_queryset().filter(
            demand_score__gte=7.0
        ).order_by('-demand_score', '-updated_at')[:20]
        
        serializer = SkillTrendSerializer(skills, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def market_demand(self, request):
        """Get market demand data for skills."""
        skills_with_demand = self.get_queryset().exclude(
            market_demand='moderate'
        ).order_by('-popularity_score')[:20]
        
        demand_data = []
        for skill in skills_with_demand:
            demand_data.append({
                'skill': SkillSerializer(skill, context={'request': request}).data,
                'demand_level': skill.market_demand,
                'growth_rate': skill.growth_rate,
                'average_salary': float(skill.average_salary) if skill.average_salary else None,
                'job_postings_count': skill.usage_count,
                'learning_difficulty': skill.difficulty_level
            })
        
        return Response(demand_data)
    
    @action(detail=False, methods=['post'])
    def extract_from_text(self, request):
        """Extract skills from job description or resume text."""
        import time
        import re
        
        serializer = SkillExtractionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        text = data['text']
        extraction_type = data.get('extraction_type', 'general')
        confidence_threshold = data.get('confidence_threshold', 0.6)
        
        start_time = time.time()
        
        # Enhanced skill extraction using keyword matching
        all_skills = self.get_queryset()
        extracted_skills = []
        confidence_scores = {}
        
        text_lower = text.lower()
        
        for skill in all_skills:
            # Check skill name and aliases
            skill_terms = [skill.name.lower()]
            if hasattr(skill, 'aliases') and skill.aliases:
                skill_terms.extend([alias.lower() for alias in skill.aliases])
            
            for term in skill_terms:
                if term in text_lower:
                    # Calculate confidence based on context and frequency
                    occurrences = text_lower.count(term)
                    confidence = min(1.0, 0.6 + (occurrences * 0.1))
                    
                    if confidence >= confidence_threshold:
                        extracted_skills.append({
                            'skill_id': str(skill.id),
                            'skill_name': skill.name,
                            'category': skill.category.name if skill.category else 'General',
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
    
    def _extract_skills_from_text(self, text):
        """Extract skills from text using simple keyword matching."""
        import re
        
        skills = self.get_queryset()
        found_skills = []
        
        text_lower = text.lower()
        
        for skill in skills:
            # Simple keyword matching
            skill_patterns = [
                skill.name.lower(),
                *[alias.lower() for alias in skill.aliases.get('aliases', [])]
            ]
            
            for pattern in skill_patterns:
                if re.search(r'\b' + re.escape(pattern) + r'\b', text_lower):
                    found_skills.append({
                        'skill': SkillSerializer(skill).data,
                        'confidence': 0.8,  # Simple confidence score
                        'found_text': pattern
                    })
                    break
        
        return found_skills


class UserSkillViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user skills.
    Provides CRUD operations and skill analysis.
    """
    permission_classes = [AuthenticatedAndActive]
    pagination_class = SkillsPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['skill__category', 'proficiency_level', 'verified']
    ordering_fields = ['proficiency_level', 'acquired_date', 'last_used_date']
    ordering = ['-proficiency_level']
    
    def get_queryset(self):
        return UserSkill.objects.filter(
            user=self.request.user
        ).select_related('skill', 'skill__category')
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserSkillUpdateSerializer
        return UserSkillSerializer
    
    @action(detail=False, methods=['get'])
    def gap_analysis(self, request):
        """Analyze user's skill gaps for a specific role or industry."""
        target_role = request.query_params.get('role')
        
        if not target_role:
            return Response(
                {'error': 'role parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        user_skills = self.get_queryset()
        user_skill_names = [us.skill.name.lower() for us in user_skills]
        
        # Mock required skills for the target role
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
            ['Python', 'JavaScript', 'SQL', 'Communication', 'Problem Solving']
        )
        
        # Find required skills in database
        from .models import Skill
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
        
        # Calculate skill gaps
        skill_gaps = []
        proficiency_scores = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}
        target_proficiency = 3
        
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
            'overall_readiness_score': round(overall_readiness_score, 1)
        }
        
        return Response(analysis_data)
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """Get personalized skill recommendations for the user."""
        user_skills = self.get_queryset()
        user_skill_categories = [us.skill.category for us in user_skills]
        
        # Find skills in similar categories that user doesn't have
        from .models import Skill
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
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get analytics for user's skills."""
        user_skills = self.get_queryset()
        
        # Skills by category
        skills_by_category = {}
        for user_skill in user_skills:
            category = user_skill.skill.category.name if user_skill.skill.category else 'General'
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
        verified_skills = user_skills.filter(verified=True).count()
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
    
    def _get_proficiency_distribution(self, user_skills):
        """Get distribution of user's skill proficiency levels."""
        return {
            'beginner': user_skills.filter(proficiency_level=1).count(),
            'intermediate': user_skills.filter(proficiency_level=2).count(),
            'advanced': user_skills.filter(proficiency_level=3).count(),
            'expert': user_skills.filter(proficiency_level=4).count(),
            'master': user_skills.filter(proficiency_level=5).count(),
        }
    
    def _get_recommended_skills(self, target_role):
        """Get recommended skills for a target role."""
        # Simplified recommendation - in production would use ML
        return Skill.objects.filter(
            demand_score__gte=7.0
        ).order_by('-demand_score')[:10]


class CertificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing certifications.
    Read-only access to certification catalog.
    """
    serializer_class = CertificationSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = SkillsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'provider', 'skills__name']
    filterset_fields = ['provider', 'difficulty_level', 'cost_range']
    ordering_fields = ['name', 'difficulty_level', 'estimated_duration']
    ordering = ['name']
    
    def get_queryset(self):
        return Certification.objects.filter(is_active=True).prefetch_related('skills')
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular certifications based on user enrollments."""
        certifications = self.get_queryset().annotate(
            user_count=Count('usercertification')
        ).filter(user_count__gt=0).order_by('-user_count')[:20]
        
        serializer = self.get_serializer(certifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def generate_plan(self, request):
        """Generate certification plan based on user's skills and goals."""
        serializer = CertificationPlanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        target_role = data['target_role']
        timeline_months = data.get('timeline_months', 12)
        budget_usd = data.get('budget_usd')
        current_skill_ids = data.get('current_skills', [])
        preferred_difficulty = data.get('preferred_difficulty')
        
        # Get user's current skills
        from .models import Skill
        current_skills = Skill.objects.filter(id__in=current_skill_ids)
        
        # Find relevant certifications for the target role
        relevant_certs = self.get_queryset().filter(
            Q(name__icontains=target_role) |
            Q(skills__name__icontains=target_role)
        ).distinct()
        
        # Filter by difficulty if specified
        if preferred_difficulty:
            relevant_certs = relevant_certs.filter(difficulty_level=preferred_difficulty)
        
        # Filter by budget if specified
        if budget_usd:
            relevant_certs = relevant_certs.filter(
                Q(cost_range__lte=budget_usd) | Q(cost_range__isnull=True)
            )
        
        # Order by popularity and market demand
        recommended_certs = relevant_certs.order_by('-estimated_duration')[:5]
        
        # Create timeline
        timeline = []
        total_cost = 0
        total_study_hours = 0
        current_month = 0
        
        for cert in recommended_certs:
            if current_month >= timeline_months:
                break
            
            prep_time_months = (cert.estimated_duration or 120) // 40  # Assuming 40 hours per month
            prep_time_months = max(1, min(prep_time_months, timeline_months - current_month))
            
            timeline.append({
                'certification': CertificationSerializer(cert, context={'request': request}).data,
                'start_month': current_month + 1,
                'end_month': current_month + prep_time_months,
                'estimated_hours': cert.estimated_duration or 120,
                'cost': float(cert.cost_range) if cert.cost_range else 0
            })
            
            total_cost += float(cert.cost_range) if cert.cost_range else 0
            total_study_hours += cert.estimated_duration or 120
            current_month += prep_time_months
        
        # Expected outcomes
        expected_outcomes = [
            f"Enhanced expertise in {target_role}",
            "Increased market competitiveness",
            "Potential salary increase of 15-25%",
            "Expanded career opportunities",
            "Industry recognition and credibility"
        ]
        
        plan_data = {
            'recommended_certifications': CertificationSerializer(
                recommended_certs, many=True, context={'request': request}
            ).data,
            'learning_timeline': timeline,
            'total_cost': total_cost,
            'total_study_hours': total_study_hours,
            'expected_outcomes': expected_outcomes
        }
        
        return Response(plan_data)


class UserCertificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user certifications.
    Tracks user's certification progress and achievements.
    """
    serializer_class = UserCertificationSerializer
    permission_classes = [AuthenticatedAndActive]
    pagination_class = SkillsPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['certification__provider', 'status', 'is_verified']
    ordering_fields = ['earned_date', 'expiry_date', 'status']
    ordering = ['-earned_date']
    
    def get_queryset(self):
        return UserCertification.objects.filter(
            user=self.request.user
        ).select_related('certification')
    
    @action(detail=False, methods=['get'])
    def progress(self, request):
        """Get user's certification progress and achievements."""
        user_certs = self.get_queryset()
        
        progress_data = {
            'total_certifications': user_certs.count(),
            'completed': user_certs.filter(status='completed').count(),
            'in_progress': user_certs.filter(status='in_progress').count(),
            'expired': user_certs.filter(
                expiry_date__lt=timezone.now().date()
            ).count(),
            'upcoming_expirations': user_certs.filter(
                expiry_date__lte=timezone.now().date() + timezone.timedelta(days=90),
                expiry_date__gt=timezone.now().date()
            ).count()
        }
        
        serializer = LearningProgressSerializer(progress_data)
        return Response(serializer.data)


class LearningPathViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing learning paths.
    Provides structured learning sequences.
    """
    serializer_class = LearningPathSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = SkillsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description', 'target_role']
    filterset_fields = ['difficulty_level', 'estimated_duration']
    
    def get_queryset(self):
        return LearningPath.objects.filter(is_active=True).prefetch_related(
            'skills', 'certifications'
        )


class UserLearningPathViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user learning paths.
    Tracks user's learning progress.
    """
    serializer_class = UserLearningPathSerializer
    permission_classes = [AuthenticatedAndActive]
    pagination_class = SkillsPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'learning_path__difficulty_level']
    
    def get_queryset(self):
        return UserLearningPath.objects.filter(
            user=self.request.user
        ).select_related('learning_path')


class SkillAssessmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for skill assessments.
    Provides available skill evaluation tools.
    """
    serializer_class = SkillAssessmentSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = SkillsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description', 'skill__name']
    filterset_fields = ['skill', 'difficulty_level', 'assessment_type']
    
    def get_queryset(self):
        return SkillAssessment.objects.filter(is_active=True).select_related('skill')


class UserSkillAssessmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user skill assessments.
    Manages user's assessment results and progress.
    """
    serializer_class = UserSkillAssessmentSerializer
    permission_classes = [AuthenticatedAndActive]
    pagination_class = SkillsPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['assessment__skill', 'score']
    
    def get_queryset(self):
        return UserSkillAssessment.objects.filter(
            user=self.request.user
        ).select_related('assessment', 'assessment__skill')
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get analytics for user's skill assessment performance."""
        assessments = self.get_queryset()
        
        analytics_data = {
            'total_assessments': assessments.count(),
            'average_score': assessments.aggregate(Avg('score'))['score__avg'] or 0,
            'highest_score': assessments.aggregate(max_score=Max('score'))['max_score'] or 0,
            'assessments_by_skill': assessments.values(
                'assessment__skill__name'
            ).annotate(
                count=Count('id'),
                avg_score=Avg('score')
            ).order_by('-avg_score')[:10]
        }
        
        return Response(analytics_data)
    
    @action(detail=True, methods=['post'])
    def take_assessment(self, request, pk=None):
        """Start or submit a skill assessment."""
        try:
            assessment = SkillAssessment.objects.get(id=pk, is_active=True)
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