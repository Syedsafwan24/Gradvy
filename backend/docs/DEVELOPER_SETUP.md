# 🚀 Gradvy Backend - Complete Developer Setup Guide

Welcome to the Gradvy Backend project! This guide will help you set up the complete development environment, whether you're a seasoned developer or completely new to Django, Docker, and backend development.

## 📋 Table of Contents

1. [Quick Setup (For Experienced Developers)](#quick-setup)
2. [Detailed Setup Guide (For Beginners)](#detailed-setup-guide)
3. [Prerequisites Installation](#prerequisites-installation)
4. [Project Architecture](#project-architecture)
5. [Development Workflow](#development-workflow)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

---

## 🏃‍♂️ Quick Setup (For Experienced Developers)

If you're familiar with Django, Docker, and Python development, use our automated setup script:

### Windows:

```bash
git clone https://github.com/Syedsafwan24/Gradvy.git
cd core-backend
./setup-dev.bat
```

### Linux/macOS:

```bash
git clone https://github.com/Syedsafwan24/Gradvy.git
cd core-backend
chmod +x setup-dev.sh
./setup-dev.sh
```

That's it! Skip to [Development Workflow](#development-workflow) section.

---

## 📚 Detailed Setup Guide (For Beginners)

### What is this project?

Gradvy Backend is a Django-based REST API that provides:

- **User Authentication** with JWT tokens
- **Two-Factor Authentication** (2FA) for security
- **Background Task Processing** with Celery
- **PostgreSQL Database** for data storage
- **Redis** for caching and task queues
- **Docker** for easy deployment

### What you'll need to understand:

- **Django**: A Python web framework (like building with LEGO blocks for websites)
- **PostgreSQL**: A database to store information (like a digital filing cabinet)
- **Redis**: A fast cache system (like having frequently used items on your desk)
- **Docker**: Containers that package software (like shipping containers for applications)
- **Celery**: Handles background tasks (like having a assistant do work behind the scenes)

---

## 🛠️ Prerequisites Installation

### Step 1: Install Python 3.11+

**What it is**: Python is the programming language our project uses.

#### Windows:

1. Go to [python.org](https://www.python.org/downloads/)
2. Download Python 3.11 or newer
3. **Important**: Check "Add Python to PATH" during installation
4. Verify installation:
   ```bash
   python --version
   ```

#### macOS:

```bash
# Using Homebrew (recommended)
brew install python@3.11

# Or download from python.org
```

#### Linux (Ubuntu/Debian):

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

### Step 2: Install Git

**What it is**: Git helps track changes in code and download projects.

#### Windows:

1. Download from [git-scm.com](https://git-scm.com/)
2. Install with default settings
3. Verify: `git --version`

#### macOS:

```bash
# Using Homebrew
brew install git

# Or use Xcode Command Line Tools
xcode-select --install
```

#### Linux:

```bash
sudo apt install git
```

### Step 3: Install Docker Desktop

**What it is**: Docker runs our services (Redis, Celery) in isolated containers.

1. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/)
2. Install and start Docker Desktop
3. Verify installation:
   ```bash
   docker --version
   docker-compose --version
   ```

### Step 4: Install PostgreSQL

**What it is**: Our main database system.

#### Windows:

1. Download from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Install with default settings
3. Remember the password you set for the 'postgres' user
4. Add PostgreSQL to your PATH (usually: `C:\Program Files\PostgreSQL\15\bin`)

#### macOS:

```bash
# Using Homebrew
brew install postgresql@15
brew services start postgresql@15
```

#### Linux:

```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Step 5: Install Code Editor (Recommended)

**Visual Studio Code** is recommended:

1. Download from [code.visualstudio.com](https://code.visualstudio.com/)
2. Install useful extensions:
   - Python
   - Django
   - Docker
   - PostgreSQL

---

## 🏗️ Project Architecture

Let me explain how our project is organized:

```
core-backend/
├── core/                          # Main Django project
│   ├── core/                      # Django settings and configuration
│   │   ├── settings.py           # Main configuration file
│   │   ├── urls.py               # URL routing
│   │   └── celery.py             # Background task configuration
│   ├── apps/                     # Our applications
│   │   └── accounts/             # User management app
│   │       ├── models.py         # Database structure
│   │       ├── views.py          # API endpoints
│   │       ├── tasks.py          # Background tasks
│   │       └── urls.py           # App-specific URLs
│   └── manage.py                 # Django management script
├── docs/                         # Documentation (this file!)
├── requirements.txt              # Python dependencies list
├── docker-compose.yml           # Docker services configuration
├── Dockerfile                   # Container build instructions
└── setup-dev.bat/sh            # Automated setup scripts
```

### Key Components:

1. **Django App (core/)**: Main application with APIs
2. **PostgreSQL**: Stores user data, settings, etc.
3. **Redis**: Handles caching and message queuing
4. **Celery Workers**: Process background tasks (emails, data processing)
5. **Flower**: Web interface to monitor background tasks

---

## 💻 Manual Setup (If Automated Script Fails)

### Step 1: Clone the Repository

```bash
git clone https://github.com/Syedsafwan24/Gradvy.git
cd core-backend
```

### Step 2: Create Python Virtual Environment

**What it is**: A virtual environment keeps this project's dependencies separate from other Python projects.

```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Linux/macOS)
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

### Step 3: Install Python Dependencies

```bash
# Upgrade pip (package installer)
python -m pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a file called `.env` in the `core/` directory by copying the example:

```bash
# Copy the example environment file
cp .env.example core/.env

# Edit the file with your settings
nano core/.env  # Linux
code core/.env  # VS Code
notepad core/.env  # Windows
```

Edit the `core/.env` file with your settings:

```env
# Database Configuration
POSTGRES_DB=gradvy_db
POSTGRES_USER=gradvy_user
POSTGRES_PASSWORD=gradvy_pass123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Django Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Step 5: Set Up PostgreSQL Database

**Method 1: Using psql command line**

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE gradvy_db;
CREATE USER gradvy_user WITH PASSWORD 'gradvy_pass123';
GRANT ALL PRIVILEGES ON DATABASE gradvy_db TO gradvy_user;
ALTER USER gradvy_user CREATEDB;

# Exit psql
\q
```

**Method 2: Using pgAdmin (GUI)**

1. Open pgAdmin
2. Create a new database: `gradvy_db`
3. Create a new user: `gradvy_user` with password: `gradvy_pass123`
4. Grant all privileges to the user

### Step 6: Run Django Migrations

**What it is**: Migrations create the database tables based on our models.

```bash
# Make sure you're in the core/ directory
cd core

# Create migration files
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate
```

### Step 7: Create Django Superuser (Optional)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user.

### Step 8: Start Docker Services

**What it does**: Starts Redis and Celery containers for background task processing.

```bash
# Go back to project root
cd ..

# Start all Docker services
docker-compose up -d

# Check if containers are running
docker ps
```

You should see containers named:

- `gradvy-redis`
- `gradvy-celery-worker`
- `gradvy-celery-beat`
- `gradvy-flower`

---

## 🚀 Development Workflow

### Daily Development Routine

1. **Start your development session**:

   ```bash
   # Activate virtual environment
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows

   # Start Docker services
   docker-compose up -d

   # Start Django development server
   cd core
   python manage.py runserver
   ```

2. **Access your application**:

   - **Django API**: http://localhost:8000
   - **Django Admin**: http://localhost:8000/admin
   - **Flower (Task Monitor)**: http://localhost:5555

3. **When you're done**:

   ```bash
   # Stop Django server: Ctrl+C

   # Stop Docker services
   docker-compose down

   # Deactivate virtual environment
   deactivate
   ```

### Making Changes

#### When you modify models (database structure):

```bash
python manage.py makemigrations
python manage.py migrate
```

#### When you add new Python packages:

```bash
pip install package-name
pip freeze > requirements.txt
```

#### Testing background tasks:

```bash
# Open Django shell
python manage.py shell

# Test a task
from apps.accounts.tasks import send_welcome_email
result = send_welcome_email.delay('test@example.com')
print(f"Task ID: {result.task_id}")
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue: "ModuleNotFoundError"

**Solution**: Make sure your virtual environment is activated and dependencies are installed:

```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### Issue: "Database connection failed"

**Solutions**:

1. Check if PostgreSQL is running:

   ```bash
   # Windows
   net start postgresql-x64-15

   # Linux/macOS
   sudo systemctl status postgresql
   ```

2. Verify database credentials in `core/.env`
3. Test connection:
   ```bash
   psql -U gradvy_user -d gradvy_db -h localhost
   ```

#### Issue: "Docker containers not starting"

**Solutions**:

1. Make sure Docker Desktop is running
2. Check container logs:
   ```bash
   docker-compose logs celery-worker
   ```
3. Rebuild containers:
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

#### Issue: "Port already in use"

**Solutions**:

1. Find what's using the port:

   ```bash
   # Windows
   netstat -ano | findstr :8000

   # Linux/macOS
   lsof -i :8000
   ```

2. Kill the process or use a different port:
   ```bash
   python manage.py runserver 8001
   ```

#### Issue: "Permission denied" on setup scripts

**Solution**:

```bash
# Make script executable (Linux/macOS)
chmod +x setup-dev.sh

# Run with proper permissions (Windows)
# Right-click on setup-dev.bat -> "Run as administrator"
```

### Getting Help

1. **Check the logs**:

   ```bash
   # Django logs
   python manage.py runserver --verbosity=2

   # Docker logs
   docker-compose logs -f celery-worker
   ```

2. **Verify your setup**:

   ```bash
   # Check Django
   python manage.py check

   # Check database connection
   python manage.py dbshell

   # Check Python packages
   pip list
   ```

3. **Reset everything** (nuclear option):

   ```bash
   # Stop all services
   docker-compose down

   # Remove virtual environment
   rm -rf venv  # Linux/macOS
   rmdir /s venv  # Windows

   # Start over with setup script
   ./setup-dev.sh  # or setup-dev.bat
   ```

---

## ❓ FAQ

### Q: Do I need to know Django to contribute?

**A**: Basic knowledge helps, but our code is well-documented. Start with the [Django Tutorial](https://docs.djangoproject.com/en/stable/intro/tutorial01/) to learn the basics.

### Q: Can I use a different database?

**A**: The project is configured for PostgreSQL, but Django supports MySQL, SQLite, etc. You'll need to modify `settings.py` and install appropriate drivers.

### Q: What if I don't want to use Docker?

**A**: You can install Redis locally, but Docker is recommended for consistency across development environments.

### Q: How do I add new API endpoints?

**A**:

1. Add views in `apps/accounts/views.py`
2. Add URL patterns in `apps/accounts/urls.py`
3. Run tests: `python manage.py test`

### Q: How do I add new background tasks?

**A**:

1. Add task functions in `apps/accounts/tasks.py`
2. Use `@shared_task` decorator
3. Call with `.delay()` method

### Q: Can I use this in production?

**A**: Yes, but you'll need to:

- Change `DEBUG=False` in settings
- Use a proper secret key
- Set up proper database and Redis instances
- Configure a web server (nginx, Apache)
- Set up proper logging and monitoring

### Q: How do I update my fork?

**A**:

```bash
git remote add upstream <original-repo-url>
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

---

## 🎯 Next Steps

After completing the setup:

1. **Explore the codebase**:

   - Read through `apps/accounts/models.py` to understand the data structure
   - Check `apps/accounts/views.py` for API endpoints
   - Look at `apps/accounts/tasks.py` for background tasks

2. **Try the APIs**:

   - Use tools like Postman or curl to test endpoints
   - Check the Django admin interface
   - Monitor tasks in Flower

3. **Make your first contribution**:

   - Look for issues labeled "good-first-issue"
   - Start with documentation improvements
   - Add tests for existing functionality

4. **Learn more**:
   - [Django Documentation](https://docs.djangoproject.com/)
   - [Django REST Framework](https://www.django-rest-framework.org/)
   - [Celery Documentation](https://docs.celeryproject.org/)
   - [Docker Documentation](https://docs.docker.com/)

---

## 📞 Support

If you encounter issues not covered in this guide:

1. Check existing [GitHub Issues](link-to-issues)
2. Search [Stack Overflow](https://stackoverflow.com) with specific error messages
3. Create a new issue with:
   - Your operating system
   - Python version
   - Complete error message
   - Steps you've already tried

Welcome to the team! Happy coding! 🚀
