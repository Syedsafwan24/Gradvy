@echo off
echo 🚀 Starting Gradvy Backend with Docker...

REM Stop any existing containers
echo 📋 Stopping existing containers...
docker-compose down

REM Build and start all services
echo 🔨 Building and starting services...
docker-compose up --build -d

echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check Redis connection
echo 🔍 Checking Redis connection...
docker exec gradvy-redis redis-cli ping

REM Check if containers are running
echo 📊 Container status:
docker ps --filter "name=gradvy"

echo ✅ Setup complete!
echo.
echo 🔗 Available services:
echo    Redis: localhost:6379
echo    Flower (Celery Monitor): http://localhost:5555
echo.
echo 📝 Useful commands:
echo    View logs: docker-compose logs -f [service-name]
echo    Stop all: docker-compose down
echo    Restart: docker-compose restart [service-name]
echo.
echo 🔧 To test Celery tasks, run:
echo    docker exec -it gradvy-celery-worker python manage.py shell

pause
