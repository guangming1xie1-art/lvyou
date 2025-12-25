"""推荐 Agent

基于搜索结果和用户偏好，生成定制化的旅行方案推荐。
使用 LLM 进行推理和方案生成。
"""
from typing import Any, Dict, List
from utils.logger import app_logger
from utils.claude import claude_client
from .base import BaseAgent


class RecommendationAgent(BaseAgent):
    name = "recommendation_agent"

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        app_logger.info(f"[{self.name}] Starting recommendation generation")

        collected_info = state.get("collected_info", {})
        search_results = state.get("search_results", [])

        try:
            recommendations = await self._generate_recommendations(
                collected_info, search_results
            )
            state["recommendations"] = recommendations
            app_logger.info(f"[{self.name}] Generated {len(recommendations)} recommendations")
        except Exception as e:
            app_logger.error(f"[{self.name}] Error: {e}")
            state["error"] = str(e)

        return state

    async def _generate_recommendations(
        self,
        collected_info: Dict[str, Any],
        search_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        if not claude_client.is_ready():
            app_logger.warning("Claude client not ready, using mock recommendations")
            return [
                {
                    "itinerary_id": "mock_001",
                    "title": "3日文化美食之旅",
                    "days": 3,
                    "highlights": ["故宫", "天坛", "烤鸭"]
                }
            ]

        prompt = f"""
根据以下信息生成旅行推荐方案：

用户需求:
{collected_info}

搜索结果:
{search_results}

请生成 2-3 个旅行方案，每个方案包括：
- 行程标题
- 天数
- 主要亮点
- 预估费用

以 JSON 列表格式返回。
"""

        try:
            response = await claude_client.llm.ainvoke(prompt)
            # TODO: 解析 LLM 响应为结构化推荐
            return [
                {
                    "itinerary_id": "rec_001",
                    "title": f"{collected_info.get('destination')} 经典之旅",
                    "days": 3,
                    "highlights": ["景点 A", "景点 B"],
                    "estimated_cost": collected_info.get("budget", "未知")
                }
            ]
        except Exception as e:
            app_logger.error(f"Failed to generate recommendations: {e}")
            raise
