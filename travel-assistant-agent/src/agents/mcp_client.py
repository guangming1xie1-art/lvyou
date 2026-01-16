"""
MCP Client for Java API Integration

使用 langchain_mcp_adapters 连接到后端 Java API 服务
将 Java API 方法包装为 LangChain Tools
"""
import asyncio
import httpx
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from src.config import settings

logger = logging.getLogger(__name__)


@dataclass
class JavaAPITool:
    """Java API 工具定义"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    endpoint: str


class MCPClient:
    """
    MCP Client 连接 Java API 后端
    将 Java API 的方法包装为 LLM Tool
    """
    
    def __init__(self, java_api_url: Optional[str] = None):
        self.java_api_url = java_api_url or settings.java_api_base_url
        self.timeout = settings.java_api_timeout
        self.max_retries = settings.java_api_max_retries
        self.auth_token = settings.java_api_auth_token
        
        self._connected = False
        self._tools: List[JavaAPITool] = []
        self._client: Optional[httpx.AsyncClient] = None
    
    async def connect(self) -> bool:
        """连接到 Java API 后端"""
        try:
            # 创建 httpx 客户端
            self._client = httpx.AsyncClient(
                base_url=self.java_api_url,
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bearer {self.auth_token}" if self.auth_token else None,
                    "Content-Type": "application/json"
                }
            )
            
            # 测试连接（可选）
            try:
                response = await self._client.get("/health", timeout=5)
                if response.status_code == 200:
                    logger.info(f"Connected to Java API: {self.java_api_url}")
                else:
                    logger.warning(f"Java API health check failed: {response.status_code}")
            except Exception as e:
                logger.warning(f"Java API health check failed: {e}, continuing anyway")
            
            self._connected = True
            self._init_tools()
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Java API: {e}")
            self._connected = False
            return False
    
    async def disconnect(self):
        """断开连接"""
        if self._client:
            await self._client.aclose()
            self._client = None
        self._connected = False
        logger.info("Disconnected from Java API")
    
    def _init_tools(self):
        """初始化 Java API 工具定义"""
        self._tools = [
            JavaAPITool(
                name="search_destinations",
                description="搜索旅游目的地、酒店、景点等信息",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "搜索关键词"},
                        "filters": {
                            "type": "object",
                            "description": "过滤条件（预算、日期、偏好等）"
                        }
                    },
                    "required": ["query"]
                },
                endpoint="/search/destinations"
            ),
            JavaAPITool(
                name="get_recommendations",
                description="根据用户偏好和搜索结果生成个性化推荐",
                input_schema={
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
                },
                endpoint="/recommendations/generate"
            ),
            JavaAPITool(
                name="create_booking",
                description="创建旅游预订",
                input_schema={
                    "type": "object",
                    "properties": {
                        "booking_details": {
                            "type": "object",
                            "description": "预订详情（目的地、日期、酒店、航班等）"
                        }
                    },
                    "required": ["booking_details"]
                },
                endpoint="/bookings/create"
            ),
            JavaAPITool(
                name="get_booking_status",
                description="查询预订状态",
                input_schema={
                    "type": "object",
                    "properties": {
                        "booking_id": {
                            "type": "string",
                            "description": "预订 ID"
                        }
                    },
                    "required": ["booking_id"]
                },
                endpoint="/bookings/{booking_id}/status"
            ),
        ]
        logger.info(f"Initialized {len(self._tools)} Java API tools")
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        获取所有工具定义（LangChain Tool 格式）
        
        Returns:
            工具定义列表
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
            for tool in self._tools
        ]
    
    def get_tool_summaries(self) -> List[Dict[str, str]]:
        """
        获取工具摘要（名称 + 描述）
        用于 LLM Prompt
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
            }
            for tool in self._tools
        ]
    
    def get_tool_summaries_text(self) -> str:
        """
        获取工具摘要（文本格式，用于 LLM prompt）
        
        Returns:
            格式化的文本字符串
        """
        summaries = []
        for tool in self._tools:
            summaries.append(f"- {tool.name}: {tool.description}")
        return "\n".join(summaries)
    
    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        调用 Java API 工具
        
        Args:
            tool_name: 工具名称
            parameters: 参数
            
        Returns:
            {"result": ..., "error": null | string}
        """
        # 查找工具
        tool = None
        for t in self._tools:
            if t.name == tool_name:
                tool = t
                break
        
        if not tool:
            return {
                "result": None,
                "error": f"Tool '{tool_name}' not found"
            }
        
        # 如果未连接，尝试连接
        if not self._connected:
            success = await self.connect()
            if not success:
                return self._mock_response(tool_name, parameters)
        
        # 调用 Java API
        try:
            # 处理 URL 参数
            endpoint = tool.endpoint
            if "{booking_id}" in endpoint and "booking_id" in parameters:
                endpoint = endpoint.format(booking_id=parameters["booking_id"])
                # 从 parameters 中移除 booking_id（已经在 URL 中）
                parameters = {k: v for k, v in parameters.items() if k != "booking_id"}
            
            # 发起请求
            response = await self._client.post(
                endpoint,
                json=parameters,
                timeout=self.timeout
            )
            
            # 处理响应
            if response.status_code == 200:
                result = response.json()
                return {
                    "result": result,
                    "error": None
                }
            else:
                error_msg = f"Java API error: {response.status_code}"
                logger.error(error_msg)
                return {
                    "result": None,
                    "error": error_msg
                }
        
        except httpx.TimeoutException:
            logger.error(f"Timeout calling {tool_name}")
            return self._mock_response(tool_name, parameters)
        
        except Exception as e:
            logger.error(f"Error calling {tool_name}: {e}")
            return self._mock_response(tool_name, parameters)
    
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
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected


# ============ 全局单例 ============

_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """获取全局 MCP Client 实例（懒加载）"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client


async def init_mcp_client(java_api_url: Optional[str] = None) -> MCPClient:
    """初始化并连接 MCP Client"""
    global _mcp_client
    _mcp_client = MCPClient(java_api_url)
    await _mcp_client.connect()
    return _mcp_client


__all__ = [
    "MCPClient",
    "JavaAPITool",
    "get_mcp_client",
    "init_mcp_client",
]
