-- Fix permissions for gradvy_user
GRANT ALL PRIVILEGES ON DATABASE gradvy_db TO gradvy_user;
GRANT ALL ON SCHEMA public TO gradvy_user;
GRANT CREATE ON SCHEMA public TO gradvy_user;
GRANT USAGE ON SCHEMA public TO gradvy_user;

-- Grant permission to create tables and other objects in the public schema
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO gradvy_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO gradvy_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO gradvy_user;

-- Make gradvy_user the owner of the database (optional but recommended)
ALTER DATABASE gradvy_db OWNER TO gradvy_user;
