# Microservices Architecture and Data Model Design

## 1. Overall Architecture Design

Based on the requirements analysis, we will design two Django-based microservices: Resume Management Service and AI Suggestion Service. These two services will be developed as independent Django projects and communicate via APIs.

### 1.1 System Architecture Diagram

```
+------------------+      +------------------+
|                  |      |                  |
|   API Gateway    |      |   Client App     |
|                  |      |                  |
+--------+---------+      +--------+---------+
         |                         |
         v                         |
+--------+---------+               |
|                  |               |
| Authentication   |               |
|    Service       |               |
+------------------+               |
         ^                         |
         |                         |
+--------+---------+     +---------v--------+
|                  |     |                  |
| Resume Management|<--->| AI Suggestion    |
|     Service      |     |    Service       |
|                  |     |                  |
+--------+---------+     +------------------+
         |                         ^
         v                         |
+--------+---------+               |
|                  |               |
|   S3 Storage     |               |
|                  |               |
+------------------+               |
                                   |
+------------------+               |
|                  |               |
|   MySQL Database |---------------+
|                  |
+------------------+
```

### 1.2 Technology Stack

- **Backend Framework**: Django + Django REST Framework
- **Database**: MySQL
- **File Storage**: Amazon S3 (or compatible alternatives like MinIO)
- **API Documentation**: Swagger/OpenAPI
- **Authentication**: JWT (JSON Web Token)
- **Containerization**: Docker + Docker Compose
- **AI Integration**: OpenAI API

## 2. Resume Management Service

### 2.1 Project Structure

```
resume_management_service/
├── Dockerfile
├── requirements.txt
├── manage.py
├── resume_management/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── api/
│   ├── __init__.py
│   ├── apps.py
│   ├── urls.py
│   ├── views/
│   │   ├── __init__.py
│   │   ├── resume_views.py
│   │   └── file_views.py
│   ├── serializers/
│   │   ├── __init__.py
│   │   └── resume_serializers.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── resume_models.py
│   └── services/
│       ├── __init__.py
│       ├── s3_service.py
│       └── version_service.py
└── tests/
    ├── __init__.py
    ├── test_resume_api.py
    └── test_file_api.py
```

### 2.2 Data Model Design

#### 2.2.1 Resume Model

```python
from django.db import models
import uuid

class Resume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    user_id = models.CharField(max_length=36)  # External user ID from authentication service
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id']),
        ]

    def __str__(self):
        return f"{self.name} ({self.id})"
```

#### 2.2.2 ResumeVersion Model

```python
class ResumeVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, related_name='versions', on_delete=models.CASCADE)
    file_path = models.CharField(max_length=512)  # S3 path
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField()  # File size (bytes)
    file_type = models.CharField(max_length=50)  # MIME type
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['resume']),
        ]

    def __str__(self):
        return f"Version {self.id} of {self.resume.name}"

    @property
    def s3_key(self):
        # Return the full S3 object path
        return f"resumes/{self.resume.user_id}/{self.resume.id}/{self.id}/{self.file_name}"
```

### 2.3 API Design

#### 2.3.1 Resume API

- **POST /api/resumes**
  - Function: Upload a new resume
  - Request: `multipart/form-data` (file + name)
  - Response: Newly created resume object

- **GET /api/resumes**
  - Function: List all resumes of the current user
  - Request: None (user ID from authentication)
  - Response: List of resume objects

- **GET /api/resumes/{resumeId}**
  - Function: Get a specific resume and its versions
  - Request: Path parameter `resumeId`
  - Response: Resume object including version list

- **DELETE /api/resumes/{resumeId}**
  - Function: Delete a resume
  - Request: Path parameter `resumeId`
  - Response: 204 No Content

#### 2.3.2 Resume Version API

- **GET /api/resumes/{resumeId}/versions**
  - Function: List all versions of a resume
  - Request: Path parameter `resumeId`
  - Response: List of version objects

- **POST /api/resumes/{resumeId}/versions**
  - Function: Upload a new version for a resume
  - Request: `multipart/form-data` (file + comment)
  - Response: Newly created version object

#### 2.3.3 File API

- **GET /api/files/{fileId}**
  - Function: Download a file (resume)
  - Request: Path parameter `fileId`
  - Response: File content

- **DELETE /api/files/{fileId}**
  - Function: Delete a file
  - Request: Path parameter `fileId`
  - Response: 204 No Content

### 2.4 S3 Service Integration

```python
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,  # For MinIO or other S3-compatible services
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def upload_file(self, file_obj, s3_key):
        """
        Upload file to S3
        Args:
            file_obj: File object
            s3_key: Object key in S3
        Returns:
            bool: Whether upload succeeded
        """
        try:
            self.s3_client.upload_fileobj(file_obj, self.bucket_name, s3_key)
            return True
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {e}")
            return False

    def download_file(self, s3_key):
        """
        Download file from S3
        Args:
            s3_key: Object key in S3
        Returns:
            bytes: File content
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            return response['Body'].read()
        except ClientError as e:
            logger.error(f"Error downloading file from S3: {e}")
            return None

    def delete_file(self, s3_key):
        """
        Delete file from S3
        Args:
            s3_key: Object key in S3
        Returns:
            bool: Whether deletion succeeded
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            logger.error(f"Error deleting file from S3: {e}")
            return False
```

## 3. AI Suggestion Service

### 3.1 Project Structure

```
ai_suggestion_service/
├── Dockerfile
├── requirements.txt
├── manage.py
├── ai_suggestion/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── api/
│   ├── __init__.py
│   ├── apps.py
│   ├── urls.py
│   ├── views/
│   │   ├── __init__.py
│   │   └── suggestion_views.py
│   ├── serializers/
│   │   ├── __init__.py
│   │   └── suggestion_serializers.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── suggestion_models.py
│   └── services/
│       ├── __init__.py
│       ├── openai_service.py
│       └── resume_service.py  # Communicates with Resume Management Service
└── tests/
    ├── __init__.py
    └── test_suggestion_api.py
```

### 3.2 Data Model Design

#### 3.2.1 Suggestion Model

```python
from django.db import models
import uuid

class Suggestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=36)  # External user ID from authentication service
    resume_id = models.CharField(max_length=36)  # Resume ID from Resume Management Service
    job_description = models.TextField()
    score = models.FloatField()  # Match score
    feedback = models.TextField()  # AI feedback
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['resume_id']),
        ]

    def __str__(self):
        return f"Suggestion for resume {self.resume_id} (Score: {self.score})"
```

#### 3.2.2 SuggestionFeedback Model

```python
class SuggestionFeedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    suggestion = models.ForeignKey(Suggestion, related_name='feedbacks', on_delete=models.CASCADE)
    is_helpful = models.BooleanField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback for suggestion {self.suggestion.id}"
```

### 3.3 API Design

#### 3.3.1 Suggestion API

- **POST /api/suggestions**
  - Function: Get AI recommendation for resume and job description
  - Request: JSON (resume ID + job description)
  - Response: AI suggestion object

- **GET /api/suggestions**
  - Function: List AI suggestions for the current user
  - Request: None (user ID from authentication)
  - Response: List of suggestion objects

#### 3.3.2 Feedback API (Extension)

- **POST /api/suggestions/{suggestionId}/feedback**
  - Function: Submit feedback for a suggestion
  - Request: JSON (is helpful + comment)
  - Response: Feedback object

### 3.4 OpenAI Service Integration

```python
import openai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    def analyze_resume_job_match(self, resume_text, job_description):
        """
        Analyze the match between resume and job description
        Args:
            resume_text: Resume text
            job_description: Job description
        Returns:
            dict: Dictionary containing score and feedback
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer and job application advisor."},
                    {"role": "user", "content": f"I want to apply for this job:\n\n{job_description}\n\nHere is my resume:\n\n{resume_text}\n\nPlease analyze how well my resume matches this job. Give me a match score from 0 to 100 and specific feedback on how to improve my resume for this job."}
                ],
                temperature=0.7,
            )
            # Parse response
            content = response.choices[0].message.content
            # Logic to extract score from content
            import re
            score_match = re.search(r'(\d+)/100', content)
            score = float(score_match.group(1)) if score_match else 50.0
            return {
                "score": score,
                "feedback": content
            }
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return {
                "score": 0.0,
                "feedback": "Error analyzing resume. Please try again later."
            }
```

### 3.5 Resume Service Integration

```python
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ResumeService:
    def __init__(self):
        self.base_url = settings.RESUME_SERVICE_URL
    
    def get_resume(self, resume_id, user_id, auth_token):
        """
        Get resume from Resume Management Service
        Args:
            resume_id: Resume ID
            user_id: User ID
            auth_token: Authentication token
        Returns:
            dict: Resume object
        """
        try:
            headers = {
                'Authorization': f'Bearer {auth_token}'
            }
            response = requests.get(
                f"{self.base_url}/api/resumes/{resume_id}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching resume from Resume Service: {e}")
            return None
    
    def get_resume_file(self, file_id, auth_token):
        """
        Get resume file from Resume Management Service
        Args:
            file_id: File ID
            auth_token: Authentication token
        Returns:
            bytes: File content
        """
        try:
            headers = {
                'Authorization': f'Bearer {auth_token}'
            }
            response = requests.get(
                f"{self.base_url}/api/files/{file_id}",
                headers=headers
            )
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching resume file from Resume Service: {e}")
            return None
```

## 4. Authentication and Security

### 4.1 JWT Authentication

Both microservices will use JWT for authentication. JWT tokens are generated by the authentication service and verified by the API gateway.

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': settings.SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

### 4.2 CORS Configuration

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'corsheaders',
    # ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ...
]

# Allow all origins for CORS
CORS_ALLOW_ALL_ORIGINS = True

# Or specify allowed origins
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
# ]
```

## 5. Deployment Configuration

### 5.1 Docker Configuration

#### 5.1.1 Resume Management Service Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "resume_management.wsgi:application"]
```

#### 5.1.2 AI Suggestion Service Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["gunicorn", "--bind", "0.0.0.0:8001", "ai_suggestion.wsgi:application"]
```

### 5.2 Docker Compose Configuration

```yaml
version: '3'

services:
  resume-service:
    build: ./resume_management_service
    ports:
      - "8000:8000"
    environment:
      - DEBUG=0
      - SECRET_KEY=${RESUME_SECRET_KEY}
      - DATABASE_URL=mysql://${DB_USER}:${DB_PASSWORD}@db:3306/resume_db
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_STORAGE_BUCKET_NAME=${AWS_STORAGE_BUCKET_NAME}
      - AWS_S3_REGION_NAME=${AWS_S3_REGION_NAME}
      - AWS_S3_ENDPOINT_URL=${AWS_S3_ENDPOINT_URL}
    depends_on:
      - db
    restart: always

  ai-suggestion-service:
    build: ./ai_suggestion_service
    ports:
      - "8001:8001"
    environment:
      - DEBUG=0
      - SECRET_KEY=${AI_SECRET_KEY}
      - DATABASE_URL=mysql://${DB_USER}:${DB_PASSWORD}@db:3306/ai_suggestion_db
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - RESUME_SERVICE_URL=http://resume-service:8000
    depends_on:
      - db
      - resume-service
    restart: always

  db:
    image: mysql:8.0
    ports:
      - "3306:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=${DB_ROOT_PASSWORD}
      - MYSQL_USER=${DB_USER}
      - MYSQL_PASSWORD=${DB_PASSWORD}
      - MYSQL_DATABASE=resume_db
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: always

volumes:
  mysql_data:
```

### 5.3 Database Initialization Script

```sql
-- init.sql
CREATE DATABASE IF NOT EXISTS resume_db;
CREATE DATABASE IF NOT EXISTS ai_suggestion_db;

USE resume_db;

-- Create Resume table
CREATE TABLE IF NOT EXISTS api_resume (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);

-- Create ResumeVersion table
CREATE TABLE IF NOT EXISTS api_resumeversion (
    id CHAR(36) PRIMARY KEY,
    resume_id CHAR(36) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size INT NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_resume_id (resume_id),
    FOREIGN KEY (resume_id) REFERENCES api_resume(id) ON DELETE CASCADE
);

USE ai_suggestion_db;

-- Create Suggestion table
CREATE TABLE IF NOT EXISTS api_suggestion (
    id CHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    resume_id VARCHAR(36) NOT NULL,
    job_description TEXT NOT NULL,
    score FLOAT NOT NULL,
    feedback TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_resume_id (resume_id)
);

-- Create SuggestionFeedback table
CREATE TABLE IF NOT EXISTS api_suggestionfeedback (
    id CHAR(36) PRIMARY KEY,
    suggestion_id CHAR(36) NOT NULL,
    is_helpful BOOLEAN NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (suggestion_id) REFERENCES api_suggestion(id) ON DELETE CASCADE
);
```

## 6. Summary

This document provides a detailed design of the microservices architecture and data models for the Resume Management Service and AI Suggestion Service based on the Django framework. The main contents include:

1. Overall architecture design, including system architecture diagram and technology stack selection
2. Project structure, data models, API design, and S3 service integration for the Resume Management Service
3. Project structure, data models, API design, OpenAI service integration, and resume service integration for the AI Suggestion Service
4. Authentication and security configuration, including JWT authentication and CORS configuration
5. Deployment configuration, including Docker configuration, Docker Compose configuration, and database initialization script

This design provides a complete framework that can serve as the foundation for developing these two microservices. In actual development, adjustments and extensions may be needed according to specific requirements.
