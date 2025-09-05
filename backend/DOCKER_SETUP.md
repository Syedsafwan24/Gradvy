# Docker Setup for Gradvy Backend

This document explains how to run the Gradvy backend services using Docker, including Celery workers, Redis, and monitoring tools.

## 🏗️ Architecture

Our Docker setup includes:

- **Redis**: Message broker for Celery
- **Celery Worker**: Background task processor
- **Celery Beat**: Periodic task scheduler
- **Flower**: Web-based Celery monitoring tool

## 🚀 Quick Start

### Prerequisites

1. Install Docker Desktop for Windows
2. Ensure PostgreSQL is running locally (for development)

### Start All Services

#### Windows (PowerShell/CMD):

```bash
.\start-docker.bat
```

#### Manual Docker Compose:

```bash
docker-compose up --build -d
```

## 📋 Services

### Redis (Message Broker)

- **Container**: `gradvy-redis`
- **Port**: 6379
- **Image**: redis:alpine
- **Data**: Persisted in `redis_data` volume

### Celery Worker

- **Container**: `gradvy-celery-worker`
- **Command**: `celery -A core worker --loglevel=info --pool=solo`
- **Pool**: Solo (Windows compatible)

### Celery Beat (Scheduler)

- **Container**: `gradvy-celery-beat`
- **Command**: `celery -A core beat --loglevel=info`
- **Purpose**: Runs periodic tasks

### Flower (Monitoring)

- **Container**: `gradvy-flower`
- **Port**: 5555
- **URL**: http://localhost:5555
- **Purpose**: Monitor Celery tasks and workers

## 🛠️ Management Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f celery-worker
docker-compose logs -f redis
docker-compose logs -f flower
```

### Stop Services

```bash
docker-compose down
```

### Restart Services

```bash
docker-compose restart celery-worker
```

### Scale Workers

```bash
docker-compose up --scale celery-worker=3 -d
```

## 🔧 Testing Celery Tasks

### Access Worker Shell

```bash
docker exec -it gradvy-celery-worker python manage.py shell
```

### Test a Task

```python
from apps.accounts.tasks import send_welcome_email
result = send_welcome_email.delay("test@example.com", "Test User")
print(f"Task ID: {result.task_id}")
```

### Monitor in Flower

Visit http://localhost:5555 to see:

- Active workers
- Task history
- Real-time monitoring
- Worker statistics

## 📁 File Structure

```
core-backend/
├── docker-compose.yml      # Main Docker configuration
├── Dockerfile             # Container definition
├── requirements.txt       # Python dependencies
├── docker.env            # Docker environment variables
├── start-docker.bat      # Windows startup script
└── start-docker.sh       # Linux/macOS startup script
```

## 🔧 Configuration

### Environment Variables (docker.env)

```env
# Database (connects to host PostgreSQL)
POSTGRES_HOST=host.docker.internal
POSTGRES_DB=gradvy_db
POSTGRES_USER=gradvy_user
POSTGRES_PASSWORD=gradvy_pass123

# Redis (internal Docker network)
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### Database Connection

The containers connect to your local PostgreSQL using `host.docker.internal`, so ensure:

1. PostgreSQL is running locally
2. Database `gradvy_db` exists
3. User `gradvy_user` has access

## 🚨 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs celery-worker

# Rebuild
docker-compose up --build
```

### Redis Connection Issues

```bash
# Test Redis
docker exec gradvy-redis redis-cli ping

# Should return: PONG
```

### Database Connection Issues

```bash
# Test from container
docker exec -it gradvy-celery-worker python manage.py check --database default
```

### Permission Issues (Windows)

If you encounter permission errors, try:

1. Run Docker Desktop as Administrator
2. Ensure your project folder isn't in a restricted location

## 🎯 Production Considerations

For production deployment, consider:

1. **External Redis**: Use managed Redis service
2. **Database**: External PostgreSQL (not host.docker.internal)
3. **Scaling**: Use Docker Swarm or Kubernetes
4. **Monitoring**: Add logging aggregation
5. **Security**: Use secrets for sensitive data

## 📊 Monitoring URLs

- **Flower**: http://localhost:5555
- **Redis**: localhost:6379 (CLI: `redis-cli`)
- **PostgreSQL**: localhost:5432

## 🔄 Development Workflow

1. Start services: `.\start-docker.bat`
2. Monitor tasks: Visit http://localhost:5555
3. View logs: `docker-compose logs -f`
4. Test tasks: Use Django shell or Flower
5. Stop when done: `docker-compose down`
