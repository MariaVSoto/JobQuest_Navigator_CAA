-- Initialize JobQuest Navigator Database

-- Create user if not exists (this runs in the default database context)
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'jobquest_user') THEN

      CREATE ROLE jobquest_user LOGIN PASSWORD 'jobquest_password';
   END IF;
END
$do$;

-- Create databases if they don't exist
SELECT 'CREATE DATABASE jobquest_navigator'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'jobquest_navigator')\gexec

SELECT 'CREATE DATABASE jobquest_users'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'jobquest_users')\gexec

-- Grant privileges on the created databases
GRANT ALL PRIVILEGES ON DATABASE jobquest_navigator TO jobquest_user;
GRANT ALL PRIVILEGES ON DATABASE jobquest_users TO jobquest_user;

-- Connect to the jobquest_navigator database
\c jobquest_navigator;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO jobquest_user;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Grant usage on extensions
GRANT USAGE ON SCHEMA public TO jobquest_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO jobquest_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO jobquest_user;

-- Create initial schema comment
COMMENT ON DATABASE jobquest_navigator IS 'JobQuest Navigator - Job Search Platform Database';

-- Set up user database
\c jobquest_users;

-- Grant schema privileges for user database
GRANT ALL ON SCHEMA public TO jobquest_user;

-- Create extensions for user database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Grant usage on extensions
GRANT USAGE ON SCHEMA public TO jobquest_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO jobquest_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO jobquest_user;

-- Create initial schema comment for user database
COMMENT ON DATABASE jobquest_users IS 'JobQuest Navigator - User Management Database';

-- Create initial tables will be handled by Django migrations and FastAPI migrations