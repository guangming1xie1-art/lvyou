# lvyou 项目规范与约定

> OpenSpec 项目级配置文件 - lvyou 旅游助手 monorepo

## 项目愿景与目标

lvyou 是一个智能旅游助手平台，致力于为用户提供个性化、全方位的旅行规划服务。通过整合前端交互、Java 微服务后端和 AI Agent 能力，实现从旅行需求收集、方案规划到预订下单的全流程智能化体验。

### 核心目标

- **智能化规划**: 利用 Claude AI 能力提供个性化旅行方案
- **无缝体验**: 前后端 + AI Agent 协同，提供流畅的用户旅程
- **可扩展架构**: 微服务设计，支持功能模块化扩展
- **高质量交付**: 规范化的开发流程，确保代码质量和可维护性

## 技术栈概览

### travel-assistant-front (前端)

| 技术 | 版本/说明 |
|------|----------|
| React | 18.x |
| TypeScript | 5.x |
| Vite | 6.x |
| React Router | 6.x |
| TanStack Query | 5.x |
| Zustand | 5.x |
| Tailwind CSS | 3.x |
| Axios | 1.x |
| Vitest | 2.x |

### travel-assistant (Java 后端)

| 技术 | 版本/说明 |
|------|----------|
| Java | 17 |
| Spring Boot | 3.2.x |
| Spring Cloud | 2023.x |
| Spring Cloud Alibaba | 2023.x |
| Nacos | 服务发现 + 配置中心 |
| PostgreSQL | 15.x |
| Maven | 3.9.x |

### travel-assistant-agent (Python Agent)

| 技术 | 版本/说明 |
|------|----------|
| Python | 3.10+ |
| FastAPI | 0.109.x |
| LangChain | 1.0.x |
| LangGraph | 1.0.x |
| Claude API | 3.5 Sonnet |
| PostgreSQL | 15.x |
| MCP | 1.0.x |

## 架构概览与服务交互

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户浏览器                              │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  travel-assistant-front (React 18 + Vite)                       │
│  端口: 3000 (开发) / 80 (生产 Nginx)                            │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  travel-assistant (Spring Cloud Gateway)                        │
│  端口: 8080                                                      │
└───────┬─────────────────┬───────────────────┬───────────────────┘
        │                 │                   │
        ▼                 ▼                   ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────────────┐
│ auth-service  │ │ travel-       │ │ travel-plan-service   │
│ 端口: 8081    │ │ request-      │ │ 端口: 8083            │
│ JWT 认证      │ │ service       │ │ 行程规划              │
│               │ │ 端口: 8082    │ │                       │
│               │ │ 需求收集      │ │                       │
└───────────────┘ └───────────────┘ └───────────────────────┘
        │                 │                   │
        └─────────────────┼───────────────────┘
                          │
                          ▼ (内部 API 调用)
┌─────────────────────────────────────────────────────────────────┐
│  travel-assistant-agent (FastAPI + LangGraph + Claude)          │
│  端口: 8000                                                      │
│  功能: AI 旅行规划、目的地搜索、技能调用                         │
└─────────────────────────────────────────────────────────────────┘
```

### 服务职责边界

| 服务 | 职责 | 通信协议 |
|------|------|---------|
| frontend | 用户界面、交互逻辑、数据展示 | HTTP REST |
| gateway | 请求路由、认证转发、限流 | HTTP REST |
| auth-service | 用户认证、JWT 签发、权限验证 | HTTP REST |
| travel-request-service | 旅行需求收集、状态管理 | HTTP REST |
| travel-plan-service | 行程方案管理、订单协调 | HTTP REST |
| agent-service | AI 推理、技能执行、旅行规划 | HTTP REST |

## 命名规范

### 通用规范

- **文件命名**: 使用描述性名称，英文全小写，单词间用连字符 (`-`)
- **ID 命名**: 使用 UUID v4 格式
- **版本号**: 语义化版本 (Semantic Versioning) `MAJOR.MINOR.PATCH`

### 前端命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 组件 | PascalCase | `TravelPlanCard.tsx` |
| Hooks | camelCase，`use` 前缀 | `useTravelStore.ts` |
| 工具函数 | camelCase | `formatDate.ts` |
| 常量 | UPPER_SNAKE_CASE | `API_BASE_URL` |
| 类型/接口 | PascalCase | `TravelRequest` |
| CSS 类名 | kebab-case | `.travel-card` |
| 目录 | camelCase | `travelStore/` |

### Java 后端命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 类名 | PascalCase | `TravelPlanController` |
| 方法 | camelCase | `createTravelPlan()` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 包名 | 全小写 | `com.travelassistant.auth` |
| 表名 | snake_case | `travel_request` |
| 字段 | snake_case | `created_at` |

### Python Agent 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 类名 | PascalCase | `TravelPlanAgent` |
| 函数/方法 | snake_case | `create_travel_plan()` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 模块 | snake_case | `mcp_client.py` |
| 变量 | snake_case | `travel_request` |

### API 端点命名规范

```
# 基础格式
GET    /api/v1/{resource}           # 列表
GET    /api/v1/{resource}/{id}      # 详情
POST   /api/v1/{resource}           # 创建
PUT    /api/v1/{resource}/{id}      # 全量更新
PATCH  /api/v1/{resource}/{id}      # 部分更新
DELETE /api/v1/{resource}/{id}      # 删除

# 示例
GET    /api/v1/travel-requests
POST   /api/v1/travel-requests
GET    /api/v1/travel-requests/{id}
DELETE /api/v1/travel-requests/{id}
```

## 代码组织

### 前端目录结构

```
travel-assistant-front/src/
├── components/          # React 组件
│   ├── common/         # 通用组件 (Button, Input, Modal 等)
│   ├── layout/         # 布局组件 (Header, Footer, Sidebar)
│   └── travel/         # 业务组件 (TravelCard, PlanList)
├── hooks/              # 自定义 Hooks
│   ├── useAuth.ts
│   ├── useTravel.ts
│   └── useAsync.ts
├── pages/              # 页面组件
│   ├── Home.tsx
│   └── TravelPlan.tsx
├── services/           # API 服务层
│   ├── api.ts          # Axios 实例配置
│   ├── authService.ts
│   └── travelService.ts
├── store/              # Zustand 状态管理
│   ├── authStore.ts
│   └── travelStore.ts
├── theme/              # 主题配置
│   └── theme.ts
├── types/              # TypeScript 类型定义
│   └── index.ts
├── utils/              # 工具函数
│   ├── format.ts
│   └── validation.ts
├── App.tsx             # 根组件
├── main.tsx            # 入口文件
└── router.tsx          # 路由配置
```

### Java 后端目录结构

```
travel-assistant/{service}/
├── src/main/java/com/travelassistant/{module}/
│   ├── controller/     # REST 控制器
│   ├── service/        # 业务逻辑层
│   ├── repository/     # 数据访问层
│   ├── entity/         # 实体类
│   ├── dto/            # 数据传输对象
│   ├── mapper/         # MyBatis/MapStruct 映射
│   ├── exception/      # 异常处理
│   └── config/         # 配置类
└── src/main/resources/
    ├── application.yml
    └── mapper/         # SQL 映射文件
```

### Python Agent 目录结构

```
travel-assistant-agent/src/
├── main.py             # FastAPI 入口
├── config.py           # 配置管理
├── agents/             # Agent 实现
│   ├── base.py
│   ├── mcp_client.py
│   └── skill_agent.py
├── mcp_server/         # MCP Server & Skills
│   ├── server.py
│   └── skills/
│       ├── base_skill.py
│       └── destination.py
├── workflows/          # LangGraph 工作流
│   └── planning_workflow.py
├── models/             # Pydantic 数据模型
│   └── schemas.py
├── tools/              # 工具集成
│   └── mcp_tools.py
└── utils/              # 工具函数
    ├── logger.py
    └── api_client.py
```

## API 设计原则

### RESTful 规范

1. **资源命名**: 使用名词表示资源，使用复数形式
2. **HTTP 方法**: 正确使用 GET/POST/PUT/PATCH/DELETE
3. **版本控制**: URL 路径中包含版本号 `/api/v1/`
4. **响应格式**: 统一使用标准响应结构

### 标准响应格式

```json
{
  "code": 0,
  "message": "OK",
  "data": {},
  "timestamp": "2025-01-01T00:00:00Z"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| code | int | 状态码，0 表示成功 |
| message | string | 状态描述 |
| data | object | 响应数据 |
| timestamp | string | 响应时间 ISO 8601 格式 |

### 错误码规范

| 错误码范围 | 说明 |
|-----------|------|
| 0 | 成功 |
| 40001-40099 | 请求参数错误 |
| 40101-40199 | 认证错误 |
| 40301-40399 | 权限错误 |
| 40401-40499 | 资源不存在 |
| 50001-50099 | 服务端错误 |

### 分页查询规范

```
GET /api/v1/travel-requests?page=1&size=20&sort=created_at,desc
```

```json
{
  "code": 0,
  "message": "OK",
  "data": {
    "items": [],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 100,
      "totalPages": 5
    }
  }
}
```

## 数据库规范

### PostgreSQL 命名规范

- **表名**: snake_case 复数形式
- **主键**: `id` UUID 类型
- **时间戳**: `created_at`, `updated_at` TIMESTAMP WITH TIME ZONE
- **软删除**: `deleted_at` TIMESTAMP WITH TIME ZONE (可选)

### 通用表结构模板

```sql
CREATE TABLE travel_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    destination VARCHAR(255) NOT NULL,
    start_date DATE,
    end_date DATE,
    budget DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_travel_requests_user_id ON travel_requests(user_id);
CREATE INDEX idx_travel_requests_status ON travel_requests(status);
```

## 代码风格与格式化

### 前端代码规范

```json
// .eslintrc.json 核心规则
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react-hooks/recommended"
  ],
  "rules": {
    "react/react-in-jsx-scope": "off",
    "@typescript-eslint/explicit-function-return-type": "warn"
  }
}
```

### Java 代码规范

- **缩进**: 4 空格
- **行宽**: 120 字符
- **括号**: K&R 风格 (换行开括号)
- **命名**: 遵循 Java 命名约定

### Python 代码规范

- **风格**: Black 格式化 (行长度 88)
- **检查**: Ruff (E, F, I, W, B 规则)
- **类型**: Pydantic 模型用于数据验证

## 分支与版本策略

### Git 分支模型

```
main                    # 生产环境代码
├── develop             # 开发环境主分支
│   ├── feature/*       # 功能分支
│   ├── bugfix/*        # Bug 修复分支
│   └── release/*       # 发布分支
```

### 分支命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 功能 | `feature/` + 描述 | `feature/user-authentication` |
| Bug 修复 | `bugfix/` + 描述 | `bugfix/login-error` |
| 发布 | `release/` + 版本 | `release/v1.0.0` |
| 热修复 | `hotfix/` + 描述 | `hotfix/critical-security` |

### 版本号规范

- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向后兼容的功能新增
- **PATCH**: 向后兼容的 Bug 修复

示例: `v1.2.0` 表示第一个主要版本的第 2 个次要版本

## 测试要求

### 前端测试策略

| 测试类型 | 工具 | 覆盖率目标 | 说明 |
|---------|------|-----------|------|
| 单元测试 | Vitest | 70% | 组件、Hook、工具函数 |
| 集成测试 | Vitest | 50% | 多组件交互 |
| E2E 测试 | 可选 | - | 用户流程测试 |

### Java 后端测试策略

| 测试类型 | 工具 | 覆盖率目标 | 说明 |
|---------|------|-----------|------|
| 单元测试 | JUnit 5 + Mockito | 70% | Service 层逻辑 |
| 集成测试 | TestContainers | 40% | Repository 层 |
| API 测试 | REST Assured | 60% | Controller 层 |

### Python Agent 测试策略

| 测试类型 | 工具 | 覆盖率目标 | 说明 |
|---------|------|-----------|------|
| 单元测试 | pytest | 70% | Agent、工具函数 |
| 集成测试 | pytest | 50% | API 端点 |
| 异步测试 | pytest-asyncio | - | 异步工作流 |

## 文档标准

### 代码文档要求

1. **类/模块**: 必须包含 docstring 说明用途
2. **公开方法**: 必须包含 docstring 说明参数和返回值
3. **复杂逻辑**: 添加行内注释说明
4. **TODO**: 使用统一格式标注待办事项

### API 文档

- Java 后端: 使用 SpringDoc OpenAPI (Swagger UI)
- Python Agent: 使用 FastAPI 自动生成 OpenAPI

### README 要求

每个模块必须包含:

- 项目描述与技术栈
- 快速开始指南
- 环境配置说明
- 主要功能说明
- API 端点列表 (如适用)

## 部署与环境

### 环境配置

| 环境 | 前端端口 | Java 端口 | Agent 端口 | 说明 |
|------|---------|----------|-----------|------|
| local | 3000 | 8080-8084 | 8000 | 本地开发 |
| dev | 80 | 8080-8084 | 8000 | 开发环境 |
| prod | 80 | 8080-8084 | 8000 | 生产环境 |

### Docker Compose 服务

```yaml
# 核心服务端口映射
frontend:     80:80
gateway:      8080:8080
auth-service: 8081:8081
agent:        8000:8000
nacos:        8848:8848
postgres:     5432:5432
```

## 性能与可靠性

### 性能要求

| 指标 | 目标值 | 说明 |
|------|-------|------|
| API 响应时间 (P95) | < 500ms | 除 AI 推理外 |
| AI Agent 响应时间 | < 30s | 完整规划流程 |
| 前端 FCP | < 1.5s | 首次内容绘制 |
| 前端 TTI | < 3s | 可交互时间 |

### 可靠性要求

- **可用性**: 99.5% SLA
- **错误率**: < 1% 请求失败
- **数据一致性**: 关键操作使用事务

## 日志与监控

### 日志规范

| 服务 | 日志框架 | 日志级别 |
|------|---------|---------|
| 前端 | 浏览器控制台 | DEBUG (开发) / WARN (生产) |
| Java | SLF4J + Logback | INFO (正常) / WARN (警告) / ERROR (错误) |
| Python | Loguru | DEBUG (开发) / INFO (生产) |

### 关键日志点

- API 请求入口/出口
- 业务关键操作
- 错误与异常
- 性能相关 (耗时统计)

## 变更管理流程

### OpenSpec 变更生命周期

```
1. 创建变更提案    → openspec/changes/{change-name}/proposal.md
2. 技术设计评审    → openspec/changes/{change-name}/design.md
3. 任务分解        → openspec/changes/{change-name}/tasks.md
4. 实现与验证      → 代码实现
5. 规范更新        → specs/ 目录增量更新
6. 归档            → openspec archive {change-name}
```

### 变更触发条件

以下情况必须创建 OpenSpec 变更:

- 新功能开发 (涉及多服务/模块)
- API 接口变更
- 数据库结构变更
- 安全相关修改
- 性能优化 (影响架构)

以下情况可简化处理:

- 单纯 Bug 修复
- 文档更新
- 单模块内的微调

## 审批流程

| 变更类型 | 审批要求 | 说明 |
|---------|---------|------|
| 规范制定 | 技术负责人 | 初始规范定义 |
| 功能开发 | 代码评审 | PR 评审时确认 |
| 架构变更 | 团队评审 | 涉及多服务改动 |

## 附录: 快速参考

### 常用命令

```bash
# 前端
cd travel-assistant-front
npm install          # 安装依赖
npm run dev          # 开发模式
npm run build        # 生产构建
npm run lint         # 代码检查

# Java 后端
cd travel-assistant
mvn clean install    # 构建
mvn spring-boot:run  # 运行

# Python Agent
cd travel-assistant-agent
pip install -r requirements.txt
python src/main.py   # 或 uvicorn src.main:app --reload
```

### 外部服务地址

| 服务 | 地址 | 凭证 |
|------|------|------|
| Nacos | http://localhost:8848/nacos | nacos/nacos |
| API Gateway | http://localhost:8080 | - |
| Frontend | http://localhost:3000 | - |
| Agent | http://localhost:8000 | - |

---

*本文档由 OpenSpec 管理，修改后自动更新 AGENTS.md*
