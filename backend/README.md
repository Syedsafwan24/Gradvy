# 🚀 Gradvy Backend - Complete Developer Guide

Welcome to the Gradvy Backend project! This comprehensive guide contains everything you need to get started with development, deployment, and maintenance of the Gradvy Backend system.

## 🚨 CRITICAL: Directory Structure Guidelines

**⚠️ MANDATORY READING: ALL DEVELOPERS MUST FOLLOW THESE GUIDELINES**

Before making ANY changes to the codebase, developers MUST:

1. Read and understand the [Directory Structure Standards](#-directory-structure-standards)
2. Follow the [Development Guidelines](#-development-guidelines)
3. Adhere to [File Organization Rules](#-file-organization-rules)
4. Review [Code Standards](#-code-standards) before writing code

**Failure to follow these guidelines will result in rejected pull requests.**

## 🚀 Getting Started

### For New Developers

**MANDATORY SEQUENCE** - Follow this exact order:

1. **[Directory Structure Standards](#-directory-structure-standards)** - MUST READ FIRST
2. **[Development Guidelines](#-development-guidelines)** - MUST READ SECOND
3. **[Developer Setup Guide](docs/DEVELOPER_SETUP.md)** - Complete setup instructions
4. **[Quick Reference](docs/QUICK_REFERENCE.md)** - Essential commands and shortcuts
5. **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Solutions to common problems

### Quick Setup (TL;DR)

```bash
# Clone the repository
git clone <repository-url>
cd core-backend

# Run automated setup
./setup-dev.sh      # Linux/macOS
./setup-dev.bat     # Windows

# Start development
source venv/bin/activate  # or venv\Scripts\activate on Windows
docker-compose up -d
cd core && python manage.py runserver
```

## 📖 Documentation Structure

| Document                                               | Purpose                                  | Audience                       |
| ------------------------------------------------------ | ---------------------------------------- | ------------------------------ |
| [docs/DEVELOPER_SETUP.md](docs/DEVELOPER_SETUP.md)     | Complete development environment setup   | New developers, contributors   |
| [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)     | Daily development commands and shortcuts | All developers                 |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)     | Common issues and solutions              | Developers facing problems     |
| [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) | API endpoints and usage                  | Frontend developers, API users |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)               | Production deployment guide              | DevOps, system administrators  |
| [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)           | How to contribute to the project         | Contributors, developers       |

## 🔴 Directory Structure Standards

### CRITICAL RULES - NO EXCEPTIONS

#### 1. **ROOT LEVEL ORGANIZATION**

```
core-backend/           # ✅ Project root - NEVER rename or move
├── core/              # ✅ Django project - NEVER rename or move
├── docs/              # ✅ Documentation - NEVER rename or move
├── venv/              # ✅ Virtual environment - NEVER commit to git
├── requirements.txt   # ✅ Dependencies - SINGLE source of truth
├── .env.example       # ✅ ENV template - Template for configuration
└── setup-dev.*        # ✅ Setup scripts - Automated environment setup
```

#### 2. **DJANGO PROJECT STRUCTURE**

```
core/                   # ✅ Django project directory
├── core/              # ✅ Settings package - Project configuration
│   ├── settings.py    # ✅ MANDATORY - All Django settings
│   ├── urls.py        # ✅ MANDATORY - Root URL configuration
│   ├── celery.py      # ✅ MANDATORY - Celery configuration
│   ├── asgi.py        # ✅ MANDATORY - ASGI configuration
│   ├── wsgi.py        # ✅ MANDATORY - WSGI configuration
│   └── __init__.py    # ✅ MANDATORY - Package initialization
├── apps/              # ✅ MANDATORY - ALL Django apps go here
│   ├── __init__.py    # ✅ MANDATORY - Package initialization
│   └── accounts/      # ✅ Example app structure
├── templates/         # ✅ Django templates directory
├── .env               # ✅ Local environment (NEVER commit)
└── manage.py          # ✅ MANDATORY - Django management
```

#### 3. **DJANGO APP STRUCTURE**

Every app in `core/apps/` MUST follow this structure:

```
your_app/              # ✅ App directory name (lowercase, underscores)
├── __init__.py        # ✅ MANDATORY - Package marker
├── apps.py            # ✅ MANDATORY - App configuration
├── models.py          # ✅ MANDATORY - Database models
├── views.py           # ✅ MANDATORY - API views
├── serializers.py     # ✅ MANDATORY - DRF serializers
├── urls.py            # ✅ MANDATORY - App URL patterns
├── tests.py           # ✅ MANDATORY - Unit tests
├── admin.py           # 🟡 Optional - Django admin
├── managers.py        # 🟡 Optional - Custom model managers
├── signals.py         # 🟡 Optional - Django signals
├── tasks.py           # 🟡 Optional - Celery tasks
├── utils.py           # 🟡 Optional - Helper functions
└── migrations/        # ✅ MANDATORY - Database migrations
    └── __init__.py    # ✅ MANDATORY - Package marker
```

#### 4. **CONFIGURATION FILES HIERARCHY**

**Environment Configuration:**

- `/.env.example` → Template for all environments
- `/core/.env` → Local development configuration (from template)
- **NEVER** create multiple .env files in different locations

**Dependencies:**

- `/requirements.txt` → SINGLE source of truth for ALL dependencies
- **NEVER** create app-specific requirements files
- **NEVER** create multiple requirements files

## 🔴 Development Guidelines

### MANDATORY PRACTICES

#### 1. **Before Making ANY Changes**

```bash
# ✅ MANDATORY - Always run these checks
git status                    # Check current state
git pull origin develop       # Get latest changes
source venv/bin/activate     # Activate environment
python manage.py check       # Validate Django setup
python manage.py test        # Run existing tests
```

#### 2. **File Naming Conventions**

- **Python files**: `snake_case.py` (e.g., `user_management.py`)
- **Django apps**: `lowercase_with_underscores` (e.g., `user_profiles`)
- **Classes**: `PascalCase` (e.g., `UserProfileManager`)
- **Functions/variables**: `snake_case` (e.g., `get_user_profile`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_LOGIN_ATTEMPTS`)

#### 3. **Import Organization**

```python
<<<<<<< HEAD
# ✅ MANDATORY - Import order in ALL Python files
# 1. Standard library imports
import os
import json
from datetime import datetime

# 2. Third-party imports
from django.contrib.auth import authenticate
from rest_framework import serializers
from celery import shared_task

# 3. Local application imports
from core.apps.accounts.models import User
from core.apps.accounts.utils import generate_token
=======
from core.modules.auth.accounts.tasks import send_welcome_email
send_welcome_email.delay("test@example.com")
# Check your Celery worker terminal for output.
>>>>>>> b2629e6c9f4632eca6009cf78db6b314a041b8c6
```

#### 4. **Django App Creation Process**

```bash
# ✅ MANDATORY - Exact steps to create new Django app
cd core
python manage.py startapp your_app_name apps/your_app_name

# ✅ MANDATORY - Add to INSTALLED_APPS in settings.py
# 'core.apps.your_app_name',

# ✅ MANDATORY - Create initial files
touch apps/your_app_name/serializers.py
touch apps/your_app_name/tasks.py
touch apps/your_app_name/utils.py
```

#### 5. **Database Migration Rules**

```bash
# ✅ MANDATORY - Always follow this sequence
python manage.py makemigrations           # Create migration
python manage.py migrate                  # Apply migration
python manage.py test                     # Validate no breakage
git add core/apps/*/migrations/           # Stage migrations
git commit -m "Add: migration for [description]"  # Commit with clear message
```

## 🔴 File Organization Rules

### ABSOLUTE PROHIBITIONS

#### ❌ NEVER DO THESE:

1. **Move core Django files** (`settings.py`, `urls.py`, `manage.py`)
2. **Create apps outside** `core/apps/` directory
3. **Create multiple requirements.txt** files
4. **Create .env files** in multiple locations
5. **Commit .env files** to version control
6. **Create circular imports** between apps
7. **Import using relative paths** from parent directories
8. **Mix business logic** in views (use services/utils)
9. **Create models** outside Django apps
10. **Hardcode configuration** values (use settings/environment)

#### ✅ ALWAYS DO THESE:

1. **Create new apps** in `core/apps/` directory
2. **Use single requirements.txt** in project root
3. **Follow Django app** structure exactly
4. **Write tests** for all new features
5. **Update documentation** for any structural changes
6. **Use descriptive commit** messages
7. **Run tests** before committing
8. **Follow import** organization rules
9. **Use environment variables** for configuration
10. **Document any new** dependencies or setup steps

### Where to Put Different Types of Files

| File Type            | Location                                       | Example                             |
| -------------------- | ---------------------------------------------- | ----------------------------------- |
| **Django Apps**      | `core/apps/your_app/`                          | `core/apps/user_profiles/`          |
| **Models**           | `core/apps/your_app/models.py`                 | User models in `accounts/models.py` |
| **API Views**        | `core/apps/your_app/views.py`                  | API endpoints                       |
| **Serializers**      | `core/apps/your_app/serializers.py`            | DRF serializers                     |
| **Background Tasks** | `core/apps/your_app/tasks.py`                  | Celery tasks                        |
| **Utilities**        | `core/apps/your_app/utils.py`                  | Helper functions                    |
| **Tests**            | `core/apps/your_app/tests.py`                  | Unit tests                          |
| **Templates**        | `core/templates/your_app/`                     | HTML templates                      |
| **Static Files**     | `core/static/your_app/`                        | CSS, JS, images                     |
| **Documentation**    | `docs/`                                        | All documentation                   |
| **Configuration**    | `core/core/settings.py`                        | Django settings                     |
| **Dependencies**     | `requirements.txt`                             | Python packages                     |
| **Environment**      | `.env.example` (template), `core/.env` (local) | Configuration                       |

## 🏗️ Project Architecture

### Technology Stack

- **Backend Framework**: Django 5.1.3 with Django REST Framework
- **Database**: PostgreSQL 15+
- **Cache & Task Queue**: Redis
- **Background Tasks**: Celery
- **Authentication**: JWT with Two-Factor Authentication (2FA)
- **Containerization**: Docker & Docker Compose
- **Monitoring**: Flower (Celery task monitoring)

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend App  │    │  Django API     │    │   PostgreSQL    │
│   (React/Vue)   │◄──►│   (Backend)     │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │     Redis       │◄──►│  Celery Workers │
                       │  (Cache/Queue)  │    │ (Background)    │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │     Flower      │
                       │  (Monitoring)   │
                       └─────────────────┘
```

### Directory Structure

```
core-backend/                   # 🔴 PROJECT ROOT - NEVER move or rename
├── 📁 core/                    # 🔴 DJANGO PROJECT ROOT - Main Django project
│   ├── 📁 core/               # 🔴 DJANGO SETTINGS - Project configuration
│   │   ├── settings.py        # 🔴 MANDATORY - Django configuration
│   │   ├── urls.py           # 🔴 MANDATORY - Root URL routing
│   │   ├── celery.py         # 🔴 MANDATORY - Celery configuration
│   │   ├── asgi.py           # 🔴 MANDATORY - ASGI entry point
│   │   ├── wsgi.py           # 🔴 MANDATORY - WSGI entry point
│   │   └── __init__.py       # 🔴 MANDATORY - Python package marker
│   ├── 📁 apps/              # 🔴 DJANGO APPS - ALL Django applications go here
│   │   ├── __init__.py       # 🔴 MANDATORY - Python package marker
│   │   └── 📁 accounts/      # 🟡 USER MANAGEMENT - User auth & management
│   │       ├── models.py     # 🔴 MANDATORY - Database models
│   │       ├── views.py      # 🔴 MANDATORY - API endpoints
│   │       ├── serializers.py # 🔴 MANDATORY - Data serialization
│   │       ├── tasks.py      # 🟡 CELERY TASKS - Background tasks
│   │       ├── urls.py       # 🔴 MANDATORY - App URLs
│   │       ├── admin.py      # 🟡 DJANGO ADMIN - Admin interface
│   │       ├── managers.py   # 🟡 CUSTOM MANAGERS - Database managers
│   │       ├── signals.py    # 🟡 DJANGO SIGNALS - Event handlers
│   │       ├── utils.py      # 🟡 UTILITIES - Helper functions
│   │       ├── tests.py      # 🔴 MANDATORY - Unit tests
│   │       ├── apps.py       # 🔴 MANDATORY - App configuration
│   │       ├── __init__.py   # 🔴 MANDATORY - Python package marker
│   │       └── 📁 migrations/ # 🔴 MANDATORY - Database migrations
│   │           ├── __init__.py # 🔴 MANDATORY - Python package marker
│   │           └── *.py      # 🔴 AUTO-GENERATED - Migration files
│   ├── 📁 templates/         # 🟡 HTML TEMPLATES - Django templates
│   │   └── 📁 two_factor/    # 🟡 2FA TEMPLATES - Two-factor auth templates
│   ├── .env                  # 🔴 ENVIRONMENT CONFIG - Local settings (NEVER commit)
│   └── manage.py             # 🔴 MANDATORY - Django management script
├── 📁 docs/                  # 🔴 DOCUMENTATION - Project documentation
│   ├── README.md             # 🔴 MANDATORY - Documentation index
│   ├── DEVELOPER_SETUP.md    # 🔴 MANDATORY - Setup instructions
│   ├── QUICK_REFERENCE.md    # 🔴 MANDATORY - Daily commands
│   ├── TROUBLESHOOTING.md    # 🔴 MANDATORY - Problem solutions
│   ├── CONTRIBUTING.md       # 🟡 CONTRIBUTION GUIDELINES
│   └── api_documentation_template.md # 🟡 API DOCS TEMPLATE
├── 📁 venv/                  # 🔴 VIRTUAL ENVIRONMENT - Python isolation (NEVER commit)
├── 📁 frontend/              # 🟡 FRONTEND DEMO - Optional demo frontend
├── .env.example              # 🔴 ENV TEMPLATE - Environment configuration template
├── requirements.txt          # 🔴 DEPENDENCIES - Python package requirements
├── docker-compose.yml        # 🔴 DOCKER CONFIG - Multi-service configuration
├── Dockerfile               # 🔴 CONTAINER CONFIG - Container build instructions
├── setup-dev.sh/.bat       # 🔴 SETUP SCRIPTS - Automated environment setup
├── .gitignore               # 🔴 GIT CONFIG - Files to ignore in version control
├── .dockerignore            # 🔴 DOCKER CONFIG - Files to ignore in containers
└── README.md                # 🔴 PROJECT OVERVIEW - Main project README
```

**Legend:**

- 🔴 **MANDATORY** - Required files/folders, DO NOT delete or move
- 🟡 **OPTIONAL** - Can be modified or extended as needed
- 📁 **DIRECTORY** - Folder structure

## 🔧 Development Workflow

### Daily Development Process

1. **Start Development Session**

   ```bash
   source venv/bin/activate    # Activate virtual environment
   docker-compose up -d        # Start background services
   cd core && python manage.py runserver  # Start Django
   ```

2. **Access Services**

   - Django API: http://localhost:8000
   - Admin Interface: http://localhost:8000/admin
   - Celery Monitor: http://localhost:5555

3. **Make Changes**

   - Edit code in your preferred editor
   - Run tests: `python manage.py test`
   - Check migrations: `python manage.py makemigrations`

4. **End Development Session**
   ```bash
   # Stop Django server (Ctrl+C)
   docker-compose down         # Stop background services
   deactivate                  # Deactivate virtual environment
   ```

### Key Development Commands

| Task                  | Command                            |
| --------------------- | ---------------------------------- |
| Run server            | `python manage.py runserver`       |
| Run tests             | `python manage.py test`            |
| Create migrations     | `python manage.py makemigrations`  |
| Apply migrations      | `python manage.py migrate`         |
| Django shell          | `python manage.py shell`           |
| Create superuser      | `python manage.py createsuperuser` |
| Start Docker services | `docker-compose up -d`             |
| View Docker logs      | `docker-compose logs -f`           |
| Stop Docker services  | `docker-compose down`              |

## 🌐 Service URLs & Ports

| Service      | URL                         | Port | Purpose                  |
| ------------ | --------------------------- | ---- | ------------------------ |
| Django API   | http://localhost:8000       | 8000 | Main application server  |
| Django Admin | http://localhost:8000/admin | 8000 | Admin interface          |
| PostgreSQL   | localhost:5432              | 5432 | Database server          |
| Redis        | localhost:6379              | 6379 | Cache and message broker |
| Flower       | http://localhost:5555       | 5555 | Celery task monitoring   |

## 🔐 Security Features

### Authentication & Authorization

- **JWT Authentication**: Secure token-based authentication
- **Two-Factor Authentication (2FA)**: TOTP-based MFA support
- **Role-Based Permissions**: Fine-grained access control
- **Password Security**: Strong password requirements and hashing

### Security Measures

- **CORS Protection**: Cross-origin request filtering
- **CSRF Protection**: Cross-site request forgery prevention
- **Rate Limiting**: API rate limiting (planned)
- **Input Validation**: Comprehensive data validation
- **SQL Injection Protection**: Django ORM protection

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.accounts

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Test Types

- **Unit Tests**: Testing individual functions and methods
- **Integration Tests**: Testing component interactions
- **API Tests**: Testing REST API endpoints
- **Authentication Tests**: Testing security features

## 📊 Monitoring & Debugging

### Available Tools

- **Django Debug Toolbar**: SQL queries and performance metrics
- **Flower**: Celery task monitoring and management
- **Django Admin**: Database administration interface
- **Logs**: Comprehensive logging throughout the application

### Performance Monitoring

```bash
# Check container resources
docker stats

# Monitor database performance
python manage.py dbshell

# View application logs
docker-compose logs -f celery-worker
```

## 🚀 Deployment Options

### Development

- Local development with SQLite/PostgreSQL
- Docker Compose for service orchestration
- Hot reloading with Django development server

### Production (Planned)

- Docker containers with orchestration (Kubernetes/Docker Swarm)
- Separate databases and Redis instances
- Load balancing and horizontal scaling
- Monitoring and alerting systems

## 🤝 Contributing

We welcome contributions! Please see:

1. **[Contributing Guidelines](docs/CONTRIBUTING.md)** - How to contribute
2. **[Code Style Guide](docs/CODE_STYLE.md)** - Coding standards
3. **[Issue Templates](.github/ISSUE_TEMPLATE/)** - Bug reports and features

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support & Help

### Getting Help

1. **Check Documentation**: Start with this documentation
2. **Search Issues**: Look for existing GitHub issues
3. **Ask Questions**: Create a new issue with the question label
4. **Community**: Join our developer community (links TBD)

### Reporting Issues

When reporting bugs, include:

- Operating system and version
- Python version
- Complete error messages
- Steps to reproduce
- Expected vs actual behavior

### Feature Requests

We're always open to new ideas! When requesting features:

- Describe the use case
- Explain the expected behavior
- Consider the impact on existing functionality
- Be willing to contribute to the implementation

## 📚 Additional Resources

### Learning Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)

### External Tools

- [Postman](https://www.postman.com/) - API testing
- [pgAdmin](https://www.pgadmin.org/) - PostgreSQL administration
- [Redis Commander](http://joeferner.github.io/redis-commander/) - Redis management
- [DBeaver](https://dbeaver.io/) - Universal database tool

---

**🚨 CRITICAL REMINDER: Guidelines Compliance is MANDATORY**

Every developer working on this project MUST:

- ✅ Follow the directory structure standards
- ✅ Adhere to development guidelines
- ✅ Complete the compliance checklist
- ✅ Maintain code quality standards
- ✅ Keep documentation current

**Violation of these guidelines will result in rejected pull requests and required training.**

---

**Last Updated**: August 31, 2025  
**Version**: 2.0.0 - Comprehensive Guidelines Edition
**Maintainers**: Gradvy Development Team  
**Guidelines Status**: ENFORCED - Compliance Required

## 📜 Guidelines Summary

| Category             | Status       | Enforcement        |
| -------------------- | ------------ | ------------------ |
| Directory Structure  | 🔴 MANDATORY | PR Review Required |
| Code Standards       | 🔴 MANDATORY | Automated Checks   |
| Testing Requirements | 🔴 MANDATORY | CI/CD Pipeline     |
| Documentation        | 🔴 MANDATORY | Review Required    |
| Security Practices   | 🔴 MANDATORY | Security Audit     |

**Remember: These guidelines exist to ensure code quality, team collaboration, and project success. Following them makes everyone's life easier! 🚀**

Happy coding! 🎯

## Admin Dashboard

You can access the admin dashboard at `http://127.0.0.1:8000/admin/`. You will be redirected to a login page where you can use your superuser credentials.
