# JobQuest Navigator - Docker Local Development Environment

这个目录包含了使用Docker在本地创建完整JobQuest Navigator开发环境的所有配置文件和脚本。

## 🚀 快速开始

### 先决条件

- Docker Desktop (或 Docker Engine + Docker Compose)
- 至少 4GB 可用内存
- 至少 10GB 可用磁盘空间

### 一键启动

```bash
# 进入docker目录
cd infrastructure/docker

# 启动开发环境
./scripts/start-local-env.sh --dev

# 或者启动生产类似的环境
./scripts/start-local-env.sh --prod
```

## 📁 文件结构

```
infrastructure/docker/
├── Dockerfile.backend          # Django后端生产环境镜像
├── Dockerfile.backend.dev      # Django后端开发环境镜像  
├── Dockerfile.frontend         # React前端生产环境镜像
├── Dockerfile.frontend.dev     # React前端开发环境镜像
├── Dockerfile.devtools         # 开发工具容器镜像
├── docker-compose.yml          # 主要的Docker Compose配置
├── docker-compose.dev.yml      # 开发环境覆盖配置
├── nginx.conf                  # Nginx配置（前端）
├── nginx-proxy.conf            # Nginx代理配置
├── init-db.sql                 # 数据库初始化脚本
├── init-dev-db.sql            # 开发数据库初始化脚本
├── scripts/
│   ├── start-local-env.sh     # 启动环境脚本
│   ├── stop-local-env.sh      # 停止环境脚本
│   └── manage.sh              # Django管理脚本
└── README.md                  # 本文档
```

## 🛠️ 可用的启动模式

### 开发模式 (推荐)
```bash
./scripts/start-local-env.sh --dev
```
- 热重载支持
- 开发工具容器
- 源代码挂载
- 详细日志输出

### 生产模式
```bash
./scripts/start-local-env.sh --prod
```
- 构建优化的镜像
- Nginx代理
- 生产级配置

### 完整模式
```bash
./scripts/start-local-env.sh --full
```
- 包含所有可选服务
- 监控工具 (Prometheus + Grafana)
- 邮件测试 (MailHog)
- 对象存储 (MinIO)
- 搜索引擎 (Elasticsearch)

### 最小模式
```bash
./scripts/start-local-env.sh --minimal
```
- 仅核心服务
- 数据库、后端、前端

## 🌐 服务访问地址

| 服务 | 地址 | 描述 |
|------|------|------|
| 前端应用 | http://localhost:3000 | React应用程序 |
| 后端API | http://localhost:8000 | Django REST API |
| Django管理 | http://localhost:8000/admin/ | Django管理界面 |
| API文档 | http://localhost:8000/api/docs/ | API文档 |
| 数据库 | localhost:5432 | PostgreSQL数据库 |
| Redis | localhost:6379 | Redis缓存 |

### 可选服务地址

| 服务 | 地址 | 描述 |
|------|------|------|
| MailHog | http://localhost:8025 | 邮件测试工具 |
| MinIO | http://localhost:9001 | S3兼容对象存储 |
| Elasticsearch | http://localhost:9200 | 搜索引擎 |
| Prometheus | http://localhost:9090 | 监控指标 |
| Grafana | http://localhost:3001 | 监控仪表板 (admin/admin123) |
| Nginx代理 | http://localhost:8080 | Nginx反向代理 |

## 🔧 管理命令

### 使用管理脚本

```bash
# Django迁移
./scripts/manage.sh migrate

# 创建超级用户
./scripts/manage.sh createsuperuser

# 运行测试
./scripts/manage.sh test

# 查看日志
./scripts/manage.sh logs

# 进入后端容器shell
./scripts/manage.sh bash

# 安装Python包
./scripts/manage.sh pip install package-name
```

### 直接使用Docker Compose

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend

# 执行Django命令
docker-compose exec backend python manage.py migrate

# 进入容器shell
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec database psql -U jobquest_user jobquest_navigator
```

## 🛑 停止和清理

### 软停止（保留数据）
```bash
./scripts/stop-local-env.sh --soft
```

### 清理停止（删除数据卷）
```bash
./scripts/stop-local-env.sh --clean
```

### 完全重置（删除所有镜像）
```bash
./scripts/stop-local-env.sh --reset
```

## 🔍 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口占用
   lsof -i :3000
   lsof -i :8000
   lsof -i :5432
   ```

2. **容器启动失败**
   ```bash
   # 查看详细日志
   docker-compose logs [service_name]
   
   # 重建镜像
   docker-compose build --no-cache [service_name]
   ```

3. **数据库连接问题**
   ```bash
   # 检查数据库容器状态
   docker-compose exec database pg_isready -U jobquest_user
   
   # 重启数据库
   docker-compose restart database
   ```

4. **权限问题**
   ```bash
   # 修复文件权限
   sudo chown -R $USER:$USER ../../backend/media
   sudo chown -R $USER:$USER ../../backend/staticfiles
   ```

### 重置开发环境

```bash
# 完全清理
./scripts/stop-local-env.sh --reset

# 重新启动
./scripts/start-local-env.sh --dev

# 运行迁移
./scripts/manage.sh migrate

# 创建超级用户
./scripts/manage.sh createsuperuser
```

## 📊 监控和调试

### 查看资源使用情况
```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
docker system df
```

### 性能分析
```bash
# 启用监控模式
./scripts/start-local-env.sh --full

# 访问 Grafana 仪表板
open http://localhost:3001
```

### 日志分析
```bash
# 实时查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f database
```

## 🔐 安全配置

### 开发环境默认凭据

| 服务 | 用户名 | 密码 |
|------|--------|------|
| PostgreSQL | jobquest_user | jobquest_password |
| MinIO | minioadmin | minioadmin123 |
| Grafana | admin | admin123 |

⚠️ **警告**: 这些是开发环境的默认凭据，绝不应在生产环境中使用！

## 🚀 部署到测试环境

开发完成后，可以使用以下命令部署到AWS测试环境：

```bash
# 使用GitHub Actions部署
gh workflow run "Deploy to Test Environment" \
  --ref develop \
  --field force_deploy=false

# 或手动部署
cd ../..
./scripts/deploy-infrastructure.sh
./scripts/deploy-backend.sh
./scripts/deploy-frontend.sh
```

## 📝 开发提示

1. **代码热重载**: 开发模式下，后端和前端都支持热重载
2. **数据持久化**: 数据库和Redis数据在容器重启后保持不变
3. **静态文件**: Django静态文件自动收集到共享卷
4. **邮件测试**: 使用MailHog捕获所有发送的邮件
5. **日志查看**: 使用管理脚本轻松查看日志和执行命令

## 🤝 贡献

如果你发现任何问题或有改进建议，请：

1. 检查现有的issues
2. 创建新的issue描述问题
3. 提交Pull Request with详细说明

## 📄 许可证

本项目采用MIT许可证 - 详见LICENSE文件