"""
Recommend Skill Implementation
基于用户偏好和搜索结果生成个性化推荐
"""
from typing import Dict, Any, List, Optional
import logging
from ...skills.base import Skill
from ....agents.mcp_client import get_mcp_client

logger = logging.getLogger(__name__)


class RecommendSkill(Skill):
    """推荐技能 - 生成个性化旅游推荐方案"""
    
    def __init__(self):
        super().__init__(
            name="recommend",
            description="基于用户偏好和搜索结果生成个性化旅游推荐方案",
            version="1.0.0",
            enabled=True,
            cost_estimate=0.08,
            category="recommendation"
        )
        self.mcp_client = None
    
    def get_required_fields(self) -> list:
        """必需字段"""
        return ["user_prefs"]
    
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
        执行推荐
        
        Args:
            input_data: {
                "user_prefs": {...},
                "search_results": [...],
                "num_recommendations": int
            }
        
        Returns:
            {
                "recommendations": [...],
                "confidence": float
            }
        """
        user_prefs = input_data.get("user_prefs", {})
        search_results = input_data.get("search_results", [])
        num_recommendations = input_data.get("num_recommendations", 3)
        
        if not user_prefs:
            return {
                "recommendations": [],
                "confidence": 0.0,
                "error": "user_prefs is required"
            }
        
        # 确保 MCP Client 连接
        await self._ensure_mcp_client()
        
        # 调用 Java API 的 get_recommendations
        try:
            result = await self.mcp_client.call_tool(
                tool_name="get_recommendations",
                parameters={
                    "user_preferences": user_prefs,
                    "search_results": search_results
                }
            )
            
            if result.get("error"):
                logger.warning(f"Java API error: {result['error']}")
            
            # 提取结果
            api_result = result.get("result", {})
            recommendations = api_result.get("recommendations", [])
            
            # 限制推荐数量
            recommendations = recommendations[:num_recommendations]
            
            # 计算总体置信度
            confidence = self._calculate_confidence(recommendations)
            
            return {
                "recommendations": recommendations,
                "confidence": confidence,
                "metadata": {
                    "execution_time_ms": 800,
                    "model_used": "qwen-turbo",
                    "factors_considered": ["budget", "preferences", "season"],
                    "mock": api_result.get("mock", False)
                }
            }
        
        except Exception as e:
            logger.error(f"Error executing recommend: {e}")
            return {
                "recommendations": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _calculate_confidence(self, recommendations: List[Dict[str, Any]]) -> float:
        """计算推荐置信度"""
        if not recommendations:
            return 0.0
        
        # 基于每个推荐的 confidence 计算平均值
        total_confidence = sum(r.get("confidence", 0.5) for r in recommendations)
        avg_confidence = total_confidence / len(recommendations)
        
        return round(avg_confidence, 2)


__all__ = ["RecommendSkill"]
