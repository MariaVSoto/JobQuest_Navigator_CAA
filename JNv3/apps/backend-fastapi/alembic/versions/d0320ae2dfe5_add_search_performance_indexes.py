"""Add search performance indexes

Revision ID: d0320ae2dfe5
Revises: 254b9c96cf83
Create Date: 2025-07-20 05:56:57.669615

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0320ae2dfe5'
down_revision = '254b9c96cf83'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### Search performance indexes for job listings ###
    
    # Full-text search indexes for job titles and descriptions
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_jobs_title_search 
        ON jobs USING gin(to_tsvector('english', title))
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_jobs_description_search 
        ON jobs USING gin(to_tsvector('english', description))
    """)
    
    # Regular indexes for common search filters
    op.create_index('idx_jobs_location', 'jobs', ['location_text'])
    op.create_index('idx_jobs_user_input_active', 'jobs', ['user_input', 'is_active'])
    op.create_index('idx_jobs_job_type', 'jobs', ['job_type'])
    op.create_index('idx_jobs_experience_level', 'jobs', ['experience_level'])
    op.create_index('idx_jobs_remote_type', 'jobs', ['remote_type'])
    op.create_index('idx_jobs_posted_date', 'jobs', ['posted_date'])
    
    # Company search indexes
    op.create_index('idx_companies_name', 'companies', ['name'])
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_companies_name_search 
        ON companies USING gin(to_tsvector('english', name))
    """)
    
    # Optimize foreign key lookups
    op.create_index('idx_jobs_company_id', 'jobs', ['company_id'])
    op.create_index('idx_jobs_category_id', 'jobs', ['category_id'])
    
    # ### end custom indexes ###


def downgrade() -> None:
    # ### Remove search performance indexes ###
    
    # Drop full-text search indexes
    op.execute("DROP INDEX IF EXISTS idx_jobs_title_search")
    op.execute("DROP INDEX IF EXISTS idx_jobs_description_search")
    op.execute("DROP INDEX IF EXISTS idx_companies_name_search")
    
    # Drop regular indexes
    op.drop_index('idx_jobs_location', 'jobs')
    op.drop_index('idx_jobs_user_input_active', 'jobs')
    op.drop_index('idx_jobs_job_type', 'jobs')
    op.drop_index('idx_jobs_experience_level', 'jobs')
    op.drop_index('idx_jobs_remote_type', 'jobs')
    op.drop_index('idx_jobs_posted_date', 'jobs')
    op.drop_index('idx_companies_name', 'companies')
    op.drop_index('idx_jobs_company_id', 'jobs')
    op.drop_index('idx_jobs_category_id', 'jobs')
    
    # ### end custom index removal ###