"""
预订节点 - 处理预订相关的任务
"""
from typing import Dict, Any
from ..state import ConversationState
import logging

logger = logging.getLogger(__name__)


async def plan_booking(state: ConversationState) -> ConversationState:
    """预订规划节点"""

    try:
        user_requirements = state.get("user_requirements", {})
        recommendations = state.get("recommendations", [])

        # 生成预订详情
        booking_details = {
            "destination": user_requirements.get("destination", "未知目的地"),
            "travel_date": user_requirements.get("start_date", "待定"),
            "passengers": 1,
            "selected_package": recommendations[0] if recommendations else None
        }

        logger.info(f"Booking planning: Generated details")

        return {
            **state,
            "booking_details": booking_details,
            "stage": "booking_planning"
        }

    except Exception as e:
        logger.error(f"Booking planning failed: {str(e)}")
        return {
            **state,
            "error_message": f"预订规划失败: {str(e)}",
            "workflow_status": "failed"
        }


async def execute_booking(state: ConversationState) -> ConversationState:
    """预订执行节点"""

    try:
        booking_details = state.get("booking_details", {})

        # 简化版：模拟预订结果
        # 实际实现应该调用真实的预订服务
        booking_result = {
            "booking_id": f"BK{hash(str(booking_details)) % 1000000:06d}",
            "status": "confirmed",
            "destination": booking_details.get("destination", ""),
            "travel_date": booking_details.get("travel_date", ""),
            "total_price": 2000.0,
            "currency": "CNY",
            "confirmation_code": "ABC123"
        }

        logger.info(f"Booking execution: Booking confirmed with ID {booking_result['booking_id']}")

        return {
            **state,
            "booking_confirmed": True,
            "booking_result": booking_result,
            "stage": "booking_completed"
        }

    except Exception as e:
        logger.error(f"Booking execution failed: {str(e)}")
        return {
            **state,
            "error_message": f"预订执行失败: {str(e)}",
            "workflow_status": "failed",
            "booking_confirmed": False
        }
