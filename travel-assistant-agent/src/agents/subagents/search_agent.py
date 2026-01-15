"""
搜索智能体
专门处理旅游搜索相关任务，包括航班、酒店、景点搜索
"""
from typing import Dict, List, Any, Optional
import logging
import json

from .base import BaseAgent

logger = logging.getLogger(__name__)


class SearchAgent(BaseAgent):
    """搜索智能体"""

    def __init__(self, llm: Optional[Any] = None):
        """
        初始化搜索智能体

        Args:
            llm: LLM 实例，如果为 None 则使用默认模型
        """
        tools = []
        super().__init__(
            name="SearchAgent",
            description="旅游搜索专家，擅长搜索航班、酒店和景点信息",
            tools=tools
        )
        self.llm = llm

    async def execute(self, input_data: Dict) -> Dict:
        """
        执行搜索任务

        Args:
            input_data: 包含用户需求和搜索参数的字典

        Returns:
            搜索结果
        """
        try:
            requirements = input_data.get("user_requirements", {})
            user_message = input_data.get("user_message", "")
            destination = requirements.get("destination", "未知目的地")

            logger.info(f"SearchAgent: Searching for {destination}")

            # 并行执行多种搜索
            results = await self._execute_parallel_search(
                destination,
                requirements
            )

            self._track_tokens(
                self._estimate_tokens(
                    user_message,
                    len(str(results))
                )
            )

            return {
                "search_results": results,
                "token_usage": self.token_usage,
                "destination": destination,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"SearchAgent execution failed: {str(e)}")
            return {
                "search_results": {},
                "token_usage": self.token_usage,
                "error": str(e),
                "status": "failed"
            }

    async def stream(self, input_data: Dict):
        """流式执行搜索"""
        try:
            requirements = input_data.get("user_requirements", {})
            destination = requirements.get("destination", "未知目的地")

            yield {
                "type": "progress",
                "message": f"正在搜索 {destination} 的旅游信息...",
                "stage": "started"
            }

            # 搜索航班
            yield {"type": "progress", "message": "搜索航班信息...", "stage": "searching_flights"}
            flights = await self._search_flights(destination)
            yield {"type": "result", "category": "flights", "data": flights}

            # 搜索酒店
            yield {"type": "progress", "message": "搜索酒店信息...", "stage": "searching_hotels"}
            hotels = await self._search_hotels(destination)
            yield {"type": "result", "category": "hotels", "data": hotels}

            # 搜索景点
            yield {"type": "progress", "message": "搜索景点信息...", "stage": "searching_attractions"}
            attractions = await self._search_attractions(destination)
            yield {"type": "result", "category": "attractions", "data": attractions}

            yield {
                "type": "completed",
                "message": "搜索完成！",
                "status": "success"
            }

        except Exception as e:
            logger.error(f"SearchAgent stream failed: {str(e)}")
            yield {
                "type": "error",
                "message": f"搜索失败: {str(e)}",
                "status": "failed"
            }

    async def _execute_parallel_search(
        self,
        destination: str,
        requirements: Dict
    ) -> Dict[str, List[Dict]]:
        """并行执行所有搜索"""
        import asyncio

        results = await asyncio.gather(
            self._search_flights(destination),
            self._search_hotels(destination),
            self._search_attractions(destination),
            return_exceptions=True
        )

        return {
            "flights": results[0] if not isinstance(results[0], Exception) else [],
            "hotels": results[1] if not isinstance(results[1], Exception) else [],
            "attractions": results[2] if not isinstance(results[2], Exception) else []
        }

    async def _search_flights(self, destination: str) -> List[Dict]:
        """搜索航班"""
        logger.info(f"Searching flights to {destination}")

        # 简化版：返回模拟数据
        # 实际实现应该调用真实的航班搜索 API
        return [
            {
                "id": "FL001",
                "airline": "中国航空",
                "departure_time": "08:00",
                "arrival_time": "10:30",
                "price": 1200,
                "currency": "CNY",
                "stops": 0,
                "duration": "2h 30m"
            },
            {
                "id": "FL002",
                "airline": "东方航空",
                "departure_time": "14:00",
                "arrival_time": "16:45",
                "price": 980,
                "currency": "CNY",
                "stops": 0,
                "duration": "2h 45m"
            }
        ]

    async def _search_hotels(self, destination: str) -> List[Dict]:
        """搜索酒店"""
        logger.info(f"Searching hotels in {destination}")

        # 简化版：返回模拟数据
        return [
            {
                "id": "HT001",
                "name": "豪华酒店",
                "rating": 5,
                "price_per_night": 600,
                "currency": "CNY",
                "amenities": ["WiFi", "健身房", "游泳池", "餐厅"],
                "location": "市中心"
            },
            {
                "id": "HT002",
                "name": "舒适酒店",
                "rating": 4,
                "price_per_night": 350,
                "currency": "CNY",
                "amenities": ["WiFi", "早餐", "停车场"],
                "location": "交通便利"
            }
        ]

    async def _search_attractions(self, destination: str) -> List[Dict]:
        """搜索景点"""
        logger.info(f"Searching attractions in {destination}")

        # 简化版：返回模拟数据
        return [
            {
                "id": "AT001",
                "name": "著名景点 A",
                "category": "自然景观",
                "rating": 4.8,
                "ticket_price": 100,
                "currency": "CNY",
                "description": "绝佳的自然风光，值得一看"
            },
            {
                "id": "AT002",
                "name": "历史古迹 B",
                "category": "历史文化",
                "rating": 4.6,
                "ticket_price": 50,
                "currency": "CNY",
                "description": "深厚的历史文化底蕴"
            }
        ]

    def _estimate_tokens(self, input_text: str, output_length: int) -> int:
        """估算 token 使用量"""
        # 简单估算：4 个字符约等于 1 个 token
        input_tokens = len(input_text) // 4
        output_tokens = output_length // 4
        return input_tokens + output_tokens
