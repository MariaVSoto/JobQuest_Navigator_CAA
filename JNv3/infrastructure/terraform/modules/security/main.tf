# Security Groups Module for JobQuest Navigator v2
# Defines security groups with least privilege principle

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ============================================================================
# APPLICATION LOAD BALANCER SECURITY GROUP
# ============================================================================

resource "aws_security_group" "alb" {
  name_prefix = "${var.name_prefix}-alb-"
  vpc_id      = var.vpc_id
  description = "Security group for Application Load Balancer"

  # HTTP access from anywhere
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS access from anywhere
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # All outbound traffic
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-alb-sg"
    Type = "Security Group"
    Component = "Load Balancer"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# ============================================================================
# BACKEND ECS SERVICE SECURITY GROUP
# ============================================================================

resource "aws_security_group" "backend" {
  name_prefix = "${var.name_prefix}-backend-"
  vpc_id      = var.vpc_id
  description = "Security group for Backend ECS service"

  # HTTP access from ALB
  ingress {
    description     = "HTTP from ALB"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Health check from ALB
  ingress {
    description     = "Health check from ALB"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # All outbound traffic (for API calls, database access, etc.)
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-backend-sg"
    Type = "Security Group"
    Component = "Backend"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# ============================================================================
# FRONTEND ECS SERVICE SECURITY GROUP
# ============================================================================

resource "aws_security_group" "frontend" {
  name_prefix = "${var.name_prefix}-frontend-"
  vpc_id      = var.vpc_id
  description = "Security group for Frontend ECS service"

  # HTTP access from ALB
  ingress {
    description     = "HTTP from ALB"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # HTTPS access from ALB (if needed)
  ingress {
    description     = "HTTPS from ALB"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # All outbound traffic (for fetching assets, API calls)
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-frontend-sg"
    Type = "Security Group"
    Component = "Frontend"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# ============================================================================
# RDS DATABASE SECURITY GROUP
# ============================================================================

resource "aws_security_group" "rds" {
  name_prefix = "${var.name_prefix}-rds-"
  vpc_id      = var.vpc_id
  description = "Security group for RDS PostgreSQL database"

  # PostgreSQL access from backend services
  ingress {
    description     = "PostgreSQL from Backend"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.backend.id]
  }

  # PostgreSQL access from bastion (if needed for maintenance)
  dynamic "ingress" {
    for_each = var.enable_bastion_access ? [1] : []
    content {
      description     = "PostgreSQL from Bastion"
      from_port       = 5432
      to_port         = 5432
      protocol        = "tcp"
      security_groups = [aws_security_group.bastion[0].id]
    }
  }

  # No outbound rules needed for RDS

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-rds-sg"
    Type = "Security Group"
    Component = "Database"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# ============================================================================
# REDIS SECURITY GROUP
# ============================================================================

resource "aws_security_group" "redis" {
  name_prefix = "${var.name_prefix}-redis-"
  vpc_id      = var.vpc_id
  description = "Security group for ElastiCache Redis"

  # Redis access from backend services
  ingress {
    description     = "Redis from Backend"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.backend.id]
  }

  # Redis access from bastion (if needed for maintenance)
  dynamic "ingress" {
    for_each = var.enable_bastion_access ? [1] : []
    content {
      description     = "Redis from Bastion"
      from_port       = 6379
      to_port         = 6379
      protocol        = "tcp"
      security_groups = [aws_security_group.bastion[0].id]
    }
  }

  # No outbound rules needed for ElastiCache

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-redis-sg"
    Type = "Security Group"
    Component = "Cache"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# ============================================================================
# BASTION HOST SECURITY GROUP (Optional)
# ============================================================================

resource "aws_security_group" "bastion" {
  count = var.enable_bastion_access ? 1 : 0

  name_prefix = "${var.name_prefix}-bastion-"
  vpc_id      = var.vpc_id
  description = "Security group for Bastion host"

  # SSH access from specific IP ranges
  dynamic "ingress" {
    for_each = var.bastion_allowed_cidr_blocks
    content {
      description = "SSH from ${ingress.value}"
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
    }
  }

  # All outbound traffic
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-bastion-sg"
    Type = "Security Group"
    Component = "Bastion"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# ============================================================================
# ECS SERVICE DISCOVERY SECURITY GROUP
# ============================================================================

resource "aws_security_group" "service_discovery" {
  name_prefix = "${var.name_prefix}-service-discovery-"
  vpc_id      = var.vpc_id
  description = "Security group for ECS service discovery"

  # Allow communication between services
  ingress {
    description = "Service mesh communication"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    self        = true
  }

  # All outbound traffic
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-service-discovery-sg"
    Type = "Security Group"
    Component = "Service Discovery"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# ============================================================================
# VPC ENDPOINTS SECURITY GROUP
# ============================================================================

resource "aws_security_group" "vpc_endpoints" {
  count = var.enable_vpc_endpoints ? 1 : 0

  name_prefix = "${var.name_prefix}-vpc-endpoints-"
  vpc_id      = var.vpc_id
  description = "Security group for VPC endpoints"

  # HTTPS access from private subnets
  ingress {
    description = "HTTPS from private subnets"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.private_subnet_cidrs
  }

  # All outbound traffic
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-vpc-endpoints-sg"
    Type = "Security Group"
    Component = "VPC Endpoints"
  })

  lifecycle {
    create_before_destroy = true
  }
}