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
    
    @action(detail=False, methods=['post'])
    def extract_from_text(self, request):
        """Extract skills from job description or resume text."""
        serializer = SkillExtractionSerializer(data=request.data)
        if serializer.is_valid():
            text = serializer.validated_data['text']
            extracted_skills = self._extract_skills_from_text(text)
            
            result_serializer = SkillExtractionResultSerializer({
                'text': text,
                'extracted_skills': extracted_skills,
                'total_skills_found': len(extracted_skills)
            })
            return Response(result_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
        
        user_skills = self.get_queryset()
        # Simple gap analysis - in production this would use ML
        
        analysis_data = {
            'target_role': target_role,
            'current_skills_count': user_skills.count(),
            'proficiency_distribution': self._get_proficiency_distribution(user_skills),
            'recommended_skills': self._get_recommended_skills(target_role),
            'skill_gaps': []  # Would be populated with actual analysis
        }
        
        serializer = SkillGapAnalysisSerializer(analysis_data)
        return Response(serializer.data)
    
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
        if serializer.is_valid():
            target_role = serializer.validated_data['target_role']
            timeline = serializer.validated_data.get('timeline', 12)  # months
            
            # Simple plan generation - in production would use ML
            recommended_certs = self.get_queryset().filter(
                skills__name__icontains=target_role
            ).distinct()[:5]
            
            plan_data = {
                'target_role': target_role,
                'timeline_months': timeline,
                'recommended_certifications': recommended_certs,
                'estimated_cost': sum(cert.cost_range for cert in recommended_certs),
                'total_duration_hours': sum(cert.estimated_duration for cert in recommended_certs)
            }
            
            result_serializer = CertificationPlanResultSerializer(plan_data)
            return Response(result_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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