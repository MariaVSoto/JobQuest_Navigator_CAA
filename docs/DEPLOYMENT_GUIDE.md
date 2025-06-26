# JobQuest Navigator - AWS部署操作手册

## 📋 概述

本文档提供JobQuest Navigator项目在AWS上的完整部署指南，包括基础设施搭建、应用部署和配置说明。

**目标环境**: AWS Production Environment  
**部署架构**: Serverless (Lambda + API Gateway + RDS + S3)  
**预计部署时间**: 30-45分钟

---

## 🔧 前置要求

### 必需工具
- **AWS CLI** (版本 2.x)
- **Python 3.9+**
- **Node.js 18+**
- **Docker** (用于本地测试)
- **Git**

### AWS账户准备
- 有效的AWS账户
- 管理员权限或适当的IAM权限
- 预算设置 (建议月预算 $30)

### 环境检查
```bash
# 验证工具安装
aws --version
python --version
node --version
docker --version

# 验证AWS配置
aws sts get-caller-identity
```

---

## 🚀 快速部署步骤

### 步骤1: 克隆和准备代码

```bash
# 1. 克隆prod目录到本地
git clone <repository-url>
cd JobQuest_Navigator_CAA/prod

# 2. 设置环境变量
cp configs/environment.env .env
# 编辑 .env 文件，填入实际的AWS配置
```

### 步骤2: 基础设施部署

```bash
# 1. 部署CloudFormation堆栈
cd infrastructure
aws cloudformation create-stack \
  --stack-name jobquest-navigator-infra \
  --template-body file://cloudformation-template.yaml \
  --parameters ParameterKey=DatabasePassword,ParameterValue=YourSecurePassword123! \
               ParameterKey=AlertEmail,ParameterValue=your-email@domain.com \
  --capabilities CAPABILITY_IAM

# 2. 等待堆栈创建完成
aws cloudformation wait stack-create-complete \
  --stack-name jobquest-navigator-infra

# 3. 获取输出值
aws cloudformation describe-stacks \
  --stack-name jobquest-navigator-infra \
  --query 'Stacks[0].Outputs'
```

### 步骤3: 后端部署

```bash
# 1. 进入后端目录
cd ../backend

# 2. 安装依赖
pip install -r requirements.txt

# 3. 数据库迁移
python manage.py migrate --settings=core.settings_production

# 4. 收集静态文件
python manage.py collectstatic --noinput --settings=core.settings_production

# 5. 使用部署脚本
cd ../scripts
bash deploy-backend.sh
```

### 步骤4: 前端部署

```bash
# 1. 进入前端目录
cd ../frontend

# 2. 安装依赖并构建
npm install
npm run build

# 3. 部署到S3
cd ../scripts
bash deploy-frontend.sh
```

### 步骤5: 验证部署

```bash
# 运行部署验证脚本
cd ../scripts
bash verify-deployment.sh
```

---

## 📂 详细部署说明

### 基础设施组件

#### 1. CloudFormation堆栈部署

**创建的资源**:
- VPC和子网 (网络基础设施)
- RDS MySQL数据库 (db.t3.micro)
- S3存储桶 (前端、静态文件、Lambda代码)
- IAM角色和策略
- 安全组配置
- CloudWatch告警

**重要参数**:
```yaml
Parameters:
  DatabasePassword: 数据库密码 (最少8个字符)
  AlertEmail: 告警邮箱地址
  ProjectName: 项目名称 (默认: jobquest-navigator)
  Environment: 环境名称 (默认: production)
```

#### 2. 数据库配置

**连接信息获取**:
```bash
# 获取RDS端点
aws cloudformation describe-stacks \
  --stack-name jobquest-navigator-infra \
  --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' \
  --output text
```

**数据库初始化**:
```bash
# 连接数据库并创建表
python manage.py migrate --settings=core.settings_production

# 创建超级用户 (可选)
python manage.py createsuperuser --settings=core.settings_production

# 加载示例数据 (开发环境)
python manage.py loaddata fixtures/sample_data.json
```

### 应用部署

#### 1. 后端Lambda部署

**Zappa配置文件** (`zappa_settings.json`):
```json
{
  "production": {
    "app_function": "core.wsgi.application",
    "aws_region": "us-east-1",
    "runtime": "python3.9",
    "timeout_seconds": 300,
    "memory_size": 512,
    "keep_warm": false,
    "environment_variables": {
      "DJANGO_SETTINGS_MODULE": "core.settings_production"
    }
  }
}
```

**部署命令**:
```bash
# 安装Zappa
pip install zappa

# 首次部署
zappa deploy production

# 更新部署
zappa update production

# 设置环境变量
zappa set_env production DATABASE_URL "mysql://admin:password@endpoint/dbname"
```

#### 2. 前端S3部署

**构建配置**:
```bash
# 设置API端点
echo "REACT_APP_API_URL=https://api-gateway-url.amazonaws.com/prod" > .env.production

# 构建生产版本
npm run build

# 部署到S3
aws s3 sync build/ s3://jobquest-navigator-frontend-production \
  --delete --cache-control max-age=31536000
```

**S3网站配置**:
```bash
# 启用静态网站托管
aws s3 website s3://jobquest-navigator-frontend-production \
  --index-document index.html \
  --error-document index.html
```

---

## 🔧 配置管理

### 环境变量配置

**Django生产设置**:
```python
# core/settings_production.py
import os
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['your-api-gateway-url.amazonaws.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ['RDS_DB_NAME'],
        'USER': os.environ['RDS_USERNAME'],
        'PASSWORD': os.environ['RDS_PASSWORD'],
        'HOST': os.environ['RDS_HOSTNAME'],
        'PORT': os.environ['RDS_PORT'],
    }
}

# S3配置
AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
AWS_S3_REGION_NAME = os.environ['AWS_S3_REGION_NAME']
```

**Lambda环境变量**:
```bash
zappa set_env production RDS_HOSTNAME your-db-endpoint.amazonaws.com
zappa set_env production RDS_DB_NAME jobquest_navigator
zappa set_env production RDS_USERNAME admin
zappa set_env production RDS_PASSWORD your-secure-password
zappa set_env production AWS_STORAGE_BUCKET_NAME jobquest-navigator-static-production
```

### CORS配置

**Django CORS设置**:
```python
CORS_ALLOWED_ORIGINS = [
    "https://jobquest-navigator-frontend-production.s3-website-us-east-1.amazonaws.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://jobquest-navigator-frontend-production.s3-website-us-east-1.amazonaws.com",
]
```

**S3 CORS配置**:
```json
{
  "CORSRules": [
    {
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
      "AllowedOrigins": ["*"],
      "MaxAgeSeconds": 3600
    }
  ]
}
```

---

## 🔍 验证和测试

### 部署验证清单

#### 基础设施验证
- [ ] CloudFormation堆栈状态: CREATE_COMPLETE
- [ ] RDS实例状态: available
- [ ] S3存储桶创建成功
- [ ] IAM角色和策略正确配置

#### 应用验证
- [ ] Lambda函数部署成功
- [ ] API Gateway端点响应正常
- [ ] 数据库连接测试通过
- [ ] 静态文件上传成功

#### 功能验证
- [ ] 用户注册和登录
- [ ] 主要API端点测试
- [ ] 前端页面加载正常
- [ ] 文件上传功能正常

### 自动化测试

**API功能测试**:
```bash
# 运行API测试套件
cd tests
python test_api_endpoints.py --env production
```

**端到端测试**:
```bash
# 使用测试脚本验证整个部署
cd scripts
bash run-e2e-tests.sh
```

---

## 🔧 故障排除

### 常见问题和解决方案

#### 1. Lambda部署失败

**问题**: Zappa部署时出现权限错误
```bash
Error: An error occurred (AccessDenied) when calling the CreateFunction operation
```

**解决方案**:
```bash
# 检查IAM权限
aws iam get-user

# 确保有以下权限：
# - lambda:CreateFunction
# - iam:CreateRole
# - apigateway:*
# - s3:*
```

#### 2. 数据库连接失败

**问题**: Lambda无法连接到RDS
```bash
Error: (2003, "Can't connect to MySQL server")
```

**解决方案**:
```bash
# 检查安全组配置
aws ec2 describe-security-groups --group-ids sg-xxxxxxxx

# 确保Lambda安全组可以访问RDS安全组的3306端口
```

#### 3. CORS错误

**问题**: 前端无法访问API
```bash
Access to XMLHttpRequest blocked by CORS policy
```

**解决方案**:
```python
# 更新Django设置
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
]

# 重新部署Lambda
zappa update production
```

#### 4. 静态文件加载失败

**问题**: CSS/JS文件404错误
```bash
GET https://bucket.s3.amazonaws.com/static/css/main.css 404
```

**解决方案**:
```bash
# 重新收集静态文件
python manage.py collectstatic --noinput --settings=core.settings_production

# 检查S3存储桶策略
aws s3api get-bucket-policy --bucket jobquest-navigator-static-production
```

### 日志调试

**Lambda日志查看**:
```bash
# 实时查看Lambda日志
zappa tail production

# 获取特定时间段的日志
aws logs filter-log-events \
  --log-group-name /aws/lambda/jobquest-navigator-api-production \
  --start-time 1640995200000
```

**CloudWatch监控**:
```bash
# 检查CloudWatch指标
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=jobquest-navigator-api-production \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 300 \
  --statistics Average
```

---

## 📊 监控和维护

### 性能监控

**关键指标**:
- Lambda执行时间和内存使用
- API Gateway请求响应时间
- RDS连接数和CPU使用率
- S3存储使用量和请求数

**告警配置**:
```bash
# 创建Lambda错误告警
aws cloudwatch put-metric-alarm \
  --alarm-name "Lambda-Errors-High" \
  --alarm-description "Lambda error rate is too high" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

### 备份策略

**数据库备份**:
```bash
# 创建RDS快照
aws rds create-db-snapshot \
  --db-instance-identifier jobquest-navigator-db \
  --db-snapshot-identifier jobquest-navigator-backup-$(date +%Y%m%d)

# 设置自动备份保留期
aws rds modify-db-instance \
  --db-instance-identifier jobquest-navigator-db \
  --backup-retention-period 7
```

**代码备份**:
```bash
# S3版本控制已启用，Lambda代码自动备份到S3
# 手动备份当前部署
zappa save-python-settings-file production
```

### 更新部署

**应用更新流程**:
```bash
# 1. 拉取最新代码
git pull origin main

# 2. 更新依赖
pip install -r requirements.txt

# 3. 运行数据库迁移
python manage.py migrate --settings=core.settings_production

# 4. 更新Lambda
zappa update production

# 5. 更新前端
npm run build
aws s3 sync build/ s3://jobquest-navigator-frontend-production
```

**回滚策略**:
```bash
# Lambda版本回滚
zappa rollback production -n 1

# RDS时间点恢复
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier jobquest-navigator-db \
  --target-db-instance-identifier jobquest-navigator-db-restored \
  --restore-time 2024-01-01T12:00:00.000Z
```

---

## 💰 成本优化

### 成本监控

**设置账单告警**:
```bash
aws budgets create-budget \
  --account-id 123456789012 \
  --budget '{
    "BudgetName": "JobQuest Navigator Monthly Budget",
    "BudgetLimit": {
      "Amount": "30",
      "Unit": "USD"
    },
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }'
```

### 优化建议

1. **Lambda优化**:
   - 调整内存大小以优化执行时间
   - 启用预留并发以减少冷启动

2. **RDS优化**:
   - 使用预留实例节省成本
   - 定期清理不必要的数据

3. **S3优化**:
   - 设置生命周期策略删除旧文件
   - 使用标准-IA存储类降低存储成本

---

## 📞 支持和联系

### 技术支持
- **文档**: 参考prod/docs/目录下的详细文档
- **问题报告**: 通过项目Issue系统报告问题
- **紧急联系**: 查看configs/environment.env中的ALERT_EMAIL

### 有用链接
- [AWS Lambda文档](https://docs.aws.amazon.com/lambda/)
- [Zappa文档](https://github.com/zappa/Zappa)
- [Django部署指南](https://docs.djangoproject.com/en/4.2/howto/deployment/)

---

**部署手册版本**: v1.0  
**最后更新**: 2024年6月25日  
**维护团队**: JobQuest Navigator Development Team