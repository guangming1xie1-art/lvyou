"""推荐 Agent

基于搜索结果和用户偏好，生成定制化的旅行方案推荐。
使用 LLM 进行推理和方案生成。
支持多模型分层调用
"""
from typing import Any, Dict, List, Optional, Callable, Awaitable
from src.utils.logger import app_logger
from src.agents.error_handler import AgentErrorHandler
from .base import BaseAgent


class RecommendationAgent(BaseAgent):
    name = "recommendation_agent"

    async def ainvoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return await self.run(state)
    
    def __init__(self, llm: Optional[Any] = None):
        """初始化 Agent
        
        Args:
            llm: 可选的 LLM 实例，如果不提供则使用默认配置
        """
        self.llm = llm

    async def run(
        self, 
        state: Dict[str, Any], 
        on_progress: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        app_logger.info(f"Starting agent {self.name}")

        if on_progress:
            await on_progress({"status": "starting", "progress": 0.1, "message": "正在启动推荐代理..."})

        intent = state.get("intent") or {}
        collected_info = state.get("collected_info") or {}
        if isinstance(intent, dict):
            # Prefer explicit collected_info, but fall back to intent
            collected_info = {**intent, **collected_info}

        search_results = state.get("search_results") or []

        try:
            if on_progress:
                await on_progress({"status": "thinking", "progress": 0.4, "message": "正在根据您的需求生成旅行方案..."})

            recommendations = await self._generate_recommendations(
                collected_info, search_results
            )
            
            if on_progress:
                await on_progress({
                    "status": "partial_results", 
                    "progress": 0.8, 
                    "message": "已生成初步推荐方案",
                    "data": {"recommendations": recommendations}
                })

            state["recommendations"] = recommendations
            
            if on_progress:
                await on_progress({"status": "completed", "progress": 1.0, "message": "推荐方案生成完成"})

            app_logger.info(f"Agent {self.name} completed successfully", rec_count=len(recommendations))
            return state
        except Exception as e:
            error_res = AgentErrorHandler.handle_agent_error(self.name, e, state=state)
            state.update(error_res)
            return state

    async def _generate_recommendations(
        self,
        collected_info: Dict[str, Any],
        search_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        # 如果没有 LLM，使用 mock 数据
        if self.llm is None:
            app_logger.warning("No LLM provided, using mock recommendations")
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
            response = await self.llm.ainvoke(prompt)
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
