# Travel Assistant Agent Service

基于 Python + FastAPI + LangChain + LangGraph 的 AI 旅游助手 Agent 服务。

## 🚀 技术栈

- **Python**: 3.10+
- **Web 框架**: FastAPI
- **LLM 框架**: LangChain v1.0+
- **工作流编排**: LangGraph v1.0+
- **大模型**: Claude 3.5 Sonnet (Anthropic API)
- **数据库**: PostgreSQL
- **容器化**: Docker + Docker Compose
- **日志**: Loguru
- **HTTP 客户端**: HTTPX

## 📁 项目结构

```
travel-assistant-agent/
├── pyproject.toml           # Poetry 项目配置
├── requirements.txt         # Python 依赖
├── Dockerfile               # Docker 镜像构建
├── docker-compose.yml       # 容器编排
├── .env.example             # 环境变量模板
├── README.md                # 项目文档
├── src/                     # 源代码目录
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── mcp_server/          # MCP Server & Skills
│   │   ├── __init__.py
│   │   ├── server.py        # MCP Server 实现
│   │   ├── config.py        # MCP 配置
│   │   ├── README.md        # MCP 文档
│   │   └── skills/          # Skills 实现
│   │       ├── __init__.py
│   │       ├── base_skill.py
│   │       ├── destination.py
│   │       ├── pricing.py
│   │       ├── reviews.py
│   │       ├── weather.py
│   │       └── planning.py
│   ├── agents/              # Agent 实现
│   │   ├── __init__.py
│   │   ├── base.py          # Agent 基类
│   │   ├── mcp_client.py    # MCP Client
│   │   ├── skill_agent.py   # Skill-based Agent
│   │   ├── info_collection.py   # 信息收集 Agent
│   │   ├── search.py            # 搜索 Agent
│   │   ├── recommendation.py    # 推荐 Agent
│   │   └── booking.py           # 预订 Agent
│   ├── workflows/           # LangGraph 工作流
│   │   ├── __init__.py
│   │   └── planning_workflow.py
│   ├── tools/               # 工具集成
│   │   ├── __init__.py
│   │   └── mcp_tools.py
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   └── schemas.py
│   └── utils/               # 工具函数
│       ├── __init__.py
│       ├── logger.py        # 日志配置
│       ├── db.py            # 数据库连接
│       ├── api_client.py    # API 客户端
│       └── claude.py        # Claude 客户端
└── tests/                   # 测试目录
    ├── __init__.py
    └── test_health.py
```

## 🛠️ 快速开始

### 1. 环境准备

确保已安装：
- Python 3.10+
- Docker & Docker Compose
- PostgreSQL (或使用 Docker)

### 2. 安装依赖

```bash
cd travel-assistant-agent

# 使用 pip
pip install -r requirements.txt

# (可选) 安装开发依赖
pip install -e ".[dev]"
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

**必需配置**：
- `ANTHROPIC_API_KEY`: Claude API 密钥

### 4. 启动服务

#### 方式一：本地运行

```bash
cd src
python main.py

# 或使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 方式二：Docker Compose

```bash
docker-compose up -d
```

服务将在 `http://localhost:8000` 启动。

### 5. 验证服务

```bash
# 健康检查
curl http://localhost:8000/health

# 根端点
curl http://localhost:8000/

# 启动旅行规划
curl -X POST http://localhost:8000/agent/start-planning \
  -H "Content-Type: application/json" \
  -d '{"user_message": "我想五一去北京玩3天，预算5000元"}'
```

## 📡 API 端点

### `GET /health`
健康检查端点

**响应示例**：
```json
{
  "status": "healthy",
  "app_env": "development",
  "components": {
    "database": "ok",
    "claude": "ok"
  }
}
```

### `GET /mcp/skills`
列出所有可用的 MCP Skills

**响应示例**：
```json
{
  "skills": [
    {
      "name": "search_destination",
      "description": "Search for travel destination information...",
      "category": "destination",
      "version": "1.0.0",
      "input_schema": {...},
      "output_schema": {...}
    }
  ],
  "total_count": 5
}
```

### `GET /mcp/status`
获取 MCP 客户端状态

**响应示例**：
```json
{
  "mcp_enabled": true,
  "connected": true,
  "skills_count": 5,
  "skills": [
    "search_destination",
    "query_prices",
    "get_destination_reviews",
    "get_weather",
    "create_travel_plan"
  ]
}
```

### `POST /mcp/call-skill`
调用单个 Skill

**请求体**：
```json
{
  "skill_name": "search_destination",
  "parameters": {
    "destination": "Tokyo",
    "include_tips": true
  }
}
```

**响应示例**：
```json
{
  "success": true,
  "skill_name": "search_destination",
  "result": {
    "destination": "Tokyo",
    "country": "Japan",
    "highlights": [...]
  },
  "execution_time_ms": 15.23
}
```

### `POST /mcp/batch-call`
批量调用多个 Skills（并行执行）

**请求体**：
```json
{
  "calls": [
    {"skill_name": "search_destination", "parameters": {"destination": "Tokyo"}},
    {"skill_name": "get_weather", "parameters": {"destination": "Tokyo"}}
  ]
}
```

### `POST /agent/demo-planning-with-skills`
使用 MCP Skills 进行旅行规划演示

**请求体**：
```json
{
  "destination": "Tokyo",
  "duration_days": 5,
  "budget": 2000,
  "start_date": "2024-04-01",
  "end_date": "2024-04-06",
  "interests": ["culture", "food"],
  "accommodation_type": "mid-range",
  "pace": "moderate",
  "use_template": "comprehensive"
}
```

**响应示例**：
```json
{
  "request_id": "uuid-string",
  "destination": "Tokyo",
  "skills_used": [
    "search_destination",
    "query_prices",
    "get_destination_reviews",
    "get_weather",
    "create_travel_plan"
  ],
  "skill_results": {...},
  "travel_plan": {
    "title": "Tokyo Adventure",
    "overview": "Experience the perfect blend...",
    "itinerary": [...],
    "budget_breakdown": {...},
    "packing_list": [...],
    "tips": [...]
  }
}
```

### `POST /agent/start-planning`
启动传统旅行规划流程（LangGraph 工作流）

**请求体**：
```json
{
  "user_message": "我想去北京旅游3天，喜欢文化和美食",
  "metadata": {
    "budget": "3000-5000",
    "preferences": ["文化", "美食"]
  }
}
```

**响应示例**：
```json
{
  "request_id": "uuid-string",
  "status": "completed",
  "result": {
    "collected_info": {...},
    "search_results": [...],
    "recommendations": [...],
    "booking_status": {...},
    "final_plan": {...}
  }
}
```

## 🤖 Claude Skills (MCP 集成)

本服务实现了 **Claude Skills** 通过 **MCP (Model Context Protocol)** 的集成，为 Agent 提供结构化的能力扩展。

### MCP Skills 架构

```
travel-assistant-agent (Python FastAPI)
    │
    ├── MCP Client (src/agents/mcp_client.py)
    │       │
    │       └── 连接到本地 Skills Registry
    │               │
    │               ├── SearchDestinationSkill  ── 目的地搜索
    │               ├── QueryPricesSkill        ── 价格查询
    │               ├── GetDestinationReviewsSkill ── 评论获取
    │               ├── GetWeatherSkill         ── 天气查询
    │               └── CreateTravelPlanSkill   ── 行程规划
```

### Skills 特性

| Skill | 功能 | 示例参数 |
|-------|------|---------|
| `search_destination` | 搜索目的地信息（景点、文化、最佳旅行时间） | `{"destination": "Tokyo"}` |
| `query_prices` | 查询酒店和机票价格 | `{"destination": "Tokyo", "check_in": "2024-04-01"}` |
| `get_destination_reviews` | 获取用户评价和评分 | `{"destination": "Tokyo", "limit": 5}` |
| `get_weather` | 查询天气预报 | `{"destination": "Tokyo", "start_date": "2024-04-01"}` |
| `create_travel_plan` | 生成完整旅行行程 | `{"destination": "Tokyo", "duration_days": 5, "budget": 2000}` |

### Skill 调用示例

```bash
# 1. 列出所有 Skills
curl http://localhost:8000/mcp/skills

# 2. 调用单个 Skill
curl -X POST http://localhost:8000/mcp/call-skill \
  -H "Content-Type: application/json" \
  -d '{"skill_name": "search_destination", "parameters": {"destination": "Tokyo"}}'

# 3. 批量调用 Skills
curl -X POST http://localhost:8000/mcp/batch-call \
  -H "Content-Type: application/json" \
  -d '{
    "calls": [
      {"skill_name": "search_destination", "parameters": {"destination": "Tokyo"}},
      {"skill_name": "get_weather", "parameters": {"destination": "Tokyo"}}
    ]
  }'

# 4. 演示完整规划流程
curl -X POST http://localhost:8000/agent/demo-planning-with-skills \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Tokyo",
    "duration_days": 5,
    "budget": 2000,
    "start_date": "2024-04-01",
    "end_date": "2024-04-06"
  }'
```

### Skill 工作流模板

系统提供三种预定义的工作流模板：

| 模板 | Skills | 用途 |
|------|--------|------|
| `basic` | destination → pricing → planning | 基础规划 |
| `comprehensive` | destination → pricing → reviews → weather → planning | 完整调研 |
| `quick` | destination → reviews | 快速了解 |

### 添加新 Skill

1. 在 `src/mcp_server/skills/` 创建新文件，继承 `BaseSkill`
2. 定义 `name`、`description`、`category`、`version`
3. 实现 `input_schema` 和 `output_schema`
4. 实现 `async execute()` 方法
5. 在 `skills/__init__.py` 注册 Skill

详细文档请参考：[MCP Server README](src/mcp_server/README.md)

### Agent 集成

`SkillBasedAgent` 类演示了如何将 Skills 整合到 Agent 决策流程：

```python
from agents import SkillBasedAgent

agent = SkillBasedAgent()
result = await agent.run({
    "user_message": "Plan a 5-day trip to Tokyo",
    "metadata": {"budget": 2000}
})
```

本服务使用 **LangGraph** 编排 4 个专门的 Agent：

### 1. InfoCollectionAgent (信息收集)
从用户输入中提取：
- 目的地
- 旅行时间
- 预算
- 偏好类型

### 2. SearchAgent (搜索)
查询相关信息：
- 景点
- 酒店
- 交通
- 天气等

### 3. RecommendationAgent (推荐)
基于搜索结果生成：
- 定制化行程方案
- 预算估算
- 亮点推荐

### 4. BookingAgent (预订)
转化推荐为预订请求（MVP 阶段为骨架）

## 🔄 工作流

LangGraph 工作流定义：

```
[用户输入]
    ↓
[InfoCollectionAgent] ─── 提取关键信息
    ↓
[SearchAgent] ─────────── 搜索景点/酒店
    ↓
[RecommendationAgent] ─── 生成推荐方案
    ↓
[BookingAgent] ────────── 预订处理
    ↓
[返回结果]
```

## 🧪 测试

```bash
# 运行测试
pytest

# 带覆盖率
pytest --cov=src tests/

# 运行单个测试文件
pytest tests/test_health.py
```

## 🔧 开发

### 代码格式化

```bash
# Black
black src/

# Ruff
ruff check src/ --fix
```

### 类型检查

```bash
mypy src/
```

## 🐳 Docker

### 构建镜像

```bash
docker build -t travel-assistant-agent:latest .
```

### 运行容器

```bash
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name travel-agent \
  travel-assistant-agent:latest
```

## 📝 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `APP_NAME` | 应用名称 | `travel-assistant-agent` |
| `APP_ENV` | 运行环境 | `development` |
| `APP_PORT` | 服务端口 | `8000` |
| `ANTHROPIC_API_KEY` | Claude API Key | *必需* |
| `CLAUDE_MODEL` | Claude 模型名称 | `claude-3-5-sonnet-20241022` |
| `DATABASE_URL` | PostgreSQL 连接 URL | - |
| `BACKEND_API_URL` | 后端服务地址 | `http://localhost:3000/api` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

## 🚧 MVP 阶段说明

当前为基础框架搭建阶段，包含：

✅ 完整的项目结构  
✅ FastAPI 应用框架  
✅ 4 个 Agent 骨架代码  
✅ LangGraph 工作流定义  
✅ Claude API 集成  
✅ PostgreSQL 连接  
✅ Docker 支持  
✅ MCP (Model Context Protocol) 工具集成  
✅ Claude Skills 实现（5个演示 Skills）  

🔜 待完善功能：
- LLM 响应解析和结构化输出
- DeepAgent 深度推理框架
- 异步任务队列
- 详细的业务逻辑实现
- 完整的测试覆盖

## 📚 相关文档

- [LangChain 文档](https://python.langchain.com/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Claude API 文档](https://docs.anthropic.com/)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT
