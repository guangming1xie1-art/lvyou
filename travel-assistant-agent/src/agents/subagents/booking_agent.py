"""
预订智能体
专门处理旅游预订相关任务，包括航班、酒店、门票预订
"""
from typing import Dict, List, Any, Optional
import logging
import hashlib

from .base import BaseAgent

logger = logging.getLogger(__name__)


class BookingAgent(BaseAgent):
    """预订智能体"""

    def __init__(self, llm: Optional[Any] = None):
        """
        初始化预订智能体

        Args:
            llm: LLM 实例，如果为 None 则使用默认模型
        """
        tools = []
        super().__init__(
            name="BookingAgent",
            description="旅游预订专家，擅长航班、酒店、门票预订服务",
            tools=tools
        )
        self.llm = llm
        self._bookings_cache = {}  # 简单的预订缓存

    async def execute(self, input_data: Dict) -> Dict:
        """
        执行预订任务

        Args:
            input_data: 包含预订详情的字典

        Returns:
            预订结果
        """
        try:
            booking_details = input_data.get("booking_details", {})
            recommendations = input_data.get("recommendations", {})

            logger.info(f"BookingAgent: Processing booking for {booking_details.get('destination', 'unknown')}")

            # 执行预订
            booking_result = await self._process_booking(
                booking_details,
                recommendations
            )

            self._track_tokens(
                self._estimate_tokens(
                    str(booking_details),
                    len(str(booking_result))
                )
            )

            return {
                "booking_result": booking_result,
                "token_usage": self.token_usage,
                "status": "success" if booking_result.get("confirmed") else "failed"
            }

        except Exception as e:
            logger.error(f"BookingAgent execution failed: {str(e)}")
            return {
                "booking_result": None,
                "token_usage": self.token_usage,
                "error": str(e),
                "status": "failed"
            }

    async def stream(self, input_data: Dict):
        """流式执行预订"""
        try:
            booking_details = input_data.get("booking_details", {})
            recommendations = input_data.get("recommendations", {})

            destination = booking_details.get("destination", "未知目的地")

            yield {
                "type": "progress",
                "message": f"正在为您预订 {destination} 的旅游服务...",
                "stage": "started"
            }

            # 预订航班
            yield {"type": "progress", "message": "预订航班...", "stage": "booking_flight"}
            flight_booking = await self._book_flight(booking_details)
            yield {"type": "result", "category": "flight", "data": flight_booking}

            # 预订酒店
            yield {"type": "progress", "message": "预订酒店...", "stage": "booking_hotel"}
            hotel_booking = await self._book_hotel(booking_details)
            yield {"type": "result", "category": "hotel", "data": hotel_booking}

            # 生成确认信息
            yield {"type": "progress", "message": "生成预订确认...", "stage": "confirming"}
            confirmation = await self._generate_confirmation(
                booking_details,
                {"flight": flight_booking, "hotel": hotel_booking}
            )
            yield {"type": "result", "category": "confirmation", "data": confirmation}

            yield {
                "type": "completed",
                "message": "预订成功！",
                "status": "success",
                "confirmation": confirmation
            }

        except Exception as e:
            logger.error(f"BookingAgent stream failed: {str(e)}")
            yield {
                "type": "error",
                "message": f"预订失败: {str(e)}",
                "status": "failed"
            }

    async def _process_booking(
        self,
        booking_details: Dict,
        recommendations: Dict
    ) -> Dict[str, Any]:
        """处理完整的预订流程"""
        # 并行执行各项预订
        import asyncio

        results = await asyncio.gather(
            self._book_flight(booking_details),
            self._book_hotel(booking_details),
            return_exceptions=True
        )

        flight_booking = results[0] if not isinstance(results[0], Exception) else None
        hotel_booking = results[1] if not isinstance(results[1], Exception) else None

        # 生成确认信息
        confirmation = await self._generate_confirmation(
            booking_details,
            {
                "flight": flight_booking,
                "hotel": hotel_booking
            }
        )

        return {
            "confirmed": all([flight_booking, hotel_booking]),
            "flight_booking": flight_booking,
            "hotel_booking": hotel_booking,
            "confirmation": confirmation,
            "total_price": self._calculate_total_price(flight_booking, hotel_booking),
            "destination": booking_details.get("destination", "")
        }

    async def _book_flight(self, booking_details: Dict) -> Optional[Dict]:
        """预订航班"""
        try:
            destination = booking_details.get("destination", "")
            travel_date = booking_details.get("travel_date", "")

            # 简化版：返回模拟预订结果
            booking_id = self._generate_booking_id("FL")

            logger.info(f"Booked flight {booking_id} to {destination}")

            return {
                "booking_id": booking_id,
                "type": "flight",
                "airline": "中国航空",
                "flight_number": "CA1234",
                "destination": destination,
                "departure_date": travel_date or "待定",
                "passengers": booking_details.get("passengers", 1),
                "price": 1200.0,
                "currency": "CNY",
                "status": "confirmed",
                "booking_date": self._get_current_date()
            }

        except Exception as e:
            logger.error(f"Flight booking failed: {str(e)}")
            return None

    async def _book_hotel(self, booking_details: Dict) -> Optional[Dict]:
        """预订酒店"""
        try:
            destination = booking_details.get("destination", "")
            check_in_date = booking_details.get("travel_date", "")

            # 简化版：返回模拟预订结果
            booking_id = self._generate_booking_id("HT")

            logger.info(f"Booked hotel {booking_id} in {destination}")

            return {
                "booking_id": booking_id,
                "type": "hotel",
                "hotel_name": "豪华酒店",
                "destination": destination,
                "check_in_date": check_in_date or "待定",
                "check_out_date": "待定",
                "nights": booking_details.get("duration_days", 5),
                "rooms": 1,
                "price_per_night": 600.0,
                "total_price": 600.0 * booking_details.get("duration_days", 5),
                "currency": "CNY",
                "status": "confirmed",
                "booking_date": self._get_current_date()
            }

        except Exception as e:
            logger.error(f"Hotel booking failed: {str(e)}")
            return None

    async def _generate_confirmation(
        self,
        booking_details: Dict,
        bookings: Dict
    ) -> Dict:
        """生成预订确认信息"""
        confirmation_id = self._generate_booking_id("CONF")

        return {
            "confirmation_id": confirmation_id,
            "confirmation_code": f"CONF{hash(str(bookings)) % 100000:05d}",
            "destination": booking_details.get("destination", ""),
            "bookings": bookings,
            "booking_date": self._get_current_date(),
            "status": "confirmed"
        }

    def _calculate_total_price(
        self,
        flight_booking: Optional[Dict],
        hotel_booking: Optional[Dict]
    ) -> float:
        """计算总价格"""
        total = 0.0

        if flight_booking:
            total += flight_booking.get("price", 0)

        if hotel_booking:
            total += hotel_booking.get("total_price", 0)

        return total

    def _generate_booking_id(self, prefix: str) -> str:
        """生成预订ID"""
        import random
        timestamp = int(self._get_current_timestamp())
        random_num = random.randint(1000, 9999)
        return f"{prefix}{timestamp}{random_num}"

    def _get_current_date(self) -> str:
        """获取当前日期字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")

    def _get_current_timestamp(self) -> int:
        """获取当前时间戳"""
        from datetime import datetime
        return int(datetime.now().timestamp())

    def _estimate_tokens(self, input_text: str, output_length: int) -> int:
        """估算 token 使用量"""
        input_tokens = len(input_text) // 4
        output_tokens = output_length // 4
        return input_tokens + output_tokens
