"""
Application configuration settings
Based on the original Django settings with FastAPI adaptations
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Basic app settings
    debug: bool = True
    project_name: str = "JobQuest Navigator v2"
    version: str = "2.0.0"
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/jobquest"
    
    # CORS settings
    allowed_hosts: List[str] = [
        "http://localhost:3000",  # React development
        "http://localhost:3002",  # Docker React
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3002",
    ]
    
    # Authentication settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AWS Cognito settings
    aws_region: str = "us-east-1"  # General AWS region setting
    cognito_region: str = "us-east-1"  # Cognito specific region (alias)
    cognito_user_pool_id: str = ""
    cognito_client_id: str = ""  # Changed from app_client_id to client_id
    
    # External APIs
    openai_api_key: str = ""
    
    # File storage
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_storage_bucket_name: str = "jobquest-resumes"
    aws_s3_region_name: str = "us-east-1"
    
    # Original Django proxy settings (for migration phase)
    django_graphql_endpoint: str = "http://localhost:8000/graphql/"
    
    class Config:
        env_file = ".env"


settings = Settings()