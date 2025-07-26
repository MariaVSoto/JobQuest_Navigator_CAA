# Phase 2: 架构重构 (1-2周)

## 概述
第二阶段专注于解决v2项目的架构问题，通过模块化和分层设计提升代码的可维护性和扩展性。

## 任务清单

### 任务1：拆分GraphQL巨型文件 🟡 中优先级
**目标文件**: `jobquest-navigator-v2/backend-fastapi-graphql/app/graphql/schema.py` (1644行)

**问题描述**:
- 单个文件过于庞大，违反单一职责原则
- 代码难以维护和扩展
- 团队协作困难

**重构目标结构**:
```
graphql/
├── schema.py              # 主schema聚合器
├── types/                 # GraphQL类型定义
│   ├── __init__.py
│   ├── user_types.py
│   ├── job_types.py
│   ├── company_types.py
│   └── common_types.py
├── queries/               # 查询解析器
│   ├── __init__.py
│   ├── user_queries.py
│   ├── job_queries.py
│   └── company_queries.py
├── mutations/             # 变更解析器
│   ├── __init__.py
│   ├── user_mutations.py
│   ├── job_mutations.py
│   └── company_mutations.py
└── resolvers/             # 复杂解析逻辑
    ├── __init__.py
    ├── user_resolvers.py
    ├── job_resolvers.py
    └── company_resolvers.py
```

**实施步骤**:
1. 分析当前schema.py的功能模块
2. 创建新的目录结构
3. 按业务领域拆分代码
4. 实现模块间依赖管理
5. 更新导入和注册逻辑
6. 验证功能完整性

**验收标准**:
- [ ] 单个文件不超过500行
- [ ] 模块职责清晰分离
- [ ] 所有GraphQL功能正常
- [ ] 性能无显著下降

### 任务2：实现服务层架构 🟡 中优先级
**目标**: 分离业务逻辑和数据访问层

**问题描述**:
- 业务逻辑直接写在GraphQL解析器中
- 缺少统一的业务服务层
- 代码复用性差

**新增架构层次**:
```
services/
├── __init__.py
├── base_service.py        # 基础服务类
├── user_service.py        # 用户业务逻辑
├── job_service.py         # 工作业务逻辑
├── company_service.py     # 公司业务逻辑
├── auth_service.py        # 认证业务逻辑
├── notification_service.py # 通知业务逻辑
└── cache_service.py       # 缓存服务
```

**实施步骤**:
1. 设计服务层接口规范
2. 创建基础服务类
3. 提取业务逻辑到服务层
4. 更新GraphQL解析器调用服务
5. 实现服务间依赖注入
6. 添加服务层单元测试

**验收标准**:
- [ ] 业务逻辑完全从解析器中分离
- [ ] 服务层职责清晰
- [ ] 代码复用性提升
- [ ] 易于单元测试

### 任务3：统一错误处理 🟡 中优先级
**目标**: 实现全局异常处理和标准化错误响应

**问题描述**:
- 错误处理不统一
- 缺少全局异常捕获
- 错误响应格式不一致

**实施方案**:
```python
# 错误处理中间件
class ErrorHandler:
    def __init__(self):
        self.error_types = {
            ValidationError: "VALIDATION_ERROR",
            PermissionError: "PERMISSION_DENIED",
            NotFoundError: "NOT_FOUND",
            AuthenticationError: "AUTHENTICATION_FAILED"
        }
    
    async def handle_error(self, error, info):
        # 统一错误处理逻辑
        pass

# 标准错误响应格式
{
    "errors": [{
        "message": "用户友好的错误信息",
        "code": "ERROR_CODE",
        "path": ["query", "field"],
        "timestamp": "2023-12-01T10:00:00Z",
        "trace_id": "unique-trace-id"
    }],
    "data": null
}
```

**实施步骤**:
1. 定义标准错误类型和代码
2. 实现全局错误处理中间件
3. 创建用户友好的错误消息
4. 添加错误日志和监控
5. 更新前端错误处理逻辑
6. 编写错误处理文档

**验收标准**:
- [ ] 统一的错误响应格式
- [ ] 全局异常捕获机制
- [ ] 错误日志完整记录
- [ ] 用户体验友好

## 实施时间表

### 第1周
- **第1-2天**: 任务1 - 拆分GraphQL文件
- **第3-4天**: 任务2 - 实现服务层架构
- **第5天**: 任务3开始 - 错误处理设计

### 第2周
- **第1-2天**: 完成任务3 - 统一错误处理
- **第3-4天**: 集成测试和优化
- **第5天**: 文档更新和代码审查

## 技术实现细节

### GraphQL模块化示例
```python
# graphql/schema.py - 主聚合器
import strawberry
from .queries.user_queries import UserQuery
from .queries.job_queries import JobQuery
from .mutations.user_mutations import UserMutation
from .mutations.job_mutations import JobMutation

@strawberry.type
class Query(UserQuery, JobQuery):
    pass

@strawberry.type
class Mutation(UserMutation, JobMutation):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
```

### 服务层设计模式
```python
# services/base_service.py
class BaseService:
    def __init__(self, db_session, cache_service=None):
        self.db_session = db_session
        self.cache = cache_service
    
    async def get_by_id(self, id: str):
        # 通用获取逻辑
        pass
    
    async def create(self, data: dict):
        # 通用创建逻辑
        pass

# services/user_service.py
class UserService(BaseService):
    async def create_user(self, user_data: UserInput):
        # 用户特定业务逻辑
        validated_data = self.validate_user_data(user_data)
        user = await self.create(validated_data)
        await self.send_welcome_email(user)
        return user
```

### 错误处理中间件
```python
# middleware/error_middleware.py
class GraphQLErrorMiddleware:
    def on_request_start(self, context):
        context.trace_id = generate_trace_id()
    
    def on_validation_error(self, error, context):
        return self.format_error(error, "VALIDATION_ERROR", context)
    
    def on_execution_error(self, error, context):
        logger.error(f"GraphQL执行错误: {error}", extra={
            "trace_id": context.trace_id,
            "user_id": context.user_id
        })
        return self.format_error(error, "EXECUTION_ERROR", context)
```

## 质量保证

### 代码审查要点
- [ ] 模块职责单一明确
- [ ] 接口设计合理
- [ ] 错误处理完善
- [ ] 测试覆盖充分
- [ ] 文档更新及时

### 性能考量
- [ ] 避免过度抽象影响性能
- [ ] 保持查询效率
- [ ] 合理使用缓存
- [ ] 监控关键指标

### 测试策略
```python
# 单元测试示例
class TestUserService:
    async def test_create_user_success(self):
        service = UserService(mock_db, mock_cache)
        user = await service.create_user(valid_user_data)
        assert user.email == valid_user_data.email
    
    async def test_create_user_duplicate_email(self):
        with pytest.raises(ValidationError):
            await service.create_user(duplicate_email_data)
```

## 迁移风险管理

### 向后兼容
- 保持GraphQL schema接口不变
- 渐进式重构，避免大爆炸式更改
- 保留原有API端点直到迁移完成

### 回滚策略
- 功能开关控制新旧代码切换
- 保留原代码备份
- 详细的回滚操作文档

### 监控指标
- API响应时间变化
- 错误率监控
- 内存和CPU使用情况
- 用户体验指标

## 完成标准

### 架构质量指标
1. **模块化**: 单个文件行数<500，职责清晰
2. **可测试性**: 业务逻辑易于单元测试
3. **可维护性**: 代码结构清晰，易于理解和修改
4. **可扩展性**: 新功能开发效率提升

### 交付物
- [ ] 重构后的代码库
- [ ] 架构设计文档
- [ ] API文档更新
- [ ] 单元测试套件
- [ ] 性能测试报告
- [ ] 迁移指南

## 后续规划
Phase 2完成后，将进入Phase 3的质量提升阶段，重点关注：
- 数据库查询优化
- 缓存策略完善
- 测试覆盖率提升