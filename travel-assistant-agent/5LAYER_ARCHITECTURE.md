# 5 层架构设计文档

## 架构概览

lvyou Agent 使用 5 层架构设计，从底层到顶层依次为：

```
第5层: DeepAgent 顶层代理     ← 统一入口，协调所有子代理
   ↓
第4层: 主工作流 StateGraph     ← 顺序执行 4 个节点
   ↓
第3层: call_subagent_node      ← 工厂函数，创建节点
   ↓
第2层: CompiledSubAgent        ← 包装子图，统一接口
   ↓
第1层: 4 个子图 StateGraph     ← 业务逻辑（收集、搜索、推荐、预订）
   ↓
第0层: TokenCounter Callback   ← Token 统计
```

---

## 第0层：TokenCounter Callback

**文件**: `src/utils/token_counter.py`

**作用**: 统计单个 LLM 调用的 token 用量

**关键方法**:
- `on_llm_end()`: LLM 调用结束时提取 token 用量
- `dump()`: 返回 `{"prompt": int, "completion": int, "total": int}`

**使用示例**:
```python
from utils.token_counter import TokenCounter

counter = TokenCounter()
result = llm.invoke(messages, config={"callbacks": [counter]})
usage = counter.dump()  # {"prompt": 100, "completion": 50, "total": 150}
```

---

## 第1层：4 个子图 StateGraph

**文件**: `src/workflows/subgraphs.py`

**作用**: 实现 4 个独立的业务子图，每个子图负责一个业务步骤

### 1. 信息收集子图 (collect_info_graph)

- **系统提示**: "你是信息收集员，只负责收集需求并总结。"
- **使用模型**: deepseek-chat（便宜层）
- **输入**: `{"user_message": str, "collected_info": None, "usage": {...}}`
- **输出**: `{"collected_info": {...}, "usage": {...}}`

### 2. 搜索子图 (search_graph)

- **系统提示**: "你是搜索员，收到需求总结后返回目的地 JSON。"
- **使用模型**: qwen-turbo（标准层）
- **输入**: `{"user_message": str, "collected_info": {...}, "search_results": None, "usage": {...}}`
- **输出**: `{"search_results": {...}, "usage": {...}}`

### 3. 推荐子图 (recommend_graph)

- **系统提示**: "你是推荐员，基于需求和搜索结果生成个性化方案。"
- **使用模型**: qwen-turbo（标准层）
- **输入**: `{"user_message": str, "collected_info": {...}, "search_results": {...}, "recommendations": None, "usage": {...}}`
- **输出**: `{"recommendations": [...], "usage": {...}}`

### 4. 预订子图 (booking_graph)

- **系统提示**: "你是预订员，完成用户选定的预订。"
- **使用模型**: deepseek-chat（便宜层）
- **输入**: `{"user_message": str, "collected_info": {...}, "recommendations": [...], "booking_confirmation": None, "usage": {...}}`
- **输出**: `{"booking_confirmation": {...}, "usage": {...}}`

**使用示例**:
```python
from workflows.subgraphs import build_collect_info_graph

graph = build_collect_info_graph()
result = graph.invoke({
    "user_message": "我想6月去巴黎玩5天",
    "collected_info": None,
    "usage": {"prompt": 0, "completion": 0, "total": 0}
})
print(result["collected_info"])  # {"destination": "巴黎", ...}
print(result["usage"])  # {"prompt": 100, "completion": 50, "total": 150}
```

---

## 第2层：CompiledSubAgent 包装器

**文件**: 
- `src/workflows/subagents.py` - 子代理创建函数
- `deepagents.py` - CompiledSubAgent 类定义

**作用**: 包装 StateGraph 子图，提供统一的接口

**关键方法**:
- `invoke(input_state)`: 同步调用子图
- `ainvoke(input_state)`: 异步调用子图
- 返回格式: `{"output": str, "usage": {...}, "state": {...}}`

**4 个 CompiledSubAgent 实例**:

```python
from workflows.subagents import (
    get_info_collection_agent,  # 信息收集子代理
    get_search_agent,           # 搜索子代理
    get_recommend_agent,        # 推荐子代理
    get_booking_agent,          # 预订子代理
)

# 使用示例
agent = get_info_collection_agent()
result = agent.invoke({
    "user_message": "我想去巴黎",
    "collected_info": None,
    "usage": {"prompt": 0, "completion": 0, "total": 0}
})

print(result["output"])  # JSON 字符串形式的 collected_info
print(result["usage"])   # {"prompt": 100, "completion": 50, "total": 150}
print(result["state"])   # 完整的子图状态
```

---

## 第3层：call_subagent_node 工厂函数

**文件**: `src/workflows/main_workflow.py`

**作用**: 工厂函数，创建调用子代理的节点函数

**实现原理**:

```python
def call_subagent_node(subagent_name: str):
    """工厂函数"""
    def _node(state: MainState) -> Dict[str, Any]:
        # 1. 根据 subagent_name 获取对应的 CompiledSubAgent
        if subagent_name == "info_collection":
            agent = get_info_collection_agent()
            # ...
        
        # 2. 调用 CompiledSubAgent 的 invoke() 方法
        res = agent.invoke(input_state)
        
        # 3. 返回更新（usage 会通过 operator.add 自动累加）
        return {
            "messages": [HumanMessage(content=res["output"])],
            "usage": res["usage"],  # ← 自动累加
            "collected_info": res["state"]["collected_info"]
        }
    
    return _node
```

**使用示例**:
```python
from workflows.main_workflow import call_subagent_node

# 创建节点函数
collect_node = call_subagent_node("info_collection")

# 在 StateGraph 中使用
graph.add_node("collect", collect_node)
```

---

## 第4层：主工作流 StateGraph

**文件**: `src/workflows/main_workflow.py`

**作用**: 构建主工作流图，按顺序执行 4 个节点

**MainState 状态定义**:

```python
class MainState(TypedDict):
    messages: Sequence[BaseMessage]
    user_message: str
    
    collected_info: Optional[Dict[str, Any]]
    search_results: Optional[Dict[str, Any]]
    recommendations: Optional[List[Dict[str, Any]]]
    booking_confirmation: Optional[Dict[str, Any]]
    
    usage: Annotated[Dict[str, int], operator.add]  # ← 自动累加器
    
    final_response: Optional[str]
```

**工作流结构**:

```python
graph = StateGraph(MainState)

# 添加 4 个节点
graph.add_node("collect", call_subagent_node("info_collection"))
graph.add_node("search", call_subagent_node("search"))
graph.add_node("recommend", call_subagent_node("recommend"))
graph.add_node("booking", call_subagent_node("booking"))

# 设置边（顺序执行）
graph.set_entry_point("collect")
graph.add_edge("collect", "search")
graph.add_edge("search", "recommend")
graph.add_edge("recommend", "booking")
graph.add_edge("booking", END)

main_runnable = graph.compile()
```

**使用示例**:
```python
from workflows.main_workflow import build_main_graph

main_graph = build_main_graph()
result = main_graph.invoke({
    "messages": [HumanMessage(content="我想去巴黎")],
    "user_message": "我想去巴黎",
    "collected_info": None,
    "search_results": None,
    "recommendations": None,
    "booking_confirmation": None,
    "usage": {"prompt": 0, "completion": 0, "total": 0},
    "final_response": None
})

print(result["collected_info"])
print(result["search_results"])
print(result["recommendations"])
print(result["booking_confirmation"])
print(result["usage"])  # 所有步骤的总 token 用量
```

---

## 第5层：DeepAgent 顶层代理

**文件**: 
- `src/workflows/main_workflow.py` - 创建 DeepAgent
- `deepagents.py` - DeepAgent 类定义

**作用**: 提供统一的代理入口，协调所有子代理

**创建 DeepAgent**:

```python
from deepagents import create_deep_agent
from workflows.main_workflow import get_or_create_main_agent

# 方式 1: 直接创建
main_agent = create_deep_agent(
    model=llm,
    subagents=[
        get_info_collection_agent(),
        get_search_agent(),
        get_recommend_agent(),
        get_booking_agent(),
    ],
    runnable=build_main_graph(),
    system_prompt="你是旅游协调员，按顺序调用子代理并完成预订。"
)

# 方式 2: 使用单例
main_agent = get_or_create_main_agent()
```

**调用方式**:

```python
# 同步调用
result = main_agent.invoke({
    "messages": [HumanMessage(content=user_message)],
    "user_message": user_message,
    "collected_info": None,
    "search_results": None,
    "recommendations": None,
    "booking_confirmation": None,
    "usage": {"prompt": 0, "completion": 0, "total": 0},
    "final_response": None
})

# 异步调用
result = await main_agent.ainvoke({...})
```

---

## 便捷调用函数

**文件**: `src/workflows/main_workflow.py`

### run_main_workflow_sync()

**同步运行主工作流**:

```python
from workflows.main_workflow import run_main_workflow_sync

result = run_main_workflow_sync("我想6月去巴黎玩5天，预算1-1.5万")

print(result)
# {
#     "collected_info": {...},
#     "search_results": {...},
#     "recommendations": [...],
#     "booking_confirmation": {...},
#     "total_usage": {"prompt": 500, "completion": 300, "total": 800},
#     "status": "success"
# }
```

### run_main_workflow()

**异步运行主工作流**:

```python
from workflows.main_workflow import run_main_workflow

result = await run_main_workflow("我想6月去巴黎玩5天，预算1-1.5万")
```

---

## Token 统计机制

### 自动累加原理

使用 `Annotated[Dict[str, int], operator.add]` 实现 usage 自动累加：

```python
class MainState(TypedDict):
    usage: Annotated[Dict[str, int], operator.add]
```

**工作流程**:

1. **第1步 (collect)**: 返回 `{"usage": {"prompt": 100, "completion": 50, "total": 150}}`
2. **第2步 (search)**: 返回 `{"usage": {"prompt": 200, "completion": 80, "total": 280}}`
3. **第3步 (recommend)**: 返回 `{"usage": {"prompt": 150, "completion": 100, "total": 250}}`
4. **第4步 (booking)**: 返回 `{"usage": {"prompt": 50, "completion": 30, "total": 80}}`

**最终 state["usage"]**:
```python
{
    "prompt": 100 + 200 + 150 + 50 = 500,
    "completion": 50 + 80 + 100 + 30 = 260,
    "total": 150 + 280 + 250 + 80 = 760
}
```

### Token 统计层次

```
第0层: TokenCounter        ← 单个 LLM 调用
        ↓
第1层: 子图 usage           ← 单个子图所有 LLM 调用的累加
        ↓
第2层: CompiledSubAgent     ← 返回子图 usage
        ↓
第4层: MainState usage      ← 所有子代理的累加（operator.add）
```

---

## MCP 集成

**文件**: `src/agents/mcp_client.py`

**作用**: 连接 Java API 后端，将方法包装为 LangChain Tools

**4 个 Java API 工具**:

1. `search_destinations` → `/search/destinations`
2. `get_recommendations` → `/recommendations/generate`
3. `create_booking` → `/bookings/create`
4. `get_booking_status` → `/bookings/{id}/status`

**使用示例**:

```python
from agents.mcp_client import get_mcp_client

client = get_mcp_client()
await client.connect()

# 调用 Java API
result = await client.call_tool(
    "search_destinations",
    {"query": "Paris", "filters": {"budget": 10000}}
)

# 错误降级：如果 Java API 不可用，返回 mock 数据
print(result)
# {"result": {...}, "error": None | "API unavailable"}
```

---

## Skills 框架

**文件**: `src/skills/`

**架构**:

```
src/skills/
├── SKILLS.md                    ← 全局元数据索引
├── registry.py                  ← SkillRegistry 按需加载器
├── base.py                      ← Skill 基类
├── search/
│   ├── SKILL.md                 ← 详细描述
│   ├── __init__.py
│   └── skill.py                 ← SearchSkill 实现
├── recommend/
├── booking/
└── info_collection/
```

**使用示例**:

```python
from skills.registry import SkillRegistry

# 列出所有 skills（不加载实现）
skills = SkillRegistry.list_skills()
# [{"name": "search", "description": "..."}, ...]

# 获取 skill 摘要（用于 LLM Prompt）
summaries = SkillRegistry.get_all_summaries()

# 按需加载 skill 实现
skill = await SkillRegistry.load_skill("search")
result = await skill.execute({"query": "Paris"})
```

---

## 验证架构

**文件**: `verify_5layer_architecture.py`

运行验证脚本：

```bash
cd /home/engine/project/travel-assistant-agent
python3 verify_5layer_architecture.py
```

**验证内容**:

- ✓ 第0层: TokenCounter 类和方法
- ✓ 第1层: 4 个子图可以构建和调用
- ✓ 第2层: CompiledSubAgent 包装器
- ✓ 第3层: call_subagent_node 工厂函数
- ✓ 第4层: 主工作流 StateGraph
- ✓ 第5层: DeepAgent 顶层代理
- ✓ 整体集成: 端到端 API

---

## 关键设计决策

### 1. 为什么使用 5 层架构？

- **第0层**: 精确的 token 统计
- **第1层**: 独立的业务逻辑，易于测试和维护
- **第2层**: 统一的子代理接口
- **第3层**: 灵活的节点创建
- **第4层**: 清晰的工作流编排
- **第5层**: 统一的代理入口

### 2. 为什么使用 CompiledSubAgent？

- 提供统一的 `invoke()/ainvoke()` 接口
- 返回标准格式 `{"output", "usage", "state"}`
- 便于在主工作流中调用

### 3. 为什么使用 operator.add？

- LangGraph 原生支持
- 自动累加 usage，无需手动计算
- 代码简洁，减少错误

### 4. 为什么使用工厂函数？

- 避免重复代码
- 统一节点创建逻辑
- 易于维护和扩展

---

## 扩展指南

### 添加新的子代理

1. **创建子图** (`src/workflows/subgraphs.py`):
   ```python
   def build_new_graph():
       graph = StateGraph(NewState)
       graph.add_node("new", new_node)
       graph.set_entry_point("new")
       graph.add_edge("new", END)
       return graph.compile()
   ```

2. **创建 CompiledSubAgent** (`src/workflows/subagents.py`):
   ```python
   def get_new_agent() -> CompiledSubAgent:
       global _new_agent
       if _new_agent is None:
           _new_agent = CompiledSubAgent(
               name="new",
               runnable=build_new_graph(),
               system_prompt="..."
           )
       return _new_agent
   ```

3. **更新主工作流** (`src/workflows/main_workflow.py`):
   ```python
   # 添加到 call_subagent_node
   elif subagent_name == "new":
       agent = get_new_agent()
       result_key = "new_results"
       # ...
   
   # 更新主图
   graph.add_node("new", call_subagent_node("new"))
   graph.add_edge("booking", "new")
   graph.add_edge("new", END)
   ```

4. **更新 DeepAgent**:
   ```python
   subagents = [
       get_info_collection_agent(),
       get_search_agent(),
       get_recommend_agent(),
       get_booking_agent(),
       get_new_agent(),  # ← 添加
   ]
   ```

---

## 总结

5 层架构提供了：

✅ **清晰的层次结构**: 每层职责明确  
✅ **精确的 token 统计**: 从 LLM 调用到整体工作流  
✅ **灵活的扩展性**: 易于添加新子代理  
✅ **统一的接口**: CompiledSubAgent 统一包装  
✅ **自动化**: operator.add 自动累加 usage  
✅ **可测试性**: 每层都可独立测试  

通过这个架构，lvyou Agent 可以高效地管理多个子代理，准确统计所有 LLM 调用的 token 用量，并提供清晰的工作流编排。
