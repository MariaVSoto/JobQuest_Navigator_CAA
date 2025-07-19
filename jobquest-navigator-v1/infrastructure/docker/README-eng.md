# JobQuest Navigator - Docker Local Development Environment

This directory contains all configuration files and scripts to create a complete local development environment for JobQuest Navigator using Docker.

## 🚀 Quick Start

### Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose)
- At least 4GB available memory
- At least 10GB available disk space

### One-Click Startup

```bash
# Enter the docker directory
cd infrastructure/docker

# Start development environment
./scripts/start-local-env.sh --dev

# Or start a production-like environment
./scripts/start-local-env.sh --prod
```

## 📁 File Structure

```
infrastructure/docker/
├── Dockerfile.backend          # Django backend production image
├── Dockerfile.backend.dev      # Django backend development image  
├── Dockerfile.frontend         # React frontend production image
├── Dockerfile.frontend.dev     # React frontend development image
├── Dockerfile.devtools         # Dev tools container image
├── docker-compose.yml          # Main Docker Compose configuration
├── docker-compose.dev.yml      # Development environment override config
├── nginx.conf                  # Nginx config (frontend)
├── nginx-proxy.conf            # Nginx proxy config
├── init-db.sql                 # Database initialization script
├── init-dev-db.sql             # Development database initialization script
├── scripts/
│   ├── start-local-env.sh      # Startup script
│   ├── stop-local-env.sh       # Stop script
│   └── manage.sh               # Django management script
└── README.md                   # This document
```

## 🛠️ Available Startup Modes

### Development Mode (Recommended)
```bash
./scripts/start-local-env.sh --dev
```
- Hot reload support
- Dev tools container
- Source code mounting
- Detailed log output

### Production Mode
```bash
./scripts/start-local-env.sh --prod
```
- Build optimized images
- Nginx proxy
- Production-level configuration

### Full Mode
```bash
./scripts/start-local-env.sh --full
```
- Includes all optional services
- Monitoring tools (Prometheus + Grafana)
- Email testing (MailHog)
- Object storage (MinIO)
- Search engine (Elasticsearch)

### Storage Modes
```bash
# Start with MinIO S3-compatible storage
./scripts/start-local-env.sh --dev --with-storage

# Start with LocalStack AWS services emulation
./scripts/start-local-env.sh --dev --with-localstack
```

### Minimal Mode
```bash
./scripts/start-local-env.sh --minimal
```
- Core services only
- Database, backend, frontend

## 🌐 Service Access Addresses

| Service         | Address                      | Description                |
|-----------------|-----------------------------|----------------------------|
| Frontend App    | http://localhost (Docker) or http://localhost:3000 (Dev) | React application with real-time job data |
| Backend API     | http://localhost:8000        | Django REST API            |
| Django Admin    | http://localhost:8000/admin/ | Django admin interface     |
| API Docs        | http://localhost:8000/api/docs/ | API documentation      |
| Database        | localhost:5432               | PostgreSQL database        |
| Redis           | localhost:6379               | Redis cache                |

### Optional Service Addresses

| Service        | Address                      | Description                        |
|----------------|-----------------------------|------------------------------------|
| MailHog        | http://localhost:8025        | Email testing tool                 |
| MinIO          | http://localhost:9001        | S3-compatible object storage (minioadmin/minioadmin123) |
| LocalStack     | http://localhost:4566        | AWS services emulation             |
| Elasticsearch  | http://localhost:9200        | Search engine                      |
| Prometheus     | http://localhost:9090        | Monitoring metrics                 |
| Grafana        | http://localhost:3001        | Monitoring dashboard (admin/admin123) |
| Nginx Proxy    | http://localhost:8080        | Nginx reverse proxy                |

### Current Demo Configuration
- ✅ **Real-time Job Data**: Adzuna API integration for Los Angeles programmer jobs
- ✅ **Google Maps**: Interactive job location mapping
- ✅ **Fallback System**: All modules work with comprehensive mock data
- ✅ **Authentication**: JWT-based with demo access support
- ✅ **API Architecture**: REST API (migrated from GraphQL)

## 🔧 Management Commands

### Using the Management Script

```bash
# Django migrations
./scripts/manage.sh migrate

# Create superuser
./scripts/manage.sh createsuperuser

# Run tests
./scripts/manage.sh test

# View logs
./scripts/manage.sh logs

# Enter backend container shell
./scripts/manage.sh bash

# Install Python package
./scripts/manage.sh pip install package-name
```

### Using Docker Compose Directly

```bash
# View service status
docker-compose ps

# View logs
docker-compose logs -f backend

# Run Django command
docker-compose exec backend python manage.py migrate

# Enter container shell
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec database psql -U jobquest_user jobquest_navigator
```

## 🛑 Stop and Clean Up

### Soft Stop (keep data)
```bash
./scripts/stop-local-env.sh --soft
```

### Clean Stop (delete data volumes)
```bash
./scripts/stop-local-env.sh --clean
```

### Full Reset (delete all images)
```bash
./scripts/stop-local-env.sh --reset
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Conflict**
   ```bash
   # Check port usage
   lsof -i :3000
   lsof -i :8000
   lsof -i :5432
   ```

2. **Container Startup Failure**
   ```bash
   # View detailed logs
   docker-compose logs [service_name]
   
   # Rebuild image
   docker-compose build --no-cache [service_name]
   ```

3. **Database Connection Issues**
   ```bash
   # Check database container status
   docker-compose exec database pg_isready -U jobquest_user
   
   # Restart database
   docker-compose restart database
   ```

4. **Permission Issues**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER ../../backend/media
   sudo chown -R $USER:$USER ../../backend/staticfiles
   ```

### Reset Development Environment

```bash
# Full clean
./scripts/stop-local-env.sh --reset

# Restart
./scripts/start-local-env.sh --dev

# Run migrations
./scripts/manage.sh migrate

# Create superuser
./scripts/manage.sh createsuperuser
```

## 📊 Monitoring and Debugging

### View Resource Usage
```bash
# View container resource usage
docker stats

# View disk usage
docker system df
```

### Performance Analysis
```bash
# Enable monitoring mode
./scripts/start-local-env.sh --full

# Access Grafana dashboard
open http://localhost:3001
```

### Log Analysis
```bash
# View all logs in real time
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f database
```

## 🔐 Security Configuration

### Default Credentials for Development Environment

| Service     | Username      | Password        |
|-------------|--------------|----------------|
| PostgreSQL  | jobquest_user | jobquest_password |
| MinIO       | minioadmin    | minioadmin123  |
| Grafana     | admin         | admin123       |

⚠️ **Warning**: These are default credentials for development only and should never be used in production!

## 🚀 Deploy to Test Environment

After development, you can deploy to the AWS test environment with the following commands:

```bash
# Deploy using GitHub Actions
gh workflow run "Deploy to Test Environment" \
  --ref develop \
  --field force_deploy=false

# Or deploy manually
cd ../..
./scripts/deploy-infrastructure.sh
./scripts/deploy-backend.sh
./scripts/deploy-frontend.sh
```

## 📝 Development Tips

1. **Hot Reload**: Both backend and frontend support hot reload in development mode
2. **Data Persistence**: Database and Redis data persist after container restart
3. **Static Files**: Django static files are automatically collected to shared volume
4. **Email Testing**: Use MailHog to capture all sent emails
5. **Log Viewing**: Easily view logs and execute commands with management scripts

## 🤝 Contributing

If you find any issues or have suggestions for improvement, please:

1. Check existing issues
2. Create a new issue describing the problem
3. Submit a Pull Request with detailed explanation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details 