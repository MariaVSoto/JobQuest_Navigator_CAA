"""
Local development settings for JobQuest Navigator with LocalStack.
This configuration is optimized for local AWS services testing.
"""

import os
from .settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'host.docker.internal',
]

# Database for local development (using SQLite for simplicity)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_local.sqlite3',
    }
}

# LocalStack AWS configuration
AWS_ACCESS_KEY_ID = 'test'
AWS_SECRET_ACCESS_KEY = 'test'
AWS_STORAGE_BUCKET_NAME = 'jobquest-navigator-static-local'
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_ENDPOINT_URL = 'http://localhost:4566'
AWS_S3_USE_SSL = False
AWS_S3_VERIFY = False
AWS_S3_CUSTOM_DOMAIN = f'localhost:4566/{AWS_STORAGE_BUCKET_NAME}'
AWS_DEFAULT_ACL = None

# Static files settings for LocalStack S3
STATIC_URL = f'http://{AWS_S3_CUSTOM_DOMAIN}/static/'
MEDIA_URL = f'http://{AWS_S3_CUSTOM_DOMAIN}/media/'

# Use local storage for development instead of S3
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Override S3 settings for local development
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Security settings for local
SECRET_KEY = 'django-insecure-local-development-key-do-not-use-in-production'

# CORS settings for local development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# CSRF settings for local
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Disable security features for local development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Logging configuration for local development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'jobquest': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Email settings for local development (console backend)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache settings for local development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake-local',
    }
}

# Django REST Framework settings for local development
REST_FRAMEWORK.update({
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/hour',
        'user': '10000/hour'
    }
})

# Disable migrations in local testing if needed
LAMBDA_DEPLOYMENT = False