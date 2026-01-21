"""预订 Agent

负责将推荐方案转化为可执行的预订请求（酒店、机票、门票等）。
MVP 阶段先保留骨架接口。
"""
from typing import Any, Dict, Optional, Callable, Awaitable
from ..utils.logger import app_logger
from .error_handler import AgentErrorHandler
from .base import BaseAgent

class BookingAgent(BaseAgent):
    name = "booking_agent"

    async def ainvoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return await self.run(state)

    async def run(
        self, 
        state: Dict[str, Any], 
        on_progress: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        app_logger.info(f"Starting agent {self.name}")

        if on_progress:
            await on_progress({"status": "starting", "progress": 0.1, "message": "正在启动预订代理..."})

        recommendations = state.get("recommendations", [])

        try:
            if on_progress:
                await on_progress({"status": "booking", "progress": 0.5, "message": "正在处理您的预订请求..."})
                
            booking_status = await self._book(recommendations)
            state["booking_status"] = booking_status
            state["final_plan"] = {
                "recommendations": recommendations,
                "booking": booking_status
            }
            
            if on_progress:
                await on_progress({"status": "completed", "progress": 1.0, "message": "预订处理完成"})

            app_logger.info(f"Agent {self.name} completed successfully", status=booking_status.get("status"))
            return state
        except Exception as e:
            error_res = AgentErrorHandler.handle_agent_error(self.name, e, state=state)
            state.update(error_res)
            return state

    async def _book(self, recommendations):
        if not recommendations:
            return {"status": "no_recommendations", "message": "No recommendations to book"}

        # TODO: 集成实际预订 API / MCP 工具
        return {
            "status": "pending",
            "message": "Booking workflow not implemented yet",
            "selected_itinerary": recommendations[0].get("itinerary_id")
        }
