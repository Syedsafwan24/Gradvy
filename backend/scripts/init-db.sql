-- Gradvy Database Initialization Script
-- This script runs when the PostgreSQL container starts for the first time

-- Create additional extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "citext";

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE gradvy_db TO gradvy_user;

-- Create additional schemas if needed (optional)
-- CREATE SCHEMA IF NOT EXISTS auth_schema AUTHORIZATION gradvy_user;

-- Set default permissions for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO gradvy_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO gradvy_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO gradvy_user;

-- Log successful initialization
INSERT INTO information_schema.sql_features (feature_id, feature_name, sub_feature_id, sub_feature_name, is_supported, comments)
VALUES ('GRADVY001', 'Gradvy Database Initialized', 'INIT', 'Initial Setup Complete', 'YES', 'Database ready for Django migrations')
ON CONFLICT DO NOTHING;