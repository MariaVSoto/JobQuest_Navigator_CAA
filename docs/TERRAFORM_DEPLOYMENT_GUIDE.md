# JobQuest Navigator - Terraform部署指南

## 🏗️ 概述

本指南介绍如何使用Terraform进行JobQuest Navigator的AWS基础设施部署。Terraform提供了比CloudFormation更灵活和强大的基础设施即代码解决方案。

**Terraform的优势**：
- 🔄 多云平台支持
- 📝 更简洁的语法
- 🔧 强大的模块化系统
- 📊 详细的执行计划
- 🔍 状态管理和漂移检测

---

## 🛠️ 前置要求

### 必需工具

1. **Terraform** (>= 1.0)
   ```bash
   # macOS
   brew install terraform
   
   # Linux
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   unzip terraform_1.6.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   
   # Windows
   # 下载并安装从 https://www.terraform.io/downloads
   ```

2. **AWS CLI** (已配置)
   ```bash
   aws configure
   aws sts get-caller-identity  # 验证配置
   ```

3. **jq** (用于JSON处理)
   ```bash
   # macOS
   brew install jq
   
   # Linux
   sudo apt install jq
   ```

### AWS权限要求

确保你的AWS凭证具有以下权限：
- EC2 (VPC, 子网, 安全组)
- RDS (实例创建和管理)
- S3 (存储桶创建和策略)
- IAM (角色和策略创建)
- Lambda (函数创建)
- API Gateway (API创建)
- CloudWatch (日志和监控)
- Secrets Manager (密钥管理)

---

## 📁 Terraform项目结构

```
infrastructure/terraform/
├── main.tf                    # 主配置文件
├── variables.tf               # 输入变量定义
├── outputs.tf                 # 输出值定义
├── terraform.tfvars.example   # 变量值示例
├── terraform.tfvars          # 实际变量值 (需创建)
└── modules/                   # 可重用模块
    ├── vpc/                   # VPC网络模块
    ├── security/              # 安全组模块
    ├── s3/                    # S3存储模块
    ├── rds/                   # 数据库模块
    ├── iam/                   # IAM权限模块
    └── monitoring/            # 监控告警模块
```

---

## 🚀 快速开始

### 1. 初始化配置

```bash
# 进入Terraform目录
cd prod/infrastructure/terraform

# 创建变量配置文件
cp terraform.tfvars.example terraform.tfvars

# 编辑配置文件
nano terraform.tfvars
```

### 2. 配置关键变量

编辑 `terraform.tfvars` 文件：

```hcl
# 基础配置
project_name = "jobquest-navigator"
environment  = "production"
aws_region   = "us-east-1"
project_owner = "Your Name"

# 必需：告警邮箱
alert_email = "your-email@domain.com"

# 数据库配置
db_instance_class = "db.t3.micro"
db_allocated_storage = 20

# Lambda配置
lambda_memory_size = 512
lambda_timeout = 300

# 成本优化设置
enable_nat_gateway = false
enable_cloudfront = false
enable_detailed_monitoring = false
```

### 3. 部署基础设施

```bash
# 使用部署脚本（推荐）
scripts/deploy-terraform.sh --action plan     # 查看执行计划
scripts/deploy-terraform.sh --action apply    # 部署基础设施

# 或者手动执行
terraform init
terraform plan
terraform apply
```

---

## 📋 详细部署步骤

### 步骤 1: 环境准备

```bash
# 1. 验证工具安装
terraform version
aws --version
jq --version

# 2. 验证AWS配置
aws sts get-caller-identity

# 3. 进入Terraform目录
cd prod/infrastructure/terraform
```

### 步骤 2: 配置管理

```bash
# 创建配置文件
cp terraform.tfvars.example terraform.tfvars

# 关键配置项说明
cat >> terraform.tfvars << EOF
# 项目基本信息
project_name = "jobquest-navigator"
environment  = "production"
project_owner = "JobQuest Team"

# AWS配置
aws_region = "us-east-1"
alert_email = "admin@yourcompany.com"

# 网络配置
vpc_cidr = "10.0.0.0/16"

# 数据库配置
db_instance_class = "db.t3.micro"
db_allocated_storage = 20
enable_rds_encryption = true
rds_backup_retention_period = 7

# Lambda配置
lambda_memory_size = 512
lambda_timeout = 300

# 成本优化
enable_nat_gateway = false
enable_s3_endpoint = true
enable_detailed_monitoring = false
log_retention_days = 14
EOF
```

### 步骤 3: 初始化和验证

```bash
# 初始化Terraform
terraform init

# 验证配置
terraform validate

# 格式化代码
terraform fmt -recursive

# 查看执行计划
terraform plan
```

### 步骤 4: 部署基础设施

```bash
# 方法1: 使用部署脚本（推荐）
scripts/deploy-terraform.sh --action apply

# 方法2: 手动部署
terraform apply

# 方法3: 自动确认部署
terraform apply -auto-approve
```

### 步骤 5: 验证部署

```bash
# 查看输出
terraform output

# 查看特定输出
terraform output database_endpoint
terraform output frontend_website_url

# 验证资源状态
terraform show
```

---

## 🔧 高级配置

### 工作空间管理

使用Terraform工作空间管理多环境：

```bash
# 创建开发环境
terraform workspace new development
terraform workspace select development

# 使用不同的配置文件
cp terraform.tfvars terraform.tfvars.development
# 编辑开发环境特定配置

# 部署到开发环境
terraform apply -var-file="terraform.tfvars.development"

# 切换到生产环境
terraform workspace select production
terraform apply -var-file="terraform.tfvars"

# 查看所有工作空间
terraform workspace list
```

### 状态管理

配置远程状态存储（推荐生产环境）：

```hcl
# 在main.tf中添加后端配置
terraform {
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "jobquest-navigator/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

### 模块化配置

创建环境特定的配置：

```hcl
# environments/production/main.tf
module "jobquest_navigator" {
  source = "../../"
  
  project_name = "jobquest-navigator"
  environment  = "production"
  
  # 生产环境特定配置
  db_instance_class = "db.t3.small"
  enable_multi_az = true
  enable_rds_deletion_protection = true
  lambda_memory_size = 1024
  enable_detailed_monitoring = true
}
```

---

## 📊 输出和集成

### 重要输出值

部署完成后，Terraform会提供以下输出：

```bash
# 网络信息
terraform output vpc_id
terraform output private_subnet_ids
terraform output lambda_security_group_id

# 数据库信息
terraform output database_endpoint
terraform output database_name
terraform output database_password_secret_name

# 存储信息
terraform output static_bucket_name
terraform output frontend_bucket_name
terraform output frontend_website_url

# 部署信息
terraform output deployment_info
terraform output zappa_configuration
```

### 与Zappa集成

Terraform部署的基础设施可以直接用于Zappa部署：

```bash
# 获取Zappa所需的配置
terraform output -json zappa_configuration > zappa_config.json

# 更新Zappa配置
cat zappa_config.json | jq -r '.vpc_config'
```

### 与部署脚本集成

```bash
# Terraform输出可以被其他脚本使用
export DATABASE_ENDPOINT=$(terraform output -raw database_endpoint)
export STATIC_BUCKET=$(terraform output -raw static_bucket_name)
export FRONTEND_BUCKET=$(terraform output -raw frontend_bucket_name)

# 运行后续部署脚本
../scripts/deploy-backend.sh
../scripts/deploy-frontend.sh
```

---

## 🔍 监控和维护

### 状态检查

```bash
# 检查资源漂移
terraform plan -detailed-exitcode

# 刷新状态
terraform refresh

# 导入现有资源
terraform import aws_s3_bucket.existing bucket-name
```

### 更新基础设施

```bash
# 更新配置
nano terraform.tfvars

# 查看变更计划
terraform plan

# 应用变更
terraform apply

# 针对特定资源
terraform apply -target=module.rds
```

### 故障排除

```bash
# 调试模式
export TF_LOG=DEBUG
terraform apply

# 查看状态文件
terraform show

# 验证配置
terraform validate

# 检查格式
terraform fmt -check -diff
```

---

## 💰 成本管理

### 成本优化配置

**开发环境**：
```hcl
# terraform.tfvars.development
db_instance_class = "db.t3.micro"
lambda_memory_size = 256
enable_detailed_monitoring = false
log_retention_days = 7
enable_nat_gateway = false
rds_backup_retention_period = 1
```

**生产环境**：
```hcl
# terraform.tfvars.production
db_instance_class = "db.t3.small"
lambda_memory_size = 512
enable_detailed_monitoring = true
log_retention_days = 30
enable_multi_az = true
rds_backup_retention_period = 30
```

### 成本监控

```bash
# 使用AWS CLI查看成本
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-12-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE

# 查看预估成本
terraform output estimated_monthly_cost
```

---

## 🔒 安全最佳实践

### 状态文件安全

```bash
# 使用远程状态存储
# 启用状态文件加密
# 配置状态锁定机制
# 限制状态文件访问权限
```

### 变量管理

```bash
# 敏感变量管理
export TF_VAR_db_password="your-secure-password"

# 使用AWS Secrets Manager
# Terraform会自动生成并存储数据库密码
```

### 网络安全

```hcl
# 最小化权限原则
# 使用私有子网
# 配置安全组规则
# 启用VPC Flow Logs
```

---

## 🚀 CI/CD集成

### GitHub Actions示例

```yaml
name: Terraform Deploy

on:
  push:
    branches: [main]
    paths: ['infrastructure/terraform/**']

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Terraform
      uses: hashicorp/setup-terraform@v2
      with:
        terraform_version: 1.6.0
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Terraform Init
      run: terraform init
      working-directory: infrastructure/terraform
    
    - name: Terraform Plan
      run: terraform plan -no-color
      working-directory: infrastructure/terraform
    
    - name: Terraform Apply
      if: github.ref == 'refs/heads/main'
      run: terraform apply -auto-approve -no-color
      working-directory: infrastructure/terraform
```

---

## 📚 常用命令参考

### 基本命令

```bash
# 初始化
terraform init

# 验证
terraform validate

# 计划
terraform plan

# 应用
terraform apply

# 销毁
terraform destroy

# 格式化
terraform fmt

# 显示状态
terraform show

# 列出资源
terraform state list

# 输出值
terraform output
```

### 工作空间命令

```bash
# 列出工作空间
terraform workspace list

# 新建工作空间
terraform workspace new <name>

# 选择工作空间
terraform workspace select <name>

# 删除工作空间
terraform workspace delete <name>
```

### 状态管理命令

```bash
# 刷新状态
terraform refresh

# 导入资源
terraform import <resource_type>.<name> <id>

# 移除资源
terraform state rm <resource>

# 移动资源
terraform state mv <source> <destination>
```

---

## 🔄 Terraform vs CloudFormation

| 特性 | Terraform | CloudFormation |
|------|-----------|----------------|
| **语法** | HCL (简洁) | JSON/YAML (冗长) |
| **多云支持** | ✅ 支持多云 | ❌ 仅限AWS |
| **状态管理** | ✅ 本地/远程状态 | ✅ AWS托管 |
| **模块化** | ✅ 强大的模块系统 | ⚠️ 嵌套堆栈 |
| **执行计划** | ✅ 详细的变更预览 | ⚠️ 变更集 |
| **社区** | ✅ 庞大的社区 | ⚠️ AWS生态 |
| **学习曲线** | ⚠️ 需要学习HCL | ✅ AWS原生 |
| **调试** | ✅ 详细的日志 | ⚠️ 有限的调试 |

---

## 📞 支持和资源

### 官方文档
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Language](https://www.terraform.io/language)
- [Terraform CLI](https://www.terraform.io/cli)

### 社区资源
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [AWS Architecture Center](https://aws.amazon.com/architecture/)
- [Terraform Modules Registry](https://registry.terraform.io/)

### 故障排除
- 查看 `docs/TROUBLESHOOTING_GUIDE.md`
- 启用调试模式：`export TF_LOG=DEBUG`
- 检查AWS CloudTrail日志

---

**Terraform部署指南版本**: v1.0  
**最后更新**: 2024年6月25日  
**维护团队**: JobQuest Navigator Development Team