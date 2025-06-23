"""
Utility functions for JobQuest Navigator Backend.

This module contains helper functions for authentication, email sending,
token generation, and other common operations.
"""

import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)


class TokenGenerator(PasswordResetTokenGenerator):
    """
    Custom token generator for password reset and email verification.
    """
    
    def _make_hash_value(self, user, timestamp):
        """
        Hash the user's primary key and some user state that's sure to change
        after a password reset to produce a token that invalidated when it's used.
        """
        return (
            str(user.pk) + str(timestamp) + str(user.is_active) +
            str(user.password) + str(user.last_login)
        )


# Initialize token generator
account_activation_token = TokenGenerator()


def generate_random_string(length: int = 32) -> str:
    """
    Generate a random string of specified length.
    
    Args:
        length: Length of the string to generate
        
    Returns:
        Random string containing letters and digits
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_verification_code(length: int = 6) -> str:
    """
    Generate a numeric verification code.
    
    Args:
        length: Length of the code to generate
        
    Returns:
        Numeric verification code
    """
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def create_password_reset_token(user) -> Dict[str, str]:
    """
    Create password reset token for user.
    
    Args:
        user: User instance
        
    Returns:
        Dictionary containing token and uid
    """
    token = account_activation_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    return {
        'token': token,
        'uid': uid
    }


def verify_password_reset_token(uid: str, token: str):
    """
    Verify password reset token.
    
    Args:
        uid: Base64 encoded user ID
        token: Password reset token
        
    Returns:
        User instance if valid, None otherwise
    """
    try:
        from .models import User
        user_id = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=user_id)
        
        if account_activation_token.check_token(user, token):
            return user
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        pass
    
    return None


def send_password_reset_email(user, reset_url: str) -> bool:
    """
    Send password reset email to user.
    
    Args:
        user: User instance
        reset_url: Password reset URL
        
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        subject = 'JobQuest Navigator - Password Reset'
        
        # Create HTML email content
        html_message = render_to_string('emails/password_reset.html', {
            'user': user,
            'reset_url': reset_url,
            'site_name': 'JobQuest Navigator'
        })
        
        # Create plain text version
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Password reset email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False


def send_welcome_email(user) -> bool:
    """
    Send welcome email to new user.
    
    Args:
        user: User instance
        
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        subject = 'Welcome to JobQuest Navigator!'
        
        # Create HTML email content
        html_message = render_to_string('emails/welcome.html', {
            'user': user,
            'site_name': 'JobQuest Navigator'
        })
        
        # Create plain text version
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Welcome email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        return False


def send_verification_email(user, verification_url: str) -> bool:
    """
    Send email verification email to user.
    
    Args:
        user: User instance
        verification_url: Email verification URL
        
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        subject = 'JobQuest Navigator - Verify Your Email'
        
        # Create HTML email content
        html_message = render_to_string('emails/email_verification.html', {
            'user': user,
            'verification_url': verification_url,
            'site_name': 'JobQuest Navigator'
        })
        
        # Create plain text version
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Verification email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False


def get_client_ip(request) -> str:
    """
    Get client IP address from request.
    
    Args:
        request: Django request object
        
    Returns:
        Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request) -> str:
    """
    Get user agent from request.
    
    Args:
        request: Django request object
        
    Returns:
        User agent string
    """
    return request.META.get('HTTP_USER_AGENT', '')


def log_user_activity(user, action: str, description: str = '', 
                     epic: str = '', request=None, metadata: Dict = None):
    """
    Log user activity.
    
    Args:
        user: User instance
        action: Action performed
        description: Description of the action
        epic: Epic name (optional)
        request: Django request object (optional)
        metadata: Additional metadata (optional)
    """
    try:
        from .models import ActivityLog
        
        activity_data = {
            'user': user,
            'action': action,
            'description': description,
            'epic': epic,
            'metadata': metadata or {}
        }
        
        if request:
            activity_data['ip_address'] = get_client_ip(request)
            activity_data['user_agent'] = get_user_agent(request)
        
        ActivityLog.objects.create(**activity_data)
        
    except Exception as e:
        logger.error(f"Failed to log user activity: {str(e)}")


def generate_jwt_tokens(user) -> Dict[str, str]:
    """
    Generate JWT tokens for user.
    
    Args:
        user: User instance
        
    Returns:
        Dictionary containing access and refresh tokens
    """
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    }


def cache_user_session(user, session_data: Dict, timeout: int = 3600):
    """
    Cache user session data.
    
    Args:
        user: User instance
        session_data: Data to cache
        timeout: Cache timeout in seconds
    """
    cache_key = f"user_session_{user.id}"
    cache.set(cache_key, session_data, timeout)


def get_cached_user_session(user) -> Optional[Dict]:
    """
    Get cached user session data.
    
    Args:
        user: User instance
        
    Returns:
        Cached session data or None
    """
    cache_key = f"user_session_{user.id}"
    return cache.get(cache_key)


def clear_user_session_cache(user):
    """
    Clear cached user session data.
    
    Args:
        user: User instance
    """
    cache_key = f"user_session_{user.id}"
    cache.delete(cache_key)


def is_rate_limited(user, action: str, limit: int = 10, window: int = 3600) -> bool:
    """
    Check if user is rate limited for a specific action.
    
    Args:
        user: User instance
        action: Action being performed
        limit: Maximum number of actions allowed
        window: Time window in seconds
        
    Returns:
        True if rate limited, False otherwise
    """
    cache_key = f"rate_limit_{user.id}_{action}"
    current_count = cache.get(cache_key, 0)
    
    if current_count >= limit:
        return True
    
    # Increment counter
    cache.set(cache_key, current_count + 1, window)
    return False


def validate_file_upload(file, allowed_types: list = None, max_size: int = None) -> Dict[str, Any]:
    """
    Validate uploaded file.
    
    Args:
        file: Uploaded file object
        allowed_types: List of allowed MIME types
        max_size: Maximum file size in bytes
        
    Returns:
        Dictionary with validation result
    """
    result = {
        'valid': True,
        'errors': []
    }
    
    if not file:
        result['valid'] = False
        result['errors'].append('No file provided')
        return result
    
    # Check file size
    if max_size and file.size > max_size:
        result['valid'] = False
        result['errors'].append(f'File size exceeds maximum allowed size of {max_size} bytes')
    
    # Check file type
    if allowed_types and file.content_type not in allowed_types:
        result['valid'] = False
        result['errors'].append(f'File type {file.content_type} not allowed')
    
    return result


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Limit filename length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]
    
    return filename


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted file size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def create_user_directory(user, directory_type: str = 'general') -> str:
    """
    Create user-specific directory path.
    
    Args:
        user: User instance
        directory_type: Type of directory (resumes, documents, etc.)
        
    Returns:
        Directory path
    """
    return f"users/{user.id}/{directory_type}/"


def mask_email(email: str) -> str:
    """
    Mask email address for privacy.
    
    Args:
        email: Email address to mask
        
    Returns:
        Masked email address
    """
    if '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    if len(local) <= 2:
        masked_local = local[0] + '*' * (len(local) - 1)
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def generate_username_suggestions(base_username: str, count: int = 5) -> list:
    """
    Generate username suggestions based on a base username.
    
    Args:
        base_username: Base username to generate suggestions from
        count: Number of suggestions to generate
        
    Returns:
        List of username suggestions
    """
    from .models import User
    
    suggestions = []
    
    # Try base username with numbers
    for i in range(1, count + 1):
        suggestion = f"{base_username}{i}"
        if not User.objects.filter(username=suggestion).exists():
            suggestions.append(suggestion)
    
    # Try base username with random suffixes
    while len(suggestions) < count:
        suffix = generate_random_string(4)
        suggestion = f"{base_username}_{suffix}"
        if not User.objects.filter(username=suggestion).exists():
            suggestions.append(suggestion)
    
    return suggestions[:count] 