"""
MCP 工具管理辅助模块
负责 MCP 工具的转换、验证和包装
"""
from typing import Any, Dict, List, Optional, Union
import asyncio
import json
from dataclasses import dataclass
from langchain.tools import BaseTool
from langchain_experimental import create_agent
from langchain_anthropic import ChatAnthropic
from loguru import logger


@dataclass
class MCPToolInfo:
    """MCP 工具信息"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    tool_func: callable
    category: str = "general"


class MCPToolsManager:
    """MCP 工具管理器"""
    
    def __init__(self):
        self.tools_cache: Dict[str, List[BaseTool]] = {}
        self.mcp_client = None
        
    async def initialize(self, mcp_client):
        """初始化 MCP 客户端"""
        self.mcp_client = mcp_client
        logger.info("MCP Tools Manager initialized")
        
    async def get_search_tools(self) -> List[BaseTool]:
        """获取搜索工具"""
        if "search" in self.tools_cache:
            return self.tools_cache["search"]
            
        try:
            # 获取 MCP 工具
            mcp_tools = await self.mcp_client.get_tools("java_api")
            
            # 转换为 LangChain 工具
            search_tools = await self._convert_mcp_tools_to_langchain(
                mcp_tools, 
                category="search"
            )
            
            # 缓存结果
            self.tools_cache["search"] = search_tools
            logger.info(f"Loaded {len(search_tools)} search tools")
            return search_tools
            
        except Exception as e:
            logger.error(f"Failed to load search tools: {e}")
            # 返回降级工具
            return await self._create_fallback_search_tools()
            
    async def get_booking_tools(self) -> List[BaseTool]:
        """获取预订工具"""
        if "booking" in self.tools_cache:
            return self.tools_cache["booking"]
            
        try:
            # 获取 MCP 工具
            mcp_tools = await self.mcp_client.get_tools("java_api")
            
            # 转换为 LangChain 工具
            booking_tools = await self._convert_mcp_tools_to_langchain(
                mcp_tools, 
                category="booking"
            )
            
            # 缓存结果
            self.tools_cache["booking"] = booking_tools
            logger.info(f"Loaded {len(booking_tools)} booking tools")
            return booking_tools
            
        except Exception as e:
            logger.error(f"Failed to load booking tools: {e}")
            # 返回降级工具
            return await self._create_fallback_booking_tools()
            
    async def _convert_mcp_tools_to_langchain(self, mcp_tools: List[Any], 
                                            category: str) -> List[BaseTool]:
        """将 MCP 工具转换为 LangChain 工具"""
        converted_tools = []
        
        for mcp_tool in mcp_tools:
            try:
                langchain_tool = await self._convert_single_mcp_tool(mcp_tool, category)
                if langchain_tool:
                    converted_tools.append(langchain_tool)
            except Exception as e:
                logger.warning(f"Failed to convert MCP tool {getattr(mcp_tool, 'name', 'unknown')}: {e}")
                continue
                
        return converted_tools
        
    async def _convert_single_mcp_tool(self, mcp_tool: Any, category: str) -> Optional[BaseTool]:
        """转换单个 MCP 工具"""
        try:
            # 提取工具信息
            tool_name = getattr(mcp_tool, 'name', f"{category}_tool")
            tool_description = getattr(mcp_tool, 'description', f"{category} related tool")
            tool_schema = getattr(mcp_tool, 'input_schema', {})
            
            # 创建 LangChain 工具
            class MCPToolWrapper(BaseTool):
                def __init__(self, mcp_tool_instance, **kwargs):
                    super().__init__(**kwargs)
                    self.mcp_tool = mcp_tool_instance
                    
                def _run(self, tool_input: str) -> str:
                    """同步执行工具"""
                    try:
                        # 解析输入参数
                        if isinstance(tool_input, str):
                            try:
                                params = json.loads(tool_input)
                            except json.JSONDecodeError:
                                params = {"input": tool_input}
                        else:
                            params = tool_input
                            
                        # 调用 MCP 工具
                        result = self.mcp_tool.invoke(params)
                        
                        # 处理结果
                        if hasattr(result, 'content'):
                            return str(result.content)
                        elif isinstance(result, dict):
                            return json.dumps(result, ensure_ascii=False)
                        else:
                            return str(result)
                            
                    except Exception as e:
                        logger.error(f"MCP tool execution failed: {e}")
                        return json.dumps({"error": str(e)})
                        
                async def _arun(self, tool_input: str) -> str:
                    """异步执行工具"""
                    try:
                        # 解析输入参数
                        if isinstance(tool_input, str):
                            try:
                                params = json.loads(tool_input)
                            except json.JSONDecodeError:
                                params = {"input": tool_input}
                        else:
                            params = tool_input
                            
                        # 调用 MCP 工具
                        if hasattr(self.mcp_tool, 'ainvoke'):
                            result = await self.mcp_tool.ainvoke(params)
                        else:
                            result = self.mcp_tool.invoke(params)
                        
                        # 处理结果
                        if hasattr(result, 'content'):
                            return str(result.content)
                        elif isinstance(result, dict):
                            return json.dumps(result, ensure_ascii=False)
                        else:
                            return str(result)
                            
                    except Exception as e:
                        logger.error(f"MCP tool async execution failed: {e}")
                        return json.dumps({"error": str(e)})
            
            # 创建工具实例
            tool_instance = MCPToolWrapper(
                mcp_tool_instance=mcp_tool,
                name=tool_name,
                description=tool_description,
                args_schema=tool_schema if tool_schema else None
            )
            
            return tool_instance
            
        except Exception as e:
            logger.error(f"Failed to create MCP tool wrapper: {e}")
            return None
            
    async def _create_fallback_search_tools(self) -> List[BaseTool]:
        """创建降级搜索工具"""
        from langchain.tools import Tool
        
        def mock_search(query: str) -> str:
            """模拟搜索功能"""
            return json.dumps({
                "status": "fallback",
                "message": "使用模拟搜索结果",
                "query": query,
                "results": [
                    {
                        "title": "搜索结果示例",
                        "description": "这是搜索结果的示例数据",
                        "source": "fallback_search"
                    }
                ]
            }, ensure_ascii=False)
            
        return [
            Tool(
                name="fallback_search",
                description="模拟搜索工具（降级模式）",
                func=mock_search
            )
        ]
        
    async def _create_fallback_booking_tools(self) -> List[BaseTool]:
        """创建降级预订工具"""
        from langchain.tools import Tool
        
        def mock_booking(booking_data: str) -> str:
            """模拟预订功能"""
            try:
                data = json.loads(booking_data) if isinstance(booking_data, str) else booking_data
            except json.JSONDecodeError:
                data = {"booking_data": booking_data}
                
            return json.dumps({
                "status": "fallback",
                "message": "使用模拟预订结果",
                "booking_id": "fallback_booking_123",
                "booking_data": data,
                "confirmation": "您的预订已确认（模拟）"
            }, ensure_ascii=False)
            
        return [
            Tool(
                name="fallback_booking",
                description="模拟预订工具（降级模式）",
                func=mock_booking
            )
        ]
        
    def validate_tool_input(self, tool_name: str, input_data: Dict[str, Any]) -> bool:
        """验证工具输入参数"""
        try:
            # 获取工具定义
            tool_info = self._get_tool_info(tool_name)
            if not tool_info:
                return True  # 如果没有找到工具定义，允许通过
                
            # 检查必需字段
            required_fields = tool_info.input_schema.get("required", [])
            for field in required_fields:
                if field not in input_data:
                    logger.warning(f"Missing required field '{field}' for tool '{tool_name}'")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Tool input validation failed: {e}")
            return False
            
    def _get_tool_info(self, tool_name: str) -> Optional[MCPToolInfo]:
        """获取工具信息"""
        # 这里可以从缓存或配置中获取工具信息
        # 目前返回基础信息
        return MCPToolInfo(
            name=tool_name,
            description=f"Tool: {tool_name}",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            tool_func=None
        )
        
    async def cleanup(self):
        """清理资源"""
        self.tools_cache.clear()
        logger.info("MCP Tools Manager cleaned up")


# 全局实例
_mcp_tools_manager: Optional[MCPToolsManager] = None


async def get_mcp_tools_manager() -> MCPToolsManager:
    """获取 MCP 工具管理器实例"""
    global _mcp_tools_manager
    
    if _mcp_tools_manager is None:
        _mcp_tools_manager = MCPToolsManager()
        
    return _mcp_tools_manager


async def cleanup_mcp_tools():
    """清理 MCP 工具管理器资源"""
    global _mcp_tools_manager
    
    if _mcp_tools_manager:
        await _mcp_tools_manager.cleanup()
        _mcp_tools_manager = None