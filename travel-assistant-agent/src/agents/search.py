"""搜索 Agent

负责查询目的地信息、景点、酒店、交通等。
MVP 阶段仅提供骨架，后续接入 MCP 工具/后端服务。
"""
from typing import Any, Dict, List, Optional, Callable, Awaitable

from utils.logger import app_logger
from agents.error_handler import AgentErrorHandler
from .base import BaseAgent

class SearchAgent(BaseAgent):
    name = "search_agent"

    async def ainvoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return await self.run(state)

    async def run(
        self, 
        state: Dict[str, Any], 
        on_progress: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        app_logger.info(f"Starting agent {self.name}")

        if on_progress:
            await on_progress({"status": "starting", "progress": 0.1, "message": "正在启动搜索代理..."})

        intent = state.get("intent") or {}
        collected_info = state.get("collected_info") or {}

        # ConversationAgent may pass intent directly; keep backward compatibility
        destination = (
            (intent.get("destination") if isinstance(intent, dict) else None)
            or collected_info.get("destination")
            or state.get("destination")
        )

        # Normalize collected_info so downstream agents can rely on it
        if destination and (not collected_info.get("destination")):
            collected_info["destination"] = destination
            state["collected_info"] = collected_info

        try:
            if on_progress:
                await on_progress({"status": "searching", "progress": 0.3, "message": f"正在搜索 {destination} 的相关信息..."})
            
            search_results = await self._search(destination)
            
            if on_progress:
                await on_progress({
                    "status": "partial_results", 
                    "progress": 0.7, 
                    "message": "已获取部分搜索结果",
                    "data": {"flights": search_results} # 模拟中间数据
                })

            state["search_results"] = search_results
            
            if on_progress:
                await on_progress({"status": "completed", "progress": 1.0, "message": "搜索完成"})

            app_logger.info(f"Agent {self.name} completed successfully", results_count=len(search_results))
            return state
        except Exception as e:
            error_res = AgentErrorHandler.handle_agent_error(self.name, e, state=state)
            state.update(error_res)
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
