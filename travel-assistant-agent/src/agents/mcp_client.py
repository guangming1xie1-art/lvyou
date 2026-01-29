"""
MCP Client for Java API Integration

使用 langchain_mcp_adapters 连接到后端 Java API 服务
将 Java API 方法包装为 LangChain Tools
"""
import asyncio
import logging
import json
import httpx
from typing import Any, Dict, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

from langchain_mcp_adapters.client import MultiServerMCPClient
# from langchain_mcp_adapters.sessions import HttpConnection
from conf import settings
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class MCPClient:
    """
    MCP Client 连接 Java API 后端
    支持 HTTP 直接调用，具有重试、超时和缓存机制
    支持JWT token转发用于用户认证
    """

    # 服务端口映射表
    # Java 微服务架构 - 每个服务运行在不同端口
    SERVICE_PORTS = {
        # 基础服务地址
        "base": "localhost:8080",

        # 酒店服务 - port 8081
        # 功能：搜索酒店、获取酒店详情、价格查询
        "hotel-service": "localhost:8081",
        # 相关工具：search_hotels, get_hotel_details

        # 航班服务 - port 8082
        # 功能：搜索航班、获取航班详情、价格查询
        "flight-service": "localhost:8082",
        # 相关工具：search_flights, get_flight_details

        # 景点服务 - port 8084
        # 功能：搜索景点、获取景点详情、门票预订
        "attractions-service": "localhost:8084",
        # 相关工具：search_attractions, get_attraction_details

        # 预订服务 - port 8085
        # 功能：创建预订、查询预订状态、取消预订
        "booking-service": "localhost:8085",
        # 相关工具：create_booking, get_booking_status, cancel_booking

        # 推荐服务 - port 8086
        # 功能：生成个性化推荐、基于用户偏好的推荐
        "recommendation-service": "localhost:8086",
        # 相关工具：get_recommendations, get_personalized_recommendations
    }

    # 工具名到服务的映射
    TOOL_SERVICE_MAP = {
        "search_hotels": "hotel-service",
        "get_hotel_details": "hotel-service",
        "search_flights": "flight-service",
        "get_flight_details": "flight-service",
        "search_attractions": "attractions-service",
        "get_attraction_details": "attractions-service",
        "create_booking": "booking-service",
        "get_booking_status": "booking-service",
        "cancel_booking": "booking-service",
        "get_recommendations": "recommendation-service",
        "get_personalized_recommendations": "recommendation-service",
    }

    def __init__(
        self,
        java_api_url: Optional[str] = None,
        token: Optional[str] = None,
        user_id: Optional[str] = None,
        username: Optional[str] = None
    ):
        # 默认指向 Gateway MCP 服务端口 9000（MCP 统一入口）
        # 注意：实际调用时会根据工具名路由到具体服务
        self.java_api_url = java_api_url or "http://localhost:9000"
        self._client: Optional[MultiServerMCPClient] = None
        self._redis: Optional[redis.Redis] = None
        self.timeout = 30.0  # 增加超时时间到30秒

        # JWT token 和用户信息（用于转发到Java服务）
        self.token = token
        self.user_id = user_id
        self.username = username
        
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        构建包含JWT和用户上下文的请求headers
        
        Returns:
            Headers字典
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # 添加JWT Authorization header
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            logger.debug(f"Added Authorization header with token")
        
        # 添加用户上下文headers
        if self.user_id:
            headers["X-User-ID"] = str(self.user_id)
        if self.username:
            headers["X-Username"] = self.username
        
        return headers
    
    async def _get_redis(self) -> redis.Redis:
        if self._redis is None:
            self._redis = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True
            )
        return self._redis

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
    
    async def connect(self):
        """兼容性方法"""
        await self._get_client()
        return True

    def is_connected(self) -> bool:
        """兼容性方法"""
        return self._client is not None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def call_tool(
        self,
        tool_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        调用 Java API 工具
        支持重试机制（3次重试，指数退避）
        超时控制（30秒）
        结果缓存（Redis，1小时）
        调用 Gateway 的 MCP 统一端点，由 Gateway 路由到具体服务
        """
        # 合并参数
        params = parameters or {}
        params.update(kwargs)

        cache_key = f"mcp_cache:{tool_name}:{hash(json.dumps(params, sort_keys=True))}"

        # 1. 尝试从缓存获取
        try:
            r = await self._get_redis()
            cached_result = await r.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit for MCP tool: {tool_name}")
                return json.loads(cached_result)
        except Exception as e:
            logger.warning(f"Redis cache error: {e}")

        # 2. 构建 Gateway MCP 端点 URL
        # 新的架构：所有工具调用都通过 Gateway MCP 端点
        url = f"{self.java_api_url}/mcp/tools/{tool_name}/call"

        # 构建请求体（Gateway MCP 端点期望的格式）
        request_body = {
            "parameters": params
        }

        # 构建包含JWT的headers
        headers = self._get_auth_headers()

        logger.info(f"Calling MCP tool '{tool_name}' via Gateway at {url}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=request_body, headers=headers)
                response.raise_for_status()
                result = response.json()

                # 3. 存入缓存 (1小时)
                try:
                    await r.setex(cache_key, 3600, json.dumps(result))
                except Exception as e:
                    logger.warning(f"Failed to cache MCP result: {e}")

                logger.info(f"MCP tool {tool_name} called successfully via Gateway with JWT auth")
                return result
        except Exception as e:
            logger.error(f"Failed to call MCP tool {tool_name} via Gateway at {url}: {e}")
            # 如果是 search 相关工具失败，尝试使用 mock 数据
            if "search" in tool_name:
                return self._mock_response(tool_name, params)
            raise e

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


def get_mcp_client(
    token: Optional[str] = None,
    user_id: Optional[str] = None,
    username: Optional[str] = None
) -> MCPClient:
    """
    获取 MCP Client 实例
    
    注意：如果提供了token参数，会创建新的客户端实例而不是使用全局单例
    这样可以确保每个请求使用正确的JWT token
    
    Args:
        token: JWT access token
        user_id: 用户ID
        username: 用户名
        
    Returns:
        MCPClient实例
    """
    # 如果提供了token，创建新的实例（每个请求有不同的token）
    if token:
        return MCPClient(
            token=token,
            user_id=user_id,
            username=username
        )
    
    # 否则使用全局单例（向后兼容）
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client


__all__ = [
    "MCPClient",
    "get_mcp_client",
]
