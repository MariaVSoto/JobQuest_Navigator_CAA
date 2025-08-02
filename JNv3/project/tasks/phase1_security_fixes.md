# Phase 1: 紧急安全修复 (1-3天)

## 概述
第一阶段专注于修复v2项目中的关键安全漏洞，这些问题可能导致严重的安全风险，必须立即处理。

## 任务清单

### 任务1：移除硬编码凭据 🔴 高优先级
**目标文件**: `jobquest-navigator-v2/backend-fastapi-graphql/app/core/config.py`

**问题描述**:
- 第37行：SECRET_KEY硬编码在代码中
- 第44-46行：AWS Cognito凭据硬编码
- 风险：凭据泄露可导致完全系统控制

**修复步骤**:
1. 创建`.env`环境变量文件模板
2. 将所有敏感凭据迁移到环境变量
3. 更新config.py使用环境变量
4. 添加.env到.gitignore
5. 创建生产环境配置指南

**验收标准**:
- [ ] 代码中无硬编码凭据
- [ ] 环境变量正确配置
- [ ] 应用正常启动和运行
- [ ] 生产部署指南更新

### 任务2：修复JWT安全问题 🔴 高优先级  
**目标文件**: `jobquest-navigator-v2/frontend-react-minimal/src/context/AuthContext.jsx`

**问题描述**:
- 第57-58行：JWT token存储在localStorage
- 风险：XSS攻击可窃取用户token

**修复步骤**:
1. 后端实现HttpOnly Cookie认证
2. 前端移除localStorage token存储
3. 实现CSRF保护机制
4. 更新认证流程
5. 测试新的安全认证

**验收标准**:
- [ ] Token通过HttpOnly Cookie传输
- [ ] 无法通过JavaScript访问token
- [ ] CSRF保护机制实施
- [ ] 认证功能正常工作

### 任务3：修复SQL注入风险 🔴 高优先级
**目标文件**: `jobquest-navigator-v2/backend-fastapi-graphql/app/graphql/schema.py`

**问题描述**:
- 第250-285行：使用字符串拼接构建查询
- 风险：恶意输入可执行任意SQL

**修复步骤**:
1. 识别所有字符串拼接查询
2. 使用参数化查询替代
3. 实现输入验证和清理
4. 添加查询日志监控
5. 安全测试验证

**验收标准**:
- [ ] 所有查询使用参数化方式
- [ ] 输入验证机制完善
- [ ] 安全扫描工具验证通过
- [ ] 查询性能不受影响

## 实施时间表

### 第1天
- **上午**: 分析和评估当前安全状况
- **下午**: 完成任务1 - 移除硬编码凭据

### 第2天  
- **上午**: 完成任务2 - 修复JWT安全问题
- **下午**: 开始任务3 - SQL注入修复

### 第3天
- **上午**: 完成任务3 - SQL注入修复
- **下午**: 综合测试和验证

## 风险评估

| 风险 | 影响级别 | 概率 | 缓解措施 |
|------|----------|------|----------|
| 修复过程中服务中断 | 中 | 低 | 在开发环境充分测试 |
| 破坏现有功能 | 高 | 中 | 保持原有API接口不变 |
| 性能下降 | 低 | 低 | 性能测试验证 |

## 技术要求

### 环境变量配置
```bash
# .env 文件模板
SECRET_KEY=your-secret-key-here
COGNITO_USER_POOL_ID=your-pool-id
COGNITO_CLIENT_ID=your-client-id
DATABASE_URL=your-database-url
REDIS_URL=your-redis-url
```

### HttpOnly Cookie实现
```python
# 后端Cookie设置
response.set_cookie(
    "auth_token",
    token,
    httponly=True,
    secure=True,
    samesite="strict",
    max_age=3600
)
```

### 参数化查询示例
```python
# 安全的查询方式
query = select(Job).where(Job.title.contains(bindparam('search_term')))
result = await session.execute(query, {'search_term': search_term})
```

## 测试计划

### 安全测试
- [ ] 渗透测试验证修复效果
- [ ] OWASP ZAP扫描
- [ ] 手动安全测试

### 功能测试  
- [ ] 用户认证流程测试
- [ ] API功能验证
- [ ] 前端功能确认

### 性能测试
- [ ] 查询性能基准测试
- [ ] 负载测试
- [ ] 响应时间监控

## 完成标准

### 必须达成的目标
1. **零硬编码凭据**: 所有敏感信息通过环境变量管理
2. **安全认证**: JWT通过HttpOnly Cookie传输
3. **防注入**: 所有数据库查询使用参数化方式
4. **功能完整**: 所有现有功能正常工作
5. **安全验证**: 通过安全扫描工具验证

### 交付物
- [ ] 修复后的源代码
- [ ] 环境变量配置模板
- [ ] 安全配置文档
- [ ] 测试报告
- [ ] 部署指南更新

## 后续步骤
Phase 1完成后，立即进入Phase 2的架构重构工作，包括：
- 拆分GraphQL巨型文件
- 实现服务层架构
- 统一错误处理机制