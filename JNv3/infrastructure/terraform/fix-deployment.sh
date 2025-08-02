#!/bin/bash

# JobQuest Navigator v3 - Deployment Fix Script
# This script resolves deployment issues and completes the infrastructure setup

set -e

echo "🔧 Starting deployment fix process..."

# Step 1: Clean up any existing problematic resources
echo "📋 Step 1: Cleaning up problematic resources..."

# Remove any existing listeners that might block target group deletion
echo "   - Removing load balancer listeners..."
aws elbv2 describe-listeners --region us-east-1 --query 'Listeners[*].ListenerArn' --output text 2>/dev/null | while read listener_arn; do
    if [ ! -z "$listener_arn" ]; then
        echo "     Removing listener: $listener_arn"
        aws elbv2 delete-listener --listener-arn "$listener_arn" --region us-east-1 || true
    fi
done

# Remove any existing load balancers
echo "   - Removing load balancers..."
aws elbv2 describe-load-balancers --region us-east-1 --query 'LoadBalancers[*].LoadBalancerArn' --output text 2>/dev/null | while read lb_arn; do
    if [ ! -z "$lb_arn" ]; then
        echo "     Removing load balancer: $lb_arn"
        aws elbv2 delete-load-balancer --load-balancer-arn "$lb_arn" --region us-east-1 || true
    fi
done

# Remove any existing target groups
echo "   - Removing target groups..."
aws elbv2 describe-target-groups --region us-east-1 --query 'TargetGroups[*].TargetGroupArn' --output text 2>/dev/null | while read tg_arn; do
    if [ ! -z "$tg_arn" ]; then
        echo "     Removing target group: $tg_arn"
        aws elbv2 delete-target-group --target-group-arn "$tg_arn" --region us-east-1 || true
    fi
done

# Remove any existing ECS services
echo "   - Removing ECS services..."
aws ecs list-services --cluster jobquest-navigator-v3-cluster --region us-east-1 --query 'serviceArns' --output text 2>/dev/null | while read service_arn; do
    if [ ! -z "$service_arn" ]; then
        service_name=$(basename "$service_arn")
        echo "     Removing ECS service: $service_name"
        aws ecs update-service --cluster jobquest-navigator-v3-cluster --service "$service_name" --desired-count 0 --region us-east-1 || true
        aws ecs delete-service --cluster jobquest-navigator-v3-cluster --service "$service_name" --region us-east-1 || true
    fi
done

# Remove any existing RDS instances
echo "   - Removing RDS instances..."
aws rds describe-db-instances --region us-east-1 --query 'DBInstances[?contains(DBInstanceIdentifier, `jobquest-navigator-v3`)].DBInstanceIdentifier' --output text 2>/dev/null | while read db_id; do
    if [ ! -z "$db_id" ]; then
        echo "     Removing RDS instance: $db_id"
        aws rds delete-db-instance --db-instance-identifier "$db_id" --skip-final-snapshot --region us-east-1 || true
    fi
done

# Remove any existing internet gateways (keep only one)
echo "   - Cleaning up internet gateways..."
aws ec2 describe-internet-gateways --region us-east-1 --query 'InternetGateways[?Attachments[0].State==`available`].InternetGatewayId' --output text 2>/dev/null | while read igw_id; do
    if [ ! -z "$igw_id" ]; then
        echo "     Detaching internet gateway: $igw_id"
        aws ec2 detach-internet-gateway --internet-gateway-id "$igw_id" --region us-east-1 || true
        aws ec2 delete-internet-gateway --internet-gateway-id "$igw_id" --region us-east-1 || true
    fi
done

# Wait for cleanup to complete
echo "   - Waiting for cleanup to complete..."
sleep 30

# Step 2: Initialize Terraform
echo "📋 Step 2: Initializing Terraform..."
terraform init -reconfigure -backend-config=backend-configs/production.hcl

# Step 3: Validate configuration
echo "📋 Step 3: Validating configuration..."
terraform validate

# Step 4: Apply deployment in stages
echo "📋 Step 4: Applying deployment in stages..."

# Stage 1: Create networking resources
echo "   - Stage 1: Creating networking resources..."
terraform apply -target=aws_internet_gateway.main -target=aws_nat_gateway.main -target=aws_route_table.public -target=aws_route_table.private -target=aws_route_table_association.public -target=aws_route_table_association.private -target=aws_subnet.private -auto-approve

# Stage 2: Create security groups
echo "   - Stage 2: Creating security groups..."
terraform apply -target=aws_security_group.ecs -target=aws_security_group.rds -target=aws_security_group.alb -auto-approve

# Stage 3: Create database
echo "   - Stage 3: Creating database..."
terraform apply -target=aws_db_instance.main -auto-approve

# Stage 4: Create load balancer and target groups
echo "   - Stage 4: Creating load balancer and target groups..."
terraform apply -target=aws_lb.main -target=aws_lb_target_group.backend -target=aws_lb_target_group.frontend -target=aws_lb_listener.main -target=aws_lb_listener_rule.backend -auto-approve

# Stage 5: Create ECS resources
echo "   - Stage 5: Creating ECS resources..."
terraform apply -target=aws_ecs_task_definition.backend -target=aws_ecs_task_definition.frontend -target=aws_ecs_service.backend -target=aws_ecs_service.frontend -auto-approve

# Step 5: Final apply to ensure everything is consistent
echo "📋 Step 5: Final apply..."
terraform apply -auto-approve

echo "✅ Deployment fix completed successfully!"
echo "🌐 Application URL: $(terraform output -raw application_url 2>/dev/null || echo 'Will be available after deployment')"
echo "📊 Check the deployment status with: terraform show" 