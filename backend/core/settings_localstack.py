# Django settings for LocalStack AWS emulation environment

import os
from decouple import config
from .settings import *

# Debug mode
DEBUG = True

# LocalStack AWS Configuration
USE_LOCALSTACK = config('USE_LOCALSTACK', default=True, cast=bool)

if USE_LOCALSTACK:
    # AWS LocalStack Configuration
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='test')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='test')
    AWS_DEFAULT_REGION = config('AWS_DEFAULT_REGION', default='us-east-1')
    AWS_S3_REGION_NAME = AWS_DEFAULT_REGION
    
    # LocalStack S3 Configuration
    AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT_URL', default='http://localstack:4566')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='jobquest-resumes')
    AWS_S3_CUSTOM_DOMAIN = None
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    AWS_S3_VERIFY = False  # Disable SSL verification for LocalStack
    
    # Use S3 for file storage - but only when bucket exists
    # For development, use local storage initially
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    
    # Enable S3 storage for production or when explicitly configured
    USE_S3_STORAGE = config('USE_S3_STORAGE', default=False, cast=bool)
    
    # S3 URL configuration
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_URL_PROTOCOL = 'http:'
    
    # LocalStack Lambda Configuration
    AWS_LAMBDA_ENDPOINT_URL = config('AWS_LAMBDA_ENDPOINT_URL', default='http://localstack:4566')
    
    # LocalStack API Gateway Configuration  
    AWS_APIGATEWAY_ENDPOINT_URL = config('AWS_APIGATEWAY_ENDPOINT_URL', default='http://localstack:4566')
    
    # LocalStack RDS Configuration (if using RDS emulation)
    AWS_RDS_ENDPOINT_URL = config('AWS_RDS_ENDPOINT_URL', default='http://localstack:4566')
    
    print(f"LocalStack S3 endpoint: {AWS_S3_ENDPOINT_URL}")
    print(f"LocalStack S3 bucket: {AWS_STORAGE_BUCKET_NAME}")

# Database configuration (use PostgreSQL for LocalStack environment)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB', default='jobquest_navigator'),
        'USER': config('POSTGRES_USER', default='jobquest_user'),
        'PASSWORD': config('POSTGRES_PASSWORD', default='jobquest_password'),
        'HOST': config('POSTGRES_HOST', default='database'),
        'PORT': config('POSTGRES_PORT', default='5432'),
        'OPTIONS': {
            'connect_timeout': 30,
        },
    }
}

# Redis configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://redis:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# CORS configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://localhost:80",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:80",
]

CORS_ALLOW_CREDENTIALS = True

# Allowed hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', 'backend', 'localstack']

# Media files configuration for LocalStack
if USE_LOCALSTACK:
    MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/media/'
    STATIC_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/static/'
else:
    MEDIA_URL = '/media/'
    STATIC_URL = '/static/'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'boto3': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'botocore': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# Email configuration (use MailHog if available)
if config('USE_MAILHOG', default=False, cast=bool):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'mailhog'
    EMAIL_PORT = 1025
    EMAIL_USE_TLS = False
    EMAIL_USE_SSL = False
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Security settings for development
SECRET_KEY = config('SECRET_KEY', default='django-insecure-localstack-development-key')
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True