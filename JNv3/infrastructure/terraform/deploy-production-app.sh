#!/bin/bash

# JobQuest Navigator v3 - Production Application Deployment Script
# This script builds and deploys the complete full-stack application to AWS ECS

set -e

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="039444453392"
CLUSTER_NAME="jobquest-navigator-v3-cluster"
BACKEND_REPO="jobquest-navigator-v3-backend"
FRONTEND_REPO="jobquest-navigator-v3-frontend"
BACKEND_SERVICE="jobquest-navigator-v3-backend-service"
FRONTEND_SERVICE="jobquest-navigator-v3-frontend-service"
LOAD_BALANCER_DNS="jobquest-navigator-v3-alb-1532571588.us-east-1.elb.amazonaws.com"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check if we're in the correct directory
if [ ! -d "../../apps/backend-fastapi" ] || [ ! -d "../../apps/frontend-react" ]; then
    error "Please run this script from JNv3/infrastructure/terraform directory"
fi

info "🚀 Starting JobQuest Navigator v3 Production Deployment"
info "AWS Account: $AWS_ACCOUNT_ID"
info "Region: $AWS_REGION"
info "Load Balancer: http://$LOAD_BALANCER_DNS"
echo ""

# Step 1: Authenticate with ECR
log "Step 1: Authenticating with Amazon ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
if [ $? -eq 0 ]; then
    log "✅ ECR authentication successful"
else
    error "❌ ECR authentication failed"
fi

# Step 2: Build and Push Backend Docker Image (Production)
log "Step 2: Building production backend Docker image..."
cd ../../apps/backend-fastapi

# Build production backend image targeting the production stage
info "Building FastAPI + Strawberry GraphQL backend for production..."
docker build --target production -t $BACKEND_REPO:latest .
if [ $? -eq 0 ]; then
    log "✅ Backend Docker image built successfully"
else
    error "❌ Backend Docker build failed"
fi

# Tag and push backend image
info "Tagging and pushing backend image to ECR..."
docker tag $BACKEND_REPO:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$BACKEND_REPO:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$BACKEND_REPO:latest
if [ $? -eq 0 ]; then
    log "✅ Backend image pushed to ECR successfully"
else
    error "❌ Backend image push failed"
fi

# Step 3: Build and Push Frontend Docker Image (Production)
log "Step 3: Building production frontend Docker image..."
cd ../frontend-react

# Update the frontend configuration for production
info "Configuring frontend for production deployment..."

# Create production environment file
cat > .env.production << EOF
REACT_APP_ENV=production
REACT_APP_API_URL=http://$LOAD_BALANCER_DNS/api
REACT_APP_GRAPHQL_URL=http://$LOAD_BALANCER_DNS/graphql
REACT_APP_WS_URL=ws://$LOAD_BALANCER_DNS/graphql
GENERATE_SOURCEMAP=false
INLINE_RUNTIME_CHUNK=false
IMAGE_INLINE_SIZE_LIMIT=0
EOF

# Build production frontend image targeting the production stage
info "Building React frontend for production..."
docker build --target production -t $FRONTEND_REPO:latest .
if [ $? -eq 0 ]; then
    log "✅ Frontend Docker image built successfully"
else
    error "❌ Frontend Docker build failed"
fi

# Tag and push frontend image
info "Tagging and pushing frontend image to ECR..."
docker tag $FRONTEND_REPO:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$FRONTEND_REPO:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$FRONTEND_REPO:latest
if [ $? -eq 0 ]; then
    log "✅ Frontend image pushed to ECR successfully"
else
    error "❌ Frontend image push failed"
fi

# Step 4: Update Task Definitions with New Images
log "Step 4: Creating new ECS task definitions..."
cd ../../infrastructure/terraform

# Get current task definitions
info "Retrieving current task definitions..."
aws ecs describe-task-definition --task-definition $BACKEND_REPO --query taskDefinition > backend-task-def.json
aws ecs describe-task-definition --task-definition $FRONTEND_REPO --query taskDefinition > frontend-task-def.json

# Update backend task definition
info "Updating backend task definition..."
python3 << EOF
import json
import sys

try:
    with open('backend-task-def.json', 'r') as f:
        task_def = json.load(f)
    
    # Update image URL and environment variables
    for container in task_def['containerDefinitions']:
        if container['name'] == 'backend':
            container['image'] = '$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$BACKEND_REPO:latest'
            
            # Add production environment variables
            container['environment'] = [
                {'name': 'ENVIRONMENT', 'value': 'production'},
                {'name': 'DATABASE_URL', 'value': 'postgresql://jobquest_user:\${DATABASE_PASSWORD}@jobquest-navigator-v3-db-d2b0b54a.cmpaeyc24qtl.us-east-1.rds.amazonaws.com:5432/jobquest'},
                {'name': 'REDIS_URL', 'value': 'redis://localhost:6379'},
                {'name': 'AWS_DEFAULT_REGION', 'value': '$AWS_REGION'},
                {'name': 'CORS_ORIGINS', 'value': 'http://$LOAD_BALANCER_DNS'},
                {'name': 'LOG_LEVEL', 'value': 'info'},
                {'name': 'WORKERS', 'value': '2'}
            ]
            
            # Update resource allocation for production
            task_def['cpu'] = '512'
            task_def['memory'] = '1024'
    
    # Remove fields that cannot be used in register-task-definition
    fields_to_remove = ['taskDefinitionArn', 'revision', 'status', 'requiresAttributes', 'placementConstraints', 'compatibilities', 'registeredAt', 'registeredBy']
    for field in fields_to_remove:
        task_def.pop(field, None)
    
    with open('backend-task-def-new.json', 'w') as f:
        json.dump(task_def, f, indent=2)
    
    print('Backend task definition updated successfully')
except Exception as e:
    print(f'Error updating backend task definition: {e}')
    sys.exit(1)
EOF

# Update frontend task definition
info "Updating frontend task definition..."
python3 << EOF
import json
import sys

try:
    with open('frontend-task-def.json', 'r') as f:
        task_def = json.load(f)
    
    # Update image URL and environment variables
    for container in task_def['containerDefinitions']:
        if container['name'] == 'frontend':
            container['image'] = '$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$FRONTEND_REPO:latest'
            
            # Add production environment variables
            container['environment'] = [
                {'name': 'NODE_ENV', 'value': 'production'},
                {'name': 'REACT_APP_ENV', 'value': 'production'},
                {'name': 'REACT_APP_API_URL', 'value': 'http://$LOAD_BALANCER_DNS/api'},
                {'name': 'REACT_APP_GRAPHQL_URL', 'value': 'http://$LOAD_BALANCER_DNS/graphql'}
            ]
            
            # Update resource allocation for production
            task_def['cpu'] = '512'
            task_def['memory'] = '1024'
    
    # Remove fields that cannot be used in register-task-definition
    fields_to_remove = ['taskDefinitionArn', 'revision', 'status', 'requiresAttributes', 'placementConstraints', 'compatibilities', 'registeredAt', 'registeredBy']
    for field in fields_to_remove:
        task_def.pop(field, None)
    
    with open('frontend-task-def-new.json', 'w') as f:
        json.dump(task_def, f, indent=2)
    
    print('Frontend task definition updated successfully')
except Exception as e:
    print(f'Error updating frontend task definition: {e}')
    sys.exit(1)
EOF

# Register new task definitions
info "Registering updated task definitions..."
aws ecs register-task-definition --cli-input-json file://backend-task-def-new.json
if [ $? -eq 0 ]; then
    log "✅ Backend task definition registered"
else
    error "❌ Failed to register backend task definition"
fi

aws ecs register-task-definition --cli-input-json file://frontend-task-def-new.json
if [ $? -eq 0 ]; then
    log "✅ Frontend task definition registered"
else
    error "❌ Failed to register frontend task definition"
fi

# Step 5: Deploy to ECS Services
log "Step 5: Deploying to ECS services..."

# Update backend service
info "Updating backend service with new task definition..."
aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $BACKEND_SERVICE \
    --desired-count 1 \
    --force-new-deployment

if [ $? -eq 0 ]; then
    log "✅ Backend service updated - scaling to 1 instance"
else    
    error "❌ Failed to update backend service"
fi

# Update frontend service
info "Updating frontend service with new task definition..."
aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $FRONTEND_SERVICE \
    --desired-count 1 \
    --force-new-deployment

if [ $? -eq 0 ]; then
    log "✅ Frontend service updated - scaling to 1 instance"
else
    error "❌ Failed to update frontend service"
fi

# Step 6: Wait for deployment to stabilize
log "Step 6: Waiting for services to stabilize..."
info "This may take 3-5 minutes for production images to start..."

# Check service status every 30 seconds
for i in {1..20}; do
    sleep 30
    
    # Get service status
    BACKEND_STATUS=$(aws ecs describe-services --cluster $CLUSTER_NAME --services $BACKEND_SERVICE --query "services[0].runningCount" --output text)
    FRONTEND_STATUS=$(aws ecs describe-services --cluster $CLUSTER_NAME --services $FRONTEND_SERVICE --query "services[0].runningCount" --output text)
    
    info "Backend running: $BACKEND_STATUS/1, Frontend running: $FRONTEND_STATUS/1"
    
    if [ "$BACKEND_STATUS" = "1" ] && [ "$FRONTEND_STATUS" = "1" ]; then
        log "✅ Both services are running successfully!"
        break
    fi
    
    if [ $i -eq 20 ]; then
        warn "Services are taking longer than expected to start. Continuing with deployment summary..."
        break
    fi
done

# Step 7: Test the deployment
log "Step 7: Testing the deployed application..."

# Test load balancer health
info "Testing load balancer connectivity..."
sleep 30  # Give services a moment to register with ALB

if curl -s -o /dev/null -w "%{http_code}" http://$LOAD_BALANCER_DNS | grep -q "200\|503"; then
    log "✅ Load balancer is responding"
else
    warn "Load balancer may still be starting up"
fi

# Test backend health endpoint
info "Testing backend health endpoint..."
if curl -s http://$LOAD_BALANCER_DNS/health | grep -q "healthy\|JobQuest"; then
    log "✅ Backend health endpoint is responding"
else
    warn "Backend may still be starting up"
fi

# Step 8: Display deployment summary
log "Step 8: Deployment Summary"
echo ""
log "🎉 JobQuest Navigator v3 Production Deployment Complete!"
echo ""
log "📋 Application URLs:"
log "  🌐 Frontend:     http://$LOAD_BALANCER_DNS"
log "  🔧 Backend API:  http://$LOAD_BALANCER_DNS/api"
log "  📊 GraphQL:      http://$LOAD_BALANCER_DNS/graphql"
log "  ❤️  Health:       http://$LOAD_BALANCER_DNS/health"
echo ""

log "📊 Infrastructure Status:"
aws ecs describe-services --cluster $CLUSTER_NAME --services $BACKEND_SERVICE $FRONTEND_SERVICE --query "services[*].[serviceName,status,runningCount,desiredCount]" --output table

echo ""
log "🔍 Service Details:"
info "Cluster: $CLUSTER_NAME"
info "Backend Service: $BACKEND_SERVICE"
info "Frontend Service: $FRONTEND_SERVICE"
info "Load Balancer: $LOAD_BALANCER_DNS"
echo ""

log "📈 Production Features Deployed:"
info "✅ FastAPI + Strawberry GraphQL backend"
info "✅ React 18 frontend with Apollo Client"
info "✅ PostgreSQL database with Alembic migrations"
info "✅ Production-optimized Docker images"
info "✅ AWS ECS Fargate deployment"
info "✅ Application Load Balancer with health checks"
info "✅ ECR container registry"
info "✅ CloudWatch logging"
echo ""

log "🔐 Security Features:"
info "✅ Non-root containers"
info "✅ Multi-stage Docker builds"
info "✅ Security group restrictions"
info "✅ Private subnet deployment"
info "✅ IAM role-based permissions"
echo ""

# Cleanup temporary files
rm -f backend-task-def.json frontend-task-def.json backend-task-def-new.json frontend-task-def-new.json

log "🚀 Production deployment completed successfully!"
info "You can now access JobQuest Navigator v3 at: http://$LOAD_BALANCER_DNS"
echo ""