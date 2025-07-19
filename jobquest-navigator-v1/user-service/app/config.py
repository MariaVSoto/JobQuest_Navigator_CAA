from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://jobquest_user:jobquest_password@database:5432/jobquest_users"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    
    # JWT
    jwt_secret: str = "your-jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_lifetime_seconds: int = 3600
    
    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3002", 
        "http://localhost:80",
        "http://localhost"
    ]
    
    # Email Configuration
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: str = "noreply@jobquestnavigator.com"
    smtp_from_name: str = "JobQuest Navigator"
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    
    # Email Templates
    email_templates_dir: str = "app/templates/emails"
    frontend_url: str = "http://localhost:3002"
    
    # Account Management
    max_login_attempts: int = 5
    account_lockout_duration: int = 300  # 5 minutes in seconds
    password_reset_expire_hours: int = 24
    email_verification_expire_hours: int = 72
    
    # Development
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"


settings = Settings()