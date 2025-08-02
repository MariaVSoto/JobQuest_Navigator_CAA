# Infrastructure

This directory contains all deployment and infrastructure configurations for JobQuest Navigator v3.

## Structure

```
infrastructure/
├── docker/              # Docker compose and configurations
├── terraform/           # AWS infrastructure as code
├── k8s/                 # Kubernetes manifests (future)
└── scripts/             # Deployment automation scripts
```

## Components

### Docker (`docker/`)
- **Purpose**: Local development environment
- **Services**: PostgreSQL, Redis, Backend, Frontend, MinIO
- **Management**: Start/stop scripts and health monitoring

### Terraform (`terraform/`)
- **Purpose**: AWS infrastructure as code
- **Resources**: ECS, RDS, ElastiCache, VPC, Security Groups
- **Environments**: Development, staging, production configurations

### Scripts (`scripts/`)
- **Purpose**: Deployment automation
- **Features**: Setup, deployment, verification scripts
- **AWS Integration**: Cognito setup and validation

### Kubernetes (`k8s/`)
- **Purpose**: Future Kubernetes deployment
- **Status**: Prepared directory structure
- **Scope**: Container orchestration manifests

## Usage

### Local Development
```bash
cd docker/
./scripts/start-dev.sh start
```

### AWS Deployment
```bash
cd terraform/
terraform init
terraform plan -var-file=environments/development.tfvars
terraform apply
```

### Script Execution
```bash
cd scripts/
./deploy.sh
./verify-deployment.sh
```

See individual component READMEs for detailed instructions.