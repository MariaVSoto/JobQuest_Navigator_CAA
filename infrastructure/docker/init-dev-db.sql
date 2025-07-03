-- Initialize JobQuest Navigator Development Database

-- Create development user first
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'dev_user') THEN

      CREATE ROLE dev_user LOGIN PASSWORD 'dev_password';
   END IF;
END
$do$;

-- Create development database
CREATE DATABASE jobquest_navigator_dev;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE jobquest_navigator_dev TO dev_user;
ALTER USER dev_user CREATEDB;

-- Connect to the development database
\c jobquest_navigator_dev;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Create development schema comment
COMMENT ON DATABASE jobquest_navigator_dev IS 'JobQuest Navigator - Development Database';

-- Insert sample data will be handled by Django fixtures or management commands