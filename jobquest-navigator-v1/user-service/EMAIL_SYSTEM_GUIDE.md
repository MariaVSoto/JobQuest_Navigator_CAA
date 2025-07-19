# JobQuest Navigator - Email System & Account Management Guide

## 📧 邮件通知系统

### 功能概览

JobQuest Navigator 现在包含完整的邮件通知系统和账户管理功能：

#### ✅ 已实现的邮件功能

1. **欢迎邮件** - 用户注册后自动发送
2. **邮箱验证邮件** - 包含验证链接
3. **密码重置邮件** - 安全的密码重置流程
4. **账户锁定通知** - 安全警告邮件
5. **账户暂停通知** - 管理员操作通知
6. **工作推荐邮件** - 个性化职位匹配

#### ✅ 已实现的账户管理功能

1. **用户状态管理** - 激活/暂停/锁定
2. **登录监控** - 失败尝试跟踪
3. **管理员界面** - 用户管理面板
4. **批量邮件** - 群发通知功能
5. **安全审计** - 登录日志记录

## 🚀 快速开始

### 1. 环境配置

在 `user-service/.env` 文件中添加邮件配置：

```env
# SMTP 邮件配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@jobquestnavigator.com
SMTP_FROM_NAME=JobQuest Navigator
SMTP_USE_TLS=true

# 前端URL配置
FRONTEND_URL=http://localhost:3002

# 账户管理配置
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION=300
PASSWORD_RESET_EXPIRE_HOURS=24
EMAIL_VERIFICATION_EXPIRE_HOURS=72
```

### 2. Gmail SMTP 设置

如果使用 Gmail SMTP：

1. 启用两步验证
2. 生成应用专用密码
3. 使用应用密码作为 `SMTP_PASSWORD`

### 3. 启动服务

```bash
cd user-service
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

## 📧 邮件模板系统

### 模板结构

```
app/templates/emails/
├── base.html              # 基础模板
├── welcome.html           # 欢迎邮件
├── email_verification.html # 邮箱验证
├── password_reset.html    # 密码重置
├── account_locked.html    # 账户锁定
├── account_suspended.html # 账户暂停
└── job_alert.html        # 工作推荐
```

### 自定义邮件模板

所有模板都使用 Jinja2 模板引擎，支持：

- 响应式设计
- 现代化UI样式
- 品牌一致性
- 多语言支持（预留）

## 🛡️ 账户管理功能

### 管理员API端点

#### 用户管理
```bash
# 获取用户列表
GET /admin/users?page=1&per_page=50&status_filter=active

# 获取用户状态
GET /admin/users/{user_id}/status

# 暂停用户账户
POST /admin/users/{user_id}/suspend
{
    "user_id": "uuid",
    "reason": "spam",
    "description": "User reported for spam",
    "suspended_until": "2024-01-01T00:00:00Z",
    "is_permanent": false
}

# 激活用户账户
POST /admin/users/{user_id}/activate

# 锁定用户账户
POST /admin/users/{user_id}/lock?duration_minutes=60
```

#### 邮件管理
```bash
# 发送单个邮件
POST /admin/email/send
{
    "to_email": "user@example.com",
    "to_name": "John Doe",
    "template": "welcome",
    "context": {"verification_token": "abc123"}
}

# 批量发送邮件
POST /admin/email/bulk-send
{
    "user_ids": ["uuid1", "uuid2"],
    "template": "job_alert",
    "context": {"job_matches": [...], "preferences": {...}}
}
```

#### 系统统计
```bash
# 获取管理员统计
GET /admin/stats/overview

# 获取最近活动
GET /admin/activity/recent?limit=50
```

## 🔧 配置选项

### 邮件服务配置

```python
# app/config.py
class Settings(BaseSettings):
    # SMTP配置
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: str = "noreply@jobquestnavigator.com"
    smtp_from_name: str = "JobQuest Navigator"
    smtp_use_tls: bool = True
    
    # 账户管理
    max_login_attempts: int = 5
    account_lockout_duration: int = 300  # 秒
    password_reset_expire_hours: int = 24
    email_verification_expire_hours: int = 72
```

### 安全设置

- **最大登录尝试次数**: 5次
- **账户锁定时长**: 5分钟
- **密码重置有效期**: 24小时
- **邮箱验证有效期**: 72小时

## 📈 监控和日志

### 日志记录

系统自动记录：
- 用户注册和登录活动
- 邮件发送状态
- 管理员操作
- 安全事件

### 错误处理

- 邮件发送失败自动重试
- 详细错误日志记录
- 优雅的降级处理

## 🎯 使用场景

### 用户生命周期

1. **注册** → 自动发送欢迎邮件 + 验证链接
2. **忘记密码** → 发送安全重置链接
3. **账户异常** → 自动锁定 + 通知邮件
4. **工作匹配** → 定期推荐邮件

### 管理员操作

1. **用户管理** → 查看、搜索、管理用户
2. **安全监控** → 跟踪登录尝试、锁定账户
3. **通知管理** → 发送通知、批量邮件
4. **系统监控** → 查看统计、活动日志

## 🔮 后续扩展

### 计划中的功能

1. **OAuth2社交登录** (LinkedIn, Google)
2. **角色权限管理** (求职者、雇主、招聘顾问)
3. **Redis会话管理** (高性能缓存)
4. **实时通知** (WebSocket推送)
5. **邮件队列系统** (Celery + Redis)
6. **多语言邮件模板**

### 性能优化

1. **异步邮件发送** ✅
2. **模板缓存**
3. **批量操作优化**
4. **数据库连接池**

## 🛠️ 故障排除

### 常见问题

#### 邮件发送失败
```bash
# 检查SMTP配置
# 验证网络连接
# 确认认证信息
```

#### 模板渲染错误
```bash
# 检查模板语法
# 验证上下文变量
# 确认文件路径
```

#### 权限问题
```bash
# 确认超级用户权限
# 检查路由保护
# 验证JWT令牌
```

### 调试命令

```bash
# 测试邮件配置
curl -X POST "http://localhost:8001/admin/email/send" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "test@example.com",
    "template": "welcome",
    "context": {}
  }'

# 检查用户状态
curl -X GET "http://localhost:8001/admin/users/USER_UUID/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📞 支持和反馈

- 查看日志: `user-service/logs/`
- API文档: `http://localhost:8001/docs`
- 源码: `user-service/app/`

这套邮件通知系统和账户管理功能为JobQuest Navigator提供了企业级的用户体验和安全保障！🎉