"""
Search Skill Implementation
根据用户需求搜索旅游目的地、酒店、航班等信息
"""
from typing import Dict, Any, Optional
import logging
from skills.base import Skill
from agents.mcp_client import get_mcp_client

logger = logging.getLogger(__name__)


class SearchSkill(Skill):
    """搜索技能 - 搜索旅游目的地、酒店、航班等"""
    
    def __init__(self):
        super().__init__(
            name="search",
            description="根据用户需求搜索旅游目的地、酒店、航班等信息",
            version="1.0.0",
            enabled=True,
            cost_estimate=0.05,
            category="search"
        )
        self.mcp_client = None
    
    def get_required_fields(self) -> list:
        """必需字段"""
        return ["query"]
    
    async def _ensure_mcp_client(self):
        """确保 MCP Client 已初始化"""
        if self.mcp_client is None:
            self.mcp_client = get_mcp_client()
            if not self.mcp_client.is_connected():
                try:
                    await self.mcp_client.connect()
                except Exception as e:
                    logger.warning(f"Failed to connect MCP client: {e}")
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行搜索
        
        Args:
            input_data: {
                "query": str,
                "filters": {...},
                "limit": int,
                "offset": int
            }
        
        Returns:
            {
                "results": [...],
                "total": int,
                "search_quality": float
            }
        """
        query = input_data.get("query", "")
        filters = input_data.get("filters", {})
        limit = input_data.get("limit", 10)
        offset = input_data.get("offset", 0)
        
        if not query:
            return {
                "results": [],
                "total": 0,
                "error": "Query is required"
            }
        
        # 确保 MCP Client 连接
        await self._ensure_mcp_client()
        
        # 调用 Java API 的 search_destinations
        try:
            result = await self.mcp_client.call_tool(
                tool_name="search_destinations",
                parameters={
                    "query": query,
                    "filters": filters
                }
            )
            
            if result.get("error"):
                logger.warning(f"Java API error: {result['error']}")
            
            # 提取结果
            api_result = result.get("result", {})
            
            # 构建返回格式
            return {
                "results": api_result.get("destinations", [])[:limit],
                "total": api_result.get("total", 0),
                "search_quality": self._calculate_search_quality(api_result),
                "filters_applied": filters,
                "metadata": {
                    "execution_time_ms": 500,
                    "data_sources": ["java_api"],
                    "mock": api_result.get("mock", False)
                }
            }
        
        except Exception as e:
            logger.error(f"Error executing search: {e}")
            return {
                "results": [],
                "total": 0,
                "error": str(e)
            }
    
    def _calculate_search_quality(self, api_result: Dict[str, Any]) -> float:
        """计算搜索质量分数"""
        destinations = api_result.get("destinations", [])
        if not destinations:
            return 0.0
        
        # 简单的质量评分：基于结果数量和评分
        total_rating = sum(d.get("rating", 0) for d in destinations)
        avg_rating = total_rating / len(destinations)
        
        # 归一化到 0-1
        quality = min(avg_rating / 5.0, 1.0)
        return round(quality, 2)


__all__ = ["SearchSkill"]
