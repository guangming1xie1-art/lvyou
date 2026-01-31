# MCP 工具绑定问题修复

## 📋 问题概述

**问题根源**：当前 travel-assistant-agent 的搜索和推荐流程存在严重的 MCP 工具绑定问题。工具仅作为文本出现在 System Prompt 中，LLM 无法真正调用 Java 后端的 MCP 服务工具。

### 问题详情

1. **mcp_client.py 的 get_tools()** 返回字典元数据而非可调用的 Tool 对象
   - `MCPClient.get_tools()` 返回的是工具定义字典列表
   - 转换过程中丢失了可调用性，变成了纯数据结构

2. **common.py 中的工具构建逻辑缺陷**
   - `get_tools_and_skills_text()` 只返回工具文本描述，用于填充 System Prompt
   - `build_search_tools()` 和 `build_recommend_tools()` 直接 extend 字典列表
   - 结果：字典被传给 `create_react_agent()` 而不是真正的 Tool 对象

3. **工具绑定流程断裂**
   - search.py/recommend.py 中的 agent 没有真正获得可调用的工具
   - LLM 在 ReAct 循环中无法实际调用任何 Java 服务

## ✅ 解决方案

### 核心改进

#### 1. 新增 `tool_adapter.py` - 工具适配器模块

**文件**：`travel-assistant-agent/src/agents/tool_adapter.py`

**核心类**：`ToolAdapter`

**功能**：
- 将 MCP 工具元数据（字典）转换为 LangChain Tool 对象
- 包装异步调用方法，连接到 Java 后端
- 记录工具调用日志和性能指标

**关键方法**：
```python
class ToolAdapter:
    async def invoke_async(self, **kwargs) -> str:
        """异步调用 Java 后端工具"""
        # 调用 mcp_client.call_tool()
        # 记录日志和性能
        
    def to_langchain_tool(self) -> BaseTool:
        """转换为 LangChain Tool 对象"""
        # 返回可被 create_react_agent() 使用的工具
```

**包装函数**：
```python
def wrap_mcp_tools(mcp_tools_dicts: list, mcp_client: Any) -> list:
    """批量包装 MCP 工具为 LangChain Tools"""
```

#### 2. 新增 `tools_invocation_logger.py` - 工具调用追踪器

**文件**：`travel-assistant-agent/src/utils/tools_invocation_logger.py`

**核心类**：`ToolInvocationLogger`

**功能**：
- 记录所有工具调用的详细信息
- 跟踪性能指标（调用次数、耗时、成功率）
- 支持缓存命中率统计
- 生成调用报告

**使用示例**：
```python
from utils.tools_invocation_logger import get_tool_invocation_logger

logger = get_tool_invocation_logger()
logger.log_invocation(
    tool_name="search_hotels",
    parameters={"destination": "杭州"},
    result={"hotels": [...]},
    duration=2.5,
    cache_hit=False
)

# 获取统计信息
stats = logger.get_stats()
print(logger.report())
```

#### 3. 重构 `mcp_client.py` - 返回真正的 Tool 对象

**主要修改**：

1. **`get_tools()` 方法重构**
   ```python
   async def get_tools(self) -> List[Any]:
       """
       获取所有工具对象（LangChain Tool 对象，可调用）
       
       Returns:
           List[BaseTool]: 真正的工具对象，不是字典
       """
       client = await self._get_client()
       tools = await client.get_tools()
       
       # ✅ 直接返回 LangChain Tool 对象
       return tools
   ```

2. **新增 `get_tools_metadata()` 方法**
   ```python
   async def get_tools_metadata(self) -> List[Dict[str, Any]]:
       """
       获取工具元数据（字典格式，用于显示和缓存）
       """
       # 返回工具定义字典（用于文本描述）
   ```

3. **新增 `_create_adapted_tools()` 方法**
   ```python
   def _create_adapted_tools(self) -> List[Any]:
       """
       创建基于 ToolAdapter 的工具列表（降级方案）
       """
       from agents.tool_adapter import wrap_mcp_tools
       
       mock_tool_dicts = self._get_mock_tools()
       adapted_tools = wrap_mcp_tools(mock_tool_dicts, self)
       
       return adapted_tools
   ```

#### 4. 优化 `common.py` - 构建真正的工具对象

**主要修改**：

1. **`build_search_tools()` 增强**
   ```python
   async def build_search_tools(search_plan: Dict) -> List:
       """
       返回真正可调用的 LangChain Tool 对象列表
       """
       tools = []
       
       # 1. RAG 工具
       tools.append(rag_search_tool)
       
       # 2. MCP Java 工具（✅ 现在是真正的 Tool 对象）
       mcp_tools = await mcp_client.get_tools()
       if mcp_tools:
           tools.extend(mcp_tools)
           logger.info(f"✅ Added {len(mcp_tools)} MCP Java tools")
       
       # 3. Agent Skills
       # ...
       
       return tools
   ```

2. **`build_recommend_tools()` 增强**
   - 同样的逻辑改进
   - 返回真正的 Tool 对象列表

#### 5. 增强 `search.py` 和 `recommend.py` - 添加工具调用日志

**主要修改**：

1. **添加 logging 导入**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   ```

2. **在 search_execute_agent_node 中添加日志**
   ```python
   # 记录工具信息
   tool_names = [getattr(t, 'name', str(t)) for t in tools]
   logger.info(f"[Search Execute] 🔧 Tools available: {tool_names}")
   
   # 创建 ReAct Agent
   logger.info(f"[Search Execute] 🤖 Creating ReAct agent with {len(tools)} tools")
   agent = create_react_agent(llm, tools)
   
   logger.info(f"[Search Execute] 🚀 Starting agent execution...")
   result = await agent.ainvoke(...)
   logger.info(f"[Search Execute] ✅ Agent execution completed")
   ```

3. **在 recommend_execute_agent_node 中添加相同日志**

## 🎯 技术架构

### 工具绑定流程（修复后）

```
Java TravelMcpTools (@Tool 注解)
    ↓
Gateway MCP Server (Spring AI)
    ↓ HTTP MCP Protocol
Python MCPClient.get_tools()
    ↓
langchain_mcp_adapters.MultiServerMCPClient
    ↓ 返回 LangChain Tool 对象
build_search_tools() / build_recommend_tools()
    ↓ 真正的 Tool 对象列表
create_react_agent(llm, tools)
    ↓ 工具真正绑定到 Agent
Agent 在 ReAct 循环中调用工具
    ↓ 通过 ToolAdapter.invoke_async()
MCPClient.call_tool(tool_name, params)
    ↓ HTTP POST 到 Java Gateway
Java 服务处理并返回结果
    ↓
Tool 返回结果给 Agent
    ↓
Agent 继续推理或给出最终答案
```

### 降级机制

如果 `langchain_mcp_adapters` 连接失败：

```
MCPClient.get_tools() 失败
    ↓
调用 _create_adapted_tools()
    ↓
使用 ToolAdapter 包装 mock 工具定义
    ↓
返回基于 ToolAdapter 的工具对象
    ↓
工具仍然可调用（调用 mock 数据或本地实现）
```

## 📊 验收标准

### ✅ 功能验证

1. **工具对象类型检查**
   ```python
   tools = await build_search_tools(search_plan)
   assert all(hasattr(t, 'name') for t in tools)
   assert all(callable(t) or hasattr(t, 'invoke') for t in tools)
   ```

2. **工具绑定验证**
   ```python
   agent = create_react_agent(llm, tools)
   # 不应该抛出异常
   ```

3. **工具调用日志验证**
   - 检查日志输出中是否包含：
     - `[Build Tools] ✅ Added X MCP Java tools`
     - `[Search Execute] 🔧 Tools available: [...]`
     - `[Tool Call] 🔧 Invoking: tool_name`
     - `[Tool Call] ✅ Success: tool_name (took Xs)`

4. **工具调用统计验证**
   ```python
   from utils.tools_invocation_logger import get_tool_invocation_logger
   
   logger = get_tool_invocation_logger()
   stats = logger.get_stats()
   
   assert stats["total_calls"] > 0  # 工具被真正调用了
   assert stats["success_rate"] > 0  # 有成功的调用
   ```

### ✅ 性能指标

- **平均工具调用响应时间** < 5s（含网络延迟）
- **工具调用成功率** > 90%（在 Java 服务可用时）
- **缓存命中率** > 30%（对于重复查询）

### ✅ 错误处理

- 当 Java 服务不可用时，使用降级工具
- 工具调用失败时，Agent 能正确处理错误
- 超时保护机制（30 秒超时）

## 🧪 测试

### 单元测试

**文件**：`tests/test_tool_adapter.py`

**测试内容**：
- ToolAdapter 初始化
- 异步调用成功/失败场景
- LangChain Tool 对象创建
- 类型转换功能
- 批量包装功能

**运行**：
```bash
cd travel-assistant-agent
pytest tests/test_tool_adapter.py -v
```

### 集成测试

**文件**：`tests/test_search_tools_binding.py`

**测试内容**：
- build_search_tools() 返回工具对象
- build_recommend_tools() 返回工具对象
- 工具与 create_react_agent() 兼容性
- 工具调用日志记录
- 端到端工具绑定流程

**运行**：
```bash
cd travel-assistant-agent
pytest tests/test_search_tools_binding.py -v -s
```

## 📝 使用指南

### 开发者指南

#### 如何添加新的 MCP 工具

1. **在 Java 后端定义工具**
   ```java
   @Tool(description = "新工具描述")
   public String newTool(@ToolParam(name = "param1") String param1) {
       // 实现逻辑
       return result;
   }
   ```

2. **工具会自动被发现**
   - `MCPClient.get_tools()` 会自动获取新工具
   - 不需要在 Python 端做任何修改

3. **验证工具绑定**
   ```python
   tools = await mcp_client.get_tools()
   tool_names = [t.name for t in tools]
   assert "newTool" in tool_names
   ```

#### 如何调试工具调用问题

1. **启用详细日志**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **检查工具列表**
   ```python
   tools = await build_search_tools(search_plan)
   for tool in tools:
       print(f"Tool: {tool.name}, Type: {type(tool)}")
   ```

3. **查看工具调用日志**
   ```python
   from utils.tools_invocation_logger import get_tool_invocation_logger
   
   logger = get_tool_invocation_logger()
   print(logger.report())
   
   # 查看最近的调用
   recent = logger.get_invocations(limit=10)
   for inv in recent:
       print(inv)
   ```

4. **手动测试工具调用**
   ```python
   from agents.mcp_client import get_mcp_client
   
   client = get_mcp_client()
   result = await client.call_tool(
       "search_hotels",
       parameters={"destination": "杭州"}
   )
   print(result)
   ```

## 🚀 部署建议

### 环境变量

确保设置以下环境变量：

```bash
# Java Gateway MCP 端点
JAVA_API_URL=http://localhost:9000

# JWT 认证（如果需要）
JWT_SECRET_KEY=your_secret_key

# Redis 缓存（可选）
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 监控建议

1. **工具调用监控**
   - 定期检查工具调用统计
   - 设置告警：调用失败率 > 20%
   - 监控平均响应时间

2. **日志收集**
   - 收集所有 `[Tool Call]` 日志
   - 分析工具使用模式
   - 识别性能瓶颈

3. **缓存优化**
   - 监控 Redis 缓存命中率
   - 调整缓存过期时间（默认 1 小时）
   - 清理过期缓存

## 📚 相关文档

- [MCP 实现指南](./MCP_IMPLEMENTATION_GUIDE.md)
- [MCP 快速参考](./MCP_QUICK_REFERENCE.md)
- [系统架构文档](./AGENT_SYSTEM_ARCHITECTURE.md)

## 🔄 版本历史

### v1.0.0 (2026-01-31)

**修复内容**：
- ✅ 新增 ToolAdapter 模块
- ✅ 新增工具调用追踪器
- ✅ 重构 MCPClient.get_tools() 返回真正的工具对象
- ✅ 优化 build_search_tools() 和 build_recommend_tools()
- ✅ 增强搜索和推荐流程的工具调用日志
- ✅ 添加单元测试和集成测试
- ✅ 完善文档和使用指南

**影响范围**：
- `travel-assistant-agent/src/agents/tool_adapter.py` (新增)
- `travel-assistant-agent/src/utils/tools_invocation_logger.py` (新增)
- `travel-assistant-agent/src/agents/mcp_client.py` (修改)
- `travel-assistant-agent/src/workflows/subgraphs/common.py` (修改)
- `travel-assistant-agent/src/workflows/subgraphs/search.py` (修改)
- `travel-assistant-agent/src/workflows/subgraphs/recommend.py` (修改)
- `travel-assistant-agent/tests/test_tool_adapter.py` (新增)
- `travel-assistant-agent/tests/test_search_tools_binding.py` (新增)

**预期效果**：

修改前：
```
[Agent] Thinking: 我需要搜索杭州的酒店
[Agent] I should use search_hotels tool
[Agent] Output: 基于我的理解，推荐以下酒店...（没有真正调用工具）
```

修改后：
```
[Build Tools] ✅ Added 5 MCP Java tools
[Search Execute] 🔧 Tools available: ['rag_search_tool', 'search_hotels', 'search_flights', ...]
[Search Execute] 🤖 Creating ReAct agent with 8 tools
[Search Execute] 🚀 Starting agent execution...
[Tool Call] 🔧 Invoking: search_hotels
[Tool Call] Parameters: {'destination': '杭州', 'price_max': 1000}
[Java MCP] POST /mcp/tools/search_hotels/call - 200 OK
[Tool Call] ✅ Success: search_hotels (took 2.31s)
[Agent] Observation: 成功获得 42 家酒店数据...
[Agent] Final Answer: 根据您的预算和偏好，为您推荐以下酒店...
[Search Execute] ✅ Agent execution completed
```

---

**维护者**: AI Development Team  
**最后更新**: 2026-01-31  
**状态**: ✅ 已实现并测试
