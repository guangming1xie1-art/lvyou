"""搜索 Agent

负责查询目的地信息、景点、酒店、交通等。
MVP 阶段仅提供骨架，后续接入 MCP 工具/后端服务。
"""
from typing import Any, Dict, List

from utils.logger import app_logger

from .base import BaseAgent


class SearchAgent(BaseAgent):
    name = "search_agent"

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        app_logger.info(f"[{self.name}] Starting search")

        collected_info = state.get("collected_info", {})
        destination = collected_info.get("destination")

        try:
            search_results = await self._search(destination)
            state["search_results"] = search_results
            app_logger.info(f"[{self.name}] Search results count: {len(search_results)}")
        except Exception as e:
            app_logger.error(f"[{self.name}] Error: {e}")
            state["error"] = str(e)

        return state

    async def _search(self, destination: str) -> List[Dict[str, Any]]:
        if not destination or destination == "未指定":
            app_logger.warning("Destination not specified, returning empty results")
            return []

        try:
            # TODO: 根据后端 API 设计调整
            # 这里先做占位逻辑
            return [
                {"type": "attraction", "name": f"{destination} 景点 A", "score": 4.5},
                {"type": "hotel", "name": f"{destination} 酒店 B", "score": 4.2},
            ]
        except Exception as e:
            app_logger.error(f"Search failed: {e}")
            raise
