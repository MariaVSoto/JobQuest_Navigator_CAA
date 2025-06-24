# 🚀 JobQuest Navigator - AWS生产环境部署指南

## 📋 部署概览

本指南详细说明如何在AWS上部署JobQuest Navigator生产环境，包括基础设施规划、服务配置、安全设置和监控。

---

## 🏗️ AWS架构设计

### 整体架构图
```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   CloudFront    │    │     ALB      │    │   ECS Fargate   │
│   (CDN + SSL)   │───▶│ (Load Balancer)│───▶│   (Containers)  │
└─────────────────┘    └──────────────┘    └─────────────────┘
                              │                      │
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│      S3         │    │     RDS      │    │     Redis       │
│ (Static Files)  │    │   (MySQL)    │    │ (ElastiCache)   │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

### 核心AWS服务
- **前端**: CloudFront + S3 (React应用)
- **后端**: ECS Fargate (Django API)
- **负载均衡**: Application Load Balancer (ALB)
- **数据库**: RDS MySQL + ElastiCache Redis
- **文件存储**: S3 + CloudFront
- **邮件**: SES (Simple Email Service)
- **监控**: CloudWatch + X-Ray
- **安全**: VPC + Security Groups + IAM
- **CI/CD**: CodePipeline + CodeBuild

---

## 💰 成本估算 (月度)

### 基础配置 (适合初期运营)
```yaml
服务                配置                    月度成本(USD)
─────────────────────────────────────────────────────
ECS Fargate        2 vCPU, 4GB RAM        ~$50
RDS MySQL          db.t3.micro             ~$15
ElastiCache        cache.t3.micro          ~$15
ALB                标准负载均衡器            ~$23
S3                 10GB存储 + 传输         ~$5
CloudFront         1TB传输                 ~$85
SES                10,000封邮件            ~$1
CloudWatch         基础监控                ~$10
NAT Gateway        数据传输                ~$45
─────────────────────────────────────────────────────
总计                                      ~$249/月
```

### 扩展配置 (高流量)
```yaml
服务                配置                    月度成本(USD)
─────────────────────────────────────────────────────
ECS Fargate        4 vCPU, 8GB RAM (多实例) ~$200
RDS MySQL          db.t3.small (Multi-AZ)  ~$60
ElastiCache        cache.t3.small          ~$30
ALB                标准负载均衡器            ~$23
S3                 100GB存储 + 传输        ~$15
CloudFront         10TB传输                ~$850
SES                100,000封邮件           ~$10
─────────────────────────────────────────────────────
总计                                      ~$1,188/月
```

---

## 🔧 详细部署步骤

### Phase 1: 基础设施准备

#### 1.1 VPC和网络配置
```bash
# 创建VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=jobquest-vpc}]'

# 创建子网
# 公有子网 (ALB, NAT Gateway)
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.1.0/24 --availability-zone us-west-2a
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.2.0/24 --availability-zone us-west-2b

# 私有子网 (ECS, RDS)
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.10.0/24 --availability-zone us-west-2a
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.20.0/24 --availability-zone us-west-2b

# 创建Internet Gateway
aws ec2 create-internet-gateway --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=jobquest-igw}]'
```

#### 1.2 安全组配置
```yaml
# ALB安全组
LoadBalancerSG:
  入站规则:
    - 端口: 80 (HTTP) - 来源: 0.0.0.0/0
    - 端口: 443 (HTTPS) - 来源: 0.0.0.0/0

# ECS安全组  
ECSServiceSG:
  入站规则:
    - 端口: 8000 - 来源: LoadBalancerSG
  出站规则:
    - 所有流量 - 目标: 0.0.0.0/0

# RDS安全组
DatabaseSG:
  入站规则:
    - 端口: 3306 - 来源: ECSServiceSG

# Redis安全组
RedisSG:
  入站规则:
    - 端口: 6379 - 来源: ECSServiceSG
```

### Phase 2: 数据库和缓存

#### 2.1 RDS MySQL配置
```yaml
# RDS子网组
aws rds create-db-subnet-group \
  --db-subnet-group-name jobquest-db-subnet-group \
  --db-subnet-group-description "JobQuest DB subnet group" \
  --subnet-ids subnet-xxx subnet-yyy

# RDS实例
aws rds create-db-instance \
  --db-instance-identifier jobquest-prod-db \
  --db-instance-class db.t3.micro \
  --engine mysql \
  --engine-version 8.0.35 \
  --allocated-storage 20 \
  --storage-type gp2 \
  --db-name jobquest \
  --master-username admin \
  --master-user-password [SECURE_PASSWORD] \
  --db-subnet-group-name jobquest-db-subnet-group \
  --vpc-security-group-ids sg-xxx \
  --backup-retention-period 7 \
  --multi-az \
  --storage-encrypted
```

#### 2.2 ElastiCache Redis配置
```yaml
# Redis子网组
aws elasticache create-cache-subnet-group \
  --cache-subnet-group-name jobquest-redis-subnet-group \
  --cache-subnet-group-description "JobQuest Redis subnet group" \
  --subnet-ids subnet-xxx subnet-yyy

# Redis集群
aws elasticache create-cache-cluster \
  --cache-cluster-id jobquest-prod-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1 \
  --cache-subnet-group-name jobquest-redis-subnet-group \
  --security-group-ids sg-xxx
```

### Phase 3: 容器化和ECS部署

#### 3.1 Docker镜像构建
```dockerfile
# 生产Dockerfile
FROM python:3.9-slim as production

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 设置环境变量
ENV DJANGO_SETTINGS_MODULE=core.settings.production

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# 启动应用
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "core.wsgi:application"]
```

#### 3.2 ECR和镜像推送
```bash
# 创建ECR仓库
aws ecr create-repository --repository-name jobquest/backend
aws ecr create-repository --repository-name jobquest/frontend

# 获取登录token
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin [ACCOUNT].dkr.ecr.us-west-2.amazonaws.com

# 构建和推送镜像
docker build -t jobquest/backend:latest .
docker tag jobquest/backend:latest [ACCOUNT].dkr.ecr.us-west-2.amazonaws.com/jobquest/backend:latest
docker push [ACCOUNT].dkr.ecr.us-west-2.amazonaws.com/jobquest/backend:latest
```

#### 3.3 ECS配置
```yaml
# ECS集群
aws ecs create-cluster --cluster-name jobquest-prod-cluster --capacity-providers FARGATE

# 任务定义
{
  "family": "jobquest-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::[ACCOUNT]:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::[ACCOUNT]:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "jobquest-backend",
      "image": "[ACCOUNT].dkr.ecr.us-west-2.amazonaws.com/jobquest/backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "mysql://admin:[PASSWORD]@[RDS_ENDPOINT]:3306/jobquest"
        },
        {
          "name": "REDIS_URL", 
          "value": "redis://[REDIS_ENDPOINT]:6379/0"
        }
      ],
      "secrets": [
        {
          "name": "DJANGO_SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-west-2:[ACCOUNT]:secret:jobquest/django-secret"
        },
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-west-2:[ACCOUNT]:secret:jobquest/openai-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/jobquest-backend",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health/ || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

### Phase 4: 负载均衡和SSL

#### 4.1 Application Load Balancer
```bash
# 创建ALB
aws elbv2 create-load-balancer \
  --name jobquest-prod-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx \
  --scheme internet-facing \
  --type application

# 创建目标组
aws elbv2 create-target-group \
  --name jobquest-backend-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxx \
  --target-type ip \
  --health-check-path /health/ \
  --health-check-interval-seconds 30 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 5

# 创建监听器
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-west-2:[ACCOUNT]:loadbalancer/app/jobquest-prod-alb/xxx \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:us-west-2:[ACCOUNT]:certificate/xxx \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-west-2:[ACCOUNT]:targetgroup/jobquest-backend-tg/xxx
```

#### 4.2 SSL证书配置
```bash
# 请求SSL证书
aws acm request-certificate \
  --domain-name api.jobquest.com \
  --subject-alternative-names "*.jobquest.com" \
  --validation-method DNS
```

### Phase 5: 前端部署 (CloudFront + S3)

#### 5.1 S3静态网站托管
```bash
# 创建S3存储桶
aws s3 mb s3://jobquest-frontend-prod

# 配置静态网站托管
aws s3 website s3://jobquest-frontend-prod \
  --index-document index.html \
  --error-document error.html

# 上传构建的React应用
npm run build
aws s3 sync build/ s3://jobquest-frontend-prod/ --delete
```

#### 5.2 CloudFront配置
```yaml
{
  "CallerReference": "jobquest-frontend-2025",
  "Comment": "JobQuest Navigator Frontend Distribution",
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-jobquest-frontend-prod",
    "ViewerProtocolPolicy": "redirect-to-https",
    "TrustedSigners": {
      "Enabled": false,
      "Quantity": 0
    },
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {"Forward": "none"}
    },
    "MinTTL": 0,
    "DefaultTTL": 86400,
    "MaxTTL": 31536000
  },
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-jobquest-frontend-prod",
        "DomainName": "jobquest-frontend-prod.s3.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        }
      }
    ]
  },
  "Enabled": true,
  "Aliases": {
    "Quantity": 1,
    "Items": ["jobquest.com"]
  },
  "ViewerCertificate": {
    "ACMCertificateArn": "arn:aws:acm:us-east-1:[ACCOUNT]:certificate/xxx",
    "SSLSupportMethod": "sni-only"
  }
}
```

### Phase 6: 环境变量和密钥管理

#### 6.1 AWS Secrets Manager
```bash
# 存储敏感信息
aws secretsmanager create-secret \
  --name "jobquest/django-secret" \
  --description "Django Secret Key" \
  --secret-string "your-super-secret-django-key"

aws secretsmanager create-secret \
  --name "jobquest/openai-key" \
  --description "OpenAI API Key" \
  --secret-string "sk-your-openai-api-key"

aws secretsmanager create-secret \
  --name "jobquest/database-credentials" \
  --description "Database credentials" \
  --secret-string '{"username":"admin","password":"your-db-password"}'
```

#### 6.2 环境变量配置
```yaml
# ECS任务定义中的环境变量
environment:
  - name: "DEBUG"
    value: "False"
  - name: "ALLOWED_HOSTS"
    value: "api.jobquest.com,jobquest.com"
  - name: "AWS_DEFAULT_REGION"
    value: "us-west-2"
  - name: "AWS_STORAGE_BUCKET_NAME"
    value: "jobquest-media-prod"
  - name: "DATABASE_URL"
    value: "mysql://admin:[PASSWORD]@[RDS_ENDPOINT]:3306/jobquest"
  - name: "REDIS_URL"
    value: "redis://[ELASTICACHE_ENDPOINT]:6379/0"
  - name: "EMAIL_BACKEND"
    value: "django_ses.SESBackend"
  - name: "AWS_SES_REGION_NAME"
    value: "us-west-2"
```

### Phase 7: 监控和日志

#### 7.1 CloudWatch配置
```bash
# 创建日志组
aws logs create-log-group --log-group-name /ecs/jobquest-backend
aws logs create-log-group --log-group-name /ecs/jobquest-frontend

# CloudWatch Dashboard
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ECS", "CPUUtilization", "ServiceName", "jobquest-backend-service"],
          [".", "MemoryUtilization", ".", "."]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-west-2",
        "title": "ECS Service Metrics"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "jobquest-prod-db"],
          [".", "DatabaseConnections", ".", "."]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-west-2",
        "title": "Database Metrics"
      }
    }
  ]
}
```

#### 7.2 报警配置
```bash
# CPU使用率报警
aws cloudwatch put-metric-alarm \
  --alarm-name "jobquest-backend-high-cpu" \
  --alarm-description "High CPU utilization on backend service" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2

# 数据库连接报警
aws cloudwatch put-metric-alarm \
  --alarm-name "jobquest-db-high-connections" \
  --alarm-description "High database connections" \
  --metric-name DatabaseConnections \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --threshold 40 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

---

## 🔒 安全最佳实践

### IAM角色和策略
```yaml
# ECS任务执行角色
ECSTaskExecutionRole:
  policies:
    - AmazonECSTaskExecutionRolePolicy
    - SecretsManagerReadWrite
    - CloudWatchLogsFullAccess

# ECS任务角色  
ECSTaskRole:
  policies:
    - S3FullAccess (限制到特定bucket)
    - SESFullAccess
    - CloudWatchMetricsFullAccess
```

### 网络安全
- VPC内私有子网部署应用
- NAT Gateway提供出站internet访问
- 安全组严格限制端口和来源
- WAF保护CloudFront分发

### 数据安全
- RDS加密存储
- S3存储桶加密
- Secrets Manager管理敏感信息
- SSL/TLS端到端加密

---

## 🚀 CI/CD Pipeline

### CodePipeline配置
```yaml
Source:
  Provider: GitHub
  Repository: jobquest-navigator
  Branch: main

Build:
  Provider: CodeBuild
  BuildSpec:
    - Install dependencies
    - Run tests
    - Build Docker images
    - Push to ECR

Deploy:
  Provider: ECS
  Cluster: jobquest-prod-cluster
  Service: jobquest-backend-service
```

### 部署脚本
```bash
#!/bin/bash
# deploy.sh

# 构建新镜像
docker build -t jobquest/backend:$BUILD_NUMBER .

# 推送到ECR
docker tag jobquest/backend:$BUILD_NUMBER $ECR_REPO/jobquest/backend:$BUILD_NUMBER
docker push $ECR_REPO/jobquest/backend:$BUILD_NUMBER

# 更新ECS服务
aws ecs update-service \
  --cluster jobquest-prod-cluster \
  --service jobquest-backend-service \
  --force-new-deployment
```

---

## 📊 性能优化

### 数据库优化
- RDS性能洞察启用
- 读副本配置（高流量时）
- 连接池配置
- 索引优化

### 缓存策略
- Redis集群模式（扩展时）
- CloudFront CDN配置
- Django缓存框架
- 数据库查询缓存

### 应用优化
- ECS自动扩展
- ALB健康检查优化
- 容器资源限制
- 异步任务处理（Celery + SQS）

---

## 💡 部署检查清单

### 部署前检查
- [ ] 所有环境变量配置正确
- [ ] 数据库迁移脚本准备
- [ ] SSL证书验证完成
- [ ] IAM权限配置正确
- [ ] 监控和报警设置
- [ ] 备份策略配置

### 部署后验证
- [ ] 健康检查端点响应正常
- [ ] 数据库连接成功
- [ ] Redis缓存工作正常
- [ ] S3文件上传功能
- [ ] 邮件发送功能
- [ ] API端点功能测试
- [ ] 前端页面加载正常
- [ ] SSL证书有效
- [ ] 监控数据收集正常

---

## 🆘 故障排除

### 常见问题
1. **ECS任务启动失败**
   - 检查任务定义配置
   - 验证IAM权限
   - 查看CloudWatch日志

2. **数据库连接问题**
   - 检查安全组规则
   - 验证连接字符串
   - 确认RDS状态

3. **静态文件加载失败**
   - 检查S3权限
   - 验证CloudFront配置
   - 确认CORS设置

### 监控指标
- ECS服务CPU/内存使用率
- RDS连接数和性能
- ALB响应时间和错误率
- CloudFront缓存命中率

---

## 📝 总结

这个部署方案提供了：
1. **高可用性**: 多AZ部署，自动故障转移
2. **可扩展性**: ECS Fargate自动扩展
3. **安全性**: VPC、IAM、加密存储
4. **成本效益**: 按需付费，优化资源使用
5. **易维护**: CloudWatch监控，自动化部署

总月度成本约$249-$1,188，具体取决于流量和使用情况。

这个架构适合从初创到中等规模的应用，并且可以随着业务增长轻松扩展。