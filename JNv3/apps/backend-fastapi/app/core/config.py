"""
Application configuration settings
Based on the original Django settings with FastAPI adaptations
"""

from pydantic_settings import BaseSettings
from typing import List
import os


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
    allowed_hosts: List[str] = [
        "http://localhost:3000",  # React development
        "http://localhost:3001",  # Docker React (actual port)
        "http://localhost:3002",  # Docker React (alternative)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ]
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
    
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
    
    # File storage - MOVED TO ENVIRONMENT VARIABLES
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_storage_bucket_name: str = os.getenv("AWS_STORAGE_BUCKET_NAME", "jobquest-resumes")
    aws_s3_region_name: str = os.getenv("AWS_S3_REGION_NAME", "us-east-1")
    
    # Original Django proxy settings (for migration phase) - MOVED TO ENVIRONMENT VARIABLES
    django_graphql_endpoint: str = os.getenv("DJANGO_GRAPHQL_ENDPOINT", "http://localhost:8000/graphql/")
    
    class Config:
        env_file = ".env"
    
    def validate_production_secrets(self):
        """Validate that required secrets are provided in production"""
        if self.environment == "production":
            required_secrets = {
                "SECRET_KEY": self.secret_key,
                "DATABASE_URL": self.database_url,
                "AWS_ACCESS_KEY_ID": self.aws_access_key_id,
                "AWS_SECRET_ACCESS_KEY": self.aws_secret_access_key,
            }
            
            missing_secrets = [name for name, value in required_secrets.items() if not value]
            if missing_secrets:
                raise ValueError(f"Missing required production secrets: {', '.join(missing_secrets)}")


settings = Settings()

# Validate production secrets on import
if settings.environment == "production":
    settings.validate_production_secrets()