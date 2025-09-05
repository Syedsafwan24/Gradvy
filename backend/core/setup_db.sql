-- Create database for Gradvy Django project
CREATE DATABASE gradvy_db;

-- Create a dedicated user for the application (optional but recommended)
CREATE USER gradvy_user WITH PASSWORD 'admin@123';

-- Grant privileges to the user
ALTER ROLE gradvy_user SET client_encoding TO 'utf8';
ALTER ROLE gradvy_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE gradvy_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE gradvy_db TO gradvy_user;

-- List databases to confirm creation
\l
