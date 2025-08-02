# JobQuest Navigator v2 - Installation Guide

## 📋 Prerequisites

Before installing JobQuest Navigator v2, ensure you have the following:

### System Requirements
- **Operating System**: macOS, Windows 10+, or Linux
- **Node.js**: Version 18.0 or higher
- **Python**: Version 3.9 or higher
- **Database**: PostgreSQL 13+ (for production) or SQLite (for development)
- **Docker**: Latest version (for containerized development)
- **Git**: Latest version for version control

### API Keys (Optional - for full functionality)
- **Adzuna API Key**: For real-time job data
- **Google Maps API Key**: For job location mapping
- **OpenAI API Key**: For AI suggestions and company research

## 🚀 Installation Methods

Choose one of the following installation methods:

### Method 1: Docker Development Environment (Recommended)

This method provides a complete containerized environment with all services.

#### Step 1: Clone the Repository
```bash
git clone https://github.com/your-org/jobquest-navigator-v2.git
cd jobquest-navigator-v2
```

#### Step 2: Configure Environment Variables
```bash
# Copy environment template
cp configs/environment.env.template configs/environment.env

# Edit the file with your API keys (optional)
nano configs/environment.env
```

#### Step 3: Start Development Environment
```bash
cd infrastructure/docker/
./scripts/start-local-env.sh --dev
```

#### Step 4: Setup Database and Test Data
```bash
# Run database migrations
./scripts/manage.sh migrate

# Create superuser (optional)
./scripts/manage.sh createsuperuser

# Load test data (optional)
./scripts/manage.sh loaddata fixtures/test_data.json
```

#### Step 5: Access the Application
- **Frontend**: http://localhost:3002
- **Backend API**: http://localhost:8000
- **GraphQL Playground**: http://localhost:8000/graphql/
- **Django Admin**: http://localhost:8000/admin/

### Method 2: Traditional Development Setup

For developers who prefer running services individually.

#### Backend Setup (FastAPI + GraphQL)

1. **Navigate to Backend Directory**
   ```bash
   cd backend-fastapi-graphql/
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.template .env
   # Edit .env with your database settings and API keys
   ```

5. **Setup Database**
   ```bash
   # For SQLite (development)
   python manage.py makemigrations
   python manage.py migrate
   
   # For PostgreSQL (recommended)
   createdb jobquest_navigator
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Backend Server**
   ```bash
   python manage.py runserver 8000
   ```

#### Frontend Setup (React)

1. **Navigate to Frontend Directory**
   ```bash
   cd frontend-react-minimal/
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Configure Environment**
   ```bash
   cp .env.template .env
   # Edit .env with your API endpoints and keys
   ```

4. **Start Frontend Server**
   ```bash
   npm start
   ```

5. **Access Application**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

## 🔧 Configuration

### Environment Variables

#### Backend Configuration (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/jobquest_navigator
# Or for SQLite: sqlite:///db.sqlite3

# Security
SECRET_KEY=your-secret-key-here
DEBUG=True
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3002

# External APIs (Optional)
ADZUNA_API_ID=your-adzuna-api-id
ADZUNA_API_KEY=your-adzuna-api-key
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
OPENAI_API_KEY=your-openai-api-key

# Email (Optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

#### Frontend Configuration (.env)
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_GRAPHQL_URL=http://localhost:8000/graphql/
REACT_APP_GOOGLE_MAPS_API_KEY=your-google-maps-api-key

# Development settings
REACT_APP_DEV_AUTH_BYPASS=false
GENERATE_SOURCEMAP=true
```

### Docker Configuration

#### Development with Storage Services
```bash
# Start with MinIO (S3-compatible storage)
./scripts/start-local-env.sh --dev --with-storage

# Start with LocalStack (AWS services emulation)
./scripts/start-local-env.sh --dev --with-localstack

# Start full environment (all services)
./scripts/start-local-env.sh --full
```

#### Service URLs (Docker Environment)
- **Frontend**: http://localhost:3002
- **Backend**: http://localhost:8000
- **Database**: localhost:5432
- **Redis**: localhost:6379
- **MinIO Web UI**: http://localhost:9001
- **LocalStack**: http://localhost:4566
- **MailHog**: http://localhost:8025

## 🧪 Testing

### Run Tests

#### Backend Tests
```bash
# Traditional setup
cd backend-fastapi-graphql/
python manage.py test

# Docker environment
./scripts/manage.sh test
```

#### Frontend Tests
```bash
# Traditional setup
cd frontend-react-minimal/
npm test

# Docker environment
docker-compose exec frontend npm test
```

### Test Coverage
```bash
# Backend coverage
cd backend-fastapi-graphql/
coverage run --source='.' manage.py test
coverage report
coverage html

# Frontend coverage
cd frontend-react-minimal/
npm test -- --coverage --watchAll=false
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
lsof -i :8000
lsof -i :3000

# Kill the process
kill -9 <PID>
```

#### 2. Database Connection Issues
```bash
# Check PostgreSQL status
brew services list | grep postgresql  # macOS
sudo systemctl status postgresql      # Linux

# Reset database
dropdb jobquest_navigator
createdb jobquest_navigator
python manage.py migrate
```

#### 3. Node Modules Issues
```bash
# Clear npm cache and reinstall
cd frontend-react-minimal/
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### 4. Docker Issues
```bash
# Clean Docker environment
./scripts/stop-local-env.sh --clean

# Rebuild containers
docker-compose build --no-cache

# Check logs
docker-compose logs backend
docker-compose logs frontend
```

#### 5. Browser Extension Conflicts
If you encounter runtime errors like "Cannot read properties of null", this is likely due to browser extensions:

**Solutions:**
- Use incognito/private browsing mode
- Disable browser extensions temporarily
- The application includes error protection for extension conflicts

### Error Logs

#### Backend Logs
```bash
# Traditional setup
tail -f backend-fastapi-graphql/logs/django.log

# Docker environment
docker-compose logs -f backend
```

#### Frontend Logs
```bash
# Check browser console for frontend errors
# Press F12 → Console tab

# Docker environment
docker-compose logs -f frontend
```

## 📚 Development Workflow

### 1. Daily Development
```bash
# Start environment
./scripts/start-local-env.sh --dev

# Make changes to code
# Frontend hot-reloads automatically
# Backend requires restart for some changes

# Run tests
./scripts/manage.sh test
docker-compose exec frontend npm test

# Stop environment
./scripts/stop-local-env.sh
```

### 2. Database Changes
```bash
# Create migrations
./scripts/manage.sh makemigrations

# Apply migrations
./scripts/manage.sh migrate

# Reset database (if needed)
./scripts/manage.sh flush
```

### 3. Adding New Dependencies

#### Backend
```bash
# Add to requirements.txt
pip install new-package
pip freeze > requirements.txt

# Rebuild Docker image
docker-compose build backend
```

#### Frontend
```bash
# Add package
cd frontend-react-minimal/
npm install new-package

# Rebuild Docker image
docker-compose build frontend
```

## 🚀 Production Deployment

### AWS Deployment

1. **Setup AWS Infrastructure**
   ```bash
   cd infrastructure/terraform/
   terraform init
   terraform plan
   terraform apply
   ```

2. **Deploy Backend**
   ```bash
   cd backend-fastapi-graphql/
   zappa deploy production
   ```

3. **Deploy Frontend**
   ```bash
   cd frontend-react-minimal/
   npm run build
   aws s3 sync build/ s3://your-frontend-bucket/
   ```

### Environment-Specific Configurations

#### Production Environment Variables
```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:pass@rds-endpoint/dbname
CORS_ALLOWED_ORIGINS=https://your-domain.com
```

## 📞 Support

### Getting Help

1. **Check this documentation first**
2. **Review error logs** (see troubleshooting section)
3. **Check GitHub issues**: [Project Issues](https://github.com/your-org/jobquest-navigator-v2/issues)
4. **Contact the development team**

### Development Commands Reference

#### Docker Commands
```bash
# Start development environment
./scripts/start-local-env.sh --dev

# Start with storage services
./scripts/start-local-env.sh --dev --with-storage

# Stop and clean
./scripts/stop-local-env.sh --clean

# Run Django commands
./scripts/manage.sh <command>

# View logs
docker-compose logs -f <service-name>
```

#### Traditional Commands
```bash
# Backend
cd backend-fastapi-graphql/
python manage.py runserver
python manage.py migrate
python manage.py test
python manage.py createsuperuser

# Frontend
cd frontend-react-minimal/
npm start
npm test
npm run build
```

## ✅ Verification

After installation, verify everything is working:

1. **Access Frontend**: http://localhost:3002 (Docker) or http://localhost:3000 (Traditional)
2. **Test Login**: Use the signup form to create an account
3. **Check Backend**: Visit http://localhost:8000/admin/ and login
4. **Test GraphQL**: Visit http://localhost:8000/graphql/ and run a test query
5. **Verify Features**: Navigate through all main sections (Resume, Jobs, Skills, Company Research)

## 🎉 You're Ready!

Your JobQuest Navigator v2 installation is complete! You can now:

- Create and manage resumes
- Search and apply for jobs
- Track your applications
- Get AI-powered suggestions
- Research companies
- Develop your skills

Happy job hunting! 🚀