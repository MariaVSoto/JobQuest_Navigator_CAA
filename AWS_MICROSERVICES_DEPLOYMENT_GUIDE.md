# 🚀 JobQuest Navigator - AWS微服务架构部署指南

## 📋 部署概览

基于 `microservices-architecture-diagram.md` 的设计，本指南详细说明如何在AWS上部署JobQuest Navigator的微服务架构，包括9个核心微服务的独立部署和管理。

---

## 🏗️ 微服务架构设计

### 架构全景图
```
┌─────────────────────────────────────────────────────────────────┐
│                         API Gateway (ALB)                       │
│                    + WAF + CloudFront                          │
└─────────────────────────┬───────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼─────┐ ┌────────▼─────┐ ┌───────▼─────┐
│   Core       │ │ Supporting    │ │   External   │
│ Microservices │ │ Microservices │ │   Services   │
└──────────────┘ └──────────────┘ └─────────────┘
```

### 微服务映射到AWS ECS服务

#### 🔴 核心微服务 (6个)
1. **Auth Service** → `auth-service`
2. **User Profile Service** → `user-service` 
3. **Job Data Service** → `job-service`
4. **Resume Management Service** → `resume-service`
5. **AI Suggestion Service** → `ai-service`
6. **Application Tracking Service** → `application-service`

#### 🟡 支撑微服务 (3个)
7. **Certification Service** → `certification-service`
8. **Notification Service** → `notification-service`
9. **Interview Prep Service** → `interview-service`

---

## 🛠️ 微服务拆分策略

### 当前代码结构 → 微服务映射

```yaml
# 从Django Apps到微服务的映射
Django Apps          →  Microservices
─────────────────────────────────────────
core/               →  auth-service + user-service
jobs/               →  job-service
resumes/            →  resume-service  
ai_suggestions/     →  ai-service
application_tracking/ →  application-service
skills/             →  certification-service
company_research/   →  interview-service
                    →  notification-service (新增)
```

### 数据库分离策略
```yaml
Microservice           Database        Tables
─────────────────────────────────────────────────
auth-service          auth-db         users, sessions, tokens
user-service          user-db         profiles, preferences
job-service           job-db          jobs, companies, locations
resume-service        resume-db       resumes, versions, templates
ai-service            ai-db           suggestions, recommendations
application-service   app-db          applications, tracking
certification-service cert-db         skills, certifications
notification-service  notif-db        notifications, settings
interview-service     interview-db    company_research, interviews
```

---

## 🎯 AWS服务架构

### 整体架构
```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   CloudFront    │    │   ALB + WAF  │    │  ECS Cluster    │
│   (CDN + SSL)   │───▶│(API Gateway) │───▶│  (9 Services)   │
└─────────────────┘    └──────────────┘    └─────────────────┘
                              │                      │
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│       S3        │    │   RDS Cluster│    │  ElastiCache    │
│  (Static Files) │    │ (Multi-DB)   │    │    (Redis)      │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

### 服务通信
```yaml
通信模式:
  同步: REST API (服务间直接调用)
  异步: SQS + SNS (事件驱动)
  缓存: Redis (ElastiCache)
  文件: S3 (共享存储)
```

---

## 💰 成本估算 (微服务架构)

### 生产环境成本 (月度)
```yaml
服务类型              配置                     数量    月度成本(USD)
──────────────────────────────────────────────────────────────
ECS Fargate:
  Core Services       1 vCPU, 2GB RAM         6      ~$180
  Supporting Services 0.5 vCPU, 1GB RAM       3      ~$90
  
数据库:
  RDS Aurora MySQL    db.t3.small (Multi-AZ)  1      ~$60
  Read Replicas       db.t3.small             2      ~$60
  
缓存:
  ElastiCache Redis   cache.t3.small          1      ~$30
  
网络:
  ALB                 标准负载均衡器           1      ~$23
  NAT Gateway         数据传输                1      ~$45
  
存储:
  S3                  100GB + 传输           1      ~$15
  CloudFront          10TB传输               1      ~$850
  
队列:
  SQS                 100万消息              多个    ~$5
  SNS                 100万通知              1      ~$2
  
监控:
  CloudWatch          详细监控               全部    ~$30
  X-Ray               分布式追踪             全部    ~$20
──────────────────────────────────────────────────────────────
总计                                                ~$1,410/月
```

---

## 🔧 详细部署实施

### Phase 1: 基础设施和网络

#### 1.1 VPC和微服务网络
```yaml
# VPC设计 - 微服务专用
VPC CIDR: 10.0.0.0/16

Subnets:
  # 公有子网 (ALB, NAT)
  public-1a:  10.0.1.0/24
  public-1b:  10.0.2.0/24
  
  # 私有子网 (微服务)
  private-1a: 10.0.10.0/24  # Core Services
  private-1b: 10.0.20.0/24  # Supporting Services
  
  # 数据库子网
  db-1a:      10.0.100.0/24
  db-1b:      10.0.200.0/24
```

#### 1.2 安全组设计
```yaml
# API Gateway ALB
alb-sg:
  入站: [80, 443] from 0.0.0.0/0
  出站: [8000-8009] to microservices-sg

# 微服务集群
microservices-sg:
  入站: [8000-8009] from alb-sg
  入站: [8000-8009] from microservices-sg  # 服务间通信
  出站: 全部 to 0.0.0.0/0

# 数据库集群
database-sg:
  入站: [3306] from microservices-sg
  
# Redis缓存
redis-sg:
  入站: [6379] from microservices-sg
```

### Phase 2: 数据库架构

#### 2.1 Aurora MySQL集群配置
```bash
# 主数据库集群 (Multi-Master)
aws rds create-db-cluster \
  --db-cluster-identifier jobquest-main-cluster \
  --engine aurora-mysql \
  --engine-version 8.0.mysql_aurora.3.05.2 \
  --master-username admin \
  --master-user-password [SECURE_PASSWORD] \
  --database-name jobquest_main \
  --db-subnet-group-name jobquest-db-subnet-group \
  --vpc-security-group-ids sg-xxx \
  --backup-retention-period 7 \
  --storage-encrypted \
  --enable-cloudwatch-logs-exports error,general,slow-query

# 为每个微服务创建独立数据库
databases=("auth" "user" "job" "resume" "ai" "application" "certification" "notification" "interview")

for db in "${databases[@]}"; do
  aws rds create-db-instance \
    --db-instance-identifier "jobquest-${db}-db" \
    --db-cluster-identifier jobquest-main-cluster \
    --db-instance-class db.t3.small \
    --engine aurora-mysql
done
```

#### 2.2 数据库初始化脚本
```sql
-- 创建微服务数据库
CREATE DATABASE jobquest_auth;
CREATE DATABASE jobquest_user; 
CREATE DATABASE jobquest_job;
CREATE DATABASE jobquest_resume;
CREATE DATABASE jobquest_ai;
CREATE DATABASE jobquest_application;
CREATE DATABASE jobquest_certification;
CREATE DATABASE jobquest_notification;
CREATE DATABASE jobquest_interview;

-- 创建服务用户
CREATE USER 'auth_service'@'%' IDENTIFIED BY 'auth_password';
CREATE USER 'user_service'@'%' IDENTIFIED BY 'user_password';
-- ... 为每个服务创建用户

-- 分配权限
GRANT ALL PRIVILEGES ON jobquest_auth.* TO 'auth_service'@'%';
GRANT ALL PRIVILEGES ON jobquest_user.* TO 'user_service'@'%';
-- ... 为每个服务分配对应权限
```

### Phase 3: 微服务容器化

#### 3.1 通用微服务Dockerfile模板
```dockerfile
# 基础镜像
FROM python:3.9-slim as base

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc default-libmysqlclient-dev pkg-config curl \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制服务代码
COPY . .

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${SERVICE_PORT}/health/ || exit 1

# 启动命令 (由docker-compose或ECS任务定义指定)
CMD ["gunicorn", "--bind", "0.0.0.0:${SERVICE_PORT}", "--workers", "2", "wsgi:application"]
```

#### 3.2 服务拆分脚本
```bash
#!/bin/bash
# extract_microservices.sh

# 从Django monolith拆分微服务
services=(
  "auth-service:core/auth,core/models.User"
  "user-service:core/models.UserProfile,core/views.User*"
  "job-service:jobs"
  "resume-service:resumes"
  "ai-service:ai_suggestions"
  "application-service:application_tracking"
  "certification-service:skills"
  "notification-service:core/notifications"
  "interview-service:company_research"
)

for service_config in "${services[@]}"; do
  IFS=':' read -r service_name source_paths <<< "$service_config"
  
  echo "Creating microservice: $service_name"
  mkdir -p "microservices/$service_name"
  
  # 复制相关代码
  for path in $(echo $source_paths | tr ',' '\n'); do
    if [ -d "$path" ]; then
      cp -r "$path" "microservices/$service_name/"
    fi
  done
  
  # 创建微服务特定的配置
  cat > "microservices/$service_name/settings.py" << EOF
from core.settings import *

# 微服务特定配置
SERVICE_NAME = '$service_name'
SERVICE_PORT = ${port}

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jobquest_${service_name//-/_}',
        'USER': '${service_name//-/_}_service',
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ['DB_HOST'],
        'PORT': '3306',
    }
}

# 微服务间通信
MICROSERVICES = {
    'auth-service': 'http://auth-service:8001',
    'user-service': 'http://user-service:8002',
    'job-service': 'http://job-service:8003',
    'resume-service': 'http://resume-service:8004',
    'ai-service': 'http://ai-service:8005',
    'application-service': 'http://application-service:8006',
    'certification-service': 'http://certification-service:8007',
    'notification-service': 'http://notification-service:8008',
    'interview-service': 'http://interview-service:8009',
}
EOF

  # 创建Docker配置
  cat > "microservices/$service_name/Dockerfile" << EOF
FROM jobquest/base-service:latest

ENV SERVICE_NAME=$service_name
ENV SERVICE_PORT=$((8000 + ${#services[@]}))

COPY . .

EXPOSE \$SERVICE_PORT
EOF

  port=$((port + 1))
done
```

### Phase 4: ECS集群和服务部署

#### 4.1 ECS集群配置
```bash
# 创建ECS集群
aws ecs create-cluster \
  --cluster-name jobquest-microservices \
  --capacity-providers FARGATE \
  --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1
```

#### 4.2 微服务任务定义模板
```json
{
  "family": "jobquest-${SERVICE_NAME}",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "${SERVICE_NAME}",
      "image": "ACCOUNT.dkr.ecr.us-west-2.amazonaws.com/jobquest/${SERVICE_NAME}:latest",
      "portMappings": [
        {
          "containerPort": "${SERVICE_PORT}",
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "SERVICE_NAME",
          "value": "${SERVICE_NAME}"
        },
        {
          "name": "SERVICE_PORT", 
          "value": "${SERVICE_PORT}"
        },
        {
          "name": "DB_HOST",
          "value": "${RDS_ENDPOINT}"
        }
      ],
      "secrets": [
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-west-2:ACCOUNT:secret:jobquest/${SERVICE_NAME}-db"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/jobquest-${SERVICE_NAME}",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:${SERVICE_PORT}/health/ || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

#### 4.3 批量服务部署脚本
```bash
#!/bin/bash
# deploy_microservices.sh

services=(
  "auth-service:8001"
  "user-service:8002" 
  "job-service:8003"
  "resume-service:8004"
  "ai-service:8005"
  "application-service:8006"
  "certification-service:8007"
  "notification-service:8008"
  "interview-service:8009"
)

for service_config in "${services[@]}"; do
  IFS=':' read -r service_name service_port <<< "$service_config"
  
  echo "Deploying $service_name on port $service_port"
  
  # 1. 构建和推送镜像
  cd "microservices/$service_name"
  
  docker build -t "jobquest/$service_name:latest" .
  docker tag "jobquest/$service_name:latest" "$ECR_REPO/jobquest/$service_name:latest"
  docker push "$ECR_REPO/jobquest/$service_name:latest"
  
  # 2. 创建任务定义
  envsubst < ../../task-definition-template.json > "task-definition-$service_name.json"
  aws ecs register-task-definition --cli-input-json "file://task-definition-$service_name.json"
  
  # 3. 创建ECS服务
  aws ecs create-service \
    --cluster jobquest-microservices \
    --service-name "$service_name" \
    --task-definition "jobquest-$service_name" \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=DISABLED}" \
    --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-west-2:ACCOUNT:targetgroup/$service_name-tg/xxx,containerName=$service_name,containerPort=$service_port"
  
  cd ../..
done
```

### Phase 5: API Gateway和路由

#### 5.1 Application Load Balancer配置
```bash
# 创建主ALB
aws elbv2 create-load-balancer \
  --name jobquest-microservices-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx \
  --scheme internet-facing

# 为每个微服务创建目标组和路由规则
services=(
  "auth-service:8001:/api/auth/*"
  "user-service:8002:/api/user/*"
  "job-service:8003:/api/jobs/*"
  "resume-service:8004:/api/resumes/*"
  "ai-service:8005:/api/ai-suggestions/*"
  "application-service:8006:/api/application-tracking/*"
  "certification-service:8007:/api/skills/*"
  "notification-service:8008:/api/notifications/*"
  "interview-service:8009:/api/company-research/*"
)

for service_config in "${services[@]}"; do
  IFS=':' read -r service_name service_port path_pattern <<< "$service_config"
  
  # 创建目标组
  aws elbv2 create-target-group \
    --name "$service_name-tg" \
    --protocol HTTP \
    --port "$service_port" \
    --vpc-id vpc-xxx \
    --target-type ip \
    --health-check-path "/health/" \
    --health-check-interval-seconds 30
  
  # 创建路由规则
  aws elbv2 create-rule \
    --listener-arn "arn:aws:elasticloadbalancing:us-west-2:ACCOUNT:listener/app/jobquest-microservices-alb/xxx" \
    --priority $((10 + service_index)) \
    --conditions "Field=path-pattern,Values=$path_pattern" \
    --actions "Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-west-2:ACCOUNT:targetgroup/$service_name-tg/xxx"
done
```

### Phase 6: 服务间通信

#### 6.1 服务发现配置
```python
# common/service_client.py - 微服务通信客户端
import requests
import os
from typing import Dict, Any
import jwt

class MicroserviceClient:
    def __init__(self):
        self.services = {
            'auth': os.environ.get('AUTH_SERVICE_URL', 'http://auth-service:8001'),
            'user': os.environ.get('USER_SERVICE_URL', 'http://user-service:8002'),
            'job': os.environ.get('JOB_SERVICE_URL', 'http://job-service:8003'),
            'resume': os.environ.get('RESUME_SERVICE_URL', 'http://resume-service:8004'),
            'ai': os.environ.get('AI_SERVICE_URL', 'http://ai-service:8005'),
            'application': os.environ.get('APP_SERVICE_URL', 'http://application-service:8006'),
            'certification': os.environ.get('CERT_SERVICE_URL', 'http://certification-service:8007'),
            'notification': os.environ.get('NOTIF_SERVICE_URL', 'http://notification-service:8008'),
            'interview': os.environ.get('INTERVIEW_SERVICE_URL', 'http://interview-service:8009'),
        }
        self.service_token = os.environ.get('MICROSERVICE_JWT_SECRET')
    
    def call_service(self, service: str, endpoint: str, method: str = 'GET', 
                    data: Dict = None, user_token: str = None) -> Dict[Any, Any]:
        """调用其他微服务"""
        url = f"{self.services[service]}{endpoint}"
        
        headers = {
            'Content-Type': 'application/json',
            'X-Service-Token': self._generate_service_token(),
        }
        
        if user_token:
            headers['Authorization'] = f'Bearer {user_token}'
        
        try:
            response = requests.request(method, url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ServiceCommunicationError(f"Failed to call {service}: {str(e)}")
    
    def _generate_service_token(self) -> str:
        """生成服务间通信token"""
        payload = {
            'service': os.environ.get('SERVICE_NAME'),
            'iat': int(time.time()),
            'exp': int(time.time()) + 300  # 5分钟过期
        }
        return jwt.encode(payload, self.service_token, algorithm='HS256')

# 使用示例
client = MicroserviceClient()

# 在resume-service中调用ai-service
def get_resume_suggestions(resume_id: str, user_token: str):
    return client.call_service(
        service='ai',
        endpoint=f'/suggestions/resume/{resume_id}',
        method='POST',
        user_token=user_token
    )
```

#### 6.2 异步消息队列
```yaml
# SQS队列配置
队列:
  job-events:           # 职位相关事件
    - job.created
    - job.updated
    - job.deleted
    
  resume-events:        # 简历相关事件  
    - resume.created
    - resume.version.created
    - resume.shared
    
  application-events:   # 申请相关事件
    - application.created
    - application.status.changed
    - application.interview.scheduled
    
  notification-queue:   # 通知队列
    - notification.email
    - notification.push
    - notification.sms

# 事件处理模式
生产者 -> SQS -> Lambda/ECS -> 消费者服务
```

### Phase 7: 监控和可观测性

#### 7.1 分布式追踪 (X-Ray)
```python
# common/tracing.py
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# 自动追踪AWS服务调用
patch_all()

@xray_recorder.capture('microservice_call')
def call_microservice(service_name: str, endpoint: str):
    subsegment = xray_recorder.current_subsegment()
    subsegment.put_metadata('service', service_name)
    subsegment.put_metadata('endpoint', endpoint)
    
    # 微服务调用
    result = client.call_service(service_name, endpoint)
    
    subsegment.put_metadata('response_size', len(str(result)))
    return result
```

#### 7.2 微服务健康检查
```python
# common/health.py
from django.http import JsonResponse
from django.views import View
import time
import psutil

class HealthCheckView(View):
    def get(self, request):
        """标准化健康检查端点"""
        start_time = time.time()
        
        health_data = {
            'service': os.environ.get('SERVICE_NAME'),
            'status': 'healthy',
            'timestamp': time.time(),
            'version': os.environ.get('SERVICE_VERSION', '1.0.0'),
            'checks': {}
        }
        
        # 数据库检查
        try:
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            health_data['checks']['database'] = 'healthy'
        except Exception as e:
            health_data['checks']['database'] = f'unhealthy: {str(e)}'
            health_data['status'] = 'unhealthy'
        
        # 依赖服务检查
        for service_name, service_url in self.get_dependencies().items():
            try:
                response = requests.get(f"{service_url}/health/", timeout=5)
                if response.status_code == 200:
                    health_data['checks'][service_name] = 'healthy'
                else:
                    health_data['checks'][service_name] = f'unhealthy: HTTP {response.status_code}'
            except Exception as e:
                health_data['checks'][service_name] = f'unhealthy: {str(e)}'
        
        # 资源使用情况
        health_data['metrics'] = {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'response_time_ms': round((time.time() - start_time) * 1000, 2)
        }
        
        status_code = 200 if health_data['status'] == 'healthy' else 503
        return JsonResponse(health_data, status=status_code)
    
    def get_dependencies(self):
        """定义服务依赖关系"""
        service_dependencies = {
            'auth-service': [],
            'user-service': ['auth-service'],
            'job-service': ['auth-service'],
            'resume-service': ['auth-service', 'user-service'],
            'ai-service': ['auth-service', 'resume-service'],
            'application-service': ['auth-service', 'resume-service', 'job-service'],
            'certification-service': ['auth-service', 'user-service'],
            'notification-service': ['auth-service'],
            'interview-service': ['auth-service', 'job-service']
        }
        
        current_service = os.environ.get('SERVICE_NAME')
        dependencies = service_dependencies.get(current_service, [])
        
        return {
            dep: f"http://{dep}:800{i+1}" 
            for i, dep in enumerate(dependencies)
        }
```

### Phase 8: 部署和CI/CD

#### 8.1 CodePipeline配置
```yaml
# buildspec.yml for microservices
version: 0.2

phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
      
  build:
    commands:
      - echo Build started on `date`
      
      # 检测变更的微服务
      - |
        if [ "$CODEBUILD_WEBHOOK_HEAD_REF" ]; then
          CHANGED_SERVICES=$(git diff --name-only $CODEBUILD_RESOLVED_SOURCE_VERSION~1 $CODEBUILD_RESOLVED_SOURCE_VERSION | grep "microservices/" | cut -d'/' -f2 | sort -u)
        else
          CHANGED_SERVICES="auth-service user-service job-service resume-service ai-service application-service certification-service notification-service interview-service"
        fi
      
      # 构建变更的服务
      - |
        for service in $CHANGED_SERVICES; do
          echo "Building $service..."
          cd microservices/$service
          
          # 构建镜像
          docker build -t $service:$CODEBUILD_BUILD_NUMBER .
          docker tag $service:$CODEBUILD_BUILD_NUMBER $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/jobquest/$service:$CODEBUILD_BUILD_NUMBER
          docker tag $service:$CODEBUILD_BUILD_NUMBER $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/jobquest/$service:latest
          
          # 运行测试
          docker run --rm $service:$CODEBUILD_BUILD_NUMBER python -m pytest tests/ -v
          
          cd ../..
        done
  
  post_build:
    commands:
      - echo Build completed on `date`
      
      # 推送镜像
      - |
        for service in $CHANGED_SERVICES; do
          echo "Pushing $service..."
          docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/jobquest/$service:$CODEBUILD_BUILD_NUMBER
          docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/jobquest/$service:latest
          
          # 更新ECS服务
          aws ecs update-service --cluster jobquest-microservices --service $service --force-new-deployment
        done
```

---

## 🔒 安全和最佳实践

### 微服务安全
```yaml
认证授权:
  外部请求: JWT (用户认证)
  服务间: 内部JWT + mTLS
  
网络安全:
  VPC: 私有子网部署
  Security Groups: 最小权限原则
  WAF: API保护和DDoS防护
  
数据安全:
  数据库: 传输和存储加密
  密钥管理: AWS Secrets Manager
  日志: CloudWatch加密存储
```

### 容错和可靠性
```yaml
Circuit Breaker: 防止级联故障
Retry Logic: 指数退避重试
Timeout: 合理的超时设置
Health Checks: 定期健康检查
Auto Scaling: 基于CPU/内存自动扩展
```

---

## 📊 运维监控

### 关键指标监控
```yaml
服务级别:
  - 响应时间 (P50, P95, P99)
  - 错误率和成功率
  - 吞吐量 (RPS)
  - CPU和内存使用率

业务级别:
  - 用户注册率
  - 简历创建和更新频率
  - AI建议使用率
  - 申请跟踪活跃度

基础设施级别:
  - ECS服务健康状态
  - 数据库连接和性能
  - 负载均衡器指标
  - 网络延迟和丢包
```

### 告警配置
```bash
# 关键服务不可用告警
aws cloudwatch put-metric-alarm \
  --alarm-name "auth-service-unavailable" \
  --alarm-description "Auth service health check failing" \
  --metric-name UnHealthyHostCount \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 60 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --evaluation-periods 2

# 高延迟告警
aws cloudwatch put-metric-alarm \
  --alarm-name "api-high-latency" \
  --alarm-description "API response time too high" \
  --metric-name TargetResponseTime \
  --namespace AWS/ApplicationELB \
  --statistic Average \
  --period 300 \
  --threshold 2.0 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

---

## 🚀 部署检查清单

### 微服务部署前检查
- [ ] 所有微服务容器构建成功
- [ ] 数据库分离和迁移完成
- [ ] 服务间通信配置正确
- [ ] 环境变量和密钥配置
- [ ] 健康检查端点响应正常
- [ ] 负载均衡器路由配置
- [ ] 监控和日志配置

### 部署后验证
- [ ] 所有9个微服务运行正常
- [ ] API Gateway路由正确
- [ ] 服务间调用成功
- [ ] 数据库连接正常
- [ ] 消息队列工作正常
- [ ] 分布式追踪数据收集
- [ ] 告警和监控正常

---

## 📝 总结

这个微服务架构提供了：

1. **高度模块化**: 9个独立微服务，各自负责特定领域
2. **独立扩展**: 每个服务可根据负载独立扩展
3. **技术多样性**: 各服务可选择最适合的技术栈
4. **故障隔离**: 单个服务故障不影响其他服务
5. **团队独立**: 各团队可独立开发和部署服务

**月度成本约$1,410**，比单体架构高约20%，但提供了更好的可扩展性、可维护性和团队协作效率。

这个架构完全符合您的`microservices-architecture-diagram.md`设计，适合中型到大型团队开发和维护。