# JobQuest Navigator - 完整本地部署指南

本指南将指导新用户从零开始完成 JobQuest Navigator 本地开发环境的完整部署，包括 Windows 和 macOS 两个平台的详细步骤。

## 📋 目录

- [系统要求](#系统要求)
- [预备知识](#预备知识)
- [Windows 部署指南](#windows-部署指南)
- [macOS 部署指南](#macos-部署指南)
- [通用部署步骤](#通用部署步骤)
- [验证部署](#验证部署)
- [常见问题排查](#常见问题排查)
- [开发工作流](#开发工作流)

---

## 📊 系统要求

### 最低配置要求
- **内存**: 8GB RAM (推荐 16GB)
- **存储**: 20GB 可用磁盘空间
- **网络**: 稳定的互联网连接
- **操作系统**: 
  - Windows 10/11 (64位)
  - macOS 10.15+ (Catalina 或更新版本)

### 必需软件
- Git 版本控制
- Docker Desktop
- 代码编辑器 (推荐 VS Code)
- 终端工具 (Windows Terminal 或 macOS Terminal)

---

## 🎓 预备知识

在开始部署前，建议了解以下基础概念：

### Docker 基础
- **容器**: 轻量级、可移植的应用程序运行环境
- **镜像**: 容器的模板，包含应用程序和依赖
- **Docker Compose**: 多容器应用程序的编排工具
- **Volume**: 数据持久化存储

### 项目架构
- **Frontend**: React 18 用户界面
- **Backend**: Django 4.2 REST API
- **Database**: PostgreSQL 15 数据库
- **Cache**: Redis 7 缓存服务
- **Storage**: MinIO S3兼容对象存储

---

## 🪟 Windows 部署指南

### 步骤 1: 准备 Windows 环境

#### 1.1 启用 WSL 2 (Windows Subsystem for Linux)

打开 **PowerShell** (管理员权限):

```powershell
# 启用 WSL 功能
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# 启用虚拟机平台功能
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 重启计算机
Restart-Computer
```

重启后，继续在 PowerShell (管理员权限) 中执行:

```powershell
# 设置 WSL 2 为默认版本
wsl --set-default-version 2

# 安装 Ubuntu (推荐)
wsl --install -d Ubuntu
```

#### 1.2 安装 Git

访问 [Git for Windows](https://git-scm.com/download/win) 下载并安装:

```powershell
# 验证安装
git --version
```

#### 1.3 安装 Docker Desktop

1. 访问 [Docker Desktop for Windows](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe)
2. 下载并运行安装程序
3. 安装时确保选择 **"Use WSL 2 instead of Hyper-V"**
4. 重启计算机

#### 1.4 配置 Docker Desktop

启动 Docker Desktop 并进行以下配置:

1. **Resources → Advanced**:
   - Memory: 最少 4GB (推荐 8GB)
   - CPUs: 最少 2 核 (推荐 4 核)
   - Disk image size: 最少 64GB

2. **Resources → WSL Integration**:
   - 启用 "Enable integration with my default WSL distro"
   - 启用 "Enable integration with additional distros" 中的 Ubuntu

3. 点击 **"Apply & Restart"**

#### 1.5 验证 Docker 安装

在 PowerShell 或 WSL Ubuntu 终端中:

```bash
# 检查 Docker 版本
docker --version
docker-compose --version

# 测试 Docker 运行
docker run hello-world
```

### 步骤 2: 克隆项目 (Windows)

打开 **Windows Terminal** 或 **WSL Ubuntu**:

```bash
# 创建项目目录
mkdir -p ~/projects
cd ~/projects

# 克隆项目 (替换为实际的仓库地址)
git clone https://github.com/yourusername/JobQuest_Navigator_CAA.git
cd JobQuest_Navigator_CAA

# 验证项目结构
ls -la
```

### 步骤 3: Windows 特定配置

#### 3.1 配置文件权限

```bash
# 在 WSL 中设置适当的权限
chmod +x infrastructure/docker/scripts/*.sh
```

#### 3.2 Windows 防火墙配置

如果遇到网络问题，可能需要在 Windows Defender 防火墙中添加规则:

1. 打开 **Windows Defender 防火墙**
2. 选择 **"允许应用或功能通过 Windows Defender 防火墙"**
3. 找到并允许 **"Docker Desktop"**

---

## 🍎 macOS 部署指南

### 步骤 1: 准备 macOS 环境

#### 1.1 安装 Homebrew (包管理器)

打开 **Terminal** 应用程序:

```bash
# 安装 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 添加到 PATH (根据提示执行)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# 验证安装
brew --version
```

#### 1.2 安装 Git

```bash
# 使用 Homebrew 安装 Git
brew install git

# 验证安装
git --version
```

#### 1.3 安装 Docker Desktop

**方法 1: 手动下载**
1. 访问 [Docker Desktop for Mac](https://desktop.docker.com/mac/main/amd64/Docker.dmg)
2. 下载 DMG 文件 (选择 Intel 或 Apple Silicon 版本)
3. 打开 DMG 文件，将 Docker 拖拽到 Applications 文件夹
4. 从 Applications 启动 Docker Desktop

**方法 2: 使用 Homebrew**
```bash
# 使用 Homebrew Cask 安装
brew install --cask docker

# 启动 Docker Desktop
open /Applications/Docker.app
```

#### 1.4 配置 Docker Desktop (macOS)

启动 Docker Desktop 并配置:

1. **Preferences → Resources**:
   - Memory: 最少 4GB (推荐 8GB)
   - CPUs: 最少 2 核 (推荐 4 核)
   - Swap: 1GB
   - Disk image size: 最少 64GB

2. 点击 **"Apply & Restart"**

#### 1.5 验证 Docker 安装 (macOS)

```bash
# 检查 Docker 版本
docker --version
docker-compose --version

# 测试 Docker 运行
docker run hello-world
```

### 步骤 2: 克隆项目 (macOS)

```bash
# 创建项目目录
mkdir -p ~/projects
cd ~/projects

# 克隆项目 (替换为实际的仓库地址)
git clone https://github.com/yourusername/JobQuest_Navigator_CAA.git
cd JobQuest_Navigator_CAA

# 验证项目结构
ls -la
```

### 步骤 3: macOS 特定配置

#### 3.1 配置文件权限

```bash
# 设置脚本执行权限
chmod +x infrastructure/docker/scripts/*.sh
```

#### 3.2 解决 M1/M2 Mac 兼容性问题

如果使用 Apple Silicon Mac:

```bash
# 设置环境变量支持 x86 容器 (如果需要)
export DOCKER_DEFAULT_PLATFORM=linux/amd64
```

---

## 🚀 通用部署步骤

以下步骤适用于 Windows 和 macOS 两个平台:

### 步骤 4: 环境配置

#### 4.1 进入 Docker 目录

```bash
cd infrastructure/docker
```

#### 4.2 检查脚本权限 (如果之前没有设置)

```bash
# Linux/macOS/WSL
chmod +x scripts/*.sh

# Windows (如果直接在 PowerShell 中)
# 脚本已包含 .bat 版本，或使用 WSL
```

### 步骤 5: 启动环境

#### 5.1 选择部署模式

**开发模式 (推荐新用户)**:
```bash
./scripts/start-local-env.sh --dev
```

**开发模式 + 存储服务**:
```bash
./scripts/start-local-env.sh --dev --with-storage
```

**完整模式 (包含所有服务)**:
```bash
./scripts/start-local-env.sh --full
```

#### 5.2 首次启动流程

脚本将执行以下步骤:
1. ✅ 检查 Docker 运行状态
2. ✅ 创建必要的目录
3. ✅ 生成环境配置文件 (.env)
4. ✅ 构建 Docker 镜像 (首次运行需要 10-15 分钟)
5. ✅ 启动所有服务
6. ✅ 健康检查

#### 5.3 交互式初始化

启动完成后，系统会提示进行初始化:

```
Do you want to run database migrations now? (y/N): y
```
输入 `y` 并按回车

```
Do you want to create a superuser account? (y/N): y
```
输入 `y` 并按回车，然后按提示创建管理员账户:
```
Username: admin
Email address: admin@example.com
Password: (输入密码，不会显示)
Password (again): (再次输入密码)
```

如果启用了存储服务:
```
Do you want to setup MinIO test data? (y/N): y
```
输入 `y` 设置测试数据

### 步骤 6: 验证服务状态

```bash
# 查看运行中的容器
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

---

## ✅ 验证部署

### 6.1 检查核心服务

打开浏览器，访问以下地址验证服务运行状态:

| 服务 | URL | 预期结果 |
|------|-----|---------|
| 🌐 前端应用 | http://localhost:3000 | JobQuest Navigator 登录页面 |
| 🔗 后端 API | http://localhost:8000 | API 根目录响应 |
| 🔧 Django 管理后台 | http://localhost:8000/admin/ | Django 管理登录页面 |
| 📊 API 文档 | http://localhost:8000/api/docs/ | API 文档页面 |

### 6.2 检查可选服务 (如果启用)

| 服务 | URL | 凭据 |
|------|-----|------|
| 📧 MailHog | http://localhost:8025 | 无需凭据 |
| 🗃️ MinIO | http://localhost:9001 | minioadmin / minioadmin123 |
| ☁️ LocalStack | http://localhost:4566 | test / test |
| 📈 Prometheus | http://localhost:9090 | 无需凭据 |
| 📊 Grafana | http://localhost:3003 | admin / admin123 |

### 6.3 功能测试

#### 测试用户注册和登录:
1. 访问 http://localhost:3000
2. 点击 "注册" 创建新账户
3. 使用新账户登录
4. 确认能够访问仪表板

#### 测试后端 API:
```bash
# 测试健康检查端点
curl http://localhost:8000/api/health/

# 测试用户认证 (使用创建的管理员账户)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'
```

---

## 🔧 常见问题排查

### Docker 相关问题

#### 问题 1: "Docker is not running"
**解决方案**:
```bash
# Windows
# 从开始菜单启动 Docker Desktop

# macOS
open /Applications/Docker.app

# 验证 Docker 状态
docker info
```

#### 问题 2: 端口被占用
**错误信息**: `Port 3000 is already in use`

**解决方案**:
```bash
# 查找占用端口的进程
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :3000
kill -9 <PID>

# 或者修改端口
docker-compose down
# 编辑 docker-compose.yml 修改端口映射
```

#### 问题 3: 内存不足
**错误信息**: `Container killed due to insufficient memory`

**解决方案**:
1. 在 Docker Desktop 设置中增加内存分配 (推荐 8GB)
2. 关闭其他不必要的应用程序
3. 使用最小模式启动:
```bash
./scripts/start-local-env.sh --minimal
```

### 网络连接问题

#### 问题 4: 容器间网络连接失败
**解决方案**:
```bash
# 重建网络
docker-compose down
docker network prune
docker-compose up -d

# 检查网络
docker network ls
docker network inspect docker_jobquest-network
```

#### 问题 5: API 无法访问
**解决方案**:
```bash
# 检查后端容器状态
docker-compose logs backend

# 检查健康状态
docker-compose ps backend

# 重启后端服务
docker-compose restart backend
```

### 数据库问题

#### 问题 6: 数据库连接失败
**解决方案**:
```bash
# 检查数据库容器
docker-compose logs database

# 检查数据库健康状态
docker-compose exec database pg_isready -U jobquest_user

# 重置数据库
./scripts/manage.sh db-reset
```

#### 问题 7: 迁移失败
**解决方案**:
```bash
# 手动运行迁移
./scripts/manage.sh migrate

# 检查迁移状态
./scripts/manage.sh showmigrations

# 如果严重损坏，重置数据库
./scripts/manage.sh db-reset
```

### 构建问题

#### 问题 8: Docker 镜像构建失败
**解决方案**:
```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建镜像
docker-compose build --no-cache

# 拉取最新基础镜像
docker-compose pull
```

#### 问题 9: 依赖安装失败
**解决方案**:
```bash
# 检查网络连接
ping pypi.org
ping registry.npmjs.org

# 使用国内镜像 (中国用户)
# 编辑 Dockerfile 添加镜像配置
```

### 权限问题

#### 问题 10: 文件权限错误 (Linux/macOS)
**解决方案**:
```bash
# 修复脚本权限
chmod +x infrastructure/docker/scripts/*.sh

# 修复数据目录权限
sudo chown -R $USER:$USER backend/media
sudo chown -R $USER:$USER backend/staticfiles
```

### 性能问题

#### 问题 11: 启动速度慢
**解决方案**:
1. **增加 Docker 资源分配**
2. **使用 SSD 硬盘**
3. **关闭不必要的服务**:
```bash
# 使用最小模式
./scripts/start-local-env.sh --minimal
```

#### 问题 12: 容器运行缓慢
**解决方案**:
```bash
# 检查资源使用情况
docker stats

# 优化 Docker 设置
# 在 Docker Desktop 中增加 CPU 和内存分配
```

### 日志和调试

#### 查看详细日志:
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f database

# 进入容器调试
docker-compose exec backend bash
docker-compose exec frontend sh
```

#### 调试网络问题:
```bash
# 检查容器网络
docker network ls
docker network inspect docker_jobquest-network

# 测试容器间连接
docker-compose exec backend ping database
docker-compose exec frontend ping backend
```

---

## 💻 开发工作流

### 日常开发操作

#### 启动开发环境:
```bash
cd infrastructure/docker
./scripts/start-local-env.sh --dev
```

#### 查看日志:
```bash
# 实时查看后端日志
./scripts/manage.sh logs

# 查看所有服务日志
docker-compose logs -f
```

#### Django 管理:
```bash
# 创建新的迁移
./scripts/manage.sh makemigrations

# 应用迁移
./scripts/manage.sh migrate

# 进入 Django shell
./scripts/manage.sh shell

# 运行测试
./scripts/manage.sh test
```

#### 停止环境:
```bash
# 软停止 (保留数据)
./scripts/stop-local-env.sh --soft

# 清理停止 (删除数据)
./scripts/stop-local-env.sh --clean

# 完全重置
./scripts/stop-local-env.sh --reset
```

### 代码更改和热重载

- **后端**: Django 代码更改会自动重载
- **前端**: React 代码更改会自动重新编译和刷新
- **数据库模型**: 需要手动运行迁移
- **配置更改**: 需要重启相应的容器

### 添加新依赖

#### Python 依赖:
```bash
# 进入后端容器
./scripts/manage.sh bash

# 安装新包
pip install package-name

# 更新 requirements.txt
pip freeze > requirements.txt

# 退出并重建镜像
exit
docker-compose build backend
```

#### Node.js 依赖:
```bash
# 进入前端容器
docker-compose exec frontend sh

# 安装新包
npm install package-name

# 更新 package.json (已自动更新)
```

---

## 🎯 下一步

成功部署后，您可以:

1. **探索应用功能**: 浏览前端界面，测试各种功能
2. **查看代码结构**: 熟悉 Django 和 React 代码组织
3. **运行测试**: 执行现有的单元测试和集成测试
4. **开始开发**: 根据项目需求添加新功能
5. **查看文档**: 阅读 [CLAUDE.md](./CLAUDE.md) 了解更多开发指导

### 有用的资源

- 📚 [项目文档](./docs/)
- 🐛 [故障排除指南](./docs/TROUBLESHOOTING_GUIDE.md)
- 🔧 [Docker 设置指南](./docs/DOCKER_MINIO_SETUP.md)
- 🚀 [部署指南](./docs/DEPLOYMENT_GUIDE.md)

### 获取帮助

如果遇到问题:
1. 查看本文档的故障排除部分
2. 检查项目 issues
3. 查看 Docker 和相关技术的官方文档
4. 联系项目维护者

---

**祝您开发愉快！** 🚀

> 这个部署指南涵盖了从零开始到完全运行的整个流程。如果您是新手，建议先使用开发模式启动，熟悉环境后再探索其他功能。