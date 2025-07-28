-- JobQuest Navigator v2 Database Initialization Script
-- Creates database extensions and initial setup

-- Enable UUID extension for primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable text search extensions
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Create application-specific schemas
CREATE SCHEMA IF NOT EXISTS jobquest;

-- Set default search path
SET search_path = jobquest, public;

-- Create enum types for consistent data
CREATE TYPE job_status AS ENUM ('draft', 'published', 'closed', 'expired');
CREATE TYPE application_status AS ENUM ('applied', 'screening', 'interview', 'offer', 'rejected', 'withdrawn');
CREATE TYPE work_type AS ENUM ('remote', 'hybrid', 'onsite', 'flexible');
CREATE TYPE job_type AS ENUM ('full_time', 'part_time', 'contract', 'freelance', 'internship');
CREATE TYPE experience_level AS ENUM ('entry', 'junior', 'mid', 'senior', 'lead', 'manager', 'director', 'executive');
CREATE TYPE skill_category AS ENUM ('programming', 'framework', 'database', 'cloud', 'devops', 'design', 'management', 'communication', 'language', 'other');

-- Create indexes for common queries
-- These will be automatically created when tables are created via SQLAlchemy

-- Grant permissions to application user
GRANT USAGE ON SCHEMA jobquest TO jobquest_user;
GRANT CREATE ON SCHEMA jobquest TO jobquest_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA jobquest TO jobquest_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA jobquest TO jobquest_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA jobquest GRANT ALL ON TABLES TO jobquest_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA jobquest GRANT ALL ON SEQUENCES TO jobquest_user;

-- Success message
SELECT 'JobQuest Navigator v2 database initialized successfully!' as status;