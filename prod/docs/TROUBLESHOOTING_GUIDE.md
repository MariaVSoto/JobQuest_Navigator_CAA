# JobQuest Navigator - 故障排除指南

## 🔧 概述

本文档提供JobQuest Navigator AWS部署过程中常见问题的诊断和解决方案。

---

## 🚨 部署阶段问题

### 1. CloudFormation部署失败

#### 问题: 堆栈创建失败
```
CREATE_FAILED: The account is not authorized to use this service
```

**原因分析**:
- AWS账户权限不足
- 服务在当前区域不可用
- 账户限制或配额问题

**解决方案**:
```bash
# 检查账户权限
aws sts get-caller-identity

# 检查服务可用性
aws ec2 describe-availability-zones --region us-east-1

# 检查服务限制
aws support describe-service-limits
```

#### 问题: 参数验证错误
```
ValidationError: Template format error: [/Resources/Database/Properties/MasterUserPassword] 
'null' values are not allowed in templates
```

**解决方案**:
```bash
# 确保所有必需参数都提供值
aws cloudformation create-stack \
  --stack-name jobquest-navigator-infra \
  --template-body file://cloudformation-template.yaml \
  --parameters ParameterKey=DatabasePassword,ParameterValue=SecurePass123! \
               ParameterKey=AlertEmail,ParameterValue=your-email@domain.com
```

### 2. RDS数据库问题

#### 问题: 数据库创建失败
```
DBSubnetGroupDoesNotCoverEnoughAZs: DB Subnet Group doesn't meet availability zone coverage requirement
```

**解决方案**:
```bash
# 检查可用区
aws ec2 describe-availability-zones --region us-east-1

# 确保子网在不同AZ中
# 修改CloudFormation模板，确保子网分布在至少两个AZ
```

#### 问题: 数据库连接超时
```
ERROR 2003 (HY000): Can't connect to MySQL server on 'xxx.amazonaws.com' (110)
```

**诊断步骤**:
```bash
# 1. 检查RDS实例状态
aws rds describe-db-instances --db-instance-identifier jobquest-navigator-db

# 2. 检查安全组配置
aws ec2 describe-security-groups --group-ids sg-xxxxxxxx

# 3. 测试网络连通性
telnet your-db-endpoint.amazonaws.com 3306
```

**解决方案**:
```bash
# 修改安全组规则
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxx \
  --protocol tcp \
  --port 3306 \
  --source-group sg-yyyyyyyy
```

---

## 🐍 Lambda部署问题

### 1. Zappa部署错误

#### 问题: IAM权限不足
```
An error occurred (AccessDenied) when calling the CreateFunction operation: 
User is not authorized to perform: lambda:CreateFunction
```

**所需权限清单**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:*",
        "iam:CreateRole",
        "iam:AttachRolePolicy",
        "iam:PutRolePolicy",
        "apigateway:*",
        "s3:*",
        "events:*",
        "logs:*"
      ],
      "Resource": "*"
    }
  ]
}
```

#### 问题: 包大小超限
```
An error occurred (InvalidParameterValueException): Unzipped size must be smaller than 262144000 bytes
```

**解决方案**:
```bash
# 1. 排除不必要的文件
echo "*.pyc
__pycache__/
.git/
tests/
*.sqlite3" > .zappaignore

# 2. 使用Slim处理器
pip install zappa[all]

# 3. 在zappa_settings.json中配置
{
  "production": {
    "slim_handler": true,
    "exclude": ["*.pyc", "*.pyo"]
  }
}
```

### 2. Lambda运行时错误

#### 问题: 模块导入失败
```
Unable to import module 'core.wsgi': No module named 'django'
```

**解决方案**:
```bash
# 确保requirements.txt包含所有依赖
pip freeze > requirements.txt

# 检查Zappa虚拟环境
zappa status production

# 重新打包部署
zappa update production
```

#### 问题: 数据库连接池耗尽
```
(1040, 'Too many connections')
```

**解决方案**:
```python
# 在Django设置中配置连接池
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'CONN_MAX_AGE': 0,  # 不保持连接
    }
}
```

### 3. API Gateway问题

#### 问题: CORS错误
```
Access to XMLHttpRequest at 'api-url' from origin 'frontend-url' has been blocked by CORS policy
```

**Django CORS配置**:
```python
# settings_production.py
CORS_ALLOWED_ORIGINS = [
    "https://jobquest-navigator-frontend-production.s3-website-us-east-1.amazonaws.com",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False  # 生产环境不要设为True
```

**API Gateway CORS配置**:
```bash
# 通过Zappa自动配置CORS
{
  "production": {
    "cors": true,
    "cors_origin": "https://your-frontend-domain.com"
  }
}
```

---

## 🌐 前端部署问题

### 1. S3部署问题

#### 问题: 存储桶策略错误
```
AccessDenied: Access Denied when putting object
```

**解决方案**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::jobquest-navigator-frontend-production/*"
    }
  ]
}
```

#### 问题: 单页应用路由404
```
The specified key does not exist when accessing /dashboard
```

**解决方案**:
```bash
# 设置错误文档为index.html
aws s3 website s3://jobquest-navigator-frontend-production \
  --index-document index.html \
  --error-document index.html
```

### 2. 前端配置问题

#### 问题: API端点无法访问
```
TypeError: Failed to fetch
```

**检查步骤**:
```bash
# 1. 验证API Gateway URL
curl -X GET "https://api-gateway-url.amazonaws.com/prod/api/health/"

# 2. 检查前端环境变量
cat build/static/js/main.*.js | grep -o 'REACT_APP_API_URL[^"]*'

# 3. 验证CORS配置
curl -H "Origin: https://your-frontend-domain.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     "https://api-gateway-url.amazonaws.com/prod/api/health/"
```

---

## 📊 性能问题

### 1. Lambda性能优化

#### 问题: 冷启动时间过长
```
Duration: 10000.00 ms    Billed Duration: 10000 ms    Memory Size: 128 MB
```

**优化方案**:
```json
{
  "production": {
    "memory_size": 512,
    "timeout_seconds": 30,
    "keep_warm": false,
    "provisioned_concurrency": 1
  }
}
```

#### 问题: 内存不足
```
Runtime.ImportModuleError: Unable to import module 'core.wsgi': No module named 'PIL'
```

**解决方案**:
```bash
# 增加内存分配
zappa update production

# 使用优化的依赖包
pip install Pillow-SIMD
```

### 2. 数据库性能问题

#### 问题: 查询超时
```
(2006, 'MySQL server has gone away')
```

**诊断和优化**:
```python
# 1. 启用查询日志
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}

# 2. 优化数据库查询
# 使用select_related和prefetch_related
queryset = Job.objects.select_related('company').prefetch_related('skills')

# 3. 添加数据库索引
class Job(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    location = models.CharField(max_length=100, db_index=True)
```

---

## 🔍 监控和诊断工具

### 1. 日志分析

#### CloudWatch日志查询
```bash
# 查看Lambda错误日志
aws logs filter-log-events \
  --log-group-name "/aws/lambda/jobquest-navigator-api-production" \
  --filter-pattern "ERROR" \
  --start-time $(date -d "1 hour ago" +%s)000

# 查看数据库连接错误
aws logs filter-log-events \
  --log-group-name "/aws/lambda/jobquest-navigator-api-production" \
  --filter-pattern "Can't connect to MySQL" \
  --start-time $(date -d "24 hours ago" +%s)000
```

#### Zappa日志工具
```bash
# 实时查看日志
zappa tail production

# 查看特定级别的日志
zappa tail production --http

# 保存日志到文件
zappa tail production > lambda-logs.txt
```

### 2. 性能监控

#### CloudWatch指标
```bash
# Lambda执行时间
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=jobquest-navigator-api-production \
  --start-time $(date -d "1 hour ago" -Iseconds) \
  --end-time $(date -Iseconds) \
  --period 300 \
  --statistics Average,Maximum

# API Gateway错误率
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name 4XXError \
  --dimensions Name=ApiName,Value=jobquest-navigator-api \
  --start-time $(date -d "1 hour ago" -Iseconds) \
  --end-time $(date -Iseconds) \
  --period 300 \
  --statistics Sum
```

### 3. 健康检查脚本

#### 自动化诊断脚本
```bash
#!/bin/bash
# health-check.sh

echo "=== JobQuest Navigator Health Check ==="

# 1. 检查Lambda函数状态
echo "Checking Lambda function..."
aws lambda get-function --function-name jobquest-navigator-api-production

# 2. 检查RDS实例状态
echo "Checking RDS instance..."
aws rds describe-db-instances --db-instance-identifier jobquest-navigator-db

# 3. 检查S3存储桶
echo "Checking S3 buckets..."
aws s3 ls s3://jobquest-navigator-frontend-production
aws s3 ls s3://jobquest-navigator-static-production

# 4. 测试API端点
echo "Testing API endpoints..."
curl -f "https://api-gateway-url.amazonaws.com/prod/api/health/" || echo "API health check failed"

# 5. 检查前端可访问性
echo "Testing frontend..."
curl -f "https://jobquest-navigator-frontend-production.s3-website-us-east-1.amazonaws.com" || echo "Frontend check failed"

echo "=== Health Check Complete ==="
```

---

## 🛠️ 常用修复命令

### 快速修复脚本

#### 重新部署所有组件
```bash
#!/bin/bash
# quick-redeploy.sh

echo "Starting quick redeploy..."

# 1. 更新Lambda
cd backend
zappa update production

# 2. 重新构建和部署前端
cd ../frontend
npm run build
aws s3 sync build/ s3://jobquest-navigator-frontend-production --delete

# 3. 清理CloudFront缓存 (如果使用)
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"

echo "Redeploy complete!"
```

#### 数据库连接修复
```bash
#!/bin/bash
# fix-db-connection.sh

# 1. 重启RDS实例
aws rds reboot-db-instance --db-instance-identifier jobquest-navigator-db

# 2. 等待实例可用
aws rds wait db-instance-available --db-instance-identifier jobquest-navigator-db

# 3. 测试连接
python manage.py check --database default

# 4. 运行迁移
python manage.py migrate --settings=core.settings_production
```

---

## 📞 获取帮助

### 支持渠道
1. **技术文档**: 查看prod/docs/目录
2. **AWS支持**: 通过AWS Support Center
3. **社区支持**: Django和Zappa社区论坛

### 报告问题时提供的信息
- 错误消息的完整内容
- CloudFormation堆栈状态
- Lambda函数日志
- 重现步骤
- 环境配置信息

---

**故障排除指南版本**: v1.0  
**最后更新**: 2024年6月25日  
**维护团队**: JobQuest Navigator Development Team