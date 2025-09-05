# 🛠️ Gradvy Backend - Troubleshooting Guide

This guide helps solve common issues developers encounter when setting up or running the Gradvy Backend project.

## 📋 Quick Diagnostic Checklist

Before diving into specific issues, run this quick diagnostic:

```bash
# 1. Check if you're in the right directory
ls -la | grep manage.py  # Should show manage.py in core/

# 2. Check if virtual environment is active
echo $VIRTUAL_ENV  # Should show path to venv

# 3. Check Docker status
docker ps  # Should show running containers

# 4. Check Python/Django
python manage.py check

# 5. Check database connection
python manage.py dbshell
```

## 🚨 Setup Issues

### Issue: Setup Script Fails

#### Symptoms:

- Script stops with error messages
- Missing dependencies
- Permission denied errors

#### Solutions:

**For Permission Errors:**

```bash
# Linux/macOS
chmod +x setup-dev.sh
sudo ./setup-dev.sh

# Windows - Run Command Prompt as Administrator
setup-dev.bat
```

**For Missing Dependencies:**

```bash
# Update package managers first
# Windows (if using Chocolatey)
choco upgrade chocolatey

# macOS
brew update

# Linux
sudo apt update
```

**For Script Partial Failure:**

1. Note where the script failed
2. Run commands manually from that point
3. Check the [Manual Setup](DEVELOPER_SETUP.md#manual-setup) section

### Issue: Virtual Environment Problems

#### Symptoms:

- "command not found" errors
- Packages not found despite installation
- Wrong Python version

#### Solutions:

**Create Fresh Virtual Environment:**

```bash
# Remove old environment
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

# Create new one
python -m venv venv

# Activate (make sure this works)
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Verify activation (should show venv path)
which python  # Linux/macOS
where python  # Windows
```

**Fix Python Version Issues:**

```bash
# Check Python version
python --version

# If wrong version, specify explicitly
python3.11 -m venv venv
```

**Fix Package Installation Issues:**

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Clear pip cache
pip cache purge

# Install packages one by one to identify problematic ones
pip install django
pip install djangorestframework
# ... etc
```

## 🗄️ Database Issues

### Issue: PostgreSQL Connection Failed

#### Symptoms:

- "could not connect to server"
- "authentication failed"
- "database does not exist"

#### Solutions:

**Check PostgreSQL Service:**

```bash
# Windows
net start postgresql-x64-15
# or
services.msc  # Look for PostgreSQL service

# macOS
brew services start postgresql@15

# Linux
sudo systemctl start postgresql
sudo systemctl status postgresql
```

**Verify Database and User:**

```bash
# Connect as postgres superuser
psql -U postgres

# Check if database exists
\l

# Check if user exists
\du

# If missing, create them:
CREATE DATABASE gradvy_db;
CREATE USER gradvy_user WITH PASSWORD 'gradvy_pass123';
GRANT ALL PRIVILEGES ON DATABASE gradvy_db TO gradvy_user;
ALTER USER gradvy_user CREATEDB;
```

**Test Connection:**

```bash
# Test direct connection
psql -U gradvy_user -d gradvy_db -h localhost

# Test from Django
python manage.py dbshell
```

**Fix Environment Variables:**

```bash
# Check .env file exists
cat core/.env

# Verify database settings
DB_NAME=gradvy_db
DB_USER=gradvy_user
DB_PASSWORD=gradvy_pass123
DB_HOST=localhost
DB_PORT=5432
```

### Issue: Migration Errors

#### Symptoms:

- "table already exists"
- "column does not exist"
- "migration conflicts"

#### Solutions:

**Reset Migrations (Nuclear Option):**

```bash
# Backup your data first!
python manage.py dumpdata > backup.json

# Remove migration files (keep __init__.py)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Create fresh migrations
python manage.py makemigrations
python manage.py migrate
```

**Fix Migration Conflicts:**

```bash
# Show migration status
python manage.py showmigrations

# Merge conflicting migrations
python manage.py makemigrations --merge

# Apply specific migration
python manage.py migrate app_name migration_name
```

## 🐳 Docker Issues

### Issue: Docker Containers Not Starting

#### Symptoms:

- Containers in "Restarting" state
- "port already in use" errors
- Containers exit immediately

#### Solutions:

**Check Container Logs:**

```bash
# View logs for specific services
docker-compose logs celery-worker
docker-compose logs redis
docker-compose logs flower

# Follow logs in real-time
docker-compose logs -f celery-worker
```

**Fix Port Conflicts:**

```bash
# Check what's using ports
netstat -tulpn | grep :5432  # Linux
netstat -ano | findstr :5432  # Windows
lsof -i :5432                 # macOS

# Kill conflicting processes or change ports in docker-compose.yml
```

**Rebuild Containers:**

```bash
# Stop everything
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Rebuild and restart
docker-compose up --build -d
```

**Reset Docker Environment:**

```bash
# Nuclear option - removes ALL Docker data
docker system prune -a --volumes
docker-compose up --build -d
```

### Issue: Celery Worker Failing

#### Symptoms:

- Tasks not processing
- Worker container restarting
- Import errors in logs

#### Solutions:

**Check Worker Logs:**

```bash
docker-compose logs celery-worker --tail=50
```

**Common Fixes:**

```bash
# Fix import paths in tasks.py
# Make sure all imports use absolute paths
from apps.accounts.models import User  # ✅ Good
from .models import User               # ❌ May fail in Celery

# Restart worker
docker-compose restart celery-worker

# Test task execution
python manage.py shell
>>> from apps.accounts.tasks import send_welcome_email
>>> result = send_welcome_email.delay('test@example.com')
>>> print(result.task_id)
```

## 🌐 Network and Port Issues

### Issue: "Port Already in Use"

#### Symptoms:

- Cannot start Django server
- Docker services fail to start
- Connection refused errors

#### Solutions:

**Find and Kill Process Using Port:**

```bash
# Linux/macOS
sudo lsof -i :8000
sudo kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Use Different Ports:**

```bash
# Django on different port
python manage.py runserver 8001

# Modify docker-compose.yml for different ports
ports:
  - "5433:5432"  # PostgreSQL
  - "6380:6379"  # Redis
```

### Issue: Cannot Access Services

#### Symptoms:

- Browser shows "connection refused"
- API calls fail
- Services appear to be running

#### Solutions:

**Check Service Status:**

```bash
# Check if Django is running
curl http://localhost:8000/

# Check if Flower is accessible
curl http://localhost:5555/

# Check Docker container health
docker ps
docker-compose ps
```

**Fix Firewall Issues:**

```bash
# Windows - Allow through firewall
# Go to Windows Firewall settings
# Allow Python and Docker through firewall

# Linux - Check iptables
sudo iptables -L

# macOS - Check if ports are bound
netstat -an | grep LISTEN
```

## 🐍 Python and Django Issues

### Issue: Import Errors

#### Symptoms:

- "ModuleNotFoundError"
- "ImportError: No module named"
- Python can't find installed packages

#### Solutions:

**Verify Virtual Environment:**

```bash
# Check if activated
which python  # Should point to venv
pip list      # Should show installed packages

# If not activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

**Reinstall Dependencies:**

```bash
# Clear pip cache
pip cache purge

# Reinstall everything
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

**Fix Python Path Issues:**

```bash
# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or add to Django settings
import sys
sys.path.append('/path/to/your/project')
```

### Issue: Django Debug Errors

#### Symptoms:

- 500 Internal Server Error
- DEBUG pages with traceback
- Template errors

#### Solutions:

**Check Django Settings:**

```python
# In core/settings.py
DEBUG = True  # Should be True for development
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']  # Allow local access
```

**Verify Database Connection:**

```bash
python manage.py check --database default
```

**Check Static Files:**

```bash
python manage.py collectstatic
```

## 📊 Performance Issues

### Issue: Slow Performance

#### Symptoms:

- Long response times
- Database queries taking too long
- High CPU/memory usage

#### Solutions:

**Enable Django Debug Toolbar:**

```bash
pip install django-debug-toolbar

# Add to settings.py INSTALLED_APPS
'debug_toolbar',

# Add to middleware
'debug_toolbar.middleware.DebugToolbarMiddleware',
```

**Check Database Performance:**

```sql
-- Connect to PostgreSQL
psql -U gradvy_user -d gradvy_db

-- Check active connections
SELECT * FROM pg_stat_activity;

-- Check slow queries
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

**Monitor Docker Resources:**

```bash
# Check container resource usage
docker stats

# Check system resources
htop  # Linux/macOS
# Task Manager on Windows
```

## 🧪 Testing Issues

### Issue: Tests Failing

#### Symptoms:

- Test database errors
- Import failures in tests
- Assertion errors

#### Solutions:

**Run Tests with Verbose Output:**

```bash
python manage.py test --verbosity=2
python manage.py test apps.accounts --verbosity=2
```

**Fix Test Database Issues:**

```bash
# Create test database manually
python manage.py test --settings=core.test_settings
```

**Check Test Environment:**

```python
# In test files, verify imports
from django.test import TestCase
from apps.accounts.models import User
```

## 🔄 Git and Version Control Issues

### Issue: Git Conflicts or Errors

#### Symptoms:

- Merge conflicts
- "Your branch is behind"
- Cannot pull/push

#### Solutions:

**Resolve Merge Conflicts:**

```bash
# Check status
git status

# Resolve conflicts manually or using tools
git mergetool

# After resolving
git add .
git commit -m "Resolve merge conflicts"
```

**Reset to Clean State:**

```bash
# Stash local changes
git stash

# Pull latest changes
git pull origin main

# Apply stashed changes
git stash pop
```

## 🆘 Nuclear Options (Last Resort)

### Complete Environment Reset

If nothing else works, start completely fresh:

```bash
# 1. Stop all services
docker-compose down -v
python manage.py runserver  # Ctrl+C to stop

# 2. Remove virtual environment
deactivate
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

# 3. Clean Docker
docker system prune -a --volumes

# 4. Clean Python cache
find . -type d -name "__pycache__" -delete  # Linux/macOS
# Manually delete __pycache__ folders on Windows

# 5. Re-run setup
./setup-dev.sh  # or setup-dev.bat
```

### Reset Database

```bash
# Drop and recreate database
psql -U postgres -c "DROP DATABASE IF EXISTS gradvy_db;"
psql -U postgres -c "CREATE DATABASE gradvy_db;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE gradvy_db TO gradvy_user;"

# Re-run migrations
python manage.py migrate
```

## 📞 Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Read error messages carefully** - they often contain the solution
3. **Check official documentation**:
   - [Django Docs](https://docs.djangoproject.com/)
   - [Docker Docs](https://docs.docker.com/)
   - [PostgreSQL Docs](https://www.postgresql.org/docs/)

### When Asking for Help

Include this information:

```bash
# System information
python --version
docker --version
pip --version

# Error details
# Copy the complete error message, not just the last line

# What you tried
# List the steps you've already attempted

# Environment details
pip list
docker ps
```

### Where to Get Help

1. **Project Issues**: GitHub Issues page
2. **Django Questions**: [Django Discord](https://discord.gg/xcRH6mN4fa)
3. **General Programming**: [Stack Overflow](https://stackoverflow.com/)
4. **Docker Issues**: [Docker Community](https://www.docker.com/community/)

## 📝 Logging and Debugging Tips

### Enable Verbose Logging

```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### Debug Django in VS Code

Add to `.vscode/launch.json`:

```json
{
	"version": "0.2.0",
	"configurations": [
		{
			"name": "Django",
			"type": "python",
			"request": "launch",
			"program": "${workspaceFolder}/core/manage.py",
			"args": ["runserver"],
			"django": true
		}
	]
}
```

---

Remember: Most issues have simple solutions. Take a deep breath, read error messages carefully, and work through problems systematically! 🚀
