# MCP 工具绑定快速参考

## 🚀 快速开始

### 查看可用工具

```python
from agents.mcp_client import get_mcp_client

client = get_mcp_client()
tools = await client.get_tools()

# 打印工具列表
for tool in tools:
    print(f"- {tool.name}: {tool.description}")
```

### 构建搜索工具

```python
from workflows.subgraphs.common import build_search_tools

search_plan = {
    "destination": "杭州",
    "search_priorities": ["hotel", "flight"],
    "rag_search_keywords": ["西湖", "灵隐寺"]
}

tools = await build_search_tools(search_plan)
print(f"Built {len(tools)} tools")
```

### 查看工具调用日志

```python
from utils.tools_invocation_logger import get_tool_invocation_logger

logger = get_tool_invocation_logger()

# 查看统计
stats = logger.get_stats()
print(f"Total calls: {stats['total_calls']}")
print(f"Success rate: {stats['success_rate']*100:.1f}%")

# 查看详细报告
print(logger.report())

# 查看最近的调用
recent = logger.get_invocations(limit=5)
for inv in recent:
    print(f"{inv['tool_name']}: {inv['status']} ({inv['duration']:.2f}s)")
```

## 🔧 工具适配器使用

### 手动创建工具适配器

```python
from agents.tool_adapter import ToolAdapter
from agents.mcp_client import get_mcp_client

tool_def = {
    "name": "search_hotels",
    "description": "搜索酒店信息",
    "args_schema": {
        "type": "object",
        "properties": {
            "destination": {"type": "string", "description": "目的地"},
            "price_max": {"type": "number", "description": "最高价格"}
        },
        "required": ["destination"]
    }
}

client = get_mcp_client()
adapter = ToolAdapter(tool_def, client)
tool = adapter.to_langchain_tool()

# 使用工具
result = await tool.coroutine(destination="杭州", price_max=1000)
print(result)
```

### 批量包装工具

```python
from agents.tool_adapter import wrap_mcp_tools
from agents.mcp_client import get_mcp_client

tool_defs = [
    {"name": "tool1", "description": "Tool 1"},
    {"name": "tool2", "description": "Tool 2"}
]

client = get_mcp_client()
tools = wrap_mcp_tools(tool_defs, client)

print(f"Wrapped {len(tools)} tools")
```

## 📊 日志格式

### 工具构建日志

```
[Build Tools] ✅ Added RAG search tool
[Build Tools] ✅ Added 5 MCP Java tools
[Build Tools] 🔧 Total tools built: 7
```

### 工具调用日志

```
[Tool Call] 🔧 Invoking: search_hotels
[Tool Call] Parameters: {"destination": "杭州", "price_max": 1000}
[Tool Call] ✅ Success: search_hotels (took 2.31s)
[Tool Call] Result summary: {"data": [...], "total": 42}
```

### Agent 执行日志

```
[Search Execute] 🔧 Tools available: ['rag_search_tool', 'search_hotels', ...]
[Search Execute] 🤖 Creating ReAct agent with 7 tools
[Search Execute] 🚀 Starting agent execution...
[Search Execute] ✅ Agent execution completed
```

## 🐛 调试技巧

### 1. 检查工具是否正确绑定

```python
from workflows.subgraphs.search import search_execute_agent_node
from workflows.subgraphs.common import SubState

state = SubState({
    "messages": [],
    "search_plan": {"destination": "杭州"},
    "collected_info": {"destination": "杭州"}
})

# 在执行前，检查日志输出
result = await search_execute_agent_node(state)
```

### 2. 验证工具类型

```python
tools = await build_search_tools({})

for tool in tools:
    print(f"Tool: {tool.name}")
    print(f"Type: {type(tool)}")
    print(f"Has invoke: {hasattr(tool, 'invoke')}")
    print(f"Has coroutine: {hasattr(tool, 'coroutine')}")
```

### 3. 测试单个工具调用

```python
from agents.mcp_client import get_mcp_client

client = get_mcp_client()

# 直接调用工具
result = await client.call_tool(
    "search_hotels",
    parameters={"destination": "杭州", "price_max": 1000}
)

print(f"Result: {result}")
```

### 4. 清空工具调用日志

```python
from utils.tools_invocation_logger import get_tool_invocation_logger

logger = get_tool_invocation_logger()
logger.clear()
print("Tool invocation logs cleared")
```

## ⚠️ 常见问题

### 问题 1: 工具调用失败

**症状**: 日志显示 `[Tool Call] ❌ Failed: tool_name`

**排查**:
1. 检查 Java 服务是否运行：`curl http://localhost:9000/mcp/tools`
2. 检查网络连接
3. 查看详细错误信息：`logger.get_invocations(limit=1)`

### 问题 2: Agent 不调用工具

**症状**: Agent 直接返回答案，没有工具调用日志

**排查**:
1. 检查工具是否正确绑定：查看 `[Build Tools]` 日志
2. 检查 LLM 是否理解工具描述
3. 尝试更明确的用户查询

### 问题 3: 工具调用超时

**症状**: `[Tool Call] ❌ Failed: timeout`

**解决**:
1. 增加超时时间（在 mcp_client.py 中修改 `self.timeout`）
2. 检查 Java 服务性能
3. 考虑使用缓存

### 问题 4: 缓存不生效

**症状**: 每次都重新调用工具，缓存命中率为 0

**排查**:
1. 检查 Redis 是否运行
2. 检查缓存键生成逻辑
3. 查看缓存过期时间设置

## 📈 性能优化

### 1. 启用缓存

```python
# 在 mcp_client.py 中已默认启用
# 缓存时间：1 小时
# 缓存键：基于工具名和参数的哈希值
```

### 2. 并发调用多个工具

```python
import asyncio

tools_to_call = [
    ("search_hotels", {"destination": "杭州"}),
    ("search_flights", {"destination": "杭州"}),
    ("search_attractions", {"destination": "杭州"})
]

results = await asyncio.gather(*[
    client.call_tool(name, parameters=params)
    for name, params in tools_to_call
])
```

### 3. 监控工具调用性能

```python
from utils.tools_invocation_logger import get_tool_invocation_logger

logger = get_tool_invocation_logger()
stats = logger.get_stats()

if stats['avg_duration'] > 3.0:
    print("⚠️ Average tool call duration is too high")

if stats['success_rate'] < 0.9:
    print("⚠️ Tool call success rate is low")
```

## 🔗 相关链接

- [完整技术文档](./MCP_TOOL_BINDING_FIX.md)
- [实施总结](./IMPLEMENTATION_SUMMARY.md)
- [测试指南](./travel-assistant-agent/tests/)
- [MCP 实现指南](./MCP_IMPLEMENTATION_GUIDE.md)

## 📞 支持

如有问题，请：
1. 查看日志：`tail -f logs/agent.log | grep -E "\[Tool Call\]|\[Build Tools\]"`
2. 运行测试：`pytest tests/test_tool_adapter.py -v`
3. 查看工具调用统计
4. 联系开发团队

---

**版本**: v1.0.0  
**最后更新**: 2026-01-31
