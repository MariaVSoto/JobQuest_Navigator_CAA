# JobQuest Navigator - AWS部署架构设计文档

## 📋 项目概述

**项目名称**: JobQuest Navigator  
**项目类型**: 毕业设计项目  
**部署环境**: AWS Staging Environment  
**设计目标**: 简化部署、成本优化、学术演示

---

## 🏗️ 架构设计概览

### 设计原则
- **简化优先**: 专注于功能实现，不考虑高可用性和弹性伸缩
- **成本优化**: 使用最经济的AWS服务组合
- **学术导向**: 适合毕业设计演示和测试需求
- **易于管理**: 最小化运维复杂度

### 核心组件
```
┌─────────────────────────────────────────────────────────────┐
│                     AWS Cloud Architecture                  │
├─────────────────────────────────────────────────────────────┤
│  Frontend (React)          Backend (Django)                 │
│  ┌─────────────────┐      ┌─────────────────────────────┐   │
│  │   Amazon S3     │      │     AWS Lambda              │   │
│  │   Static Site   │◄────►│   Django REST API          │   │
│  │   Hosting       │      │   (Zappa Deployment)       │   │
│  └─────────────────┘      └─────────────────────────────┘   │
│                                      │                      │
│                                      ▼                      │
│                            ┌─────────────────────────────┐   │
│                            │     Amazon RDS              │   │
│                            │     MySQL Database          │   │
│                            │     (db.t3.micro)          │   │
│                            └─────────────────────────────┘   │
│                                      │                      │
│                                      ▼                      │
│                            ┌─────────────────────────────┐   │
│                            │     Amazon S3               │   │
│                            │     Static/Media Files      │   │
│                            └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 详细组件设计

### 1. 前端部署 - Amazon S3 Static Website

**服务**: Amazon S3 + CloudFormation (简化CDN)
**配置**:
```yaml
Bucket Configuration:
  Name: jobquest-navigator-frontend
  Region: us-east-1
  Static Website Hosting: Enabled
  Public Read Access: Enabled
  Index Document: index.html
  Error Document: index.html (SPA routing)
```

**部署流程**:
1. React应用构建: `npm run build`
2. 构建产物上传到S3
3. 配置S3 Bucket策略允许公共读取
4. 启用Static Website Hosting

### 2. 后端部署 - AWS Lambda + Zappa

**服务**: AWS Lambda + API Gateway
**配置**:
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
      "DJANGO_SETTINGS_MODULE": "core.settings_production",
      "LAMBDA_DEPLOYMENT": "true"
    }
  }
}
```

**特性**:
- 按请求付费，成本极低
- 自动扩展，无需管理服务器
- API Gateway提供RESTful API端点
- 适合中低流量的学术项目

### 3. 数据库 - Amazon RDS MySQL

**实例规格**:
```yaml
Engine: MySQL 8.0
Instance Class: db.t3.micro (1 vCPU, 1GB RAM)
Storage: 20GB gp2 (通用SSD)
Multi-AZ: Disabled (成本优化)
Backup Retention: 7 days
Publicly Accessible: No (安全考虑)
VPC: Default VPC
Security Group: Lambda-RDS-SG
```

**连接配置**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jobquest_navigator',
        'USER': 'admin',
        'PASSWORD': '${RDS_PASSWORD}',
        'HOST': 'jobquest-db.cluster-xxxxx.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    }
}
```

### 4. 文件存储 - Amazon S3

**静态文件存储**:
```yaml
Bucket: jobquest-navigator-static
Purpose: Django static files, user uploads
Access: Private with signed URLs
Lifecycle: Standard storage class
```

**Django配置**:
```python
STATIC_URL = 'https://jobquest-navigator-static.s3.amazonaws.com/static/'
MEDIA_URL = 'https://jobquest-navigator-static.s3.amazonaws.com/media/'
```

---

## 🌐 网络架构

### VPC配置
```yaml
VPC: Default VPC (简化网络管理)
Subnets: 
  - Public Subnet (us-east-1a)
  - Public Subnet (us-east-1b)
Security Groups:
  - Lambda-RDS-SG: Lambda访问RDS
  - RDS-SG: RDS入站规则 (3306 from Lambda)
```

### 安全组规则
```yaml
Lambda Security Group:
  Outbound: 
    - All traffic to 0.0.0.0/0 (HTTPS, MySQL)

RDS Security Group:
  Inbound:
    - Port 3306 from Lambda Security Group
  Outbound:
    - All traffic denied (default)
```

---

## 🔑 环境变量配置

### AWS Lambda环境变量
```bash
# Django配置
DJANGO_SETTINGS_MODULE=core.settings_production
DJANGO_SECRET_KEY=${SECRET_KEY}
DEBUG=False
LAMBDA_DEPLOYMENT=True

# 数据库配置
RDS_HOSTNAME=${RDS_ENDPOINT}
RDS_DB_NAME=jobquest_navigator
RDS_USERNAME=admin
RDS_PASSWORD=${RDS_PASSWORD}
RDS_PORT=3306

# AWS服务配置
AWS_STORAGE_BUCKET_NAME=jobquest-navigator-static
AWS_S3_REGION_NAME=us-east-1
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}

# 前端CORS配置
CORS_ALLOWED_ORIGINS=https://jobquest-navigator-frontend.s3-website-us-east-1.amazonaws.com
```

---

## 📦 部署流程

### 1. 基础设施准备

#### RDS数据库创建
```bash
# 1. 创建RDS实例
aws rds create-db-instance \
  --db-instance-identifier jobquest-navigator-db \
  --db-instance-class db.t3.micro \
  --engine mysql \
  --master-username admin \
  --master-user-password ${RDS_PASSWORD} \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxx \
  --db-name jobquest_navigator

# 2. 等待实例可用
aws rds wait db-instance-available \
  --db-instance-identifier jobquest-navigator-db
```

#### S3存储桶创建
```bash
# 1. 创建前端静态网站存储桶
aws s3 mb s3://jobquest-navigator-frontend
aws s3 website s3://jobquest-navigator-frontend \
  --index-document index.html \
  --error-document index.html

# 2. 创建静态资源存储桶
aws s3 mb s3://jobquest-navigator-static

# 3. 配置CORS和访问策略
aws s3api put-bucket-cors --bucket jobquest-navigator-static \
  --cors-configuration file://cors-config.json
```

### 2. 后端部署

#### Django应用准备
```bash
# 1. 安装依赖
pip install -r requirements_production.txt

# 2. 数据库迁移
python manage.py migrate --settings=core.settings_production

# 3. 收集静态文件
python manage.py collectstatic --noinput --settings=core.settings_production

# 4. 创建超级用户 (可选)
python manage.py createsuperuser --settings=core.settings_production
```

#### Zappa部署配置
```bash
# 1. 初始化Zappa
zappa init

# 2. 部署到Lambda
zappa deploy production

# 3. 更新部署
zappa update production

# 4. 设置环境变量
zappa set_env production DJANGO_SECRET_KEY=${SECRET_KEY}
zappa set_env production RDS_HOSTNAME=${RDS_ENDPOINT}
# ... 其他环境变量
```

### 3. 前端部署

#### React应用构建
```bash
# 1. 安装依赖
npm install

# 2. 配置生产环境变量
echo "REACT_APP_API_URL=${API_GATEWAY_URL}" > .env.production

# 3. 构建生产版本
npm run build

# 4. 部署到S3
aws s3 sync build/ s3://jobquest-navigator-frontend

# 5. 使缓存失效 (如果使用CloudFront)
aws cloudfront create-invalidation \
  --distribution-id ${CLOUDFRONT_DISTRIBUTION_ID} \
  --paths "/*"
```

---

## 💰 成本估算

### 月度成本估算 (US East 1)

| 服务 | 规格 | 月费用 (USD) |
|------|------|-------------|
| **RDS MySQL** | db.t3.micro | ~$15 |
| **Lambda** | 1M请求/月 | ~$2 |
| **API Gateway** | 1M请求/月 | ~$3 |
| **S3 Standard** | 5GB存储 | ~$0.12 |
| **S3 Requests** | 10K请求 | ~$0.05 |
| **Data Transfer** | 10GB出站 | ~$0.90 |
| **CloudWatch Logs** | 1GB日志 | ~$0.50 |
| **合计** | | **~$21.57/月** |

### 年度预算
```
总年费: ~$259
AWS免费套餐优惠: -$120 (RDS和Lambda)
实际年费: ~$139
```

**注意**: 成本可通过以下方式进一步优化：
- 使用AWS免费套餐
- 设置停机时间表 (开发期间暂停RDS)
- 使用预留实例 (长期项目)

---

## 🔄 CI/CD流水线 (可选)

### GitHub Actions工作流程
```yaml
name: Deploy to AWS

on:
  push:
    branches: [ main ]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements_production.txt
        pip install zappa
    
    - name: Deploy to Lambda
      run: |
        zappa update production
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install and build
      run: |
        npm ci
        npm run build
    
    - name: Deploy to S3
      run: |
        aws s3 sync build/ s3://jobquest-navigator-frontend
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

---

## 🔍 监控和日志

### CloudWatch监控
```yaml
监控指标:
  - Lambda执行时间和错误率
  - API Gateway请求数和延迟
  - RDS连接数和CPU使用率
  - S3存储使用量

告警设置:
  - Lambda错误率 > 5%
  - RDS CPU使用率 > 80%
  - API Gateway 5xx错误 > 10个/5分钟
```

### 日志配置
```python
# Django日志配置
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

---

## 🔒 安全配置

### 访问控制
```yaml
IAM角色和策略:
  Lambda执行角色:
    - VPC访问权限
    - RDS连接权限
    - S3读写权限
    - CloudWatch日志权限

S3存储桶策略:
  - 前端存储桶: 公共读取
  - 静态资源存储桶: 私有访问
  - CORS配置允许前端域名
```

### 网络安全
```yaml
安全组配置:
  - RDS仅允许Lambda访问
  - Lambda出站访问受限
  - 所有敏感端口关闭

环境变量加密:
  - 所有密钥使用AWS KMS加密
  - 数据库密码通过参数存储
```

---

## 📝 部署检查清单

### 部署前检查
- [ ] AWS CLI配置完成
- [ ] 环境变量准备就绪
- [ ] 数据库迁移文件验证
- [ ] 静态文件收集测试
- [ ] CORS配置检查
- [ ] 域名DNS设置 (如需要)

### 部署后验证
- [ ] API端点响应正常
- [ ] 数据库连接成功
- [ ] 静态文件加载正常
- [ ] 前端功能完整测试
- [ ] 错误日志检查
- [ ] 性能基准测试

### 生产就绪检查
- [ ] 备份策略配置
- [ ] 监控告警设置
- [ ] 安全扫描通过
- [ ] 成本预算确认
- [ ] 文档更新完成
- [ ] 团队访问权限配置

---

## 🎓 毕业设计考虑

### 演示准备
1. **功能演示脚本**: 准备完整的用户旅程演示
2. **技术架构图**: 可视化AWS架构设计
3. **性能测试报告**: 基础的负载测试结果
4. **成本分析**: 详细的部署成本分析

### 文档交付物
- [x] 架构设计文档 (本文档)
- [ ] API文档 (Swagger/OpenAPI)
- [ ] 部署操作手册
- [ ] 故障排除指南
- [ ] 用户使用手册

### 技术亮点
- **现代化架构**: Serverless + 微服务
- **云原生设计**: 充分利用AWS服务
- **成本效益**: 适合小规模项目的经济方案
- **可扩展性**: 架构支持未来功能扩展

---

## 📞 支持和维护

### 故障排除
```bash
# 常见问题诊断命令
zappa tail production          # 查看Lambda日志
aws rds describe-db-instances  # 检查RDS状态
aws s3 ls s3://bucket-name     # 验证S3内容
```

### 备份策略
```yaml
数据库备份:
  - 自动备份: 7天保留期
  - 手动快照: 重要节点备份

代码备份:
  - Git仓库: GitHub/GitLab
  - 部署包: S3存储
```

---

**文档版本**: v1.0  
**最后更新**: 2024年6月  
**作者**: JobQuest Navigator开发团队  
**项目**: 毕业设计项目