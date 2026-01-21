# travel-assistant-front Mock API Server（Next.js）

本文档描述如何在 **travel-assistant-front** 项目中使用 **Next.js** 作为独立的 Mock API Server，用于前端快速开发与联调（无需真实后端）。

---

## 1. 项目结构详解

### 1.1 目录树（ASCII）

> 说明：`src/` 仍然是现有的 Vite + React 前端；`api/` 与 `pages/api/` 仅用于 Mock API Server。

```
travel-assistant-front/
├── src/                              # 现有前端代码（React + Vite）
│
├── api/                              # Mock API Server（业务实现）
│   ├── routes/
│   │   ├── auth.ts                   # /api/auth/* 认证：register/login/refresh/me/logout
│   │   ├── travel.ts                 # /api/v1/travel/* 旅游请求与方案
│   │   ├── attractions.ts            # /api/v1/attractions & /api/v1/restaurants
│   │   ├── orders.ts                 # /api/v1/orders
│   │   └── agent.ts                  # /api/agent/* + /api/v1/agent/* + /api/chat
│   │
│   ├── middlewares/
│   │   ├── auth.ts                   # JWT Bearer 校验
│   │   └── cors.ts                   # CORS + OPTIONS 预检
│   │
│   ├── models/
│   │   ├── db.ts                     # 内存数据库（全局单例，热更新不丢失）
│   │   ├── user.ts                   # 用户模型操作
│   │   ├── travel.ts                 # 旅游请求/方案模型操作 + 方案生成
│   │   ├── order.ts                  # 订单模型操作
│   │   ├── attraction.ts             # 景点/餐厅模型操作
│   │   └── types.ts                  # 所有模型类型定义
│   │
│   ├── mocks/
│   │   ├── flights.ts                # 航班模拟数据（120 条）
│   │   ├── hotels.ts                 # 酒店模拟数据（60 条）
│   │   ├── attractions.ts            # 景点模拟数据（25+ 条）
│   │   ├── restaurants.ts            # 餐厅模拟数据（40 条）
│   │   └── index.ts                  # mocks 聚合导出
│   │
│   ├── utils/
│   │   ├── jwt.ts                    # JWT 签发/校验（HS256）
│   │   ├── password.ts               # bcrypt 密码哈希
│   │   ├── validators.ts             # 分页/参数解析
│   │   ├── generators.ts             # uuid、随机数、delay
│   │   └── response.ts               # {code,message,data} 响应包装
│   │
│   ├── handler.ts                    # Next.js API 主路由（路由分发、CORS、日志）
│   └── [[...slug]].ts                # 需求约定的拦截器入口（export handler）
│
├── pages/
│   └── api/
│       └── [[...slug]].ts            # Next.js 实际生效的 catch-all API（转发到 api/handler.ts）
│
├── next.config.js                    # Next.js 配置 + rewrites（支持 /chat、/travel 等无前缀访问）
├── next-env.d.ts                     # Next.js TS 类型引用
├── .env.development                  # Mock API 开发环境变量
└── MOCK_API_SETUP.md                 # 本文档
```

### 1.2 文件职责说明

- `pages/api/[[...slug]].ts`
  - Next.js 真实的 API catch-all 路由（Next 约定目录）。
  - 仅做转发：`export { default } from '../../api/handler'`。

- `api/handler.ts`
  - 所有请求统一入口：
    - CORS headers
    - OPTIONS 预检
    - 路由分发（auth / v1 / agent / chat）
    - Debug 日志（`MOCK_API_DEBUG=true`）

- `api/models/db.ts`
  - 内存数据库，存储用户、刷新令牌、旅游请求/方案、订单、任务等。
  - 使用 `global.__MOCK_API_DB__` 保持热更新/重复加载时数据不丢失。

### 1.3 数据流向图（ASCII）

```
[React(Vite)]
    |
    |  HTTP (axios/fetch)
    v
[Next.js Mock API :3000]
    |
    |  handler.ts (CORS + Router)
    v
[routes/*]
    |
    |  CRUD / 生成逻辑
    v
[models/db.ts]  (内存数据)
    |
    v
 JSON Response
```

---

## 2. 快速开始指南

### 2.1 安装依赖

在 `travel-assistant-front/` 目录：

```bash
npm install
```

### 2.2 启动（推荐）

同时启动前端 + Mock API：

```bash
npm run dev
```

- Mock API：`http://localhost:3000`
- 前端（Vite）：通常是 `http://localhost:5173`

### 2.3 单独启动

- 仅 Mock API：

```bash
npm run dev:api
```

- 仅前端：

```bash
npm run dev:frontend
```

### 2.4 Debug（打印路由日志）

```bash
npm run dev:debug
```

---

## 3. API 参考文档

### 3.1 统一响应格式（除 auth 外）

除 `/api/auth/*` 外，其它接口使用统一包装：

```json
{ "code": 200, "message": "success", "data": "..." }
```

### 3.2 认证系统（JWT + Refresh）

- Access Token：1h（默认 `JWT_EXPIRE_IN=1h`）
- Refresh Token：7d（默认 `JWT_REFRESH_EXPIRE_IN=7d`）
- 算法：HS256
- 密码：bcrypt

#### 3.2.1 注册

`POST /api/auth/register`

Request:
```json
{ "username": "demo", "email": "demo@example.com", "password": "123456", "confirm_password": "123456" }
```

Response:
```json
{ "id": "...", "username": "demo", "email": "demo@example.com", "is_active": true, "created_at": "...", "last_login": null }
```

#### 3.2.2 登录

`POST /api/auth/login`

Response（与前端 `src/types/auth.ts` 对齐）：
```json
{
  "user": {
    "id": "...",
    "username": "demo",
    "email": "demo@example.com",
    "is_active": true,
    "created_at": "...",
    "last_login": "..."
  },
  "tokens": {
    "access_token": "...",
    "refresh_token": "...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

#### 3.2.3 刷新 Token（旋转刷新）

`POST /api/auth/refresh`

Request:
```json
{ "refresh_token": "..." }
```

Response:
```json
{ "access_token": "...", "refresh_token": "...", "token_type": "Bearer", "expires_in": 3600 }
```

#### 3.2.4 获取当前用户

`GET /api/auth/me`（需要 `Authorization: Bearer <access_token>`）

#### 3.2.5 登出

`POST /api/auth/logout`（需要 Authorization）

会撤销当前用户所有 refresh token。

---

## 4. 旅游请求与方案

接口前缀：`/api/v1`

### 4.1 旅游请求 CRUD

- `POST   /api/v1/travel/requests`
- `GET    /api/v1/travel/requests?page=&page_size=&destination=&keyword=`
- `GET    /api/v1/travel/requests/:id`
- `PUT    /api/v1/travel/requests/:id`
- `DELETE /api/v1/travel/requests/:id`

### 4.2 方案

- `GET  /api/v1/travel/requests/:requestId/plans`
- `GET  /api/v1/travel/plans/:planId`
- `POST /api/v1/travel/plans/compare`  body: `{ "plan_ids": ["...","..."] }`

> Mock 行为：创建旅游请求后会自动生成 3-5 个方案，每个方案包含 7-10 天游玩日程 + 费用明细 + 亮点。

---

## 5. 景点 / 餐厅

- `GET /api/v1/attractions?page=&page_size=&destination=`
- `GET /api/v1/attractions/:id`
- `GET /api/v1/attractions/search?destination=&keyword=&page=&page_size=`

- `GET /api/v1/restaurants?page=&page_size=&destination=`
- `GET /api/v1/restaurants/:id`
- `GET /api/v1/restaurants/search?destination=&keyword=&cuisine_type=&page=&page_size=`

---

## 6. 订单

- `POST /api/v1/orders`
- `GET  /api/v1/orders?page=&page_size=&status=`
- `GET  /api/v1/orders/:orderId`
- `PUT  /api/v1/orders/:orderId`
- `POST /api/v1/orders/:orderId/cancel`
- `POST /api/v1/orders/:orderId/pay` → 返回 `{ payment_url }`

状态逻辑：

```
pending + unpaid
   | (pay)
   v
confirmed + paid
   | (可自行扩展为 completed)
   v
completed

(cancel)
   v
cancelled (+ refunded if already paid)
```

---

## 7. Agent API（聊天 + 任务）

支持两套路径（方便兼容不同前端调用方式）：

- `/api/agent/*`
- `/api/v1/agent/*`（经 handler 统一转发）

### 7.1 聊天

- `POST /chat`（Next rewrite → `/api/chat`）
- `POST /api/agent/chat`

### 7.2 搜索/推荐/预订

- `POST /api/agent/search`
- `POST /api/agent/recommend`
- `POST /api/agent/book`

Mock 行为：1-2 秒延迟后返回模拟结果，并生成 `task_id`。

### 7.3 任务状态轮询

- `GET /api/agent/status/:taskId`
- `GET /api/agent/tasks`

任务状态：`pending → processing → completed`（或 `failed`）。

---

## 8. 模拟数据详情

### 8.1 航班（120 条）

- 城市：北京/上海/杭州/西安/成都/广州/深圳
- 航司：国航/东航/南航/海南/厦航/春秋
- 搜索时会根据 `origin/destination` 进行匹配；找不到匹配则随机补齐。

### 8.2 酒店（60 条）

- 分布在多个城市、商圈
- 提供 rating、图片（picsum）、价格、设施等字段

### 8.3 景点（25+）与餐厅（40）

- 覆盖：北京、上海、杭州、西安、成都
- 详情包含评分、开放时间、票价/人均、图片等

如何扩展：直接修改 `api/mocks/*.ts` 的生成规则，或添加新的城市数据。

---

## 9. 迁移到真实 API 指南

当后端就绪后，你可以：

1. 修改环境变量：
   - 将 `VITE_API_BASE_URL` 指向真实网关（例如 `http://localhost:8080/api/v1`）
   - 将 `VITE_AGENT_API_BASE_URL` 指向真实 Agent 服务
2. 检查接口兼容性：
   - 认证接口：`/api/auth/*` 的响应结构是否与前端 `src/types/auth.ts` 一致
   - 业务接口：是否使用 `{code,message,data}` 包装（或前端 axios 拦截器需要调整）
3. 逐个替换：
   - 先替换 travel/orders/attractions
   - 最后替换 agent（因涉及任务轮询/流式）

---

## 10. 开发技巧

### 10.1 新增一个 API 端点

1. 在 `api/routes/` 新建模块或在现有模块中增加分支
2. 在 `api/handler.ts` 中挂载路由
3. 如需数据存储：在 `api/models/db.ts` 中新增字段

### 10.2 修改响应数据

- 业务接口统一使用：`sendWrapped(res, data)`
- 错误响应：`sendError(res, 400, 'message')`

### 10.3 常见问题

- Q：前端请求 404？
  - A：确认走的是 Mock API（查看 `.env.development`），以及 URL 是否被 `next.config.js` rewrite 覆盖。

- Q：401 并跳转登录？
  - A：需要先调用 `/api/auth/login` 获取 token；并在请求中携带 `Authorization: Bearer ...`。

---

## 附：交互流程图

### JWT 认证流程

```
[Frontend]
   |
   |  Authorization: Bearer <access_token>
   v
[Mock API] -- verify JWT --> [OK] -> route handler
   |
   +-- expired/invalid --> 401 (前端触发 refresh)
```

### Agent 任务轮询流程

```
POST /api/agent/search  ->  { task_id, results... }
        |
        v
GET  /api/agent/status/:task_id  -> pending/processing/completed
```
