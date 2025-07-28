"""Performance indexes optimization - Fixed

Revision ID: performance_indexes_optimization_fixed  
Revises: d0320ae2dfe5
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'performance_indexes_optimization_fixed'
down_revision = 'd0320ae2dfe5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add performance optimization indexes for actual schema."""
    
    # User table indexes (based on actual User model)
    op.create_index(
        'idx_users_email', 
        'users', 
        ['email'], 
        unique=True
    )
    op.create_index(
        'idx_users_created_at', 
        'users', 
        ['created_at']
    )
    op.create_index(
        'idx_users_is_active', 
        'users', 
        ['is_active']
    )
    op.create_index(
        'idx_users_cognito_sub', 
        'users', 
        ['cognito_sub'],
        unique=True
    )
    op.create_index(
        'idx_users_username', 
        'users', 
        ['username'],
        unique=True
    )
    
    # Company table indexes (if table exists)
    try:
        op.create_index(
            'idx_companies_name', 
            'companies', 
            ['name']
        )
        op.create_index(
            'idx_companies_is_active', 
            'companies', 
            ['is_active']
        )
    except:
        # Table might not exist yet
        pass
    
    # Job table indexes (if table exists)
    try:
        op.create_index(
            'idx_jobs_title', 
            'jobs', 
            ['title']
        )
        op.create_index(
            'idx_jobs_company_id', 
            'jobs', 
            ['company_id']
        )
        op.create_index(
            'idx_jobs_created_at', 
            'jobs', 
            ['created_at']
        )
        op.create_index(
            'idx_jobs_is_active', 
            'jobs', 
            ['is_active']
        )
        
        # Composite indexes for common query patterns
        op.create_index(
            'idx_jobs_company_active', 
            'jobs', 
            ['company_id', 'is_active']
        )
    except:
        # Table might not exist yet
        pass
    
    # User Preferences table indexes
    try:
        op.create_index(
            'idx_user_preferences_user_id', 
            'user_preferences', 
            ['user_id'],
            unique=True  # One preference record per user
        )
    except:
        # Table might not exist yet
        pass
    
    # Activity Logs table indexes
    try:
        op.create_index(
            'idx_activity_logs_user_id', 
            'activity_logs', 
            ['user_id']
        )
        op.create_index(
            'idx_activity_logs_action', 
            'activity_logs', 
            ['action']
        )
        op.create_index(
            'idx_activity_logs_epic', 
            'activity_logs', 
            ['epic']
        )
        op.create_index(
            'idx_activity_logs_created_at', 
            'activity_logs', 
            ['created_at']
        )
        
        # Composite index for user activity by date
        op.create_index(
            'idx_activity_logs_user_created', 
            'activity_logs', 
            ['user_id', 'created_at']
        )
    except:
        # Table might not exist yet
        pass


def downgrade() -> None:
    """Remove performance optimization indexes."""
    
    # Drop activity logs indexes
    try:
        op.drop_index('idx_activity_logs_user_created', 'activity_logs')
        op.drop_index('idx_activity_logs_created_at', 'activity_logs')
        op.drop_index('idx_activity_logs_epic', 'activity_logs')
        op.drop_index('idx_activity_logs_action', 'activity_logs')
        op.drop_index('idx_activity_logs_user_id', 'activity_logs')
    except:
        pass
    
    # Drop user preferences indexes
    try:
        op.drop_index('idx_user_preferences_user_id', 'user_preferences')
    except:
        pass
    
    # Drop job indexes
    try:
        op.drop_index('idx_jobs_company_active', 'jobs')
        op.drop_index('idx_jobs_is_active', 'jobs')
        op.drop_index('idx_jobs_created_at', 'jobs')
        op.drop_index('idx_jobs_company_id', 'jobs')
        op.drop_index('idx_jobs_title', 'jobs')
    except:
        pass
    
    # Drop company indexes
    try:
        op.drop_index('idx_companies_is_active', 'companies')
        op.drop_index('idx_companies_name', 'companies')
    except:
        pass
    
    # Drop user indexes
    op.drop_index('idx_users_username', 'users')
    op.drop_index('idx_users_cognito_sub', 'users')
    op.drop_index('idx_users_is_active', 'users')
    op.drop_index('idx_users_created_at', 'users')
    op.drop_index('idx_users_email', 'users')