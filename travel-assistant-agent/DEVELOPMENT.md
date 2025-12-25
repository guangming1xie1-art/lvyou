# Development Guide

## 开发环境设置

### 方式一：本地开发（推荐用于快速迭代）

1. 创建虚拟环境
```bash
cd travel-assistant-agent
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
```

2. 安装依赖
```bash
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -e ".[dev]"
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填写 ANTHROPIC_API_KEY（如果需要真实的 Claude 调用）
```

4. 启动服务
```bash
cd src
python main.py

# 或使用 uvicorn 并启用自动重载
uvicorn main:app --app-dir src --reload --host 0.0.0.0 --port 8000
```

5. 验证服务
```bash
curl http://localhost:8000/health
```

### 方式二：Docker 开发（接近生产环境）

1. 启动完整环境（Agent + PostgreSQL）
```bash
cd travel-assistant-agent
docker-compose up -d
```

2. 查看日志
```bash
docker-compose logs -f agent
```

3. 停止服务
```bash
docker-compose down
```

4. 重新构建（代码修改后）
```bash
docker-compose up -d --build
```

## 项目结构说明

```
src/
├── main.py                  # FastAPI 应用入口
├── config.py                # 配置管理（读取 .env）
├── agents/                  # 4 个智能体实现
│   ├── base.py              # Agent 基类
│   ├── info_collection.py   # 信息收集 Agent
│   ├── search.py            # 搜索 Agent
│   ├── recommendation.py    # 推荐 Agent
│   └── booking.py           # 预订 Agent
├── workflows/               # LangGraph 工作流编排
│   └── planning_workflow.py # 旅行规划工作流
├── tools/                   # MCP 工具集成（占位）
│   └── mcp_tools.py
├── models/                  # 数据模型（Pydantic）
│   └── schemas.py
└── utils/                   # 工具模块
    ├── logger.py            # 日志配置
    ├── db.py                # PostgreSQL 连接
    ├── claude.py            # Claude API 客户端
    ├── api_client.py        # 后端 API 调用
    └── deepagent.py         # DeepAgent 占位
```

## 开发流程

### 1. 添加新的 Agent

继承 `BaseAgent` 并实现 `run` 方法：

```python
from agents.base import BaseAgent
from typing import Dict, Any

class MyNewAgent(BaseAgent):
    name = "my_new_agent"
    
    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # 处理逻辑
        state["my_result"] = "some result"
        return state
```

### 2. 修改工作流

在 `workflows/planning_workflow.py` 中添加节点：

```python
workflow.add_node("my_node", my_agent.run)
workflow.add_edge("previous_node", "my_node")
```

### 3. 添加 API 端点

在 `main.py` 中添加路由：

```python
@app.get("/my-endpoint")
async def my_endpoint():
    return {"message": "Hello"}
```

## 测试

### 运行测试
```bash
pytest
```

### 测试覆盖率
```bash
pytest --cov=src tests/
```

### 添加测试
在 `tests/` 目录下创建 `test_*.py` 文件：

```python
def test_my_function():
    result = my_function()
    assert result == expected_value
```

## 代码质量

### 格式化
```bash
# 使用 Black
black src/

# 使用 Ruff（更快）
ruff format src/
```

### Linting
```bash
ruff check src/ --fix
```

### 类型检查
```bash
mypy src/
```

## 调试技巧

### 1. 查看日志
本地开发时，日志会输出到 stdout。生产环境会同时写入 `logs/` 目录。

### 2. 调试 LangGraph 工作流
在 Agent 的 `run` 方法中添加日志：
```python
from utils.logger import app_logger

app_logger.debug(f"State before processing: {state}")
```

### 3. 测试 Claude API
```python
from utils.claude import claude_client

claude_client.init()
result = await claude_client.test_connection()
```

## 常见问题

### Q: Claude API 未配置怎么办？
A: 服务仍可启动，Agent 会使用 mock 数据。健康检查会显示 Claude 状态为 "not_configured"。

### Q: PostgreSQL 连接失败？
A: 检查 `.env` 中的 `DATABASE_URL`，确保 PostgreSQL 已启动（使用 Docker Compose 可自动启动）。

### Q: 如何添加新的环境变量？
A: 
1. 在 `.env.example` 中添加
2. 在 `config.py` 的 `Settings` 类中添加对应字段
3. 在需要的地方使用 `settings.your_variable`

### Q: 如何与前端集成？
A: 前端调用 `http://localhost:8000/agent/start-planning`，传入用户消息。Agent 返回处理结果。

## 部署

### 使用 Docker Compose（推荐）
```bash
docker-compose up -d
```

### 手动部署
```bash
pip install -r requirements.txt
uvicorn main:app --app-dir src --host 0.0.0.0 --port 8000 --workers 4
```

## 后续优化方向

1. **LLM 响应解析**：实现结构化输出解析（JSON mode）
2. **MCP 工具集成**：对接实际的搜索、预订工具
3. **DeepAgent**：集成深度推理能力
4. **异步任务**：使用 Celery/RQ 处理长时间运行的任务
5. **缓存**：添加 Redis 缓存热门查询
6. **监控**：集成 Prometheus + Grafana
7. **测试覆盖**：提升单元测试和集成测试覆盖率

## 相关资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [LangChain 文档](https://python.langchain.com/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [Claude API 文档](https://docs.anthropic.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
