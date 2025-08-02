#!/bin/bash

# JobQuest Navigator v3 - Complete AWS Resource Cleanup Script
# This script deletes all AWS resources except S3 buckets

set -e

echo "🧹 Starting complete AWS resource cleanup..."

REGION="us-east-1"
PROJECT_PREFIX="jobquest-navigator-v3"

echo "📋 Step 1: Cleaning up ECS resources..."

# Delete ECS services
echo "   - Deleting ECS services..."
aws ecs list-services --cluster "${PROJECT_PREFIX}-cluster" --region $REGION --query 'serviceArns' --output text 2>/dev/null | while read service_arn; do
    if [ ! -z "$service_arn" ]; then
        echo "     Deleting service: $service_arn"
        aws ecs update-service --cluster "${PROJECT_PREFIX}-cluster" --service "$service_arn" --desired-count 0 --region $REGION
        aws ecs delete-service --cluster "${PROJECT_PREFIX}-cluster" --service "$service_arn" --force --region $REGION
    fi
done

# Delete ECS cluster
echo "   - Deleting ECS cluster..."
aws ecs delete-cluster --cluster "${PROJECT_PREFIX}-cluster" --region $REGION 2>/dev/null || true

echo "📋 Step 2: Cleaning up Load Balancer resources..."

# Delete ALB listeners
echo "   - Deleting ALB listeners..."
aws elbv2 describe-load-balancers --region $REGION --query 'LoadBalancers[?contains(LoadBalancerName, `jobquest`)].LoadBalancerArn' --output text 2>/dev/null | while read lb_arn; do
    if [ ! -z "$lb_arn" ]; then
        echo "     Deleting listeners for ALB: $lb_arn"
        aws elbv2 describe-listeners --load-balancer-arn "$lb_arn" --region $REGION --query 'Listeners[*].ListenerArn' --output text 2>/dev/null | while read listener_arn; do
            if [ ! -z "$listener_arn" ]; then
                echo "       Deleting listener: $listener_arn"
                aws elbv2 delete-listener --listener-arn "$listener_arn" --region $REGION
            fi
        done
    fi
done

# Delete ALB
echo "   - Deleting ALB..."
aws elbv2 describe-load-balancers --region $REGION --query 'LoadBalancers[?contains(LoadBalancerName, `jobquest`)].LoadBalancerArn' --output text 2>/dev/null | while read lb_arn; do
    if [ ! -z "$lb_arn" ]; then
        echo "     Deleting ALB: $lb_arn"
        aws elbv2 delete-load-balancer --load-balancer-arn "$lb_arn" --region $REGION
    fi
done

# Delete target groups
echo "   - Deleting target groups..."
aws elbv2 describe-target-groups --region $REGION --query 'TargetGroups[?contains(TargetGroupName, `jqnav`)].TargetGroupArn' --output text 2>/dev/null | while read tg_arn; do
    if [ ! -z "$tg_arn" ]; then
        echo "     Deleting target group: $tg_arn"
        aws elbv2 delete-target-group --target-group-arn "$tg_arn" --region $REGION
    fi
done

echo "📋 Step 3: Cleaning up RDS resources..."

# Delete RDS instances
echo "   - Deleting RDS instances..."
aws rds describe-db-instances --region $REGION --query 'DBInstances[?contains(DBInstanceIdentifier, `jobquest`)].DBInstanceIdentifier' --output text 2>/dev/null | while read db_id; do
    if [ ! -z "$db_id" ]; then
        echo "     Deleting RDS instance: $db_id"
        aws rds delete-db-instance --db-instance-identifier "$db_id" --skip-final-snapshot --delete-automated-backups --region $REGION
    fi
done

# Delete RDS subnet groups
echo "   - Deleting RDS subnet groups..."
aws rds describe-db-subnet-groups --region $REGION --query 'DBSubnetGroups[?contains(DBSubnetGroupName, `jobquest`)].DBSubnetGroupName' --output text 2>/dev/null | while read sg_name; do
    if [ ! -z "$sg_name" ]; then
        echo "     Deleting RDS subnet group: $sg_name"
        aws rds delete-db-subnet-group --db-subnet-group-name "$sg_name" --region $REGION
    fi
done

echo "📋 Step 4: Cleaning up EC2 resources..."

# Delete NAT Gateway
echo "   - Deleting NAT Gateway..."
aws ec2 describe-nat-gateways --region $REGION --query 'NatGateways[?contains(Tags[?Key==`Name`].Value, `jobquest`)].NatGatewayId' --output text 2>/dev/null | while read nat_id; do
    if [ ! -z "$nat_id" ]; then
        echo "     Deleting NAT Gateway: $nat_id"
        aws ec2 delete-nat-gateway --nat-gateway-id "$nat_id" --region $REGION
    fi
done

# Delete Elastic IPs
echo "   - Deleting Elastic IPs..."
aws ec2 describe-addresses --region $REGION --query 'Addresses[?contains(Tags[?Key==`Name`].Value, `jobquest`)].AllocationId' --output text 2>/dev/null | while read eip_id; do
    if [ ! -z "$eip_id" ]; then
        echo "     Deleting EIP: $eip_id"
        aws ec2 release-address --allocation-id "$eip_id" --region $REGION
    fi
done

# Delete Internet Gateway
echo "   - Deleting Internet Gateway..."
aws ec2 describe-internet-gateways --region $REGION --query 'InternetGateways[?contains(Tags[?Key==`Name`].Value, `jobquest`)].InternetGatewayId' --output text 2>/dev/null | while read igw_id; do
    if [ ! -z "$igw_id" ]; then
        echo "     Detaching and deleting IGW: $igw_id"
        aws ec2 detach-internet-gateway --internet-gateway-id "$igw_id" --vpc-id $(aws ec2 describe-internet-gateways --internet-gateway-ids "$igw_id" --region $REGION --query 'InternetGateways[0].Attachments[0].VpcId' --output text) --region $REGION 2>/dev/null || true
        aws ec2 delete-internet-gateway --internet-gateway-id "$igw_id" --region $REGION
    fi
done

# Delete route tables
echo "   - Deleting route tables..."
aws ec2 describe-route-tables --region $REGION --query 'RouteTables[?contains(Tags[?Key==`Name`].Value, `jobquest`)].RouteTableId' --output text 2>/dev/null | while read rt_id; do
    if [ ! -z "$rt_id" ]; then
        echo "     Deleting route table: $rt_id"
        aws ec2 delete-route-table --route-table-id "$rt_id" --region $REGION
    fi
done

# Delete subnets
echo "   - Deleting subnets..."
aws ec2 describe-subnets --region $REGION --query 'Subnets[?contains(Tags[?Key==`Name`].Value, `jobquest`)].SubnetId' --output text 2>/dev/null | while read subnet_id; do
    if [ ! -z "$subnet_id" ]; then
        echo "     Deleting subnet: $subnet_id"
        aws ec2 delete-subnet --subnet-id "$subnet_id" --region $REGION
    fi
done

# Delete security groups
echo "   - Deleting security groups..."
aws ec2 describe-security-groups --region $REGION --query 'SecurityGroups[?contains(GroupName, `jobquest`)].GroupId' --output text 2>/dev/null | while read sg_id; do
    if [ ! -z "$sg_id" ]; then
        echo "     Deleting security group: $sg_id"
        aws ec2 delete-security-group --group-id "$sg_id" --region $REGION
    fi
done

# Delete VPC
echo "   - Deleting VPC..."
aws ec2 describe-vpcs --region $REGION --query 'Vpcs[?contains(Tags[?Key==`Name`].Value, `jobquest`)].VpcId' --output text 2>/dev/null | while read vpc_id; do
    if [ ! -z "$vpc_id" ]; then
        echo "     Deleting VPC: $vpc_id"
        aws ec2 delete-vpc --vpc-id "$vpc_id" --region $REGION
    fi
done

echo "📋 Step 5: Cleaning up ECR resources..."

# Delete ECR repositories
echo "   - Deleting ECR repositories..."
aws ecr describe-repositories --region $REGION --query 'repositories[?contains(repositoryName, `jobquest`)].repositoryName' --output text 2>/dev/null | while read repo_name; do
    if [ ! -z "$repo_name" ]; then
        echo "     Deleting ECR repository: $repo_name"
        aws ecr delete-repository --repository-name "$repo_name" --force --region $REGION
    fi
done

echo "📋 Step 6: Cleaning up IAM resources..."

# Delete IAM roles
echo "   - Deleting IAM roles..."
aws iam list-roles --query 'Roles[?contains(RoleName, `jobquest`)].RoleName' --output text 2>/dev/null | while read role_name; do
    if [ ! -z "$role_name" ]; then
        echo "     Deleting IAM role: $role_name"
        # Detach policies first
        aws iam list-attached-role-policies --role-name "$role_name" --query 'AttachedPolicies[*].PolicyArn' --output text 2>/dev/null | while read policy_arn; do
            if [ ! -z "$policy_arn" ]; then
                aws iam detach-role-policy --role-name "$role_name" --policy-arn "$policy_arn"
            fi
        done
        aws iam delete-role --role-name "$role_name"
    fi
done

echo "📋 Step 7: Cleaning up CloudWatch resources..."

# Delete CloudWatch log groups
echo "   - Deleting CloudWatch log groups..."
aws logs describe-log-groups --region $REGION --query 'logGroups[?contains(logGroupName, `jobquest`)].logGroupName' --output text 2>/dev/null | while read log_group; do
    if [ ! -z "$log_group" ]; then
        echo "     Deleting log group: $log_group"
        aws logs delete-log-group --log-group-name "$log_group" --region $REGION
    fi
done

echo "📋 Step 8: Cleaning up DynamoDB resources..."

# Delete DynamoDB tables (if any)
echo "   - Deleting DynamoDB tables..."
aws dynamodb list-tables --region $REGION --query 'TableNames[?contains(@, `jobquest`)]' --output text 2>/dev/null | while read table_name; do
    if [ ! -z "$table_name" ]; then
        echo "     Deleting DynamoDB table: $table_name"
        aws dynamodb delete-table --table-name "$table_name" --region $REGION
    fi
done

echo "✅ AWS resource cleanup completed!"
echo "📝 Note: S3 buckets have been preserved as requested." 