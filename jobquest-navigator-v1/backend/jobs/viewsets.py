"""
Jobs app ViewSets for Epic 1: Job Search & Geolocation Mapping.
Modern ViewSet-based API architecture aligned with Epic 5 standards.
"""

import math
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.db.models import Q, F, Count, Avg
from django.utils import timezone
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from core.models import Location, Company
from core.permissions import AuthenticatedAndActive
from .models import (
    Job, JobApplication, SavedJob, JobAlert, Skill, UserSkill, JobSkill
)
from .serializers import (
    JobSerializer, JobCreateSerializer, JobUpdateSerializer,
    JobApplicationSerializer, SavedJobSerializer, JobAlertSerializer,
    SkillSerializer, SkillCreateSerializer, UserSkillSerializer,
    JobSearchSerializer
)


class JobPagination(PageNumberPagination):
    """Custom pagination for job endpoints."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class JobViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing jobs.
    Provides CRUD operations, search, and geolocation features.
    """
    permission_classes = [permissions.AllowAny]
    pagination_class = JobPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'company__name']
    filterset_fields = ['job_type', 'experience_level', 'remote_type']
    ordering_fields = ['posted_date', 'title', 'salary_min', 'salary_max']
    ordering = ['-posted_date']
    
    def get_queryset(self):
        return Job.objects.filter(is_active=True).select_related(
            'company', 'location'
        ).prefetch_related('required_skills__skill')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return JobCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return JobUpdateSerializer
        return JobSerializer
    
    def get_permissions(self):
        """Admin-only permissions for create/update/delete."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    
    def list(self, request, *args, **kwargs):
        """Enhanced list with custom filtering."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Apply custom filters
        queryset = self._apply_custom_filters(queryset, request)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Create job with activity logging."""
        response = super().create(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_201_CREATED:
            # Log job creation activity
            from core.utils import log_user_activity
            job_title = response.data.get('title', 'Unknown')
            log_user_activity(
                request.user, 'job_creation',
                f'Created job: {job_title}',
                request=request
            )
        
        return response
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced job search with geolocation filtering."""
        serializer = JobSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        queryset = self.get_queryset()
        
        # Apply search filters
        queryset = self._apply_search_filters(queryset, data)
        
        # Apply geolocation filtering if location provided
        if data.get('location'):
            queryset = self._apply_location_filter(queryset, data)
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Get jobs near user's location."""
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        location = request.query_params.get('location')
        radius = int(request.query_params.get('radius', 25))
        
        if not (lat and lng) and not location:
            return Response(
                {"error": "Either coordinates (lat, lng) or location is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset()
        
        if lat and lng:
            try:
                lat = float(lat)
                lng = float(lng)
                
                # Filter jobs within radius
                filtered_jobs = []
                for job in queryset:
                    if job.location.latitude and job.location.longitude:
                        distance = self._calculate_distance(
                            lat, lng,
                            job.location.latitude, job.location.longitude
                        )
                        if distance <= radius:
                            filtered_jobs.append(job.id)
                
                queryset = queryset.filter(id__in=filtered_jobs)
            except ValueError:
                return Response(
                    {"error": "Invalid coordinates"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        elif location:
            # Use location-based filtering
            queryset = queryset.filter(
                Q(location__city__icontains=location) |
                Q(location__state__icontains=location) |
                Q(location__country__icontains=location)
            )
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def map(self, request):
        """Get job data for map visualization."""
        # Get bounds from query parameters
        north = request.query_params.get('north')
        south = request.query_params.get('south')
        east = request.query_params.get('east')
        west = request.query_params.get('west')
        
        queryset = Job.objects.filter(
            is_active=True,
            location__latitude__isnull=False,
            location__longitude__isnull=False
        ).select_related('company', 'location')
        
        # Apply bounds filtering if provided
        if all([north, south, east, west]):
            try:
                north = float(north)
                south = float(south)
                east = float(east)
                west = float(west)
                
                queryset = queryset.filter(
                    location__latitude__gte=south,
                    location__latitude__lte=north,
                    location__longitude__gte=west,
                    location__longitude__lte=east
                )
            except ValueError:
                pass
        
        # Limit results for performance
        queryset = queryset[:500]
        
        # Format data for map
        jobs_data = []
        for job in queryset:
            jobs_data.append({
                'id': str(job.id),
                'title': job.title,
                'company': job.company.name,
                'location': {
                    'lat': job.location.latitude,
                    'lng': job.location.longitude,
                    'city': job.location.city,
                    'state': job.location.state,
                    'country': job.location.country
                },
                'job_type': job.job_type,
                'experience_level': job.experience_level,
                'remote_type': job.remote_type,
                'salary_min': job.salary_min,
                'salary_max': job.salary_max,
                'posted_date': job.posted_date
            })
        
        return Response({
            'jobs': jobs_data,
            'count': len(jobs_data)
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def save(self, request, pk=None):
        """Save a job."""
        job = self.get_object()
        
        # Check if already saved
        if SavedJob.objects.filter(user=request.user, job=job).exists():
            return Response(
                {"error": "Job already saved"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        saved_job = SavedJob.objects.create(
            user=request.user,
            job=job,
            notes=request.data.get('notes', '')
        )
        
        serializer = SavedJobSerializer(saved_job, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def unsave(self, request, pk=None):
        """Unsave a job."""
        job = self.get_object()
        
        try:
            saved_job = SavedJob.objects.get(user=request.user, job=job)
            saved_job.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SavedJob.DoesNotExist:
            return Response(
                {"error": "Job not saved"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def apply(self, request, pk=None):
        """Apply to a job."""
        job = self.get_object()
        data = request.data.copy()
        data['job'] = job.id
        
        serializer = JobApplicationSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            application = serializer.save(user=request.user, job=job)
            
            # Log activity
            from core.utils import log_user_activity
            log_user_activity(
                request.user, 'job_application',
                f'Applied to job: {job.title}',
                request=request
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _apply_custom_filters(self, queryset, request):
        """Apply custom filters to queryset."""
        # Salary range filter
        salary_min = request.query_params.get('salary_min')
        if salary_min:
            queryset = queryset.filter(salary_min__gte=salary_min)
        
        salary_max = request.query_params.get('salary_max')
        if salary_max:
            queryset = queryset.filter(salary_max__lte=salary_max)
        
        # Posted date filter
        posted_since = request.query_params.get('posted_since')
        if posted_since:
            try:
                days = int(posted_since)
                since_date = timezone.now() - timedelta(days=days)
                queryset = queryset.filter(posted_date__gte=since_date)
            except ValueError:
                pass
        
        # Company filter
        company = request.query_params.get('company')
        if company:
            queryset = queryset.filter(company__name__icontains=company)
        
        # Skills filter
        skills = request.query_params.get('skills')
        if skills:
            skill_names = [s.strip() for s in skills.split(',')]
            queryset = queryset.filter(
                required_skills__skill__name__in=skill_names
            ).distinct()
        
        return queryset
    
    def _apply_search_filters(self, queryset, data):
        """Apply search filters to queryset."""
        # Keywords search
        keywords = data.get('keywords')
        if keywords:
            queryset = queryset.filter(
                Q(title__icontains=keywords) |
                Q(description__icontains=keywords) |
                Q(company__name__icontains=keywords)
            )
        
        # Basic filters
        for field in ['job_type', 'experience_level', 'remote_type']:
            value = data.get(field)
            if value:
                queryset = queryset.filter(**{field: value})
        
        # Salary range filter
        salary_min = data.get('salary_min')
        if salary_min:
            queryset = queryset.filter(
                Q(salary_min__gte=salary_min) | Q(salary_min__isnull=True)
            )
        
        salary_max = data.get('salary_max')
        if salary_max:
            queryset = queryset.filter(
                Q(salary_max__lte=salary_max) | Q(salary_max__isnull=True)
            )
        
        # Posted date filter
        posted_since = data.get('posted_since')
        if posted_since:
            since_date = timezone.now() - timedelta(days=posted_since)
            queryset = queryset.filter(posted_date__gte=since_date)
        
        # Company filter
        company = data.get('company')
        if company:
            queryset = queryset.filter(company__name__icontains=company)
        
        # Skills filter
        skills = data.get('skills')
        if skills:
            queryset = queryset.filter(
                required_skills__skill__name__in=skills
            ).distinct()
        
        return queryset
    
    def _apply_location_filter(self, queryset, data):
        """Apply geolocation filtering."""
        location_query = data.get('location')
        radius = data.get('radius', 25)  # Default 25km radius
        
        try:
            # Try to find exact location match first
            location = Location.objects.filter(
                Q(city__icontains=location_query) |
                Q(state__icontains=location_query) |
                Q(country__icontains=location_query)
            ).first()
            
            if location and location.latitude and location.longitude:
                # Filter jobs within radius
                queryset = queryset.filter(
                    location__latitude__isnull=False,
                    location__longitude__isnull=False
                )
                
                # Calculate distance and filter
                filtered_jobs = []
                for job in queryset:
                    if job.location.latitude and job.location.longitude:
                        distance = self._calculate_distance(
                            location.latitude, location.longitude,
                            job.location.latitude, job.location.longitude
                        )
                        if distance <= radius:
                            filtered_jobs.append(job.id)
                
                queryset = queryset.filter(id__in=filtered_jobs)
            else:
                # Fallback to text-based location search
                queryset = queryset.filter(
                    Q(location__city__icontains=location_query) |
                    Q(location__state__icontains=location_query) |
                    Q(location__country__icontains=location_query)
                )
        
        except Exception:
            # Fallback to text-based search if geolocation fails
            queryset = queryset.filter(
                Q(location__city__icontains=location_query) |
                Q(location__state__icontains=location_query) |
                Q(location__country__icontains=location_query)
            )
        
        return queryset
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points in kilometers."""
        # Haversine formula
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c


class SavedJobViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing user's saved jobs.
    Provides read-only access to saved jobs.
    """
    serializer_class = SavedJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = JobPagination
    
    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user).select_related(
            'job__company', 'job__location'
        ).order_by('-saved_date')


class JobApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing job applications.
    Provides CRUD operations for job applications.
    """
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = JobPagination
    
    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user).select_related(
            'job__company', 'job__location'
        ).order_by('-applied_date')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class JobAlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing job alerts.
    Provides CRUD operations for job alerts.
    """
    serializer_class = JobAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return JobAlert.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SkillViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing skills.
    Provides CRUD operations and search functionality.
    """
    permission_classes = [permissions.AllowAny]
    pagination_class = JobPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']
    filterset_fields = ['category']
    
    def get_queryset(self):
        return Skill.objects.all().order_by('name')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SkillCreateSerializer
        return SkillSerializer


class UserSkillViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user skills.
    Provides CRUD operations for user skills.
    """
    serializer_class = UserSkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserSkill.objects.filter(user=self.request.user).select_related('skill')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)