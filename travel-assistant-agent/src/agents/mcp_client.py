"""
MCP Client for Java API Integration

使用 langchain_mcp_adapters 连接到后端 Java API 服务
将 Java API 方法包装为 LangChain Tools
"""
import asyncio
import logging
from typing import Any, Dict, List, Optional

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import HttpConnection
from src.config import settings

logger = logging.getLogger(__name__)


class MCPClient:
    """
    MCP Client 连接 Java API 后端
    使用 langchain_mcp_adapters.MultiServerMCPClient 实现
    """
    
    def __init__(self, java_api_url: Optional[str] = None):
        self.java_api_url = java_api_url or settings.java_api_url
        self._client: Optional[MultiServerMCPClient] = None
        
    async def _get_client(self) -> MultiServerMCPClient:
        """获取或创建 MCP 客户端"""
        if self._client is None:
            # 配置连接
            connections = {
                "java_api": {
                    "url": f"{self.java_api_url}/mcp",
                    "transport": "http"
                }
            }
            
            self._client = MultiServerMCPClient(connections=connections)
            logger.info(f"Created MCP client for {self.java_api_url}")
        
        return self._client
    
    async def get_tools(self) -> List[Dict[str, Any]]:
        """获取所有工具定义（LangChain Tool 格式）"""
        try:
            client = await self._get_client()
            tools = await client.get_tools()
            
            # 转换为字典格式
            tool_dicts = []
            for tool in tools:
                tool_dict = {
                    "name": tool.name,
                    "description": getattr(tool, 'description', str(tool)),
                    "args_schema": tool.args_schema if hasattr(tool, 'args_schema') else None,
                }
                tool_dicts.append(tool_dict)
            
            return tool_dicts
        
        except Exception as e:
            logger.warning(f"Failed to get tools from MCP: {e}")
            return self._get_mock_tools()
    
    async def get_tool_summaries(self) -> List[Dict[str, str]]:
        """获取工具摘要（名称 + 描述）"""
        try:
            client = await self._get_client()
            tools = await client.get_tools()
            
            summaries = []
            for tool in tools:
                summaries.append({
                    "name": tool.name,
                    "description": getattr(tool, 'description', str(tool))
                })
            return summaries
        
        except Exception as e:
            logger.warning(f"Failed to get tool summaries: {e}")
            return self._get_mock_tool_summaries()
    
    def get_tool_summaries_text(self) -> str:
        """
        获取工具摘要（文本格式，用于 LLM prompt）
        同步方法，优先返回缓存或mock数据
        """
        try:
            # 这里返回mock数据，因为需要异步调用
            return self._get_mock_tool_summaries_text()
        except Exception as e:
            logger.warning(f"Failed to get tool summaries text: {e}")
            return "暂无可用工具"
    
    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """调用 Java API 工具"""
        try:
            client = await self._get_client()
            
            # 直接调用 MCP 工具
            # 注意：实际的工具调用可能需要不同的方法
            tools = await client.get_tools()
            
            # 查找匹配的工具
            target_tool = None
            for tool in tools:
                if tool.name == tool_name:
                    target_tool = tool
                    break
            
            if target_tool:
                # 调用工具
                if hasattr(target_tool, 'ainvoke'):
                    result = await target_tool.ainvoke(parameters)
                else:
                    result = target_tool.invoke(parameters)
                
                return {
                    "result": result,
                    "error": None
                }
            else:
                return {
                    "result": None,
                    "error": f"Tool '{tool_name}' not found"
                }
        
        except Exception as e:
            logger.warning(f"Failed to call tool {tool_name}: {e}")
            return self._mock_response(tool_name, parameters)
    
    def _get_mock_tools(self) -> List[Dict[str, Any]]:
        """返回 Mock 工具定义"""
        return [
            {
                "name": "search_destinations",
                "description": "搜索旅游目的地、酒店、景点等信息",
                "args_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "搜索关键词"},
                        "filters": {
                            "type": "object",
                            "description": "过滤条件（预算、日期、偏好等）"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_recommendations",
                "description": "根据用户偏好和搜索结果生成个性化推荐",
                "args_schema": {
                    "type": "object",
                    "properties": {
                        "user_preferences": {
                            "type": "object",
                            "description": "用户偏好信息"
                        },
                        "search_results": {
                            "type": "array",
                            "description": "搜索结果列表"
                        }
                    },
                    "required": ["user_preferences"]
                }
            },
            {
                "name": "create_booking",
                "description": "创建旅游预订",
                "args_schema": {
                    "type": "object",
                    "properties": {
                        "booking_details": {
                            "type": "object",
                            "description": "预订详情（目的地、日期、酒店、航班等）"
                        }
                    },
                    "required": ["booking_details"]
                }
            },
            {
                "name": "get_booking_status",
                "description": "查询预订状态",
                "args_schema": {
                    "type": "object",
                    "properties": {
                        "booking_id": {
                            "type": "string",
                            "description": "预订 ID"
                        }
                    },
                    "required": ["booking_id"]
                }
            },
        ]
    
    def _get_mock_tool_summaries(self) -> List[Dict[str, str]]:
        """返回 Mock 工具摘要"""
        return [
            {"name": "search_destinations", "description": "搜索旅游目的地、酒店、景点等信息"},
            {"name": "get_recommendations", "description": "根据用户偏好和搜索结果生成个性化推荐"},
            {"name": "create_booking", "description": "创建旅游预订"},
            {"name": "get_booking_status", "description": "查询预订状态"},
        ]
    
    def _get_mock_tool_summaries_text(self) -> str:
        """返回 Mock 工具摘要文本"""
        return """- search_destinations: 搜索旅游目的地、酒店、景点等信息
- get_recommendations: 根据用户偏好和搜索结果生成个性化推荐
- create_booking: 创建旅游预订
- get_booking_status: 查询预订状态"""
    
    def _mock_response(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        返回 Mock 数据（当 Java API 不可用时）
        """
        logger.warning(f"Returning mock data for {tool_name}")
        
        if tool_name == "search_destinations":
            return {
                "result": {
                    "destinations": [
                        {
                            "id": "dest_mock_001",
                            "name": "模拟目的地",
                            "description": "这是模拟数据（Java API 不可用）",
                            "rating": 4.5
                        }
                    ],
                    "total": 1,
                    "mock": True
                },
                "error": "Java API unavailable, using mock data"
            }
        
        elif tool_name == "get_recommendations":
            return {
                "result": {
                    "recommendations": [
                        {
                            "id": "rec_mock_001",
                            "title": "模拟推荐方案",
                            "description": "这是模拟数据（Java API 不可用）",
                            "confidence": 0.5
                        }
                    ],
                    "mock": True
                },
                "error": "Java API unavailable, using mock data"
            }
        
        elif tool_name == "create_booking":
            return {
                "result": {
                    "booking_id": "BK_MOCK_001",
                    "status": "pending",
                    "mock": True
                },
                "error": "Java API unavailable, using mock data"
            }
        
        elif tool_name == "get_booking_status":
            return {
                "result": {
                    "booking_id": parameters.get("booking_id", "unknown"),
                    "status": "unknown",
                    "mock": True
                },
                "error": "Java API unavailable, using mock data"
            }
        
        else:
            return {
                "result": None,
                "error": f"No mock data available for {tool_name}"
            }


# ============ 全局单例 ============

_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """获取全局 MCP Client 实例（懒加载）"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client


__all__ = [
    "MCPClient",
    "get_mcp_client",
]
