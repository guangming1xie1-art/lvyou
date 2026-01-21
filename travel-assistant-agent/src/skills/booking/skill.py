"""
Booking Skill Implementation
创建和管理旅游预订
"""
from typing import Dict, Any, Optional
import logging
from skills.base import Skill
from agents.mcp_client import get_mcp_client

logger = logging.getLogger(__name__)


class BookingSkill(Skill):
    """预订技能 - 创建和管理旅游预订"""
    
    def __init__(self):
        super().__init__(
            name="booking",
            description="创建旅游预订、获取预订状态",
            version="1.0.0",
            enabled=True,
            cost_estimate=0.03,
            category="booking"
        )
        self.mcp_client = None
    
    def get_required_fields(self) -> list:
        """必需字段（创建预订或查询状态二选一）"""
        return []  # 动态检查
    
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
        执行预订操作
        
        Args:
            input_data: {
                "booking_details": {...}  # 创建预订
                或
                "booking_id": "..."       # 查询状态
            }
        
        Returns:
            预订详情或状态
        """
        booking_details = input_data.get("booking_details")
        booking_id = input_data.get("booking_id")
        
        # 确保 MCP Client 连接
        await self._ensure_mcp_client()
        
        # 创建预订
        if booking_details:
            return await self._create_booking(booking_details)
        
        # 查询状态
        elif booking_id:
            return await self._get_booking_status(booking_id)
        
        else:
            return {
                "error": "Either booking_details or booking_id is required"
            }
    
    async def _create_booking(self, booking_details: Dict[str, Any]) -> Dict[str, Any]:
        """创建预订"""
        try:
            result = await self.mcp_client.call_tool(
                tool_name="create_booking",
                parameters={
                    "booking_details": booking_details
                }
            )
            
            if result.get("error"):
                logger.warning(f"Java API error: {result['error']}")
            
            # 提取结果
            api_result = result.get("result", {})
            
            return {
                "booking_id": api_result.get("booking_id", "UNKNOWN"),
                "status": api_result.get("status", "pending"),
                "details": booking_details,
                "metadata": {
                    "mock": api_result.get("mock", False)
                }
            }
        
        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            return {
                "error": str(e)
            }
    
    async def _get_booking_status(self, booking_id: str) -> Dict[str, Any]:
        """查询预订状态"""
        try:
            result = await self.mcp_client.call_tool(
                tool_name="get_booking_status",
                parameters={
                    "booking_id": booking_id
                }
            )
            
            if result.get("error"):
                logger.warning(f"Java API error: {result['error']}")
            
            # 提取结果
            api_result = result.get("result", {})
            
            return {
                "booking_id": booking_id,
                "status": api_result.get("status", "unknown"),
                "metadata": {
                    "mock": api_result.get("mock", False)
                }
            }
        
        except Exception as e:
            logger.error(f"Error getting booking status: {e}")
            return {
                "booking_id": booking_id,
                "status": "error",
                "error": str(e)
            }


__all__ = ["BookingSkill"]
