# Gradvy - Hybrid Development Authentication System

<div align="center">

![Gradvy Logo](https://img.shields.io/badge/Gradvy-Authentication-blue?style=for-the-badge)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![Django 5.1](https://img.shields.io/badge/Django-5.1-green.svg?style=flat-square)](https://djangoproject.com/)
[![PostgreSQL 15](https://img.shields.io/badge/PostgreSQL-15-blue.svg?style=flat-square)](https://postgresql.org/)
[![Redis 7](https://img.shields.io/badge/Redis-7-red.svg?style=flat-square)](https://redis.io/)

*Fast hybrid development with Docker data services + local Django*

</div>

## 🚀 Quick Start

Get Gradvy running in under 2 minutes with our hybrid setup:

```bash
# 1. Clone and navigate
git clone https://github.com/Syedsafwan24/Gradvy.git
cd Gradvy/backend

# 2. Setup local environment
./scripts/local-setup.sh

# 3. Start data services (PostgreSQL + Redis)
./scripts/data-start.sh

# 4. Run migrations
./scripts/local-migrate.sh

# 5. Create admin user  
./scripts/local-superuser.sh

# 6. Start Django locally
./scripts/local-dev.sh
```

🎉 **Access your application:**
- **Django Admin**: http://localhost:8000/admin/
- **Main API**: http://localhost:8000/api/
- **Flower Monitoring**: http://localhost:5555/ (when running Celery)

## 🏗️ Hybrid Architecture Overview

Gradvy uses a **hybrid development architecture** for optimal developer experience - data services in Docker, application services local:

### 🛠️ Hybrid Tech Stack

| Component | Technology | Version | Location | Purpose |
|-----------|------------|---------|----------|---------|
| **Django** | Django | 5.1.3 | 🏠 Local | Web framework & API |
| **Database** | PostgreSQL | 15 | 🐳 Docker | Data persistence |  
| **Cache** | Redis | 7 | 🐳 Docker | Caching & message broker |
| **Queue** | Celery | 5.3.6 | 🏠 Local | Background processing |
| **Monitoring** | Flower | 2.0.1 | 🏠 Local | Task monitoring UI |
| **Auth** | JWT + TOTP | Latest | 🏠 Local | Authentication & MFA |

### 🔧 Hybrid Development Benefits

- ⚡ **Fast Development** - No container rebuilds on code changes
- 🐛 **Easy Debugging** - Direct IDE integration and breakpoints
- 💾 **Data Persistence** - PostgreSQL and Redis data preserved in Docker
- 🔄 **Hot Reload** - Instant Django auto-reload on file changes  
- 🧪 **Simple Testing** - Direct access to Django test commands
- 🛠️ **Local Tools** - Full access to Python debugging tools
- 📊 **Consistent Data** - Shared Docker data services for team consistency

## 📋 Prerequisites

- **Docker & Docker Compose** (recommended)
- **Python 3.13+** (for local development)
- **Git** for version control

## 🛠️ Hybrid Development Setup

### Step-by-Step Setup

```bash
# 1. Setup complete local environment
./scripts/local-setup.sh

# 2. Start data services (PostgreSQL + Redis in Docker)  
./scripts/data-start.sh

# 3. Run database migrations locally
./scripts/local-migrate.sh

# 4. Create admin user (interactive)
./scripts/local-superuser.sh

# 5. Start Django development server locally
./scripts/local-dev.sh
```

### Advanced Usage

```bash
# Start Celery worker locally (optional)
./scripts/local-celery.sh

# Start Flower monitoring locally (optional)  
./scripts/local-flower.sh

# Stop data services when done
docker-compose down

# Restart data services
./scripts/data-start.sh
```

## 🔧 Configuration

### Environment Variables

Key configuration options:

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | `dev-secret-key...` |
| `DJANGO_DEBUG` | Debug mode | `True` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://...` |
| `CELERY_BROKER_URL` | Redis connection | `redis://localhost:6379/0` |
| `FLOWER_PASSWORD` | Flower UI password | `flower_admin_2024` |

### Service Configuration

Services in `docker-compose.yml`:

- **gradvy-postgres**: PostgreSQL database with persistence
- **gradvy-redis**: Redis cache with AOF persistence
- **gradvy-celery-worker**: Background task processor
- **gradvy-celery-beat**: Periodic task scheduler
- **gradvy-flower**: Task monitoring interface

## 📊 Hybrid Development Scripts

Professional scripts optimized for hybrid development:

```bash
# Environment Setup
./scripts/local-setup.sh     # Complete local environment setup
./scripts/data-start.sh      # Start PostgreSQL + Redis containers

# Database Management
./scripts/local-migrate.sh   # Run migrations locally
./scripts/local-superuser.sh # Create admin user locally

# Development Servers  
./scripts/local-dev.sh       # Start Django development server
./scripts/local-celery.sh    # Start Celery worker locally
./scripts/local-flower.sh    # Start Flower monitoring locally

# Data Services
docker-compose up -d         # Start data services
docker-compose down          # Stop data services  
docker-compose ps            # Check service status
```

## 🧪 Authentication API

### Core Endpoints

```bash
# Authentication
POST /api/auth/login/          # User login
POST /api/auth/refresh/        # Refresh JWT
POST /api/auth/logout/         # User logout

# Multi-Factor Authentication
POST /api/auth/mfa/enroll/     # Setup MFA
PUT  /api/auth/mfa/enroll/     # Confirm MFA setup
POST /api/auth/mfa/verify/     # Verify MFA code
POST /api/auth/mfa/disable/    # Disable MFA

# User Management
GET  /api/auth/profile/        # Get user profile
PUT  /api/auth/profile/        # Update profile
POST /api/auth/password/change/ # Change password
```

### Example: MFA Enrollment

```http
POST /api/auth/mfa/enroll/
Authorization: Bearer <access_token>
```

Response:
```json
{
    "secret": "JBSWY3DPEHPK3PXP",
    "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "backup_codes": [
        "ABC123DEF",
        "GHI456JKL"
    ],
    "device_id": 1
}
```

## 🔍 Monitoring

### Service Health

```bash
# Check all services
docker-compose ps

# View specific service logs
./scripts/dev-logs.sh gradvy-celery-worker

# Monitor with Flower
open http://localhost:5555
```

### Database Access

```bash
# Direct PostgreSQL access
docker exec -it gradvy-postgres psql -U gradvy_user -d gradvy_db

# Run migrations
./scripts/db-migrate.sh
```

## 🏗️ Hybrid Project Structure

```
backend/
├── 📁 core/                      # 🏠 Django project (Local)
│   ├── 📁 apps/                 # Applications
│   │   └── 📁 auth/             # 🔐 Authentication app
│   │       ├── models.py        # User, UserProfile, BackupCode
│   │       ├── views.py         # Auth API endpoints
│   │       ├── serializers.py   # API serializers
│   │       ├── urls.py          # URL routing
│   │       └── tasks.py         # Background tasks
│   ├── 📁 core/                 # Django settings
│   └── manage.py                # Django management
├── 📁 scripts/                  # 🛠️ Hybrid development scripts
│   ├── local-setup.sh          # Complete environment setup
│   ├── data-start.sh           # Start Docker data services
│   ├── local-dev.sh            # Start Django locally
│   ├── local-celery.sh         # Start Celery locally
│   ├── local-flower.sh         # Start Flower locally
│   ├── local-migrate.sh        # Run migrations locally
│   └── local-superuser.sh      # Create superuser locally
├── 📁 venv/                     # 🏠 Python virtual environment (Local)
├── 📄 docker-compose.yml        # 🐳 Data services only (PostgreSQL + Redis)
├── 📄 requirements.txt         # Python dependencies
├── 📄 .env.example             # Hybrid environment template
└── 📄 README.md                # This documentation
```

## 🔒 Security Features

- **JWT Tokens**: Secure authentication with refresh tokens
- **MFA/2FA**: Time-based OTP with backup codes
- **QR Code Generation**: Easy TOTP device setup
- **Account Locking**: Brute force protection
- **Password Security**: Strong password requirements
- **Environment Secrets**: Secure configuration management

## 🚀 Production Deployment

```bash
# 1. Configure production environment
cp .env.example .env.production

# 2. Build production containers
docker-compose -f docker-compose.prod.yml build

# 3. Deploy services
docker-compose -f docker-compose.prod.yml up -d

# 4. Run migrations
docker-compose exec gradvy-django python manage.py migrate
```

## 🆘 Troubleshooting

### Common Issues

**Database Connection Error:**
```bash
# Check PostgreSQL service
./scripts/dev-logs.sh gradvy-postgres

# Restart database
docker-compose restart gradvy-postgres
```

**Celery Tasks Not Processing:**
```bash
# Check worker status
./scripts/dev-logs.sh gradvy-celery-worker

# Restart Celery services
docker-compose restart gradvy-celery-worker
```

**Port Conflicts:**
```bash
# Check port usage
netstat -tulpn | grep :5432

# Modify ports in docker-compose.yml if needed
```

## 🤝 Contributing

1. **Fork & Clone**
2. **Setup Environment**: `./scripts/dev-start.sh`
3. **Create Branch**: `git checkout -b feature/awesome-feature`
4. **Test Changes**: `python manage.py test`
5. **Submit PR**

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**🔐 Built for secure, scalable authentication**

[⭐ Star this repo](https://github.com/Syedsafwan24/Gradvy) | [🐛 Report Bug](https://github.com/Syedsafwan24/Gradvy/issues) | [💡 Request Feature](https://github.com/Syedsafwan24/Gradvy/issues)

</div>