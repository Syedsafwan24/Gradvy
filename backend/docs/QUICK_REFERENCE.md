# 🚀 Gradvy Backend - Quick Reference

## 📋 Daily Commands

### Starting Development

```bash
# 1. Activate virtual environment
source venv/scripts/activate        # Linux/macOS
venv\Scripts\activate          # Windows

# 2. Start Docker services
docker-compose up -d

# 3. Start Django server
cd core && python manage.py runserver
```

### Stopping Development

```bash
# 1. Stop Django: Ctrl+C

# 2. Stop Docker services
docker-compose down

# 3. Deactivate virtual environment
deactivate
```

## 🔧 Common Tasks

### Database Operations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Access database shell
python manage.py dbshell

# Reset database (careful!)
python manage.py flush
```

### Docker Operations

```bash
# View running containers
docker ps

# View logs
docker-compose logs -f celery-worker
docker-compose logs -f redis

# Restart services
docker-compose restart celery-worker
docker-compose restart redis

# Rebuild containers
docker-compose up --build -d

# Remove all containers and start fresh
docker-compose down
docker-compose up -d
```

### Testing Celery Tasks

```bash
# Open Django shell
python manage.py shell

# Test welcome email task
from apps.accounts.tasks import send_welcome_email
result = send_welcome_email.delay('test@example.com')
print(f"Task ID: {result.task_id}")

# Test data processing task
from apps.accounts.tasks import process_user_data
result = process_user_data.delay(user_id=1)
```

### Package Management

```bash
# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt

# Install from requirements.txt
pip install -r requirements.txt

# List installed packages
pip list
```

### ML Operations (Optional)

```bash
# Install ML dependencies (auto-detect)
./scripts/ml-install.sh

# Install ML dependencies (CPU-only)
pip install -r requirements-ml-base.txt

# Install ML dependencies (GPU)
./scripts/ml-install-gpu.sh

# Verify ML setup
python test_ml_setup.py

# Check model registry
python manage.py shell
>>> from ml_services.utils.model_registry import get_global_registry
>>> registry = get_global_registry()
>>> print(registry.get_all_model_status())

# Clear model cache
rm -rf core/ML_Models/cache/*

# View model storage
du -sh core/ML_Models/
```

## 🌐 Service URLs

| Service      | URL                         | Purpose             |
| ------------ | --------------------------- | ------------------- |
| Django API   | http://localhost:8080       | Main application    |
| Django Admin | http://localhost:8080/admin | Admin interface     |
| Flower       | http://localhost:5555       | Celery task monitor |
| PostgreSQL   | localhost:5432              | Database            |
| Redis        | localhost:6379              | Cache & task queue  |

## 📁 Important Files

| File/Directory                 | Purpose               |
| ------------------------------ | --------------------- |
| `core/core/settings.py`        | Django configuration  |
| `core/apps/accounts/`          | User management app   |
| `core/apps/accounts/models.py` | Database models       |
| `core/apps/accounts/views.py`  | API endpoints         |
| `core/apps/accounts/tasks.py`  | Background tasks      |
| `requirements.txt`             | Python dependencies   |
| `requirements-ml-base.txt`     | ML dependencies (CPU) |
| `requirements-ml-gpu.txt`      | ML dependencies (GPU) |
| `docker-compose.yml`           | Docker services       |
| `core/.env`                    | Environment variables |
| `ml_services/`                 | ML models & services  |
| `docs/ML_SETUP.md`             | ML installation guide |

## 🐛 Debugging

### Check System Status

```bash
# Django system check
python manage.py check

# Test database connection
python manage.py dbshell

# Check Redis connection
docker exec gradvy-redis redis-cli ping

# View Django logs (verbose)
python manage.py runserver --verbosity=2
```

### Common Error Solutions

| Error                        | Solution                                              |
| ---------------------------- | ----------------------------------------------------- |
| `ModuleNotFoundError`        | Activate venv: `source venv/scripts/activate`         |
| `Database connection failed` | Check PostgreSQL is running & credentials in `.env`   |
| `Redis connection failed`    | Run `docker-compose up -d`                            |
| `Port 8080 in use`           | Use different port: `python manage.py runserver 8081` |
| `Permission denied`          | Run as admin or `chmod +x script.sh`                  |

## 🔄 Git Workflow

```bash
# Check status
git status

# Stage changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to remote
git push origin branch-name

# Pull latest changes
git pull origin main

# Create new branch
git checkout -b feature-name
```

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.accounts

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📦 Environment Management

### Virtual Environment

```bash
# Create new environment
python -m venv venv

# Activate
source venv/scripts/activate    # Linux/macOS
venv\Scripts\activate      # Windows

# Deactivate
deactivate

# Remove environment
rm -rf venv                # Linux/macOS
rmdir /s venv             # Windows
```

### Environment Variables

```bash
# View current environment
printenv | grep POSTGRES    # Linux/macOS
set | findstr POSTGRES     # Windows

# Load environment file
export $(cat core/.env | xargs)    # Linux/macOS
```

## 🚀 Deployment Preparation

```bash
# Collect static files
python manage.py collectstatic

# Check deployment readiness
python manage.py check --deploy

# Create requirements.txt for production
pip freeze > requirements.txt
```

## 📚 Quick Learning Resources

- [Django Tutorial](https://docs.djangoproject.com/en/stable/intro/tutorial01/)
- [Django REST Framework](https://www.django-rest-framework.org/tutorial/quickstart/)
- [Celery First Steps](https://docs.celeryproject.org/en/stable/getting-started/first-steps-with-celery.html)
- [Docker for Beginners](https://docker-curriculum.com/)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)

## 🆘 Emergency Reset

If everything breaks and you need to start over:

```bash
# Stop all services
docker-compose down

# Remove containers and volumes
docker-compose down -v
docker system prune -a

# Remove virtual environment
rm -rf venv

# Re-run setup script
./setup-dev.sh    # Linux/macOS
./setup-dev.bat   # Windows
```

---

💡 **Tip**: Bookmark this page and keep it open while developing!
