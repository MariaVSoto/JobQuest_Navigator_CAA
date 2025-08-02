"""
Application configuration settings
Based on the original Django settings with FastAPI adaptations
"""

from pydantic_settings import BaseSettings
from typing import List, Optional, Dict
import os
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings"""
    
    # Basic app settings - CONFIGURED VIA ENVIRONMENT VARIABLES
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "development")
    project_name: str = os.getenv("PROJECT_NAME", "JobQuest Navigator v2")
    version: str = os.getenv("VERSION", "2.0.0")
    
    # Database - MOVED TO ENVIRONMENT VARIABLES  
    database_url: str = os.getenv("DATABASE_URL", "")
    
    # Redis - MOVED TO ENVIRONMENT VARIABLES
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # CORS settings
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
    
    @property
    def allowed_hosts(self) -> List[str]:
        """Dynamic CORS origins based on environment variable"""
        origins = self.cors_origins.split(",")
        # Add default localhost origins for development
        default_origins = [
            "http://localhost:3000",  # React development
            "http://localhost:3001",  # Docker React (actual port)
            "http://localhost:3002",  # Docker React (alternative)
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:3002",
        ]
        # Combine and deduplicate
        all_origins = list(set(origins + default_origins))
        return [origin.strip() for origin in all_origins if origin.strip()]
    
    # Authentication settings - MOVED TO ENVIRONMENT VARIABLES
    secret_key: str = os.getenv("SECRET_KEY", "")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # AWS Cognito settings - MOVED TO ENVIRONMENT VARIABLES
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    cognito_region: str = os.getenv("COGNITO_REGION", "us-east-1")
    cognito_user_pool_id: str = os.getenv("COGNITO_USER_POOL_ID", "")
    cognito_client_id: str = os.getenv("COGNITO_CLIENT_ID", "")
    cognito_app_client_id: str = os.getenv("COGNITO_APP_CLIENT_ID", "")
    
    # External APIs - MOVED TO ENVIRONMENT VARIABLES
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # File storage - AWS credentials from Secrets Manager or environment variables
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_storage_bucket_name: str = os.getenv("AWS_STORAGE_BUCKET_NAME", "jobquest-resumes")
    aws_s3_region_name: str = os.getenv("AWS_S3_REGION_NAME", "us-east-1")
    
    # Original Django proxy settings (for migration phase) - MOVED TO ENVIRONMENT VARIABLES
    django_graphql_endpoint: str = os.getenv("DJANGO_GRAPHQL_ENDPOINT", "http://localhost:8000/graphql/")
    
    class Config:
        env_file = ".env"
    
    def load_aws_credentials(self) -> Dict[str, str]:
        """
        Load AWS credentials from Secrets Manager or environment variables
        
        Priority:
        1. Environment variables (for local development)
        2. AWS Secrets Manager (for production)
        3. IAM role (when no explicit credentials)
        """
        # First try environment variables (for local development)
        env_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        env_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        
        if env_access_key and env_secret_key:
            logger.info("Using AWS credentials from environment variables")
            return {
                "aws_access_key_id": env_access_key,
                "aws_secret_access_key": env_secret_key
            }
        
        # For production, try Secrets Manager
        if self.environment == "production":
            try:
                from .secrets import secrets_manager
                credentials = secrets_manager.get_aws_credentials()
                if credentials:
                    logger.info("Using AWS credentials from Secrets Manager")
                    return credentials
            except Exception as e:
                logger.warning(f"Failed to load credentials from Secrets Manager: {e}")
        
        # If no explicit credentials, rely on IAM role
        logger.info("No explicit AWS credentials found, using IAM role")
        return {
            "aws_access_key_id": "",
            "aws_secret_access_key": ""
        }
    
    def validate_production_secrets(self):
        """Validate that required secrets are provided in production"""
        if self.environment == "production":
            # Core required secrets
            required_secrets = {
                "SECRET_KEY": self.secret_key,
                "DATABASE_URL": self.database_url,
            }
            
            # AWS credentials are loaded dynamically from Secrets Manager or IAM roles
            # No validation needed here
            
            missing_secrets = [name for name, value in required_secrets.items() if not value]
            if missing_secrets:
                raise ValueError(f"Missing required production secrets: {', '.join(missing_secrets)}")


settings = Settings()

# Load AWS credentials dynamically
aws_credentials = settings.load_aws_credentials()
settings.aws_access_key_id = aws_credentials["aws_access_key_id"]
settings.aws_secret_access_key = aws_credentials["aws_secret_access_key"]

# Validate production secrets on import
if settings.environment == "production":
    settings.validate_production_secrets()