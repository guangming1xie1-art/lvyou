"""
MCP Tool Adapter - 将 MCP 工具元数据转换为 LangChain Tool 对象

这个模块解决了当前工具绑定的核心问题：
1. mcp_client.get_tools() 返回的是字典而不是可调用的工具
2. LangChain Agent 需要真正的 Tool 对象才能调用
3. 工具转换需要保持异步调用能力
"""

from typing import Any, Dict, Optional, Type
import logging
import json
import time
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool, StructuredTool

logger = logging.getLogger(__name__)


class ToolAdapter:
    """
    将 MCP 工具元数据转换为 LangChain Tool 对象
    
    核心功能：
    1. 接收 MCP 工具定义（字典格式）
    2. 包装成可调用的异步函数
    3. 返回 LangChain Tool 对象
    4. 记录工具调用日志和性能指标
    """
    
    def __init__(self, tool_def: Dict[str, Any], mcp_client: Any):
        """
        初始化工具适配器
        
        Args:
            tool_def: MCP 工具定义字典
                {
                    "name": "tool_name",
                    "description": "tool description",
                    "args_schema": {...}
                }
            mcp_client: MCPClient 实例（用于实际调用 Java 服务）
        """
        self.tool_def = tool_def
        self.mcp_client = mcp_client
        self.tool_name = tool_def.get("name", "unknown_tool")
        self.description = tool_def.get("description", "No description available")
        self.args_schema = tool_def.get("args_schema")
        
    async def invoke_async(self, **kwargs) -> str:
        """
        异步调用 Java 后端工具
        
        Args:
            **kwargs: 工具参数（由 LangChain Agent 传入）
            
        Returns:
            工具执行结果（JSON 字符串）
        """
        start_time = time.time()
        
        try:
            logger.info(f"[Tool Call] 🔧 Invoking: {self.tool_name}")
            logger.debug(f"[Tool Call] Parameters: {json.dumps(kwargs, ensure_ascii=False)}")
            
            # 调用 MCP Client 的 call_tool 方法
            # 这会通过 HTTP 请求 Java Gateway MCP 端点
            result = await self.mcp_client.call_tool(
                self.tool_name,
                parameters=kwargs
            )
            
            elapsed = time.time() - start_time
            
            # 记录结果摘要
            result_summary = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
            logger.info(f"[Tool Call] ✅ Success: {self.tool_name} (took {elapsed:.2f}s)")
            logger.debug(f"[Tool Call] Result summary: {result_summary}")
            
            # 返回 JSON 字符串（LangChain Agent 期望的格式）
            return json.dumps(result, ensure_ascii=False)
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[Tool Call] ❌ Failed: {self.tool_name} (took {elapsed:.2f}s) - {e}")
            
            # 返回错误信息
            return json.dumps({
                "error": str(e),
                "tool_name": self.tool_name,
                "status": "failed"
            }, ensure_ascii=False)
    
    def invoke_sync(self, **kwargs) -> str:
        """
        同步调用（包装异步调用）
        
        Args:
            **kwargs: 工具参数
            
        Returns:
            工具执行结果（JSON 字符串）
        """
        import asyncio
        
        try:
            # 获取或创建事件循环
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果循环正在运行，创建新任务
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.invoke_async(**kwargs)
                    )
                    return future.result()
            else:
                # 如果循环未运行，直接运行
                return loop.run_until_complete(self.invoke_async(**kwargs))
        except Exception as e:
            logger.error(f"[Tool Call] ❌ Sync invoke failed: {self.tool_name} - {e}")
            return json.dumps({
                "error": str(e),
                "tool_name": self.tool_name,
                "status": "failed"
            }, ensure_ascii=False)
    
    def to_langchain_tool(self) -> BaseTool:
        """
        转换为 LangChain Tool 对象
        
        Returns:
            BaseTool: 可被 create_react_agent() 使用的工具对象
        """
        # 创建 Pydantic 模型（如果有 schema）
        args_schema_model = None
        if self.args_schema:
            try:
                # 动态创建 Pydantic 模型
                fields = {}
                properties = self.args_schema.get("properties", {})
                required = self.args_schema.get("required", [])
                
                for field_name, field_def in properties.items():
                    field_type = self._json_type_to_python(field_def.get("type", "string"))
                    field_description = field_def.get("description", "")
                    is_required = field_name in required
                    
                    if is_required:
                        fields[field_name] = (field_type, Field(..., description=field_description))
                    else:
                        fields[field_name] = (field_type, Field(None, description=field_description))
                
                # 动态创建 Pydantic 模型类
                args_schema_model = type(
                    f"{self.tool_name}_Schema",
                    (BaseModel,),
                    {
                        "__annotations__": {k: v[0] for k, v in fields.items()},
                        **{k: v[1] for k, v in fields.items()}
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to create args_schema for {self.tool_name}: {e}")
        
        # 创建 LangChain StructuredTool
        tool = StructuredTool(
            name=self.tool_name,
            description=self.description,
            func=self.invoke_sync,
            coroutine=self.invoke_async,
            args_schema=args_schema_model
        )
        
        logger.debug(f"[Tool Adapter] Created LangChain tool: {self.tool_name}")
        return tool
    
    @staticmethod
    def _json_type_to_python(json_type: str) -> Type:
        """
        将 JSON Schema 类型转换为 Python 类型
        
        Args:
            json_type: JSON Schema 类型字符串
            
        Returns:
            对应的 Python 类型
        """
        type_mapping = {
            "string": str,
            "number": float,
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict
        }
        return type_mapping.get(json_type, str)


def wrap_mcp_tools(mcp_tools_dicts: list, mcp_client: Any) -> list:
    """
    批量包装 MCP 工具为 LangChain Tools
    
    Args:
        mcp_tools_dicts: MCP 工具定义字典列表
        mcp_client: MCPClient 实例
        
    Returns:
        LangChain Tool 对象列表
    """
    langchain_tools = []
    
    for tool_def in mcp_tools_dicts:
        try:
            adapter = ToolAdapter(tool_def, mcp_client)
            tool = adapter.to_langchain_tool()
            langchain_tools.append(tool)
            logger.info(f"[Tool Adapter] ✅ Wrapped tool: {tool_def.get('name')}")
        except Exception as e:
            logger.error(f"[Tool Adapter] ❌ Failed to wrap tool {tool_def.get('name')}: {e}")
    
    logger.info(f"[Tool Adapter] Wrapped {len(langchain_tools)}/{len(mcp_tools_dicts)} tools")
    return langchain_tools


__all__ = [
    "ToolAdapter",
    "wrap_mcp_tools",
]
