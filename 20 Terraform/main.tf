# main.tf

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }

  # 生产环境中推荐使用S3后端存储状态文件
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket-name"
  #   key            = "jobquest/terraform.tfstate"
  #   region         = "your-aws-region"
  #   dynamodb_table = "your-terraform-locks-table"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region
}

# ------------------------------------------------------------------------------
# Data Sources
# ------------------------------------------------------------------------------

data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  # 确保至少使用2个AZ，并且与子网数量匹配
  azs = slice(data.aws_availability_zones.available.names, 0, min(length(var.public_subnet_cidrs), length(data.aws_availability_zones.available.names)))
}

# ------------------------------------------------------------------------------
# VPC and Networking
# ------------------------------------------------------------------------------

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

resource "aws_subnet" "public" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = local.azs[count.index]
  map_public_ip_on_launch = true # 公共子网中的实例可以有公网IP

  tags = {
    Name = "${var.project_name}-public-subnet-${count.index + 1}"
  }
}

resource "aws_subnet" "private" {
  count                   = length(var.private_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.private_subnet_cidrs[count.index]
  availability_zone       = local.azs[count.index]
  map_public_ip_on_launch = false

  tags = {
    Name = "${var.project_name}-private-subnet-${count.index + 1}"
  }
}

# 为私有子网创建NAT网关，以便访问外部服务（如第三方API）
resource "aws_eip" "nat" {
  count = length(local.azs) # 每个AZ一个NAT网关以实现高可用
  domain   = "vpc" # Terraform v0.12 及更高版本需要此参数

  tags = {
    Name = "${var.project_name}-nat-eip-${count.index + 1}"
  }
}

resource "aws_nat_gateway" "nat" {
  count         = length(local.azs)
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id # NAT网关放在公共子网

  tags = {
    Name = "${var.project_name}-nat-gw-${count.index + 1}"
  }

  depends_on = [aws_internet_gateway.gw]
}

# 路由表
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  count  = length(local.azs)
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat[count.index].id # 私有子网通过NAT网关访问外部
  }

  tags = {
    Name = "${var.project_name}-private-rt-${count.index + 1}"
  }
}

resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id # 每个私有子网关联到其AZ的NAT网关路由表
}

# ------------------------------------------------------------------------------
# Security Groups
# ------------------------------------------------------------------------------

# Lambda 函数安全组
resource "aws_security_group" "lambda" {
  name        = "${var.project_name}-lambda-sg"
  description = "Security group for Lambda functions"
  vpc_id      = aws_vpc.main.id

  # 允许出站到任何地方 (用于访问外部API, S3, RDS, DocumentDB)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-lambda-sg"
  }
}

# RDS MySQL 安全组
resource "aws_security_group" "rds_mysql" {
  name        = "${var.project_name}-rds-mysql-sg"
  description = "Security group for RDS MySQL instance"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda.id] # 只允许来自Lambda安全组的访问
  }

  egress { # 通常RDS不需要出站，但如果需要访问KMS等，可以打开
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-rds-mysql-sg"
  }
}

# DocumentDB 安全组
resource "aws_security_group" "docdb" {
  name        = "${var.project_name}-docdb-sg"
  description = "Security group for DocumentDB cluster"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 27017 # DocumentDB 默认端口
    to_port         = 27017
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda.id] # 只允许来自Lambda安全组的访问
  }

   egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-docdb-sg"
  }
}

# ALB 安全组 (如果使用)
resource "aws_security_group" "alb" {
  name        = "${var.project_name}-alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # 允许来自互联网的HTTP访问
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # 允许来自互联网的HTTPS访问
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-alb-sg"
  }
}


# ------------------------------------------------------------------------------
# S3 Bucket for Resumes and potentially Lambda code
# ------------------------------------------------------------------------------

resource "aws_s3_bucket" "resumes" {
  bucket = "${var.project_name}-resumes-${random_string.bucket_suffix.id}" # Bucket 名称需要全局唯一

  tags = {
    Name        = "${var.project_name}-resumes-bucket"
    Environment = "production" # 或者 "development"
  }
}

resource "aws_s3_bucket_acl" "resumes_acl" {
  bucket = aws_s3_bucket.resumes.id
  acl    = "private" # 默认私有，Lambda通过IAM角色访问
}

resource "aws_s3_bucket_versioning" "resumes_versioning" {
  bucket = aws_s3_bucket.resumes.id
  versioning_configuration {
    status = "Enabled" # 为简历启用版本控制
  }
}

resource "aws_s3_bucket_public_access_block" "resumes_public_access" {
  bucket                  = aws_s3_bucket.resumes.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# ------------------------------------------------------------------------------
# IAM Roles and Policies for Lambda
# ------------------------------------------------------------------------------

resource "aws_iam_role" "lambda_exec_role" {
  name = "${var.project_name}-lambda-exec-role"

  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-lambda-exec-role"
  }
}

# 基础 Lambda 执行权限 (CloudWatch Logs)
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda VPC 访问权限
resource "aws_iam_role_policy_attachment" "lambda_vpc_access_execution" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# 自定义策略允许 Lambda 访问 S3, RDS, DocumentDB 等
resource "aws_iam_policy" "lambda_custom_permissions" {
  name        = "${var.project_name}-lambda-custom-permissions"
  description = "Custom permissions for Lambda functions"

  policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ],
        Resource = [
          aws_s3_bucket.resumes.arn,
          "${aws_s3_bucket.resumes.arn}/*"
        ]
      },
      # 如果使用 Secrets Manager 存储数据库凭证
      # {
      #   Effect = "Allow",
      #   Action = "secretsmanager:GetSecretValue",
      #   Resource = [
      #     aws_secretsmanager_secret.rds_credentials.arn,
      #     aws_secretsmanager_secret.docdb_credentials.arn
      #   ]
      # },
      # 如果需要调用其他AWS服务 (e.g., SNS, SQS) 在此添加
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_custom_policy_attachment" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_custom_permissions.arn
}

# ------------------------------------------------------------------------------
# RDS MySQL Database
# ------------------------------------------------------------------------------

resource "aws_db_subnet_group" "rds_mysql" {
  name       = "${var.project_name}-rds-mysql-subnet-group"
  subnet_ids = aws_subnet.private[*].id # RDS 放在私有子网

  tags = {
    Name = "${var.project_name}-rds-mysql-subnet-group"
  }
}

resource "random_password" "rds_master_password" {
  length           = 16
  special          = true
  override_special = "_%@"
}

# 生产中，密码应存储在 Secrets Manager
# resource "aws_secretsmanager_secret" "rds_credentials" {
#   name = "${var.project_name}/rds/master_credentials"
# }

# resource "aws_secretsmanager_secret_version" "rds_credentials_version" {
#   secret_id     = aws_secretsmanager_secret.rds_credentials.id
#   secret_string = random_password.rds_master_password.result
# }

resource "aws_db_instance" "mysql_db" {
  identifier             = "${var.project_name}-mysql-db"
  allocated_storage      = 20 # GB
  storage_type           = "gp2"
  engine                 = "mysql"
  engine_version         = "8.0" # 确认您需要的版本
  instance_class         = var.rds_mysql_instance_class
  db_name                = "${var.project_name}db" # 初始数据库名
  username               = "${var.project_name}admin"
  password               = random_password.rds_master_password.result # 引用随机密码，或从Secrets Manager获取
  parameter_group_name   = "default.mysql8.0"
  db_subnet_group_name   = aws_db_subnet_group.rds_mysql.name
  vpc_security_group_ids = [aws_security_group.rds_mysql.id]
  skip_final_snapshot    = true # 生产中应设置为 false，并配置备份
  multi_az               = false # 生产中建议设置为 true 以实现高可用
  publicly_accessible    = false # 数据库不应公开访问

  tags = {
    Name = "${var.project_name}-mysql-db"
  }
}

# ------------------------------------------------------------------------------
# DocumentDB (MongoDB compatible)
# ------------------------------------------------------------------------------

resource "aws_docdb_subnet_group" "docdb" {
  name       = "${var.project_name}-docdb-subnet-group"
  subnet_ids = aws_subnet.private[*].id # DocumentDB 放在私有子网

  tags = {
    Name = "${var.project_name}-docdb-subnet-group"
  }
}

resource "random_password" "docdb_master_password" {
  length           = 16
  special          = true
  override_special = "_%@"
}

# 生产中，密码应存储在 Secrets Manager
# resource "aws_secretsmanager_secret" "docdb_credentials" {
#   name = "${var.project_name}/docdb/master_credentials"
# }

# resource "aws_secretsmanager_secret_version" "docdb_credentials_version" {
#   secret_id     = aws_secretsmanager_secret.docdb_credentials.id
#   secret_string = random_password.docdb_master_password.result
# }

resource "aws_docdb_cluster" "docdb_cluster" {
  cluster_identifier      = "${var.project_name}-docdb-cluster"
  engine                  = "docdb"
  engine_version          = "4.0.0" # 或 "5.0.0"，确认您需要的版本
  master_username         = "${var.project_name}docadmin"
  master_password         = random_password.docdb_master_password.result # 引用随机密码，或从Secrets Manager获取
  db_subnet_group_name    = aws_docdb_subnet_group.docdb.name
  vpc_security_group_ids  = [aws_security_group.docdb.id]
  skip_final_snapshot     = true    # 生产中应设置为 false
  # storage_encrypted       = true # 默认启用
  # kms_key_id              = "your-kms-key-arn" # (可选) 自定义KMS密钥
  backup_retention_period = 1 # 生产中应增加

  # DocumentDB 需要 TLS 连接，可以创建一个参数组启用它，尽管默认可能已启用
  # db_cluster_parameter_group_name = aws_docdb_cluster_parameter_group.main.name

  tags = {
    Name = "${var.project_name}-docdb-cluster"
  }
}

# resource "aws_docdb_cluster_parameter_group" "main" {
#   name        = "${var.project_name}-docdb-pg"
#   family      = "docdb4.0" # 根据您的引擎版本调整
#   description = "DocumentDB cluster parameter group with TLS enabled"

#   parameter {
#     name  = "tls"
#     value = "enabled"
#   }
# }


resource "aws_docdb_cluster_instance" "docdb_instance" {
  count                = 2 # 至少部署2个实例以实现高可用
  identifier           = "${var.project_name}-docdb-instance-${count.index}"
  cluster_identifier   = aws_docdb_cluster.docdb_cluster.id
  instance_class       = var.docdb_instance_class
  # promotion_tier     = count.index == 0 ? 0 : 1 # 可选，指定主实例

  tags = {
    Name = "${var.project_name}-docdb-instance-${count.index}"
  }
}


# ------------------------------------------------------------------------------
# Lambda Functions (示例：Job Data Service MS1)
# 您需要为每个微服务复制并调整此部分
# ------------------------------------------------------------------------------

# 假设您的Lambda代码已打包成 job-data-service.zip 并上传到S3
# resource "aws_s3_object" "job_data_service_lambda_code" {
#   bucket = aws_s3_bucket.resumes.id # 或者一个专门的lambda代码 S3 bucket
#   key    = "lambda-code/job-data-service.zip"
#   source = "path/to/your/job-data-service.zip" # 本地代码包路径
#   etag   = filemd5("path/to/your/job-data-service.zip")
# }

resource "aws_lambda_function" "job_data_service" {
  function_name = "${var.project_name}-job-data-service"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "index.handler" # 根据您的代码调整 (e.g., app.lambda_handler for Python)
  runtime       = var.lambda_runtime
  timeout       = 30 # 秒
  memory_size   = 256 # MB

  # 如果代码包在S3
  # s3_bucket = aws_s3_bucket.resumes.id
  # s3_key    = aws_s3_object.job_data_service_lambda_code.key
  # source_code_hash = aws_s3_object.job_data_service_lambda_code.etag

  # 如果直接上传zip (小于50MB)
  filename         = "dummy_lambda_payload.zip" # 替换为您的代码包路径或创建一个空zip用于测试
  source_code_hash = filebase64sha256("dummy_lambda_payload.zip") # Terraform 需要此项来检测代码更改

  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      # 数据库连接信息应通过Secrets Manager传递，而不是硬编码
      DB_HOST              = aws_db_instance.mysql_db.address
      DB_PORT              = aws_db_instance.mysql_db.port
      DB_USER              = aws_db_instance.mysql_db.username
      # DB_PASSWORD_SECRET_ARN = aws_secretsmanager_secret.rds_credentials.arn # 在Lambda代码中获取
      DOCDB_ENDPOINT       = aws_docdb_cluster.docdb_cluster.endpoint
      DOCDB_USER           = aws_docdb_cluster.docdb_cluster.master_username
      # DOCDB_PASSWORD_SECRET_ARN = aws_secretsmanager_secret.docdb_credentials.arn # 在Lambda代码中获取
      S3_BUCKET_RESUMES    = aws_s3_bucket.resumes.bucket
      # 其他环境变量，如外部API密钥 (应使用Secrets Manager)
      # GOOGLE_JOBS_API_KEY_SECRET_ARN = "arn:aws:secretsmanager:..."
    }
  }

  tags = {
    Name        = "${var.project_name}-job-data-service"
    Microservice = "MS1-JobDataService"
  }

  # 确保先创建dummy_lambda_payload.zip文件
  # touch dummy_lambda_payload.zip
  # zip dummy_lambda_payload.zip dummy_lambda_payload.zip # 创建一个包含自身的空zip
  # 或者提供一个真实的占位 Lambda zip 包
}

# 您需要为其他8个微服务（MS2-MS9）创建类似的 aws_lambda_function 资源
# 例如：aws_lambda_function.resume_management_service, aws_lambda_function.ai_suggestion_service, etc.
# 确保每个函数的 function_name, handler, tags 及可能的环境变量都正确设置。

# ------------------------------------------------------------------------------
# API Gateway (HTTP API - 更简单且成本更低)
# ------------------------------------------------------------------------------

resource "aws_apigatewayv2_api" "main_api" {
  name          = "${var.project_name}-http-api"
  protocol_type = "HTTP"
  description   = "API Gateway for JobQuest Navigator microservices"

  # CORS 配置 (根据您的前端需求调整)
  # cors_configuration {
  #   allow_origins = ["http://localhost:3000", "https://your-frontend-domain.com"]
  #   allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
  #   allow_headers = ["Content-Type", "Authorization", "X-Amz-Date", "X-Api-Key", "X-Amz-Security-Token"]
  #   max_age = 300
  # }

  tags = {
    Name = "${var.project_name}-http-api"
  }
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.main_api.id
  name        = "$default" # 默认阶段
  auto_deploy = true

  # access_log_settings { # 可选：启用访问日志
  #   destination_arn = aws_cloudwatch_log_group.api_gw_logs.arn
  #   format          = jsonencode({
  #       requestId               = "$context.requestId"
  #       sourceIp                = "$context.identity.sourceIp"
  #       requestTime             = "$context.requestTime"
  #       httpMethod              = "$context.httpMethod"
  #       path                    = "$context.path"
  #       status                  = "$context.status"
  #       protocol                = "$context.protocol"
  #       responseLength          = "$context.responseLength"
  #     })
  # }

  tags = {
    Name = "${var.project_name}-api-stage-default"
  }
}

# resource "aws_cloudwatch_log_group" "api_gw_logs" {
#   name              = "/aws/apigateway/${var.project_name}-http-api"
#   retention_in_days = 7 # 根据需要调整日志保留时间
# }


# 示例：为 Job Data Service 创建集成和路由
resource "aws_apigatewayv2_integration" "job_data_service_integration" {
  api_id           = aws_apigatewayv2_api.main_api.id
  integration_type = "AWS_PROXY" # 用于 Lambda 代理集成
  integration_uri  = aws_lambda_function.job_data_service.invoke_arn
  payload_format_version = "2.0" # 适用于 HTTP API 的 Lambda 代理集成
}

resource "aws_apigatewayv2_route" "get_jobs_route" {
  api_id    = aws_apigatewayv2_api.main_api.id
  route_key = "GET /api/v1/jobs" # 您的 API 端点
  target    = "integrations/${aws_apigatewayv2_integration.job_data_service_integration.id}"
}

resource "aws_apigatewayv2_route" "get_job_by_id_route" {
  api_id    = aws_apigatewayv2_api.main_api.id
  route_key = "GET /api/v1/jobs/{jobId}" # 路径参数
  target    = "integrations/${aws_apigatewayv2_integration.job_data_service_integration.id}"
}

# ... 为 MS1 的其他端点（如 POST /jobs/search）创建更多路由
# ... 为 MS2 到 MS9 的每个 Lambda 函数及其端点创建集成和路由

# 允许 API Gateway 调用 Lambda 函数
resource "aws_lambda_permission" "api_gw_lambda_job_data_service" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.job_data_service.function_name
  principal     = "apigateway.amazonaws.com"

  # Source ARN 限制了哪个 API Gateway 可以调用此 Lambda
  source_arn = "${aws_apigatewayv2_api.main_api.execution_arn}/*/*" # 允许任何方法和路径
  # 更精细的控制：
  # source_arn = "${aws_apigatewayv2_api.main_api.execution_arn}/*/GET/api/v1/jobs"
}

# 为其他 Lambda 函数重复 aws_lambda_permission


# ------------------------------------------------------------------------------
# Application Load Balancer (ALB) - 可选
# 如果您未来计划使用容器化服务 (ECS/EKS) 或需要更复杂的路由/WAF，ALB会很有用
# 对于纯Lambda后端，API Gateway 通常是更直接的选择。
# 此处提供一个基础ALB配置，但它当前没有目标。
# ------------------------------------------------------------------------------

resource "aws_lb" "main_alb" {
  name               = "${var.project_name}-alb"
  internal           = false # 面向公网
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id # ALB 放在公共子网

  enable_deletion_protection = false # 生产中建议设置为 true

  tags = {
    Name = "${var.project_name}-alb"
  }
}

# 默认目标组 (可以指向 ECS 服务, EC2 实例, 或通过 VPC Link 指向 API Gateway)
resource "aws_lb_target_group" "default_tg" {
  name     = "${var.project_name}-default-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
  target_type = "ip" # 或 "instance" 或 "lambda" (ALB直接调用Lambda不常见，如果API Gateway已在用)

  health_check {
    path                = "/" # 根据您的应用调整
    protocol            = "HTTP"
    matcher             = "200-399"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = {
    Name = "${var.project_name}-default-tg"
  }
}

resource "aws_lb_listener" "http_listener" {
  load_balancer_arn = aws_lb.main_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.default_tg.arn
  }

  # 生产中，应重定向 HTTP 到 HTTPS
  # default_action {
  #   type = "redirect"
  #   redirect {
  #     port        = "443"
  #     protocol    = "HTTPS"
  #     status_code = "HTTP_301"
  #   }
  # }
}

# resource "aws_lb_listener" "https_listener" {
#   load_balancer_arn = aws_lb.main_alb.arn
#   port              = 443
#   protocol          = "HTTPS"
#   ssl_policy        = "ELBSecurityPolicy-2016-08" # 根据需要选择策略
#   certificate_arn   = "arn:aws:acm:your-region:your-account-id:certificate/your-certificate-id" # 需要一个 ACM 证书

#   default_action {
#     type             = "forward"
#     target_group_arn = aws_lb_target_group.default_tg.arn
#   }
# }


# ------------------------------------------------------------------------------
# Outputs
# ------------------------------------------------------------------------------

output "vpc_id" {
  description = "ID of the created VPC."
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets."
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets."
  value       = aws_subnet.private[*].id
}

output "lambda_execution_role_arn" {
  description = "ARN of the IAM role for Lambda functions."
  value       = aws_iam_role.lambda_exec_role.arn
}

output "s3_resumes_bucket_name" {
  description = "Name of the S3 bucket for resumes."
  value       = aws_s3_bucket.resumes.bucket
}

output "s3_resumes_bucket_arn" {
  description = "ARN of the S3 bucket for resumes."
  value       = aws_s3_bucket.resumes.arn
}

output "rds_mysql_endpoint" {
  description = "Endpoint address for the RDS MySQL instance."
  value       = aws_db_instance.mysql_db.address
  sensitive   = true
}

output "rds_mysql_port" {
  description = "Port for the RDS MySQL instance."
  value       = aws_db_instance.mysql_db.port
}

output "docdb_cluster_endpoint" {
  description = "Endpoint for the DocumentDB cluster."
  value       = aws_docdb_cluster.docdb_cluster.endpoint
  sensitive   = true
}

output "docdb_cluster_reader_endpoint" {
  description = "Reader endpoint for the DocumentDB cluster."
  value       = aws_docdb_cluster.docdb_cluster.reader_endpoint
  sensitive   = true
}

output "api_gateway_invoke_url" {
  description = "Invoke URL for the API Gateway (default stage)."
  value       = aws_apigatewayv2_api.main_api.api_endpoint # 这是基础 URL，需要附加阶段名（如果不是 $default）和路径
}

output "api_gateway_default_stage_invoke_url" {
  description = "Invoke URL for the API Gateway default stage."
  value       = aws_apigatewayv2_stage.default.invoke_url
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer."
  value       = aws_lb.main_alb.dns_name
  # sensitive = true # 取决于您的安全策略
}