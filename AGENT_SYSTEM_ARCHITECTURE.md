# Lvyou Agent 系统架构文档（LangChain v1 + LangGraph v1 + DeepAgent v0.2.7）

> 目标：在 **LangGraph v1.0** 中集中控制所有业务流程与分支细节；用 **DeepAgent v0.2.7 子智能体**减少 token；以 **LangChain v1.0** 实现可演进的 RAG（向量 + BM25 混合检索）；兼容多大模型并做成本最优；通过 **Prompt Cache + Redis 缓存层 + 高并发优化 + MCP + Skills 按需加载** 将延迟、成本与 token 消耗降到最低。

---

## 版本与核心约束（硬性要求）

- **langchain**: `>=1.0.0,<2.0.0`
- **langgraph**: `>=1.0.0,<2.0.0`
- **deepagent**: `>=0.2.7,<0.3.0`

设计原则：
1. **LangGraph 是唯一的流程真相来源（Single Source of Truth）**：所有业务分支、重试、降级、缓存策略都由 LangGraph 节点与 conditional edges 决定。
2. **DeepAgent 只做“子任务推理 + 结构化输出”**：最大化复用主工作流状态，最小化对话历史传入，减少 token。
3. **工具（Tools）与 Skills 按需加载**：在不同阶段只加载必要工具定义，降低“工具定义 token”与误调用概率。
4. **成本最优优先**：默认用便宜层模型执行规划/抽取/格式化，用标准层做检索/推荐，用强力层仅在“高价值推理”时触发。

---

## 1. 系统整体架构

### 1.1 三层逻辑结构

- **主工作流（LangGraph）**：控制所有业务细节与分支（规划/执行/缓存/回滚/重试/降级）。
- **子智能体（DeepAgent）**：Search / Recommendation / Booking 三个子智能体，专注各自领域推理与结构化输出，减少 token。
- **工具调用层（Tools/Skills）**：RAG 检索、外部搜索、供应商预订、支付、用户画像、价格对比等。

### 1.2 组件拓扑图（ASCII）

```text
┌────────────────────────────┐
│ Frontend (Single Chat UI)   │
│ - Web / Mobile / MiniApp    │
│ - SSE streaming             │
└──────────────┬─────────────┘
               │ HTTP(S)
               ▼
┌──────────────────────────────────────────────────────────────┐
│ Backend API (FastAPI)                                        │
│ - /chat (SSE)                                                 │
│ - /tasks                                                     │
│ - /mcp/* (skills registry & dispatch)                         │
│ - Auth / RateLimit / Observability                            │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│ LangGraph v1 Workflow Orchestrator                            │
│ - StateGraph(ConversationState)                               │
│ - entry → ... → response → end                                │
│ - Branching / Retry / Budget / Cache decisions                │
└───────┬───────────────────┬───────────────────┬──────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ DeepAgent       │  │ DeepAgent         │  │ DeepAgent         │
│ SearchAgent     │  │ RecommendationAgent│  │ BookingAgent      │
│ (token saver)   │  │ (token saver)      │  │ (token saver)     │
└───────┬────────┘  └──────────┬────────┘  └──────────┬────────┘
        │                       │                     │
        ▼                       ▼                     ▼
┌──────────────────────────────────────────────────────────────┐
│ Tools / Skills Layer (MCP + LangChain Tools)                  │
│ - Search APIs, Supplier APIs, Payment, Profile, etc.          │
│ - RAG Retriever (Vector + BM25)                               │
│ - Structured schemas                                           │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│ Data Layer                                                     │
│ - Redis (cache + prompt cache metadata + rate limit)           │
│ - Vector Store (pgvector/qdrant/redis vector)                  │
│ - BM25 Index (in-memory + persisted snapshot)                  │
│ - PostgreSQL (orders/users/logs/docs metadata)                 │
└──────────────────────────────────────────────────────────────┘
```

### 1.3 交互数据流（描述性流程图）

```text
User → UI → /chat (SSE)
  → LangGraph(entry)
    → search_planning (cheap/standard)
    → search_execution (DeepAgent Search + tools + Redis cache)
    → recommend_planning
    → recommend_execution (DeepAgent Rec + RAG)
    → booking_planning (若用户触发预订)
    → booking_execution (DeepAgent Booking + supplier tools)
    → response (stream to UI)
  → end

任何节点：
  - 可读取/写入 Redis 缓存
  - 可触发模型降级
  - 可触发重试/回滚/短路（cache hit 直接跳过执行）
```

**Token/成本优化点（全局）**
- 主工作流不把完整对话历史传给子智能体：只传递 **结构化的 ConversationState** + 必要摘要。
- 子智能体只加载当下阶段工具定义（Skills 按需加载），减少“工具描述 token”。
- Prompt Cache：系统提示词/工具定义/RAG 结构化上下文尽量固定，利用“头部缓存/前缀缓存”。

---

## 2. LangGraph v1.0 工作流设计

### 2.1 StateGraph 结构定义

**核心约束**：LangGraph 控制全部分支与业务细节。

```python
from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict, Literal
from langgraph.graph import StateGraph, END

Stage = Literal[
    "entry",
    "search_planning", "search_execution",
    "recommend_planning", "recommend_execution",
    "booking_planning", "booking_execution",
    "response", "end"
]

class ConversationState(TypedDict, total=False):
    request_id: str
    user_id: str
    user_message: str

    stage: Stage
    locale: str

    # 结构化用户需求（由 info extraction / planning 生成）
    intent: Optional[str]
    constraints: Dict[str, Any]

    # 中间结果
    search_plan: Dict[str, Any]
    search_results: Dict[str, Any]

    recommend_plan: Dict[str, Any]
    recommendations: Dict[str, Any]

    booking_plan: Dict[str, Any]
    booking_result: Dict[str, Any]

    # RAG
    rag_query: Optional[str]
    rag_context: List[Dict[str, Any]]

    # 预算/成本
    budget_tokens: Dict[str, int]           # per stage token budget
    cost_estimate_usd: float

    # 缓存命中信息
    cache_hits: Dict[str, str]              # key -> hit/miss

    # 错误与重试
    error: Optional[str]
    retry_count: int
    should_retry: bool
```

### 2.2 节点设计（entry → ... → end）

节点职责（严格分层）：
- **planning 节点**：只做“决策/拆解/参数化”，尽量使用 cheap 模型；输出结构化 plan。
- **execution 节点**：只做“调用子智能体/工具”，并写缓存。

推荐的节点列表（满足需求中的节点顺序）：

1. `entry`
2. `search_planning`
3. `search_execution`
4. `recommend_planning`
5. `recommend_execution`
6. `booking_planning`
7. `booking_execution`
8. `response`
9. `end`

### 2.3 条件分支逻辑

- `entry → search_planning`：默认进入搜索规划。
- `search_execution → recommend_planning`：搜索成功（或缓存命中）则进入推荐。
- `recommend_execution → booking_planning`：仅当用户明确表达“预订/下单/支付”意图时进入预订规划，否则直接响应。
- 任意节点失败：进入 `response` 输出“可恢复错误 + 下一步建议”；必要时 `should_retry=True` 回到对应 planning。

```python

def should_book(state: ConversationState) -> str:
    # 强制用结构化字段判断，避免把整段对话再丢给 LLM
    intent = (state.get("intent") or "").lower()
    if intent in {"book", "booking", "pay"}:
        return "booking_planning"
    return "response"


def build_graph():
    g = StateGraph(ConversationState)

    g.add_node("entry", entry)
    g.add_node("search_planning", search_planning)
    g.add_node("search_execution", search_execution)
    g.add_node("recommend_planning", recommend_planning)
    g.add_node("recommend_execution", recommend_execution)
    g.add_node("booking_planning", booking_planning)
    g.add_node("booking_execution", booking_execution)
    g.add_node("response", response)

    g.set_entry_point("entry")

    g.add_edge("entry", "search_planning")
    g.add_edge("search_planning", "search_execution")
    g.add_edge("search_execution", "recommend_planning")
    g.add_edge("recommend_planning", "recommend_execution")

    g.add_conditional_edges("recommend_execution", should_book, {
        "booking_planning": "booking_planning",
        "response": "response",
    })

    g.add_edge("booking_planning", "booking_execution")
    g.add_edge("booking_execution", "response")

    g.add_edge("response", END)

    return g.compile()
```

**Token/成本优化点（LangGraph 层）**
- planning 与 execution 拆分：planning 模型更便宜、输出更短、结构化。
- 分支判断尽量不调用 LLM，使用结构化字段（intent/flags），避免额外 token。
- 通过节点级缓存与短路减少“重复搜索/重复推荐”。

---

## 3. DeepAgent 子智能体架构（v0.2.7）

### 3.1 设计目标：为什么 DeepAgent 能省 token？

传统做法：主 Agent 在一次对话中携带大量历史、工具说明、上下文，导致 prompt 体积膨胀。

DeepAgent 子智能体做法：
- 主工作流只传递 **子任务所需最小输入**（结构化状态 + 必要摘要）。
- 子智能体系统提示词保持稳定（利于 Prompt Cache）。
- 子智能体工具集合按需加载（减少工具定义 token）。

### 3.2 SearchAgent 设计

**输入**（最小集合）：
- 用户目标/偏好结构化字段（目的地、时间、预算、人数、偏好）
- search_plan（来自 search_planning）

**工具**（按需加载）：
- `search_flights`, `search_hotels`, `filter_by_budget`, `compare_results`
- RAG 检索工具（可选，若需要本地知识）

**输出**（结构化）：
- 搜索结果（候选 flights/hotels/套餐）
- 覆盖度与可信度评分

```python
from deepagent import DeepAgent  # deepagent>=0.2.7 (示意)

search_agent = DeepAgent(
    name="SearchAgent",
    system_prompt=SEARCH_SYSTEM_PROMPT,  # 稳定，利于 cache
    tools=load_skills(agent_type="search", only=[
        "search_flights", "search_hotels", "compare_results", "filter_by_budget"
    ])
)

result = await search_agent.ainvoke({
    "constraints": state["constraints"],
    "plan": state["search_plan"],
})
state["search_results"] = result
```

### 3.3 RecommendationAgent 设计（推荐 + RAG）

**输入**：
- search_results（候选集）
- rag_context（来自 RAG 混合检索）
- recommend_plan（来自 recommend_planning）

**推荐逻辑**：
- 强制结构化输出（JSON schema），减少自然语言冗余。
- 在推荐执行阶段才加载“目的地信息/天气/评价”类 skills。

**输出**：
- 3~5 个候选方案（分层：省钱/舒适/高端）
- 每个方案包含证据引用（来自 rag_context），减少“重复解释” token。

### 3.4 BookingAgent 设计（预订流程与验证）

**输入**：
- 用户确认的方案 id
- 乘机人/入住人信息（结构化）
- 支付方式/发票需求

**工具**：
- `create_booking`, `process_payment`, `confirm_booking`, `get_booking_status`

**关键策略**：
- 所有外部操作（下单/扣款）必须走“工具调用层”，LLM 不直接拼接请求。
- 重要字段二次校验：由工具层返回校验错误，不让 LLM 猜。

### 3.5 子智能体协作机制

- 主工作流负责“子智能体之间的结果传递与依赖关系”。
- 子智能体之间不直接对话，避免 token 叠加。

```text
LangGraph State
  ├── search_results  → RecommendationAgent
  ├── recommendations → BookingAgent
  └── booking_result  → response
```

**Token/成本优化点（DeepAgent 层）**
- 子智能体输入是“结构化 state”，不传长对话历史：通常可减少 30%~70% prompt 体积。
- 每个子智能体固定系统提示词：利于 Prompt Cache（尤其是系统提示 + 工具定义）。

---

## 4. RAG 知识库与检索（LangChain v1.0）

### 4.1 知识库数据结构

- **向量索引（Vector Store）**：用于语义相似检索（适合“景点特色/玩法/注意事项”）。
- **BM25 索引**：用于关键词/实体检索（适合“门票价格/交通方式/政策条款/酒店名称”）。
- 文档元数据（PostgreSQL）：source、更新时间、语言、地区、可信度、版本。

建议数据模型：

```text
documents
  - doc_id (uuid)
  - title
  - content
  - locale
  - tags
  - source
  - updated_at
  - hash (用于缓存/增量更新)

vector_store
  - doc_id
  - embedding

bm25_index
  - snapshot_version
  - serialized_index (blob)
```

### 4.2 混合检索策略（Vector + BM25）

- 先分别取 TopK：`vector_top_k` 与 `bm25_top_k`
- 再做合并与重排（Rerank）
- 最终输出统一 `rag_context`（带引用）

```python
# 伪代码：Ensemble Retriever

def hybrid_retrieve(query: str) -> list[dict]:
    vec_hits = vector_retriever.search(query, k=20)
    bm25_hits = bm25_retriever.search(query, k=20)

    merged = dedupe_by_doc_id(vec_hits + bm25_hits)
    reranked = rerank(query, merged, method="reciprocal_rank_fusion")

    return reranked[:8]
```

### 4.3 Embedding 模型选择（成本考虑）

优先策略：
1. **本地/开源 embedding**（如 bge-small-zh / gte-small）
   - 优点：单次成本几乎为 0（仅算力）
   - 适用：知识库固定、更新频率可控
2. **云 embedding（如 OpenAI/通义/智谱 embedding）**
   - 优点：质量稳定、部署简单
   - 缺点：按量收费，知识库大时成本上升

建议：
- **离线批量构建 embedding** + **增量更新**，避免在线每次写入都触发 embedding。

### 4.4 知识库更新机制

- 批处理（每天/每小时）采集 → 清洗 → 分块（chunk）→ embedding → 写入 vector store
- BM25 索引生成快照（snapshot_version），并在服务启动时加载最新快照
- Redis 缓存 RAG 结果 24h（对“热门目的地”节省大量 token + 降延迟）

**Token/成本优化点（RAG）**
- 用 RAG 上下文替代长解释：减少 LLM“重复生成事实” token。
- `rag_context` 结构化与限长：控制输出 token。

---

## 5. 多模型兼容方案（成本最优）

### 5.1 统一的 ChatOpenAI 接口（base_url 方式）

核心策略：用 OpenAI-compatible 协议统一接入（Claude/Qwen/DeepSeek/GLM 等），避免业务代码写 provider 分支。

代码示意（与现有 `LLMFactory` 思路一致）：

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen-turbo",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    temperature=0.3,
    max_tokens=2048,
)
```

### 5.2 模型配置管理（示例）

建议将模型配置集中化（类似 `travel-assistant-agent/src/config/llm_config.py`）：

```python
MODEL_CONFIGS = {
  "deepseek-chat": {
    "tier": "cheap",
    "base_url": "https://api.deepseek.com/v1",
    "model": "deepseek-chat",
    "cost": "low"
  },
  "qwen-turbo": {
    "tier": "standard",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model": "qwen-turbo",
    "cost": "mid"
  },
  "claude-3.5-sonnet": {
    "tier": "power",
    "base_url": "https://api.anthropic.com/v1", 
    "model": "claude-3-5-sonnet-20241022",
    "cost": "high"
  }
}
```

### 5.3 成本预算管理

- 每个请求维护 `budget_tokens` 与 `cost_estimate_usd`
- 当达到预算上限：
  - 优先降级模型 tier（power → standard → cheap）
  - 其次减少 TopK（检索/候选数）
  - 最后减少输出长度（max_tokens）

### 5.4 动态模型选择策略

推荐默认策略：
- `planning`：cheap tier（DeepSeek Chat / Qwen Plus）
- `search_execution`：standard tier（Qwen Turbo / GLM-4）
- `recommend_execution`：standard tier；仅当用户需求复杂或约束冲突时升到 power
- `booking_execution`：cheap/standard（以工具调用为主，LLM 只负责校验与解释）

**Token/成本优化点（多模型）**
- 用 cheap 模型做“规划/抽取/格式化”，通常能将总成本降低 70%~95%。

---

## 6. Prompt Cache 机制（头部缓存/前缀缓存）

### 6.1 需要启用 Cache 的内容

优先缓存“稳定且复用频率高”的 prompt 前缀：
1. 系统提示词（system prompt）
2. 工具定义（tools/skills schema）
3. RAG 上下文模板（不是内容本身，而是“拼接格式”与“引用规则”）
4. 规范化输出 schema（JSON schema、评分规则）

### 6.2 Cache 键生成策略

Cache Key 需要满足：
- 可复用：相同系统提示 + 相同工具集合 → 相同 key
- 可失效：当 prompt/skills 版本变化 → key 自动变化

建议：

```text
prompt_cache:{model}:{locale}:{agent}:{skills_hash}:{prompt_version}

skills_hash = sha256(sorted(skill_names + skill_versions))
prompt_version = git_commit or semantic version
```

### 6.3 TTL 设置

- 系统提示/工具定义：TTL 7~30 天（版本变更用 key 变化触发失效）
- RAG 结果内容：TTL 24h（见 Redis 缓存章节）

### 6.4 预期 token 节省比例

经验预估（取决于模型是否对“前缀缓存”计费减免）：
- 工具定义 + 系统提示通常占 20%~60% prompt tokens
- 启用前缀缓存后，**有效节省 15%~50%** 的计费 tokens（高复用场景更高）

**注意**：如果 provider 不支持真正的“计费级前缀缓存”，仍可通过 Redis 做“响应级缓存/语义缓存”，降低重复调用。

---

## 7. Redis 缓存设计（搜索、推荐、RAG、预订）

### 7.1 缓存键设计规范

统一 key 命名：

```text
lvyou:{env}:{feature}:{version}:{hash}

feature ∈ {search, recommend, rag, booking, prompt, rate}
version = schema_version 或 git commit short sha
hash = sha256(normalized_input_json)
```

“normalized_input_json” 要求：
- 排序 key
- 去除无关字段（request_id、timestamp）
- 对用户隐私字段做脱敏或不参与 hash

### 7.2 TTL 配置表

| 缓存项 | Key 前缀 | TTL | 说明 |
|---|---|---:|---|
| 搜索结果 | `lvyou:prod:search:*` | 1h | 航班/酒店价格波动，短 TTL |
| 推荐结果 | `lvyou:prod:recommend:*` | 6h | 同需求复用高 |
| RAG 检索结果 | `lvyou:prod:rag:*` | 24h | 热门目的地复用 |
| 预订状态 | `lvyou:prod:booking:*` | 5m~30m | 以订单状态为准 |
| Prompt 元数据 | `lvyou:prod:prompt:*` | 7d~30d | 版本驱动失效 |

### 7.3 缓存失效策略

- **版本前缀失效**：发布新版本（或 prompt/skills 变更）时自动切换 version 前缀。
- **主动失效**：对“价格敏感”数据（航班）可以按供应商回调触发失效。
- **抖动保护**：对同一 key 的并发 miss 用 single-flight（互斥锁/SETNX）避免击穿。

### 7.4 缓存预热机制

- 基于 Top destination / Top query 的离线预热：
  - 热门城市：东京/大阪/新加坡/曼谷…
  - 经典问题：签证、最佳季节、交通卡、天气
- 预热只生成 RAG 与推荐模板，不生成用户私有数据。

**Token/成本优化点（Redis）**
- 搜索/推荐/RAG 的响应缓存命中可直接“短路 LLM 调用”，节省 100% LLM token 成本。

---

## 8. 高并发优化

### 8.1 内存池管理

高并发下，频繁创建大对象（长字符串、JSON、embedding 列表）会导致 GC 压力。

建议：
- 对“结构化 JSON 编码/解码”使用更快实现（如 orjson），减少 CPU 与内存碎片。
- 对“向量/embedding 结果”使用批量与复用对象（例如复用 list buffer / numpy arrays）。

### 8.2 连接池配置（Redis、数据库、HTTP）

- Redis：使用 `redis.asyncio` + `max_connections`
- PostgreSQL：SQLAlchemy async engine + pool_size/max_overflow
- 外部 HTTP：`httpx.AsyncClient(limits=...)`，避免每次新建连接

```python
import httpx

http = httpx.AsyncClient(
    timeout=15.0,
    limits=httpx.Limits(
        max_connections=200,
        max_keepalive_connections=50,
        keepalive_expiry=30,
    ),
)
```

### 8.3 流式响应设计（Server-Sent Events）

- /chat 使用 SSE 将“规划进度 + 部分回答”流式推送
- LangGraph 节点可以产出 events（规划、检索、推荐、预订）

```python
# FastAPI SSE 伪代码
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

@router.post("/chat")
async def chat(req: ChatRequest):
    async def gen():
        async for event in workflow.astream_events(req):
            yield {"event": event.type, "data": event.payload}

    return EventSourceResponse(gen())
```

### 8.4 任务队列与异步处理

- 长耗时搜索/预订：可异步化为任务（task_id），前端轮询/订阅。
- 对供应商 API 使用并发限制（Semaphore），避免触发对方限流。

**Token/成本优化点（并发）**
- 流式返回减少用户“重复提问/催促”的额外 token。
- 连接池与并发限制减少失败重试，从而减少重复 LLM 调用。

---

## 9. MCP（Model Context Protocol）集成

> 目标：把“工具与资源”以标准化协议暴露给模型/代理，支持运行时发现、按需加载与安全治理。

### 9.1 MCP Server 架构

与现有结构对齐（示例路径）：

```text
travel-assistant-agent/src/mcp_server/
  - server.py            # registry + dispatcher
  - skill_registry.py    # skill discovery
  - skills/*             # skills grouped by agent responsibility
```

### 9.2 工具与资源的暴露方式

- Skills 以 JSON Schema 定义输入/输出
- 支持：
  - 列举技能：`GET /mcp/skills?agent_type=search`
  - 调用技能：`POST /mcp/call-skill`
  - 批量调用：`POST /mcp/batch-call`

### 9.3 Claude 与 MCP Server 的通信协议

- Claude/LLM 侧通过“工具调用（tool call）”触发 MCP skill
- MCP Client 将 tool call 转成 HTTP 请求
- 返回结构化结果给 LLM（减少自然语言解释 token）

### 9.4 安全认证机制

- MCP 服务必须启用：
  - API Key / JWT / mTLS（二选一或组合）
  - Skill allowlist（按 agent_type、环境、租户）
  - 审计日志（记录 skill_name、参数 hash、耗时、结果摘要）

**Token/成本优化点（MCP）**
- 工具输出结构化 → LLM 处理更短。
- Skills 运行时发现 → 按需加载 → 工具定义 token 显著下降。

---

## 10. Agent Skills 框架（按需加载降低 token）

### 10.1 Skill 定义规范

Skill 最小元数据：
- `name`：全局唯一
- `description`：一句话
- `input_schema` / `output_schema`：JSON Schema
- `agent_type`：search/recommendation/booking/info_collection
- `version`：语义化版本

（与现有 `BaseSkill` / `SkillRegistry` 模式一致）

### 10.2 Skill 注册与发现机制

- 启动时注册（基础技能）
- 或按需加载（lazy import）：只有在进入某个 workflow stage 时加载对应 skills

```python
# 伪代码：按需加载

def load_skills(agent_type: str, only: list[str] | None = None):
    registry = get_skill_registry()
    skills = registry.get_by_agent_type(agent_type)
    if only:
        skills = [s for s in skills if s.name in set(only)]
    return skills
```

### 10.3 按需加载的实现要点

- `search_execution`：只加载搜索类 skills
- `recommend_execution`：只加载推荐 + RAG 类 skills
- `booking_execution`：只加载预订/支付类 skills

这会直接减少 LLM prompt 中的工具定义长度。

### 10.4 Skill 组合与优化

- 支持 batch-call：一次请求执行多个 skills，减少网络开销与 LLM 往返。
- 对高频组合（如 search_flights + search_hotels + compare_results）提供“组合 skill”作为优化选项。

**Token/成本优化点（Skills）**
- 工具定义 token 在复杂系统中常是最大隐形成本之一；按需加载可减少 30%~80% 的工具相关 tokens。

---

## 11. 依赖版本与环境配置

### 11.1 requirements.txt（带版本锁定，示例）

> 建议使用 `>=,<` 锁定 major/minor，并用 pip-tools/poetry 生成 lock 以获得可复现构建。

```txt
fastapi>=0.109.0,<1.0.0
uvicorn[standard]>=0.27.0,<1.0.0
pydantic>=2.5.0,<3.0.0
pydantic-settings>=2.1.0,<3.0.0
python-dotenv>=1.0.0,<2.0.0
httpx>=0.26.0,<1.0.0
loguru>=0.7.2,<1.0.0

# LangChain / LangGraph (hard requirement)
langchain>=1.0.0,<2.0.0
langchain-core>=1.0.0,<2.0.0
langgraph>=1.0.0,<2.0.0

# DeepAgent (hard requirement)
deepagent>=0.2.7,<0.3.0

# MCP
mcp>=1.0.0,<2.0.0
langchain-mcp-adapters>=0.1.0,<1.0.0

# Redis
redis>=5.0.0,<6.0.0

# Token accounting
tiktoken>=0.5.0,<1.0.0
```

### 11.2 环境变量配置说明（建议）

```bash
# Model keys
DEEPSEEK_API_KEY=...
DASHSCOPE_API_KEY=...
ZHIPU_API_KEY=...
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...

# Multi-tier model strategy
LLM_CHEAP_PROVIDER=deepseek-chat
LLM_STANDARD_PROVIDER=qwen-turbo
LLM_POWER_PROVIDER=claude-3.5-sonnet
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4096

# Prompt Cache
PROMPT_CACHE_ENABLED=true
PROMPT_CACHE_TTL_SECONDS=2592000

# Redis
REDIS_ENABLED=true
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_MAX_CONNECTIONS=200

# MCP
MCP_SERVER_URL=http://agent:8000
MCP_API_KEY=...
```

### 11.3 Docker 镜像构建建议

- 使用多阶段构建，尽可能缓存依赖层
- 生产环境启动：`uvicorn --workers N --loop uvloop`（若兼容）
- 将 RAG 的 BM25 快照与向量索引初始化放到启动脚本中，并在 readiness probe 前完成

---

## 12. 实施路线图

### Phase 1: 核心框架搭建
- 版本升级与锁定：LangChain >=1.0, LangGraph >=1.0, DeepAgent >=0.2.7
- LangGraph 工作流：主流程与条件分支（entry → ... → response）
- 多模型统一接口：ChatOpenAI(base_url) + LLMFactory/配置驱动
- DeepAgent 子智能体基础：Search/Recommendation/Booking 的最小可用闭环

### Phase 2: 智能增强
- RAG（向量 + BM25）混合检索落地
- Prompt Cache（前缀缓存/响应级缓存）机制落地
- Redis 缓存层：search/recommend/rag/booking

### Phase 3: 高级特性
- MCP 深度集成：skills runtime discovery + batch call + 安全治理
- Agent Skills 框架：按需加载 + 组合 skills
- 高并发优化：连接池/限流/streaming/任务队列

---

## 13. 关键决策说明（含 token/成本考量）

### 13.1 为什么选择 LangGraph 而不是其他框架？

- LangGraph 的优势：
  - **显式状态机**：业务分支可审计、可测试、可回放
  - **节点级缓存/重试/短路**：天然适合“搜索/推荐/预订”这类多阶段业务
  - 将 LLM 从“万能黑箱”降级为“可控的推理组件”，减少无意义 token 消耗

**成本视角**：可将“重复的 LLM 推理与工具调用”通过缓存与短路消除，直接降低总 token 账单。

### 13.2 DeepAgent vs 传统 Agent 的 token 节省对比

- 传统 Agent：每次调用携带大量 history + tools + context
- DeepAgent 子智能体：
  - 输入最小化（结构化 state + 摘要）
  - 工具按需加载
  - 固定系统提示利于缓存

**经验预估**：
- prompt tokens 可降低 30%~70%
- 误调用工具下降（减少失败重试与额外解释）

### 13.3 Prompt Cache 的实际应用场景

- system prompt 长且稳定（旅行助手角色、输出格式、合规约束）
- tools schema 多且稳定（几十个 skills）
- 这些内容每个请求都重复，适合前缀缓存

**效果**：在高复用场景（同一 agent_type 多次调用）可显著减少计费 token 或减少重复请求。

### 13.4 多模型成本对比与选择策略

- Claude（power）：质量高但单价高，适合高价值深度推理
- Qwen/GLM（standard）：综合性价比好，适合检索+推荐
- DeepSeek（cheap/standard）：低成本，适合规划/抽取/格式化

**策略**：绝大多数请求使用 cheap/standard；仅在“复杂冲突/高客单价预订/用户强需求”触发 power。

---

## 附录 A：建议的工作流事件（用于前端 streaming 展示）

```json
{ "event": "stage", "data": { "stage": "search_planning" } }
{ "event": "cache", "data": { "feature": "search", "hit": true } }
{ "event": "progress", "data": { "message": "正在对比航班与酒店…" } }
{ "event": "final", "data": { "answer": "...", "recommendations": [...] } }
```
