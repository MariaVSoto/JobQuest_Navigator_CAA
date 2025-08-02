# Configuration

This directory contains all environment configurations and secret management for JobQuest Navigator v3.

## Structure

```
config/
├── environments/        # Environment-specific configurations
└── secrets/             # Secret management templates
```

## Components

### Environment Configurations (`environments/`)
- **Development**: Local development settings
- **Staging**: Pre-production environment settings  
- **Production**: Production environment settings
- **Purpose**: Environment-specific variable management

### Secret Management (`secrets/`)
- **Templates**: Secret configuration templates
- **Security**: Secure credential management patterns
- **Integration**: AWS Secrets Manager integration
- **Purpose**: Secure secret handling procedures

## Environment Files

### Development Environment
- **File**: `environments/development.env`
- **Scope**: Local development with Docker
- **Database**: Local PostgreSQL instance
- **Cache**: Local Redis instance

### Staging Environment  
- **File**: `environments/staging.env`
- **Scope**: Pre-production testing
- **Database**: AWS RDS staging instance
- **Cache**: AWS ElastiCache staging

### Production Environment
- **File**: `environments/production.env`
- **Scope**: Production deployment
- **Database**: AWS RDS production instance
- **Security**: Enhanced security configurations

## Usage

### Local Development
```bash
# Environment variables are automatically loaded by Docker
cd ../../infrastructure/docker
./scripts/start-dev.sh start
```

### Staging/Production
```bash
# Copy environment template
cp environments/production.env.template environments/production.env

# Edit with actual values
nano environments/production.env

# Deploy with Terraform
cd ../infrastructure/terraform
terraform apply -var-file=../../config/environments/production.tfvars
```

## Security Guidelines

1. **Never commit actual secrets to version control**
2. **Use environment variable injection for sensitive data**
3. **Reference AWS Secrets Manager for production secrets**
4. **Rotate credentials regularly**
5. **Use least privilege access principles**

## Environment Variables

Common variables across environments:
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Cache connection string  
- `SECRET_KEY`: Application secret key
- `AWS_REGION`: AWS region for services
- `COGNITO_USER_POOL_ID`: Authentication pool ID