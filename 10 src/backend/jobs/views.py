"""
Jobs app views for Epic 1: Job Search & Geolocation Mapping.
"""

import math
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.db.models import Q, F, Count, Avg
from django.utils import timezone
# Removed GIS imports - using simple distance calculation instead
from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
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
    """Custom pagination for job listings."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class JobListView(generics.ListAPIView):
    """Job list view with filtering and search."""
    serializer_class = JobSerializer
    pagination_class = JobPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'company__name']
    ordering_fields = ['posted_date', 'title', 'salary_min', 'salary_max']
    ordering = ['-posted_date']
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get filtered job queryset."""
        queryset = Job.objects.filter(is_active=True).select_related(
            'company', 'location'
        ).prefetch_related('required_skills__skill')
        
        # Apply custom filters
        queryset = self._apply_filters(queryset)
        
        return queryset
    
    def _apply_filters(self, queryset):
        """Apply custom filters to queryset."""
        # Job type filter
        job_type = self.request.query_params.get('job_type')
        if job_type:
            queryset = queryset.filter(job_type=job_type)
        
        # Experience level filter
        experience_level = self.request.query_params.get('experience_level')
        if experience_level:
            queryset = queryset.filter(experience_level=experience_level)
        
        # Remote type filter
        remote_type = self.request.query_params.get('remote_type')
        if remote_type:
            queryset = queryset.filter(remote_type=remote_type)
        
        # Salary range filter
        salary_min = self.request.query_params.get('salary_min')
        if salary_min:
            queryset = queryset.filter(salary_min__gte=salary_min)
        
        salary_max = self.request.query_params.get('salary_max')
        if salary_max:
            queryset = queryset.filter(salary_max__lte=salary_max)
        
        # Posted date filter
        posted_since = self.request.query_params.get('posted_since')
        if posted_since:
            try:
                days = int(posted_since)
                since_date = timezone.now() - timedelta(days=days)
                queryset = queryset.filter(posted_date__gte=since_date)
            except ValueError:
                pass
        
        # Company filter
        company = self.request.query_params.get('company')
        if company:
            queryset = queryset.filter(company__name__icontains=company)
        
        # Skills filter
        skills = self.request.query_params.get('skills')
        if skills:
            skill_names = [s.strip() for s in skills.split(',')]
            queryset = queryset.filter(
                required_skills__skill__name__in=skill_names
            ).distinct()
        
        return queryset


class JobDetailView(generics.RetrieveAPIView):
    """Job detail view."""
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Job.objects.filter(is_active=True).select_related(
            'company', 'location'
        ).prefetch_related('required_skills__skill')


class JobCreateView(generics.CreateAPIView):
    """Job creation view (admin only)."""
    serializer_class = JobCreateSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def perform_create(self, serializer):
        """Create job with additional processing."""
        job = serializer.save()
        
        # Log job creation activity
        from core.utils import log_user_activity
        log_user_activity(
            self.request.user, 'job_creation',
            f'Created job: {job.title}',
            request=self.request
        )


class JobUpdateView(generics.UpdateAPIView):
    """Job update view (admin only)."""
    serializer_class = JobUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return Job.objects.all()


class JobSearchView(APIView):
    """Advanced job search with geolocation."""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Search jobs with advanced filters."""
        serializer = JobSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        queryset = Job.objects.filter(is_active=True).select_related(
            'company', 'location'
        ).prefetch_related('required_skills__skill')
        
        # Apply search filters
        queryset = self._apply_search_filters(queryset, data)
        
        # Apply geolocation filtering if location provided
        if data.get('location'):
            queryset = self._apply_location_filter(queryset, data)
        
        # Paginate results
        paginator = JobPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = JobSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        
        serializer = JobSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
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
        
        # Job type filter
        job_type = data.get('job_type')
        if job_type:
            queryset = queryset.filter(job_type=job_type)
        
        # Experience level filter
        experience_level = data.get('experience_level')
        if experience_level:
            queryset = queryset.filter(experience_level=experience_level)
        
        # Remote type filter
        remote_type = data.get('remote_type')
        if remote_type:
            queryset = queryset.filter(remote_type=remote_type)
        
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


class NearbyJobsView(APIView):
    """Get jobs near user's location."""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get nearby jobs based on coordinates or location."""
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        location = request.query_params.get('location')
        radius = int(request.query_params.get('radius', 25))
        
        if not (lat and lng) and not location:
            return Response(
                {"error": "Either coordinates (lat, lng) or location is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = Job.objects.filter(is_active=True).select_related(
            'company', 'location'
        ).prefetch_related('required_skills__skill')
        
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
        paginator = JobPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = JobSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        
        serializer = JobSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
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


class JobMapView(APIView):
    """Get job data for map visualization."""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get jobs with location data for map display."""
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


class SavedJobsView(generics.ListAPIView):
    """User's saved jobs."""
    serializer_class = SavedJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = JobPagination
    
    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user).select_related(
            'job__company', 'job__location'
        ).order_by('-saved_date')


class SaveJobView(APIView):
    """Save a job."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """Save a job."""
        try:
            job = Job.objects.get(id=pk, is_active=True)
        except Job.DoesNotExist:
            return Response(
                {"error": "Job not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
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


class UnsaveJobView(APIView):
    """Unsave a job."""
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, pk):
        """Unsave a job."""
        try:
            saved_job = SavedJob.objects.get(user=request.user, job_id=pk)
            saved_job.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SavedJob.DoesNotExist:
            return Response(
                {"error": "Saved job not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class ApplyJobView(APIView):
    """Apply to a job."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """Apply to a job."""
        data = request.data.copy()
        data['job_id'] = pk
        
        serializer = JobApplicationSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            application = serializer.save()
            
            # Log activity
            from core.utils import log_user_activity
            log_user_activity(
                request.user, 'job_application',
                f'Applied to job: {application.job.title}',
                request=request
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobApplicationListView(generics.ListAPIView):
    """User's job applications."""
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = JobPagination
    
    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user).select_related(
            'job__company', 'job__location'
        ).order_by('-applied_date')


class JobApplicationDetailView(generics.RetrieveUpdateAPIView):
    """Job application detail and update."""
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user)


class JobAlertListView(generics.ListCreateAPIView):
    """Job alerts list and creation."""
    serializer_class = JobAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return JobAlert.objects.filter(user=self.request.user).order_by('-created_at')


class JobAlertDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Job alert detail, update, and deletion."""
    serializer_class = JobAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return JobAlert.objects.filter(user=self.request.user)


class SkillListView(generics.ListCreateAPIView):
    """Skills list and creation."""
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SkillCreateSerializer
        return SkillSerializer
    
    def get_queryset(self):
        queryset = Skill.objects.all().order_by('name')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Search by name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset


class UserSkillListView(generics.ListCreateAPIView):
    """User skills list and creation."""
    serializer_class = UserSkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserSkill.objects.filter(user=self.request.user).select_related('skill')


class UserSkillDetailView(generics.RetrieveUpdateDestroyAPIView):
    """User skill detail, update, and deletion."""
    serializer_class = UserSkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserSkill.objects.filter(user=self.request.user)


# Function-based views for backward compatibility
# The following FBVs are refactored to CBVs below.

class JobListCBV(APIView):
    """CBV version of job_list (was FBV)"""
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        view = JobListView.as_view()
        return view(request)

class JobDetailCBV(APIView):
    """CBV version of job_detail (was FBV)"""
    permission_classes = [permissions.AllowAny]
    def get(self, request, pk):
        view = JobDetailView.as_view()
        return view(request, pk=pk)

class JobSearchCBV(APIView):
    """CBV version of job_search (was FBV)"""
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        view = JobSearchView.as_view()
        return view(request)

class NearbyJobsCBV(APIView):
    """CBV version of nearby_jobs (was FBV)"""
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        view = NearbyJobsView.as_view()
        return view(request)

class JobMapCBV(APIView):
    """CBV version of job_map (was FBV)"""
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        view = JobMapView.as_view()
        return view(request)

class SavedJobsCBV(APIView):
    """CBV version of saved_jobs (was FBV)"""
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        view = SavedJobsView.as_view()
        return view(request)

class SaveJobCBV(APIView):
    """CBV version of save_job (was FBV)"""
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, pk):
        view = SaveJobView.as_view()
        return view(request, pk=pk)

class UnsaveJobCBV(APIView):
    """CBV version of unsave_job (was FBV)"""
    permission_classes = [permissions.IsAuthenticated]
    def delete(self, request, pk):
        view = UnsaveJobView.as_view()
        return view(request, pk=pk)

class ApplyJobCBV(APIView):
    """CBV version of apply_job (was FBV)"""
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, pk):
        view = ApplyJobView.as_view()
        return view(request, pk=pk)

class JobApplicationsCBV(APIView):
    """CBV version of job_applications (was FBV)"""
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        view = JobApplicationListView.as_view()
        return view(request)

class SkillsCBV(APIView):
    """CBV version of skills (was FBV)"""
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        view = SkillListView.as_view()
        return view(request)

class UserSkillsCBV(APIView):
    """CBV version of user_skills (was FBV)"""
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        view = UserSkillListView.as_view()
        return view(request)
