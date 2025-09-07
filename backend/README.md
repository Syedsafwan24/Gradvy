# Gradvy - Hybrid Development Authentication System

<div align="center">

![Gradvy Logo](https://img.shields.io/badge/Gradvy-Authentication-blue?style=for-the-badge)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![Django 5.1](https://img.shields.io/badge/Django-5.1-green.svg?style=flat-square)](https://djangoproject.com/)
[![PostgreSQL 15](https://img.shields.io/badge/PostgreSQL-15-blue.svg?style=flat-square)](https://postgresql.org/)
[![Redis 7](https://img.shields.io/badge/Redis-7-red.svg?style=flat-square)](https://redis.io/)
[![Cross Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-brightgreen.svg?style=flat-square)](#cross-platform-setup)

*Professional authentication system with MFA support - works on all platforms*

</div>

## 🚀 Quick Start

Get Gradvy running in under 2 minutes with our hybrid setup:

| Platform | Quick Setup |
|----------|-------------|
| 🪟 **Windows** | [Windows Setup](#-windows-setup) |
| 🍎 **macOS** | [macOS Setup](#-macos-setup) |
| 🐧 **Linux** | [Linux Setup](#-linux-setup) |
| 🐳 **Docker** | [Docker Setup](#-docker-setup-universal) |

**Universal Quick Start:**
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

## 💻 Cross-Platform Setup

### 📋 Prerequisites (All Platforms)

#### Required Software
- **Python 3.13+** 
- **Git** 
- **Docker & Docker Compose** (recommended)

#### Optional but Recommended
- **VS Code** or **PyCharm** for development
- **Postman** or **Thunder Client** for API testing

---

### 🪟 Windows Setup

#### Windows Quick Start
```powershell
# 1. Clone repository
git clone https://github.com/Syedsafwan24/Gradvy.git
cd Gradvy\backend

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
copy .env.example .env

# 5. Start Docker services (PostgreSQL + Redis)
docker-compose up -d

# 6. Run migrations
python core\manage.py migrate

# 7. Create superuser
python core\manage.py createsuperuser

# 8. Start development server
python core\manage.py runserver
```

#### Windows Prerequisites Installation

**Option 1: Using Chocolatey (Recommended)**
```powershell
# Install Chocolatey first: https://chocolatey.org/install
choco install python git docker-desktop -y
refreshenv
```

**Option 2: Manual Installation**
1. **Python 3.13**: Download from [python.org](https://www.python.org/downloads/windows/)
   - ✅ Check "Add Python to PATH"
   - ✅ Check "Install pip"
2. **Git**: Download from [git-scm.com](https://git-scm.com/download/win)
3. **Docker Desktop**: Download from [docker.com](https://www.docker.com/products/docker-desktop)

#### Windows Troubleshooting

**PowerShell Execution Policy Error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Port Already in Use:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000
# Kill process (replace PID)
taskkill /F /PID <PID>
```

---

### 🍎 macOS Setup

#### macOS Quick Start
```bash
# 1. Clone repository
git clone https://github.com/Syedsafwan24/Gradvy.git
cd Gradvy/backend

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env

# 5. Start Docker services
docker-compose up -d

# 6. Run migrations
python core/manage.py migrate

# 7. Create superuser
python core/manage.py createsuperuser

# 8. Start development server
python core/manage.py runserver
```

#### macOS Prerequisites Installation

**Option 1: Using Homebrew (Recommended)**
```bash
# Install Homebrew first: https://brew.sh
brew install python@3.13 git
brew install --cask docker
open /Applications/Docker.app
```

**Option 2: Using MacPorts**
```bash
# Install MacPorts first: https://www.macports.org
sudo port install python313 git
# Download Docker Desktop manually
```

#### macOS Troubleshooting

**Python Version Issues:**
```bash
# If python3 points to older version
brew unlink python@3.12  # or older version
brew link python@3.13

# Or use pyenv for version management
brew install pyenv
pyenv install 3.13.0
pyenv global 3.13.0
```

**Port Issues:**
```bash
# Find process using port
lsof -ti:8000
# Kill process
kill -9 $(lsof -ti:8000)
```

---

### 🐧 Linux Setup

#### Linux Quick Start
```bash
# 1. Clone repository
git clone https://github.com/Syedsafwan24/Gradvy.git
cd Gradvy/backend

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env

# 5. Start Docker services
docker-compose up -d

# 6. Run migrations
python core/manage.py migrate

# 7. Create superuser
python core/manage.py createsuperuser

# 8. Start development server
python core/manage.py runserver
```

#### Linux Prerequisites Installation

**Ubuntu/Debian**
```bash
# Update package index
sudo apt update

# Install Python 3.13 and prerequisites
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-dev python3-pip git -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose -y
```

**CentOS/RHEL/Fedora**
```bash
# Install Python 3.13 (Fedora)
sudo dnf install python3.13 python3-pip git -y

# Install Docker
sudo dnf install docker docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

**Arch Linux**
```bash
# Install prerequisites
sudo pacman -S python python-pip git docker docker-compose

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

#### Linux Troubleshooting

**Permission Denied (Docker):**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Logout and login, or use:
newgrp docker
```

**Port in Use:**
```bash
# Find process
sudo lsof -i :8000
# Kill process
sudo kill -9 <PID>
```

**Python Version Not Available:**
```bash
# Install pyenv for version management
curl https://pyenv.run | bash
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

pyenv install 3.13.0
pyenv local 3.13.0
```

---

### 🐳 Docker Setup (Universal)

#### Docker Quick Start
```bash
# 1. Clone repository
git clone https://github.com/Syedsafwan24/Gradvy.git
cd Gradvy/backend

# 2. Build and start all services
docker-compose -f docker-compose.full.yml up -d --build

# 3. Run migrations
docker-compose exec gradvy-django python manage.py migrate

# 4. Create superuser
docker-compose exec gradvy-django python manage.py createsuperuser

# 5. Access application
# Django: http://localhost:8000
# Admin: http://localhost:8000/admin/
```

---

### 🔧 Development Tools

#### VS Code Setup

1. Install extensions:
   - Python
   - Django
   - Docker
   - REST Client

2. Open workspace:
   ```bash
   code Gradvy/backend
   ```

3. Configure Python interpreter:
   - Ctrl/Cmd + Shift + P
   - "Python: Select Interpreter"
   - Choose venv/bin/python or venv/Scripts/python.exe

#### Environment Variables

Create `.env` file with:
```env
# Django
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://gradvy_user:gradvy_password@localhost:5432/gradvy_db

# Redis
CELERY_BROKER_URL=redis://localhost:6380/0
CELERY_RESULT_BACKEND=redis://localhost:6380/0

# Optional
FLOWER_PASSWORD=flower_admin_2024
```

---

## 🆘 Troubleshooting

### Cross-Platform Issues

| Issue | Windows | macOS | Linux |
|-------|---------|-------|--------|
| Permission Denied | Run as Administrator | Use `sudo` | Use `sudo` |
| Port in Use | `netstat -ano \| findstr :8000` | `lsof -ti:8000` | `sudo netstat -tulnp \| grep :8000` |
| Docker not found | Restart Docker Desktop | Open Docker.app | `sudo systemctl start docker` |
| Python not found | Add to PATH | Use `python3` | Install python3-dev |

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

## 🧪 Testing & Validation

### Test Your Installation

```bash
# Activate virtual environment (if using local setup)
# Windows: .\venv\Scripts\Activate.ps1
# macOS/Linux: source venv/bin/activate

# Run basic tests
python core/manage.py check
python core/manage.py test

# Test API endpoints
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer <your-token>"
```

### Health Checks

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs gradvy-postgres
docker-compose logs gradvy-redis

# Test database connection
python core/manage.py dbshell
```

---

## 📚 Next Steps

1. **API Documentation**: Visit http://localhost:8000/api/docs/ (when available)
2. **Admin Panel**: http://localhost:8000/admin/
3. **MFA Setup**: Configure TOTP devices and backup codes
4. **Production Deployment**: See production configuration above

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Follow platform-specific setup above
4. Make changes and test
5. Submit pull request

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**🔐 Built for secure, scalable authentication**

[⭐ Star this repo](https://github.com/Syedsafwan24/Gradvy) | [🐛 Report Bug](https://github.com/Syedsafwan24/Gradvy/issues) | [💡 Request Feature](https://github.com/Syedsafwan24/Gradvy/issues)

</div>