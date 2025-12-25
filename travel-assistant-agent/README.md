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
│   ├── agents/              # Agent 实现
│   │   ├── __init__.py
│   │   ├── base.py          # Agent 基类
│   │   ├── info_collection.py   # 信息收集 Agent
│   │   ├── search.py            # 搜索 Agent
│   │   ├── recommendation.py    # 推荐 Agent
│   │   └── booking.py           # 预订 Agent
│   ├── workflows/           # LangGraph 工作流
│   │   ├── __init__.py
│   │   └── planning_workflow.py
│   ├── tools/               # MCP 工具集成
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

### `POST /agent/start-planning`
启动旅行规划流程

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

## 🤖 Agent 架构

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

🔜 待完善功能：
- LLM 响应解析和结构化输出
- MCP (Model Context Protocol) 工具集成
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
