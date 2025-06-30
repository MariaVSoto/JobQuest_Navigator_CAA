# Docker MinIO 设置指南

JobQuest Navigator 在 Docker 环境中使用 MinIO 作为 S3 兼容的本地对象存储服务，用于处理简历文件和其他媒体文件。

## MinIO 配置概述

### 什么是 MinIO？
MinIO 是一个高性能的 S3 兼容对象存储服务，完全兼容 Amazon S3 API。在本项目中，我们使用它作为本地开发环境的文件存储后端。

### 服务配置
- **容器名称**: `jobquest-minio`
- **Web UI 端口**: `http://localhost:9001`
- **API 端口**: `9000`
- **默认用户名**: `minioadmin`
- **默认密码**: `minioadmin123`
- **默认存储桶**: `jobquest-resumes`

## 启动 MinIO 服务

### 1. 启动包含 MinIO 的完整服务栈
```bash
cd infrastructure/docker/
./scripts/start-local-env.sh --dev --with-storage
```

### 2. 仅启动 MinIO 服务
```bash
docker-compose --profile storage up minio
```

### 3. 验证 MinIO 运行状态
```bash
docker-compose ps minio
```

## 初始化测试数据

### 1. 创建存储桶并上传测试数据
```bash
# 进入后端容器
docker-compose exec backend bash

# 创建存储桶并上传测试数据
python manage.py setup_minio_test_data --create-bucket

# 验证上传结果
python manage.py test_s3_connection --bucket jobquest-resumes
```

### 2. 验证连接（可选）
```bash
# 测试 MinIO 连接
python manage.py test_s3_connection
```

## 访问 MinIO Web 界面

1. 打开浏览器访问：`http://localhost:9001`
2. 使用以下凭据登录：
   - **用户名**: `minioadmin`
   - **密码**: `minioadmin123`
3. 查看 `jobquest-resumes` 存储桶中的测试数据

## 文件存储结构

MinIO 中的文件按以下结构组织：

```
jobquest-resumes/
├── resumes/
│   ├── samples/               # 示例简历文件
│   │   ├── software_engineer_resume.pdf
│   │   ├── data_scientist_resume.pdf
│   │   └── product_manager_resume.pdf
│   ├── data/                  # JSON 格式的简历数据
│   │   ├── software_engineer.json
│   │   └── data_scientist.json
│   ├── users/                 # 用户上传的简历（按用户 ID 组织）
│   │   ├── 1/                 # 用户 ID 1 的文件
│   │   ├── 2/                 # 用户 ID 2 的文件
│   │   └── ...
│   └── minio_config.json      # 配置元数据
```

## Django 设置说明

### 环境变量配置
在 Docker 环境中，以下环境变量自动配置：

```bash
USE_MINIO=True
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_BUCKET_NAME=jobquest-resumes
```

### 存储后端
- **Django 存储后端**: `storages.backends.s3boto3.S3Boto3Storage`
- **访问方式**: Django 通过 `boto3` 客户端与 MinIO 通信
- **文件 URL**: `http://minio:9000/jobquest-resumes/...`

## 常用管理命令

### 测试连接
```bash
python manage.py test_s3_connection
```

### 上传测试数据
```bash
python manage.py setup_minio_test_data --create-bucket
```

### 列出存储桶中的文件
```bash
python manage.py test_s3_connection --prefix resumes/
```

### 干运行模式（查看会执行什么操作）
```bash
python manage.py setup_minio_test_data --dry-run
```

## 编程方式使用

### 在 Django 代码中使用
```python
from resumes.s3_utils import resume_manager

# 上传文件
with open('resume.pdf', 'rb') as f:
    s3_key = resume_manager.upload_resume(
        file_content=f.read(),
        original_filename='resume.pdf',
        user_id=1
    )

# 获取下载 URL
download_url = resume_manager.get_resume_url(s3_key)

# 删除文件
resume_manager.delete_resume(s3_key)
```

### 便捷函数
```python
from resumes.s3_utils import upload_resume_file, get_resume_download_url

# 快速上传
s3_key = upload_resume_file(file_content, 'resume.pdf', user_id=1)

# 获取下载链接
url = get_resume_download_url(s3_key)
```

## 故障排除

### MinIO 容器无法启动
```bash
# 检查容器状态
docker-compose ps minio

# 查看日志
docker-compose logs minio

# 重启服务
docker-compose restart minio
```

### 连接测试失败
```bash
# 确保 MinIO 服务正在运行
docker-compose ps minio

# 检查网络连接
docker-compose exec backend ping minio

# 验证环境变量
docker-compose exec backend env | grep MINIO
```

### 存储桶不存在
```bash
# 创建存储桶
python manage.py setup_minio_test_data --create-bucket
```

### 权限问题
MinIO 默认配置允许所有操作。如果遇到权限问题：

1. 检查访问密钥是否正确
2. 确认存储桶名称拼写正确
3. 通过 Web 界面检查存储桶权限设置

## 生产环境注意事项

在生产环境中：

1. **更改默认凭据**: 更新 `MINIO_ROOT_USER` 和 `MINIO_ROOT_PASSWORD`
2. **启用 HTTPS**: 配置 SSL 证书
3. **设置持久存储**: 确保 MinIO 数据卷正确挂载
4. **备份策略**: 实施定期备份策略
5. **监控**: 添加健康检查和监控

## 从 MinIO 迁移到 AWS S3

如需迁移到真实的 AWS S3：

1. 更新环境变量：
   ```bash
   USE_MINIO=False
   AWS_ACCESS_KEY_ID=your_aws_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret
   AWS_STORAGE_BUCKET_NAME=your_s3_bucket
   ```

2. 移除 MinIO 相关配置：
   ```bash
   unset MINIO_ENDPOINT
   unset AWS_S3_ENDPOINT_URL
   ```

3. 数据迁移（如需要）：
   ```bash
   # 使用 AWS CLI 同步数据
   aws s3 sync s3://local-minio-bucket s3://aws-s3-bucket
   ```