-- Initialize JobQuest Navigator Database

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS jobquest_navigator;

-- Create user if not exists
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

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE jobquest_navigator TO jobquest_user;

-- Connect to the database
\c jobquest_navigator;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Create initial schema comment
COMMENT ON DATABASE jobquest_navigator IS 'JobQuest Navigator - Job Search Platform Database';

-- Create initial tables will be handled by Django migrations