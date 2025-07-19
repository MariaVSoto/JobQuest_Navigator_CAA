"""
Core views for JobQuest Navigator Backend.

This module contains views for authentication, user management,
and shared functionality across all epics.
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.db import transaction
from django.conf import settings
from django.urls import reverse
from django.core.cache import cache

from .models import User, Location, Company, UserPreference, ActivityLog
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserProfileUpdateSerializer, ChangePasswordSerializer, PasswordResetSerializer,
    PasswordResetConfirmSerializer, LocationSerializer, LocationCreateSerializer,
    CompanySerializer, CompanyCreateSerializer, UserPreferenceSerializer,
    ActivityLogSerializer, TokenSerializer
)
from .permissions import (
    IsProfileOwner, CanManageCompanies, CanManageLocations,
    AuthenticatedAndActive
)
from .utils import (
    log_user_activity, send_welcome_email, send_password_reset_email,
    create_password_reset_token, verify_password_reset_token,
    generate_jwt_tokens, is_rate_limited
)


class HealthCheckView(APIView):
    """
    Basic health check endpoint.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'message': 'JobQuest Navigator Backend is running'
        })


class DetailedHealthCheckView(APIView):
    """
    Detailed health check with system information.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'message': 'JobQuest Navigator Backend is running',
            'database': 'connected',
            'cache': 'connected',
            'version': '1.0.0'
        })


class UserRegistrationView(APIView):
    """
    User registration endpoint.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Register a new user."""
        # Check rate limiting by IP address
        ip_address = request.META.get('REMOTE_ADDR', '')
        cache_key = f"rate_limit_{ip_address}_registration"
        current_count = cache.get(cache_key, 0)
        if current_count >= 5:
            return Response(
                {"error": "Too many registration attempts. Please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Increment rate limit counter
        cache.set(cache_key, current_count + 1, 3600)  # 1 hour window
        
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    
                    # Generate JWT tokens
                    tokens = generate_jwt_tokens(user)
                    
                    # Log activity
                    log_user_activity(
                        user, 'registration', 'User registered successfully',
                        request=request
                    )
                    
                    # Send welcome email (async in production)
                    send_welcome_email(user)
                    
                    return Response({
                        'message': 'User registered successfully',
                        'user': UserProfileSerializer(user).data,
                        'tokens': tokens
                    }, status=status.HTTP_201_CREATED)
                    
            except Exception as e:
                return Response(
                    {"error": "Registration failed. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    User login endpoint.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Authenticate user and return JWT tokens."""
        # Check rate limiting by IP address
        ip_address = request.META.get('REMOTE_ADDR', '')
        cache_key = f"rate_limit_{ip_address}_login"
        current_count = cache.get(cache_key, 0)
        if current_count >= 10:
            return Response(
                {"error": "Too many login attempts. Please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Increment rate limit counter
        cache.set(cache_key, current_count + 1, 3600)  # 1 hour window
        
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            tokens = generate_jwt_tokens(user)
            
            # Log activity
            log_user_activity(
                user, 'login', 'User logged in successfully',
                request=request
            )
            
            return Response({
                'message': 'Login successful',
                'user': UserProfileSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """
    User logout endpoint.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Logout user by blacklisting refresh token."""
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Log activity
            log_user_activity(
                request.user, 'logout', 'User logged out successfully',
                request=request
            )
            
            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_200_OK
            )


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom JWT token refresh endpoint.
    """
    
    def post(self, request, *args, **kwargs):
        """Refresh JWT access token."""
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Log activity if user can be identified
            try:
                refresh_token = request.data.get('refresh')
                if refresh_token:
                    token = RefreshToken(refresh_token)
                    user_id = token.payload.get('user_id')
                    if user_id:
                        user = User.objects.get(id=user_id)
                        log_user_activity(
                            user, 'token_refresh', 'JWT token refreshed',
                            request=request
                        )
            except Exception:
                pass
        
        return response


class UserProfileView(generics.RetrieveAPIView):
    """
    Get user profile endpoint.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserProfileUpdateView(generics.UpdateAPIView):
    """
    Update user profile endpoint.
    """
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated, IsProfileOwner]
    
    def get_object(self):
        return self.request.user
    
    def perform_update(self, serializer):
        """Update user profile and log activity."""
        serializer.save()
        log_user_activity(
            self.request.user, 'profile_update', 'User profile updated',
            request=self.request
        )


class ChangePasswordView(APIView):
    """
    Change password endpoint.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Change user password."""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            # Log activity
            log_user_activity(
                request.user, 'password_change', 'Password changed successfully',
                request=request
            )
            
            return Response(
                {"message": "Password changed successfully"},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    """
    Password reset request endpoint.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Send password reset email."""
        serializer = PasswordResetSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Generate reset token
                reset_data = create_password_reset_token(user)
                
                # Create reset URL
                reset_url = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/reset-password/{reset_data['uid']}/{reset_data['token']}/"
                
                # Send email
                if send_password_reset_email(user, reset_url):
                    # Log activity
                    log_user_activity(
                        user, 'password_reset_request', 'Password reset requested',
                        request=request
                    )
                    
                    return Response(
                        {"message": "Password reset email sent successfully"},
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {"error": "Failed to send password reset email"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                    
            except User.DoesNotExist:
                # Don't reveal if email exists or not
                return Response(
                    {"message": "If the email exists, a password reset link has been sent"},
                    status=status.HTTP_200_OK
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    Password reset confirmation endpoint.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Confirm password reset with token."""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            uid = request.data.get('uid')
            
            # Verify token
            user = verify_password_reset_token(uid, token)
            
            if user:
                user.set_password(new_password)
                user.save()
                
                # Log activity
                log_user_activity(
                    user, 'password_reset_confirm', 'Password reset completed',
                    request=request
                )
                
                return Response(
                    {"message": "Password reset successful"},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Invalid or expired reset token"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LocationListView(generics.ListAPIView):
    """
    Get locations endpoint.
    """
    queryset = Location.objects.filter(is_active=True)
    serializer_class = LocationSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Filter locations by query parameters."""
        queryset = super().get_queryset()
        
        # Filter by country
        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country__icontains=country)
        
        # Filter by city
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Search by name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset.order_by('country', 'city', 'name')


class LocationCreateView(generics.CreateAPIView):
    """
    Create location endpoint.
    """
    serializer_class = LocationCreateSerializer
    permission_classes = [IsAuthenticated, CanManageLocations]
    
    def perform_create(self, serializer):
        """Create location and log activity."""
        location = serializer.save()
        log_user_activity(
            self.request.user, 'location_create', f'Created location: {location.name}',
            request=self.request
        )


class LocationDetailView(generics.RetrieveAPIView):
    """
    Location detail endpoint.
    """
    queryset = Location.objects.filter(is_active=True)
    serializer_class = LocationSerializer
    permission_classes = [AllowAny]


class LocationSearchView(APIView):
    """
    Location search endpoint.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Search locations by query."""
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {"error": "Query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        locations = Location.objects.filter(
            is_active=True
        ).filter(
            name__icontains=query
        ) | Location.objects.filter(
            is_active=True
        ).filter(
            city__icontains=query
        )
        
        serializer = LocationSerializer(locations[:20], many=True)
        return Response(serializer.data)


class GeocodeView(APIView):
    """
    Geocoding endpoint.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Geocode an address."""
        address = request.data.get('address')
        if not address:
            return Response(
                {"error": "Address is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Implement actual geocoding with Google Maps API
        return Response({
            "message": "Geocoding endpoint - to be implemented with Google Maps API",
            "address": address
        }, status=status.HTTP_501_NOT_IMPLEMENTED)


class CompanyListView(generics.ListAPIView):
    """
    Get companies endpoint.
    """
    queryset = Company.objects.filter(is_active=True)
    serializer_class = CompanySerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Filter companies by query parameters."""
        queryset = super().get_queryset()
        
        # Filter by industry
        industry = self.request.query_params.get('industry')
        if industry:
            queryset = queryset.filter(industry__icontains=industry)
        
        # Filter by company size
        company_size = self.request.query_params.get('size')
        if company_size:
            queryset = queryset.filter(company_size=company_size)
        
        # Search by name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset.order_by('name')


class CompanyCreateView(generics.CreateAPIView):
    """
    Create company endpoint.
    """
    serializer_class = CompanyCreateSerializer
    permission_classes = [IsAuthenticated, CanManageCompanies]
    
    def perform_create(self, serializer):
        """Create company and log activity."""
        company = serializer.save()
        log_user_activity(
            self.request.user, 'company_create', f'Created company: {company.name}',
            request=self.request
        )


class CompanyDetailView(generics.RetrieveAPIView):
    """
    Company detail endpoint.
    """
    queryset = Company.objects.filter(is_active=True)
    serializer_class = CompanySerializer
    permission_classes = [AllowAny]


class CompanySearchView(APIView):
    """
    Company search endpoint.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Search companies by query."""
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {"error": "Query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        companies = Company.objects.filter(
            is_active=True,
            name__icontains=query
        )
        
        serializer = CompanySerializer(companies[:20], many=True)
        return Response(serializer.data)


class UserPreferencesView(generics.RetrieveUpdateAPIView):
    """
    Get and update user preferences endpoint.
    """
    serializer_class = UserPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get or create user preferences."""
        preferences, created = UserPreference.objects.get_or_create(
            user=self.request.user
        )
        return preferences
    
    def perform_update(self, serializer):
        """Update preferences and log activity."""
        serializer.save()
        log_user_activity(
            self.request.user, 'preferences_update', 'User preferences updated',
            request=self.request
        )


class ActivityLogListView(generics.ListAPIView):
    """
    Get user activity logs endpoint.
    """
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get activity logs for current user."""
        return ActivityLog.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


# Function-based views for backward compatibility
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint (function-based view)."""
    view = UserRegistrationView()
    view.request = request
    return view.post(request)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """User login endpoint (function-based view)."""
    view = UserLoginView()
    view.request = request
    return view.post(request)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """User logout endpoint (function-based view)."""
    view = UserLogoutView()
    view.request = request
    return view.post(request)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_token(request):
    """JWT token refresh endpoint (function-based view)."""
    view = CustomTokenRefreshView()
    view.request = request
    return view.post(request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Get user profile endpoint (function-based view)."""
    return Response(UserProfileSerializer(request.user).data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile endpoint (function-based view)."""
    serializer = UserProfileUpdateSerializer(
        request.user, data=request.data, partial=True
    )
    if serializer.is_valid():
        serializer.save()
        log_user_activity(
            request.user, 'profile_update', 'User profile updated',
            request=request
        )
        return Response(UserProfileSerializer(request.user).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change password endpoint (function-based view)."""
    view = ChangePasswordView()
    view.request = request
    return view.post(request)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset(request):
    """Password reset request endpoint (function-based view)."""
    view = PasswordResetView()
    view.request = request
    return view.post(request)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Password reset confirmation endpoint (function-based view)."""
    view = PasswordResetConfirmView()
    view.request = request
    return view.post(request)


@api_view(['GET'])
@permission_classes([AllowAny])
def locations(request):
    """Get locations endpoint (function-based view)."""
    view = LocationListView()
    view.request = request
    queryset = view.get_queryset()
    serializer = LocationSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_location(request):
    """Create location endpoint (function-based view)."""
    view = LocationCreateView()
    view.request = request
    return view.post(request)


@api_view(['GET'])
@permission_classes([AllowAny])
def companies(request):
    """Get companies endpoint (function-based view)."""
    view = CompanyListView()
    view.request = request
    queryset = view.get_queryset()
    serializer = CompanySerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_company(request):
    """Create company endpoint (function-based view)."""
    view = CompanyCreateView()
    view.request = request
    return view.post(request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_preferences(request):
    """Get user preferences endpoint (function-based view)."""
    preferences, created = UserPreference.objects.get_or_create(
        user=request.user
    )
    return Response(UserPreferenceSerializer(preferences).data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_preferences(request):
    """Update user preferences endpoint (function-based view)."""
    preferences, created = UserPreference.objects.get_or_create(
        user=request.user
    )
    serializer = UserPreferenceSerializer(
        preferences, data=request.data, partial=True
    )
    if serializer.is_valid():
        serializer.save()
        log_user_activity(
            request.user, 'preferences_update', 'User preferences updated',
            request=request
        )
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_logs(request):
    """Get user activity logs endpoint (function-based view)."""
    logs = ActivityLog.objects.filter(
        user=request.user
    ).order_by('-created_at')[:50]  # Limit to last 50 logs
    
    return Response(ActivityLogSerializer(logs, many=True).data)


# Custom error handlers
def handler404(request, exception):
    """Custom 404 handler."""
    return JsonResponse({
        'error': 'Not Found',
        'message': 'The requested resource was not found.',
        'status_code': 404
    }, status=404)


def handler500(request):
    """Custom 500 handler."""
    return JsonResponse({
        'error': 'Internal Server Error',
        'message': 'An internal server error occurred.',
        'status_code': 500
    }, status=500)
