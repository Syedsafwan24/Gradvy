# Gradvy - Cross-Platform Setup Guide

<div align="center">

![Gradvy Logo](https://img.shields.io/badge/Gradvy-Authentication-blue?style=for-the-badge)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![Django 5.1](https://img.shields.io/badge/Django-5.1-green.svg?style=flat-square)](https://djangoproject.com/)
[![Cross Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-brightgreen.svg?style=flat-square)](#)

*Professional authentication system with MFA support - works on all platforms*

</div>

## 🚀 Quick Start (All Platforms)

Choose your platform for optimized setup instructions:

| Platform | Quick Setup | Full Guide |
|----------|-------------|------------|
| 🪟 **Windows** | [Windows Quick Start](#-windows-setup) | [Detailed Windows Guide](#windows-detailed-setup) |
| 🍎 **macOS** | [macOS Quick Start](#-macos-setup) | [Detailed macOS Guide](#macos-detailed-setup) |
| 🐧 **Linux** | [Linux Quick Start](#-linux-setup) | [Detailed Linux Guide](#linux-detailed-setup) |
| 🐳 **Docker** | [Docker Setup](#-docker-setup-universal) | [Docker Production](#docker-production-setup) |

---

## 📋 Prerequisites (All Platforms)

### Required Software
- **Python 3.13+** 
- **Git** 
- **Docker & Docker Compose** (recommended)

### Optional but Recommended
- **VS Code** or **PyCharm** for development
- **Postman** or **Thunder Client** for API testing

---

## 🪟 Windows Setup

### Windows Quick Start

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

### Windows Prerequisites Installation

#### Option 1: Using Chocolatey (Recommended)
```powershell
# Install Chocolatey first: https://chocolatey.org/install

# Install all prerequisites
choco install python git docker-desktop -y

# Refresh environment
refreshenv
```

#### Option 2: Manual Installation
1. **Python 3.13**: Download from [python.org](https://www.python.org/downloads/windows/)
   - ✅ Check "Add Python to PATH"
   - ✅ Check "Install pip"

2. **Git**: Download from [git-scm.com](https://git-scm.com/download/win)

3. **Docker Desktop**: Download from [docker.com](https://www.docker.com/products/docker-desktop)

### Windows Detailed Setup

```powershell
# 1. Verify installations
python --version  # Should show 3.13+
git --version
docker --version

# 2. Clone and navigate
git clone https://github.com/Syedsafwan24/Gradvy.git
cd Gradvy\backend

# 3. Create virtual environment
python -m venv venv

# 4. Activate virtual environment
.\venv\Scripts\Activate.ps1
# For Command Prompt: .\venv\Scripts\activate.bat

# 5. Upgrade pip
python -m pip install --upgrade pip

# 6. Install dependencies
pip install -r requirements.txt

# 7. Environment configuration
copy .env.example .env
# Edit .env file with your preferred editor

# 8. Start data services
docker-compose up -d

# 9. Wait for services to be ready (30 seconds)
timeout /t 30

# 10. Run database setup
python core\manage.py migrate
python core\manage.py collectstatic --noinput

# 11. Create admin user
python core\manage.py createsuperuser

# 12. Start development server
python core\manage.py runserver

# 13. Open in browser
start http://localhost:8000/admin/
```

### Windows Troubleshooting

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

## 🍎 macOS Setup

### macOS Quick Start

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

### macOS Prerequisites Installation

#### Option 1: Using Homebrew (Recommended)
```bash
# Install Homebrew first: https://brew.sh

# Install all prerequisites
brew install python@3.13 git
brew install --cask docker

# Start Docker Desktop
open /Applications/Docker.app
```

#### Option 2: Using MacPorts
```bash
# Install MacPorts first: https://www.macports.org

sudo port install python313 git
# Download Docker Desktop manually
```

### macOS Detailed Setup

```bash
# 1. Verify installations
python3 --version  # Should show 3.13+
git --version
docker --version

# 2. Clone repository
git clone https://github.com/Syedsafwan24/Gradvy.git
cd Gradvy/backend

# 3. Create virtual environment
python3 -m venv venv

# 4. Activate virtual environment
source venv/bin/activate

# 5. Upgrade pip
pip install --upgrade pip

# 6. Install dependencies
pip install -r requirements.txt

# 7. Environment setup
cp .env.example .env
# Edit with your preferred editor: nano .env, vim .env, or code .env

# 8. Start data services
docker-compose up -d

# 9. Wait for services
sleep 30

# 10. Database setup
python core/manage.py migrate
python core/manage.py collectstatic --noinput

# 11. Create superuser
python core/manage.py createsuperuser

# 12. Start development server
python core/manage.py runserver

# 13. Open in browser
open http://localhost:8000/admin/
```

### macOS Troubleshooting

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

## 🐧 Linux Setup

### Linux Quick Start

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
python manage.py migrate

# 7. Create superuser
python manage.py createsuperuser

# 8. Start development server
python manage.py runserver
```

### Linux Prerequisites Installation

#### Ubuntu/Debian
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

# Logout and login to apply docker group changes
```

#### CentOS/RHEL/Fedora
```bash
# Install Python 3.13 (Fedora)
sudo dnf install python3.13 python3-pip git -y

# Install Python 3.13 (CentOS/RHEL)
sudo yum install python39 python3-pip git -y  # Use available version
# Or use pyenv to install 3.13

# Install Docker
sudo dnf install docker docker-compose -y  # Fedora
sudo yum install docker docker-compose -y  # CentOS/RHEL

sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

#### Arch Linux
```bash
# Install prerequisites
sudo pacman -S python python-pip git docker docker-compose

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

### Linux Detailed Setup

```bash
# 1. Verify installations
python3 --version  # Should show 3.13+ or available version
git --version
docker --version
docker-compose --version

# 2. Clone repository
git clone https://github.com/Syedsafwan24/Gradvy.git
cd Gradvy/backend

# 3. Create virtual environment
python3 -m venv venv

# 4. Activate virtual environment
source venv/bin/activate

# 5. Upgrade pip
pip install --upgrade pip

# 6. Install system dependencies (if needed)
# Ubuntu/Debian:
sudo apt install libpq-dev python3-dev build-essential -y
# CentOS/RHEL:
# sudo yum install postgresql-devel python3-devel gcc -y

# 7. Install Python dependencies
pip install -r requirements.txt

# 8. Environment configuration
cp .env.example .env
# Edit configuration
nano .env  # or vim .env

# 9. Start data services
docker-compose up -d

# 10. Wait for services to start
sleep 30

# 11. Database setup
python core/manage.py migrate
python core/manage.py collectstatic --noinput

# 12. Create superuser
python core/manage.py createsuperuser

# 13. Start development server
python core/manage.py runserver 0.0.0.0:8000

# 14. Test connection
curl http://localhost:8000/admin/
```

### Linux Troubleshooting

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
# Or
sudo netstat -tulnp | grep :8000

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

## 🐳 Docker Setup (Universal)

### Docker Quick Start

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

### Docker Production Setup

```bash
# 1. Build production images
docker-compose -f docker-compose.prod.yml build

# 2. Start production services
docker-compose -f docker-compose.prod.yml up -d

# 3. Run migrations
docker-compose -f docker-compose.prod.yml exec django python manage.py migrate

# 4. Collect static files
docker-compose -f docker-compose.prod.yml exec django python manage.py collectstatic --noinput

# 5. Create superuser
docker-compose -f docker-compose.prod.yml exec django python manage.py createsuperuser
```

---

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

## 🔧 Development Tools

### VS Code Setup

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

### Environment Variables

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

## 🚨 Troubleshooting

### Common Issues

| Issue | Windows | macOS | Linux |
|-------|---------|-------|--------|
| Permission Denied | Run as Administrator | Use `sudo` | Use `sudo` |
| Port in Use | `netstat -ano \| findstr :8000` | `lsof -ti:8000` | `sudo netstat -tulnp \| grep :8000` |
| Docker not found | Restart Docker Desktop | Open Docker.app | `sudo systemctl start docker` |
| Python not found | Add to PATH | Use `python3` | Install python3-dev |

### Getting Help

1. **Check logs**: `docker-compose logs <service-name>`
2. **Verify services**: `docker-compose ps`
3. **Test connectivity**: Use provided curl commands
4. **Reset environment**: `docker-compose down -v && docker-compose up -d`

---

## 📚 Next Steps

1. **API Documentation**: Visit http://localhost:8000/api/docs/ (when available)
2. **Admin Panel**: http://localhost:8000/admin/
3. **Development Guide**: See [DEVELOPER_SETUP.md](docs/DEVELOPER_SETUP.md)
4. **Deployment Guide**: See [docs/deployment/](docs/deployment/)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Follow platform-specific setup above
4. Make changes and test
5. Submit pull request

---

<div align="center">

**🔐 Gradvy - Secure Authentication for Everyone, Everywhere**

[Report Bug](https://github.com/Syedsafwan24/Gradvy/issues) | [Request Feature](https://github.com/Syedsafwan24/Gradvy/issues) | [Documentation](docs/)

</div>