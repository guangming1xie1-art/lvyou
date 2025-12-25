"""预订 Agent

负责将推荐方案转化为可执行的预订请求（酒店、机票、门票等）。
MVP 阶段先保留骨架接口。
"""
from typing import Any, Dict
from utils.logger import app_logger
from .base import BaseAgent


class BookingAgent(BaseAgent):
    name = "booking_agent"

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        app_logger.info(f"[{self.name}] Starting booking process")

        recommendations = state.get("recommendations", [])

        try:
            booking_status = await self._book(recommendations)
            state["booking_status"] = booking_status
            state["final_plan"] = {
                "recommendations": recommendations,
                "booking": booking_status
            }
            app_logger.info(f"[{self.name}] Booking status: {booking_status}")
        except Exception as e:
            app_logger.error(f"[{self.name}] Error: {e}")
            state["error"] = str(e)

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
