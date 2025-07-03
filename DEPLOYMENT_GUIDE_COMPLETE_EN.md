# JobQuest Navigator - Complete Local Deployment Guide

This guide will walk new users through the complete deployment of JobQuest Navigator's local development environment from scratch, including detailed steps for both Windows and macOS platforms.

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Prerequisites](#prerequisites)
- [Windows Deployment Guide](#windows-deployment-guide)
- [macOS Deployment Guide](#macos-deployment-guide)
- [Universal Deployment Steps](#universal-deployment-steps)
- [Deployment Verification](#deployment-verification)
- [Troubleshooting](#troubleshooting)
- [Development Workflow](#development-workflow)

---

## 📊 System Requirements

### Minimum Configuration
- **Memory**: 8GB RAM (16GB recommended)
- **Storage**: 20GB available disk space
- **Network**: Stable internet connection
- **Operating System**: 
  - Windows 10/11 (64-bit)
  - macOS 10.15+ (Catalina or newer)

### Required Software
- Git version control
- Docker Desktop
- Code editor (VS Code recommended)
- Terminal application (Windows Terminal or macOS Terminal)

---

## 🎓 Prerequisites

Before starting deployment, it's recommended to understand these basic concepts:

### Docker Fundamentals
- **Container**: Lightweight, portable application runtime environment
- **Image**: Container template containing applications and dependencies
- **Docker Compose**: Multi-container application orchestration tool
- **Volume**: Persistent data storage

### Project Architecture
- **Frontend**: React 18 user interface
- **Backend**: Django 4.2 REST API
- **Database**: PostgreSQL 15 database
- **Cache**: Redis 7 caching service
- **Storage**: MinIO S3-compatible object storage

---

## 🪟 Windows Deployment Guide

### Step 1: Prepare Windows Environment

#### 1.1 Enable WSL 2 (Windows Subsystem for Linux)

Open **PowerShell** (as Administrator):

```powershell
# Enable WSL feature
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Enable Virtual Machine Platform
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart computer
Restart-Computer
```

After restart, continue in PowerShell (as Administrator):

```powershell
# Set WSL 2 as default version
wsl --set-default-version 2

# Install Ubuntu (recommended)
wsl --install -d Ubuntu
```

#### 1.2 Install Git

Visit [Git for Windows](https://git-scm.com/download/win) to download and install:

```powershell
# Verify installation
git --version
```

#### 1.3 Install Docker Desktop

1. Visit [Docker Desktop for Windows](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe)
2. Download and run the installer
3. During installation, ensure **"Use WSL 2 instead of Hyper-V"** is selected
4. Restart computer

#### 1.4 Configure Docker Desktop

Launch Docker Desktop and configure:

1. **Resources → Advanced**:
   - Memory: Minimum 4GB (8GB recommended)
   - CPUs: Minimum 2 cores (4 cores recommended)
   - Disk image size: Minimum 64GB

2. **Resources → WSL Integration**:
   - Enable "Enable integration with my default WSL distro"
   - Enable "Enable integration with additional distros" for Ubuntu

3. Click **"Apply & Restart"**

#### 1.5 Verify Docker Installation

In PowerShell or WSL Ubuntu terminal:

```bash
# Check Docker version
docker --version
docker-compose --version

# Test Docker installation
docker run hello-world
```

### Step 2: Clone Project (Windows)

Open **Windows Terminal** or **WSL Ubuntu**:

```bash
# Create project directory
mkdir -p ~/projects
cd ~/projects

# Clone project (replace with actual repository URL)
git clone https://github.com/yourusername/JobQuest_Navigator_CAA.git
cd JobQuest_Navigator_CAA

# Verify project structure
ls -la
```

### Step 3: Windows-Specific Configuration

#### 3.1 Configure File Permissions

```bash
# Set appropriate permissions in WSL
chmod +x infrastructure/docker/scripts/*.sh
```

#### 3.2 Windows Firewall Configuration

If you encounter network issues, you may need to add rules in Windows Defender Firewall:

1. Open **Windows Defender Firewall**
2. Select **"Allow an app or feature through Windows Defender Firewall"**
3. Find and allow **"Docker Desktop"**

---

## 🍎 macOS Deployment Guide

### Step 1: Prepare macOS Environment

#### 1.1 Install Homebrew (Package Manager)

Open **Terminal** application:

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add to PATH (follow the prompts)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# Verify installation
brew --version
```

#### 1.2 Install Git

```bash
# Install Git using Homebrew
brew install git

# Verify installation
git --version
```

#### 1.3 Install Docker Desktop

**Method 1: Manual Download**
1. Visit [Docker Desktop for Mac](https://desktop.docker.com/mac/main/amd64/Docker.dmg)
2. Download DMG file (choose Intel or Apple Silicon version)
3. Open DMG file, drag Docker to Applications folder
4. Launch Docker Desktop from Applications

**Method 2: Using Homebrew**
```bash
# Install using Homebrew Cask
brew install --cask docker

# Launch Docker Desktop
open /Applications/Docker.app
```

#### 1.4 Configure Docker Desktop (macOS)

Launch Docker Desktop and configure:

1. **Preferences → Resources**:
   - Memory: Minimum 4GB (8GB recommended)
   - CPUs: Minimum 2 cores (4 cores recommended)
   - Swap: 1GB
   - Disk image size: Minimum 64GB

2. Click **"Apply & Restart"**

#### 1.5 Verify Docker Installation (macOS)

```bash
# Check Docker version
docker --version
docker-compose --version

# Test Docker installation
docker run hello-world
```

### Step 2: Clone Project (macOS)

```bash
# Create project directory
mkdir -p ~/projects
cd ~/projects

# Clone project (replace with actual repository URL)
git clone https://github.com/yourusername/JobQuest_Navigator_CAA.git
cd JobQuest_Navigator_CAA

# Verify project structure
ls -la
```

### Step 3: macOS-Specific Configuration

#### 3.1 Configure File Permissions

```bash
# Set script execution permissions
chmod +x infrastructure/docker/scripts/*.sh
```

#### 3.2 M1/M2 Mac Compatibility

If using Apple Silicon Mac:

```bash
# Set environment variable for x86 container support (if needed)
export DOCKER_DEFAULT_PLATFORM=linux/amd64
```

---

## 🚀 Universal Deployment Steps

The following steps apply to both Windows and macOS platforms:

### Step 4: Environment Configuration

#### 4.1 Navigate to Docker Directory

```bash
cd infrastructure/docker
```

#### 4.2 Check Script Permissions (if not previously set)

```bash
# Linux/macOS/WSL
chmod +x scripts/*.sh

# Windows (if directly in PowerShell)
# Scripts include .bat versions, or use WSL
```

### Step 5: Start Environment

#### 5.1 Choose Deployment Mode

**Development Mode (recommended for new users)**:
```bash
./scripts/start-local-env.sh --dev
```

**Development Mode + Storage Services**:
```bash
./scripts/start-local-env.sh --dev --with-storage
```

**Full Mode (includes all services)**:
```bash
./scripts/start-local-env.sh --full
```

#### 5.2 First Startup Process

The script will execute the following steps:
1. ✅ Check Docker running status
2. ✅ Create necessary directories
3. ✅ Generate environment configuration file (.env)
4. ✅ Build Docker images (first run takes 10-15 minutes)
5. ✅ Start all services
6. ✅ Health checks

#### 5.3 Interactive Initialization

After startup completion, the system will prompt for initialization:

```
Do you want to run database migrations now? (y/N): y
```
Type `y` and press Enter

```
Do you want to create a superuser account? (y/N): y
```
Type `y` and press Enter, then follow prompts to create admin account:
```
Username: admin
Email address: admin@example.com
Password: (enter password, won't be displayed)
Password (again): (enter password again)
```

If storage services are enabled:
```
Do you want to setup MinIO test data? (y/N): y
```
Type `y` to setup test data

### Step 6: Verify Service Status

```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs -f backend
```

---

## ✅ Deployment Verification

### 6.1 Check Core Services

Open your browser and visit the following URLs to verify service status:

| Service | URL | Expected Result |
|---------|-----|----------------|
| 🌐 Frontend App | http://localhost:3000 | JobQuest Navigator login page |
| 🔗 Backend API | http://localhost:8000 | API root directory response |
| 🔧 Django Admin | http://localhost:8000/admin/ | Django admin login page |
| 📊 API Documentation | http://localhost:8000/api/docs/ | API documentation page |

### 6.2 Check Optional Services (if enabled)

| Service | URL | Credentials |
|---------|-----|------------|
| 📧 MailHog | http://localhost:8025 | No credentials needed |
| 🗃️ MinIO | http://localhost:9001 | minioadmin / minioadmin123 |
| ☁️ LocalStack | http://localhost:4566 | test / test |
| 📈 Prometheus | http://localhost:9090 | No credentials needed |
| 📊 Grafana | http://localhost:3003 | admin / admin123 |

### 6.3 Functional Testing

#### Test User Registration and Login:
1. Visit http://localhost:3000
2. Click "Register" to create new account
3. Login with new account
4. Confirm you can access the dashboard

#### Test Backend API:
```bash
# Test health check endpoint
curl http://localhost:8000/api/health/

# Test user authentication (using created admin account)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'
```

---

## 🔧 Troubleshooting

### Docker-Related Issues

#### Issue 1: "Docker is not running"
**Solution**:
```bash
# Windows
# Launch Docker Desktop from Start menu

# macOS
open /Applications/Docker.app

# Verify Docker status
docker info
```

#### Issue 2: Port Already in Use
**Error Message**: `Port 3000 is already in use`

**Solution**:
```bash
# Find process using port
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :3000
kill -9 <PID>

# Or modify ports
docker-compose down
# Edit docker-compose.yml to change port mappings
```

#### Issue 3: Insufficient Memory
**Error Message**: `Container killed due to insufficient memory`

**Solution**:
1. Increase memory allocation in Docker Desktop settings (recommend 8GB)
2. Close other unnecessary applications
3. Use minimal mode:
```bash
./scripts/start-local-env.sh --minimal
```

### Network Connection Issues

#### Issue 4: Inter-container Network Connection Failed
**Solution**:
```bash
# Rebuild network
docker-compose down
docker network prune
docker-compose up -d

# Check network
docker network ls
docker network inspect docker_jobquest-network
```

#### Issue 5: API Inaccessible
**Solution**:
```bash
# Check backend container status
docker-compose logs backend

# Check health status
docker-compose ps backend

# Restart backend service
docker-compose restart backend
```

### Database Issues

#### Issue 6: Database Connection Failed
**Solution**:
```bash
# Check database container
docker-compose logs database

# Check database health
docker-compose exec database pg_isready -U jobquest_user

# Reset database
./scripts/manage.sh db-reset
```

#### Issue 7: Migration Failed
**Solution**:
```bash
# Manually run migrations
./scripts/manage.sh migrate

# Check migration status
./scripts/manage.sh showmigrations

# If severely corrupted, reset database
./scripts/manage.sh db-reset
```

### Build Issues

#### Issue 8: Docker Image Build Failed
**Solution**:
```bash
# Clean Docker cache
docker system prune -a

# Rebuild images
docker-compose build --no-cache

# Pull latest base images
docker-compose pull
```

#### Issue 9: Dependency Installation Failed
**Solution**:
```bash
# Check network connectivity
ping pypi.org
ping registry.npmjs.org

# Use domestic mirrors (for users in China)
# Edit Dockerfile to add mirror configuration
```

### Permission Issues

#### Issue 10: File Permission Errors (Linux/macOS)
**Solution**:
```bash
# Fix script permissions
chmod +x infrastructure/docker/scripts/*.sh

# Fix data directory permissions
sudo chown -R $USER:$USER backend/media
sudo chown -R $USER:$USER backend/staticfiles
```

### Performance Issues

#### Issue 11: Slow Startup
**Solution**:
1. **Increase Docker resource allocation**
2. **Use SSD hard drive**
3. **Close unnecessary services**:
```bash
# Use minimal mode
./scripts/start-local-env.sh --minimal
```

#### Issue 12: Slow Container Performance
**Solution**:
```bash
# Check resource usage
docker stats

# Optimize Docker settings
# Increase CPU and memory allocation in Docker Desktop
```

### Logging and Debugging

#### View detailed logs:
```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f database

# Enter container for debugging
docker-compose exec backend bash
docker-compose exec frontend sh
```

#### Debug network issues:
```bash
# Check container networks
docker network ls
docker network inspect docker_jobquest-network

# Test inter-container connectivity
docker-compose exec backend ping database
docker-compose exec frontend ping backend
```

---

## 💻 Development Workflow

### Daily Development Operations

#### Start development environment:
```bash
cd infrastructure/docker
./scripts/start-local-env.sh --dev
```

#### View logs:
```bash
# Real-time backend logs
./scripts/manage.sh logs

# View all service logs
docker-compose logs -f
```

#### Django management:
```bash
# Create new migrations
./scripts/manage.sh makemigrations

# Apply migrations
./scripts/manage.sh migrate

# Enter Django shell
./scripts/manage.sh shell

# Run tests
./scripts/manage.sh test
```

#### Stop environment:
```bash
# Soft stop (preserve data)
./scripts/stop-local-env.sh --soft

# Clean stop (delete data)
./scripts/stop-local-env.sh --clean

# Complete reset
./scripts/stop-local-env.sh --reset
```

### Code Changes and Hot Reload

- **Backend**: Django code changes automatically reload
- **Frontend**: React code changes automatically recompile and refresh
- **Database models**: Require manual migration execution
- **Configuration changes**: Require restarting relevant containers

### Adding New Dependencies

#### Python dependencies:
```bash
# Enter backend container
./scripts/manage.sh bash

# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt

# Exit and rebuild image
exit
docker-compose build backend
```

#### Node.js dependencies:
```bash
# Enter frontend container
docker-compose exec frontend sh

# Install new package
npm install package-name

# package.json is automatically updated
```

---

## 🎯 Next Steps

After successful deployment, you can:

1. **Explore application features**: Browse the frontend interface, test various functionalities
2. **Review code structure**: Familiarize yourself with Django and React code organization
3. **Run tests**: Execute existing unit tests and integration tests
4. **Start development**: Add new features based on project requirements
5. **Read documentation**: Review [CLAUDE.md](./CLAUDE.md) for more development guidance

### Useful Resources

- 📚 [Project Documentation](./docs/)
- 🐛 [Troubleshooting Guide](./docs/TROUBLESHOOTING_GUIDE.md)
- 🔧 [Docker Setup Guide](./docs/DOCKER_MINIO_SETUP.md)
- 🚀 [Deployment Guide](./docs/DEPLOYMENT_GUIDE.md)

### Getting Help

If you encounter issues:
1. Check the troubleshooting section in this document
2. Review project issues
3. Consult official documentation for Docker and related technologies
4. Contact project maintainers

---

**Happy developing!** 🚀

> This deployment guide covers the entire process from zero to fully running. If you're a beginner, it's recommended to start with development mode and explore other features after becoming familiar with the environment.