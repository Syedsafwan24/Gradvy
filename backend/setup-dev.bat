@echo off
setlocal EnableDelayedExpansion

REM Gradvy Backend - Automated Developer Setup Script for Windows
REM This script sets up the complete development environment for new developers

echo 🚀 Welcome to Gradvy Backend Setup!
echo ====================================
echo.

REM Step 1: Check Prerequisites
echo [INFO] Step 1: Checking prerequisites...

REM Check Git
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed. Please install Git first.
    pause
    exit /b 1
)
echo [SUCCESS] Git is installed

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.11+ first.
    pause
    exit /b 1
)
echo [SUCCESS] Python is installed

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)
echo [SUCCESS] Docker is installed

REM Check Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    docker compose version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Docker Compose is not installed. Please install Docker Compose first.
        pause
        exit /b 1
    )
)
echo [SUCCESS] Docker Compose is available

REM Check PostgreSQL
psql --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] PostgreSQL client ^(psql^) not found. You might need to install it.
    echo [WARNING] The setup will continue, but database commands might not work.
) else (
    echo [SUCCESS] PostgreSQL client is installed
)

echo.

REM Step 2: Check Project Directory
echo [INFO] Step 2: Setting up project directory...

if not exist "core\manage.py" (
    echo [ERROR] Please run this script from the core-backend project root directory.
    pause
    exit /b 1
)
echo [SUCCESS] Project directory confirmed

REM Step 3: Create Virtual Environment
echo [INFO] Step 3: Setting up Python virtual environment...

if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    echo [SUCCESS] Virtual environment created
) else (
    echo [SUCCESS] Virtual environment already exists
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
echo [SUCCESS] Virtual environment activated

REM Step 4: Install Python Dependencies
echo [INFO] Step 4: Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo [SUCCESS] Python dependencies installed

REM Step 5: Environment Configuration
echo [INFO] Step 5: Setting up environment configuration...

if not exist "core\.env" (
    echo [INFO] Creating environment configuration file...
    copy .env.example core\.env >nul 2>&1
    if errorlevel 1 (
        echo [INFO] Creating default environment configuration...
        (
        echo # Database Configuration
        echo POSTGRES_DB=gradvy_db
        echo POSTGRES_USER=gradvy_user
        echo POSTGRES_PASSWORD=gradvy_pass123
        echo POSTGRES_HOST=localhost
        echo POSTGRES_PORT=5432
        echo.
        echo # Django Configuration
        echo DEBUG=True
        echo SECRET_KEY=your-secret-key-here-change-in-production
        echo ALLOWED_HOSTS=localhost,127.0.0.1
        echo.
        echo # Celery Configuration
        echo CELERY_BROKER_URL=redis://localhost:6379/0
        echo CELERY_RESULT_BACKEND=redis://localhost:6379/0
        echo.
        echo # Security
        echo USE_TLS=False
    ) > core\.env
    echo [SUCCESS] Environment file created: core\.env
) else (
    echo [SUCCESS] Environment file already exists
)

REM Step 6: Database Setup
echo [INFO] Step 6: Setting up PostgreSQL database...
echo [WARNING] Please set up PostgreSQL database manually:
echo   1. Create database: gradvy_db
echo   2. Create user: gradvy_user with password: gradvy_pass123
echo   3. Grant all privileges to gradvy_user on gradvy_db
echo.
echo You can use pgAdmin or run these SQL commands:
echo   CREATE DATABASE gradvy_db;
echo   CREATE USER gradvy_user WITH PASSWORD 'gradvy_pass123';
echo   GRANT ALL PRIVILEGES ON DATABASE gradvy_db TO gradvy_user;
echo.
set /p continue="Press Enter after setting up the database to continue..."

REM Step 7: Django Setup
echo [INFO] Step 7: Setting up Django application...

cd core

REM Run migrations
echo [INFO] Running database migrations...
python manage.py makemigrations
python manage.py migrate
echo [SUCCESS] Database migrations completed

REM Create superuser (optional)
set /p create_superuser="Would you like to create a Django superuser? (y/n): "
if /i "!create_superuser!"=="y" (
    echo [INFO] Creating Django superuser...
    python manage.py createsuperuser
    echo [SUCCESS] Superuser created
)

cd ..

REM Step 8: Docker Setup
echo [INFO] Step 8: Setting up Docker containers for Celery and Redis...

echo [INFO] Building and starting Docker containers...
docker-compose down 2>nul
docker-compose up --build -d

REM Wait for containers to start
echo [INFO] Waiting for containers to start...
timeout /t 10 /nobreak >nul

REM Check container status
docker ps --filter "name=gradvy-redis" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Redis container might have issues
) else (
    echo [SUCCESS] Redis container is running
)

docker ps --filter "name=gradvy-celery-worker" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Celery worker container might have issues
) else (
    echo [SUCCESS] Celery worker container is running
)

REM Step 9: Test Setup
echo [INFO] Step 9: Testing the setup...

REM Test Django
echo [INFO] Testing Django setup...
cd core
python manage.py check >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Django setup has issues
) else (
    echo [SUCCESS] Django setup is working
)

REM Test Redis connection
echo [INFO] Testing Redis connection...
docker exec gradvy-redis redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Redis connection failed
) else (
    echo [SUCCESS] Redis is working
)

cd ..

REM Step 10: Final Instructions
echo.
echo [SUCCESS] 🎉 Setup completed successfully!
echo ==============================
echo.
echo Your Gradvy Backend development environment is ready!
echo.
echo 📋 Next Steps:
echo   1. Start the Django development server:
echo      cd core ^&^& python manage.py runserver
echo.
echo   2. Access the application:
echo      • Django API: http://localhost:8000
echo      • Django Admin: http://localhost:8000/admin
echo      • Flower ^(Celery Monitor^): http://localhost:5555
echo.
echo   3. Useful commands:
echo      • Start Docker services: docker-compose up -d
echo      • Stop Docker services: docker-compose down
echo      • View logs: docker-compose logs -f
echo      • Run tests: python manage.py test
echo.
echo 📚 Documentation:
echo   • See docs/ folder for detailed guides
echo   • API documentation will be available at /api/docs/
echo.
echo 🛠️  Development workflow:
echo   1. Always activate virtual environment: venv\Scripts\activate
echo   2. Make sure Docker containers are running before testing Celery tasks
echo   3. Run migrations after model changes: python manage.py makemigrations ^&^& python manage.py migrate
echo.
echo [SUCCESS] Happy coding! 🚀

pause
