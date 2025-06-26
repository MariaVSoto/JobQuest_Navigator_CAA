"""
ViewSets for Epic 2: Resume Management & Versioning.
Modern DRF ViewSets implementation replacing traditional views.
"""

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.db import transaction
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action as drf_action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
import copy

from .models import (
    ResumeTemplate, Resume, ResumeVersion, ResumeSkillMatch,
    ResumeShare, ResumeComment, ResumeExport
)
from .serializers import (
    ResumeTemplateSerializer, ResumeSerializer, ResumeDetailSerializer,
    ResumeCreateSerializer, ResumeUpdateSerializer, ResumeListSerializer,
    ResumeVersionSerializer, ResumeSkillMatchSerializer, ResumeShareSerializer,
    ResumeCommentSerializer, ResumeExportSerializer, ResumeCloneSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for resume endpoints"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ResumeTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing resume templates.
    Provides read-only access with filtering and usage tracking.
    """
    serializer_class = ResumeTemplateSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_premium', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'usage_count', 'created_at']
    ordering = ['-usage_count', 'name']
    
    def get_queryset(self):
        """Filter to active templates."""
        return ResumeTemplate.objects.filter(is_active=True)

    @drf_action(detail=True, methods=['post'])
    def use_template(self, request, pk=None):
        """
        Track template usage and increment usage count.
        POST /resume-templates/{id}/use_template/
        """
        template = self.get_object()
        template.usage_count += 1
        template.save(update_fields=['usage_count'])
        
        return Response({
            'message': 'Template usage tracked',
            'usage_count': template.usage_count
        })

    @drf_action(detail=False, methods=['get'])
    def popular(self, request):
        """
        Get most popular templates.
        GET /resume-templates/popular/
        """
        popular_templates = self.get_queryset().order_by('-usage_count')[:10]
        serializer = self.get_serializer(popular_templates, many=True)
        return Response(serializer.data)

    @drf_action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get templates grouped by category.
        GET /resume-templates/by_category/
        """
        categories = {}
        for template in self.get_queryset():
            category = template.get_category_display()
            if category not in categories:
                categories[category] = []
            categories[category].append(ResumeTemplateSerializer(template).data)
        
        return Response(categories)


class ResumeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing resumes.
    Provides CRUD operations, cloning, default management, and analytics.
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'target_role', 'target_industry', 'is_default']
    search_fields = ['title', 'full_name', 'professional_summary', 'keywords']
    ordering_fields = ['created_at', 'updated_at', 'title', 'view_count']
    ordering = ['-updated_at']

    def get_queryset(self):
        """Filter resumes to authenticated user's data."""
        return Resume.objects.filter(user=self.request.user).select_related('template')

    def get_serializer_class(self):
        """Use appropriate serializer based on action."""
        if self.action == 'list':
            return ResumeListSerializer
        elif self.action == 'create':
            return ResumeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ResumeUpdateSerializer
        elif self.action == 'retrieve':
            return ResumeDetailSerializer
        return ResumeSerializer

    def perform_create(self, serializer):
        """Set user when creating resume."""
        serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """Increment view count on resume retrieval."""
        resume = self.get_object()
        resume.view_count += 1
        resume.save(update_fields=['view_count'])
        return super().retrieve(request, *args, **kwargs)

    @drf_action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        """
        Clone a resume with optional modifications.
        POST /resumes/{id}/clone/
        """
        original_resume = self.get_object()
        
        # Prepare clone data
        clone_data = {
            'title': request.data.get('title', f"{original_resume.title} (Copy)"),
            'template': original_resume.template.id if original_resume.template else None,
            'full_name': original_resume.full_name,
            'email': original_resume.email,
            'phone': original_resume.phone,
            'location': original_resume.location,
            'website': original_resume.website,
            'linkedin_url': original_resume.linkedin_url,
            'github_url': original_resume.github_url,
            'professional_summary': original_resume.professional_summary,
            'resume_data': copy.deepcopy(original_resume.resume_data),
            'target_role': original_resume.target_role,
            'target_industry': original_resume.target_industry,
            'keywords': original_resume.keywords,
        }
        
        # Apply any modifications from request
        for field in ['title', 'target_role', 'target_industry']:
            if field in request.data:
                clone_data[field] = request.data[field]

        serializer = ResumeCreateSerializer(data=clone_data, context={'request': request})
        
        if serializer.is_valid():
            cloned_resume = serializer.save()
            return Response(
                ResumeDetailSerializer(cloned_resume).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @drf_action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """
        Set resume as user's default.
        POST /resumes/{id}/set_default/
        """
        resume = self.get_object()
        
        with transaction.atomic():
            # Remove default from all user's resumes
            Resume.objects.filter(user=request.user, is_default=True).update(is_default=False)
            # Set this resume as default
            resume.is_default = True
            resume.save(update_fields=['is_default'])
        
        return Response({
            'message': 'Resume set as default',
            'resume_id': resume.id
        })

    @drf_action(detail=False, methods=['get'])
    def default(self, request):
        """
        Get user's default resume.
        GET /resumes/default/
        """
        try:
            default_resume = self.get_queryset().get(is_default=True)
            serializer = ResumeDetailSerializer(default_resume)
            return Response(serializer.data)
        except Resume.DoesNotExist:
            return Response(
                {'error': 'No default resume found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @drf_action(detail=False, methods=['get'])
    def analytics(self, request):
        """
        Get resume analytics for user.
        GET /resumes/analytics/
        """
        queryset = self.get_queryset()
        
        analytics = {
            'total_resumes': queryset.count(),
            'by_status': dict(queryset.values_list('status').annotate(count=Count('id'))),
            'total_views': sum(queryset.values_list('view_count', flat=True)),
            'total_downloads': sum(queryset.values_list('download_count', flat=True)),
            'by_target_role': dict(queryset.exclude(target_role='').values_list('target_role').annotate(count=Count('id'))[:10]),
            'recent_activity': queryset.order_by('-updated_at')[:5].values(
                'id', 'title', 'updated_at', 'view_count'
            )
        }
        
        return Response(analytics)

    @drf_action(detail=True, methods=['post'])
    def duplicate_for_job(self, request, pk=None):
        """
        Create a job-specific copy of resume.
        POST /resumes/{id}/duplicate_for_job/
        """
        original_resume = self.get_object()
        job_title = request.data.get('job_title', '')
        company_name = request.data.get('company_name', '')
        
        if not job_title:
            return Response(
                {'error': 'job_title is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create targeted copy
        new_title = f"{original_resume.title} - {job_title}"
        if company_name:
            new_title += f" at {company_name}"
        
        clone_data = {
            'title': new_title,
            'template': original_resume.template.id if original_resume.template else None,
            'target_role': job_title,
            'target_industry': request.data.get('industry', original_resume.target_industry),
        }
        
        return self.clone(request, pk, **{'title': new_title, **clone_data})


class ResumeVersionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing resume versions.
    Provides version control, restoration, and comparison features.
    """
    serializer_class = ResumeVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_current']
    ordering_fields = ['version_number', 'created_at']
    ordering = ['-version_number']

    def get_queryset(self):
        """Filter versions to user's resumes."""
        return ResumeVersion.objects.filter(
            resume__user=self.request.user
        ).select_related('resume', 'created_by')

    def perform_create(self, serializer):
        """Set created_by when creating version."""
        serializer.save(created_by=self.request.user)

    @drf_action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        Restore a resume version.
        POST /resume-versions/{id}/restore/
        """
        version = self.get_object()
        resume = version.resume
        
        # Verify user owns the resume
        if resume.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        with transaction.atomic():
            # Create new version from current state before restoring
            current_version = ResumeVersion.objects.create(
                resume=resume,
                version_number=ResumeVersion.objects.filter(resume=resume).count() + 1,
                title=resume.title,
                resume_data=resume.resume_data,
                changes_summary=f"Auto-saved before restoring version {version.version_number}",
                created_by=request.user
            )
            
            # Restore the selected version
            resume.title = version.title
            resume.resume_data = version.resume_data
            resume.save()
            
            # Mark versions appropriately
            ResumeVersion.objects.filter(resume=resume).update(is_current=False)
            current_version.is_current = True
            current_version.save(update_fields=['is_current'])
        
        return Response({
            'message': f'Resume restored to version {version.version_number}',
            'new_version_id': current_version.id
        })

    @drf_action(detail=False, methods=['get'])
    def by_resume(self, request):
        """
        Get versions for a specific resume.
        GET /resume-versions/by_resume/?resume_id={id}
        """
        resume_id = request.query_params.get('resume_id')
        if not resume_id:
            return Response(
                {'error': 'resume_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verify user owns the resume
            resume = Resume.objects.get(id=resume_id, user=request.user)
            versions = self.get_queryset().filter(resume=resume)
            
            page = self.paginate_queryset(versions)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(versions, many=True)
            return Response(serializer.data)
            
        except Resume.DoesNotExist:
            return Response(
                {'error': 'Resume not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @drf_action(detail=False, methods=['post'])
    def compare(self, request):
        """
        Compare two resume versions.
        POST /resume-versions/compare/
        """
        version1_id = request.data.get('version1_id')
        version2_id = request.data.get('version2_id')
        
        if not version1_id or not version2_id:
            return Response(
                {'error': 'Both version1_id and version2_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            version1 = self.get_queryset().get(id=version1_id)
            version2 = self.get_queryset().get(id=version2_id)
            
            # Basic comparison (can be enhanced with diff algorithms)
            comparison = {
                'version1': {
                    'id': version1.id,
                    'version_number': version1.version_number,
                    'title': version1.title,
                    'created_at': version1.created_at,
                },
                'version2': {
                    'id': version2.id,
                    'version_number': version2.version_number,
                    'title': version2.title,
                    'created_at': version2.created_at,
                },
                'differences': {
                    'title_changed': version1.title != version2.title,
                    'data_changed': version1.resume_data != version2.resume_data,
                }
            }
            
            return Response(comparison)
            
        except ResumeVersion.DoesNotExist:
            return Response(
                {'error': 'One or both versions not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ResumeShareViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing resume sharing.
    Provides sharing functionality with permission controls.
    """
    serializer_class = ResumeShareSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['permission_level', 'is_active']
    search_fields = ['shared_with_email', 'shared_with_name']

    def get_queryset(self):
        """Filter shares to user's resumes."""
        return ResumeShare.objects.filter(
            resume__user=self.request.user
        ).select_related('resume', 'shared_by')

    def perform_create(self, serializer):
        """Set shared_by when creating share."""
        serializer.save(shared_by=self.request.user)

    @drf_action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """
        Revoke resume share access.
        POST /resume-shares/{id}/revoke/
        """
        share = self.get_object()
        share.is_active = False
        share.revoked_at = timezone.now()
        share.save(update_fields=['is_active', 'revoked_at'])
        
        return Response({'message': 'Share access revoked'})

    @drf_action(detail=False, methods=['get'])
    def by_resume(self, request):
        """
        Get shares for a specific resume.
        GET /resume-shares/by_resume/?resume_id={id}
        """
        resume_id = request.query_params.get('resume_id')
        if not resume_id:
            return Response(
                {'error': 'resume_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        shares = self.get_queryset().filter(resume_id=resume_id)
        serializer = self.get_serializer(shares, many=True)
        return Response(serializer.data)


class ResumeCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing resume comments.
    Provides comment functionality with threading support.
    """
    serializer_class = ResumeCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['section', 'is_resolved']
    search_fields = ['content', 'author_name']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter comments to user's resumes."""
        return ResumeComment.objects.filter(
            resume__user=self.request.user
        ).select_related('resume')

    @drf_action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Mark comment as resolved.
        POST /resume-comments/{id}/resolve/
        """
        comment = self.get_object()
        comment.is_resolved = True
        comment.resolved_at = timezone.now()
        comment.save(update_fields=['is_resolved', 'resolved_at'])
        
        return Response({'message': 'Comment marked as resolved'})

    @drf_action(detail=False, methods=['get'])
    def by_resume(self, request):
        """
        Get comments for a specific resume.
        GET /resume-comments/by_resume/?resume_id={id}
        """
        resume_id = request.query_params.get('resume_id')
        if not resume_id:
            return Response(
                {'error': 'resume_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        comments = self.get_queryset().filter(resume_id=resume_id)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)


class ResumeExportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing resume exports.
    Provides export functionality in various formats.
    """
    serializer_class = ResumeExportSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['format', 'status']
    ordering_fields = ['created_at', 'file_size']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter exports to user's resumes."""
        return ResumeExport.objects.filter(
            resume__user=self.request.user
        ).select_related('resume')

    @drf_action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Download exported resume file.
        GET /resume-exports/{id}/download/
        """
        export = self.get_object()
        
        if export.status != 'completed':
            return Response(
                {'error': 'Export not ready for download'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Increment download count on the resume
        export.resume.download_count += 1
        export.resume.save(update_fields=['download_count'])
        
        # In a real implementation, this would serve the actual file
        return Response({
            'download_url': export.file_path,
            'filename': f"{export.resume.title}.{export.format}",
            'file_size': export.file_size
        })

    @drf_action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate new resume export.
        POST /resume-exports/generate/
        """
        resume_id = request.data.get('resume_id')
        format_type = request.data.get('format', 'pdf')
        
        if not resume_id:
            return Response(
                {'error': 'resume_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            resume = Resume.objects.get(id=resume_id, user=request.user)
        except Resume.DoesNotExist:
            return Response(
                {'error': 'Resume not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create export record
        export_data = {
            'resume': resume.id,
            'format': format_type,
            'status': 'processing',
            'metadata': request.data.get('metadata', {})
        }
        
        serializer = ResumeExportSerializer(data=export_data)
        
        if serializer.is_valid():
            export = serializer.save()
            
            # In a real implementation, this would trigger async export generation
            # For now, we'll simulate it
            export.status = 'completed'
            export.file_path = f"exports/{export.id}.{format_type}"
            export.file_size = 1024  # Simulated file size
            export.save()
            
            return Response(
                ResumeExportSerializer(export).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @drf_action(detail=False, methods=['get'])
    def by_resume(self, request):
        """
        Get exports for a specific resume.
        GET /resume-exports/by_resume/?resume_id={id}
        """
        resume_id = request.query_params.get('resume_id')
        if not resume_id:
            return Response(
                {'error': 'resume_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        exports = self.get_queryset().filter(resume_id=resume_id)
        serializer = self.get_serializer(exports, many=True)
        return Response(serializer.data)