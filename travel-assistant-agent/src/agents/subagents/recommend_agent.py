"""
推荐智能体
专门处理旅游推荐相关任务，包括行程规划、预算建议等
"""
from typing import Dict, List, Any, Optional
import logging

from .base import BaseAgent

logger = logging.getLogger(__name__)


class RecommendationAgent(BaseAgent):
    """推荐智能体"""

    def __init__(self, llm: Optional[Any] = None):
        """
        初始化推荐智能体

        Args:
            llm: LLM 实例，如果为 None 则使用默认模型
        """
        tools = []
        super().__init__(
            name="RecommendationAgent",
            description="旅游推荐专家，擅长个性化行程规划和预算建议",
            tools=tools
        )
        self.llm = llm

    async def execute(self, input_data: Dict) -> Dict:
        """
        执行推荐任务

        Args:
            input_data: 包含用户需求、搜索结果等的字典

        Returns:
            推荐结果
        """
        try:
            requirements = input_data.get("user_requirements", {})
            search_results = input_data.get("search_results", {})

            logger.info("RecommendationAgent: Generating recommendations")

            # 生成个性化推荐
            recommendations = await self._generate_recommendations(
                requirements,
                search_results
            )

            self._track_tokens(
                self._estimate_tokens(
                    str(requirements),
                    len(str(recommendations))
                )
            )

            return {
                "recommendations": recommendations,
                "token_usage": self.token_usage,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"RecommendationAgent execution failed: {str(e)}")
            return {
                "recommendations": [],
                "token_usage": self.token_usage,
                "error": str(e),
                "status": "failed"
            }

    async def stream(self, input_data: Dict):
        """流式执行推荐"""
        try:
            requirements = input_data.get("user_requirements", {})
            search_results = input_data.get("search_results", {})

            yield {
                "type": "progress",
                "message": "正在分析您的需求...",
                "stage": "analyzing"
            }

            # 生成行程推荐
            yield {"type": "progress", "message": "规划行程安排...", "stage": "planning_itinerary"}
            itinerary = await self._generate_itinerary(requirements, search_results)
            yield {"type": "result", "category": "itinerary", "data": itinerary}

            # 生成预算建议
            yield {"type": "progress", "message": "制定预算方案...", "stage": "planning_budget"}
            budget = await self._generate_budget(requirements, search_results)
            yield {"type": "result", "category": "budget", "data": budget}

            # 生成景点推荐
            yield {"type": "progress", "message": "推荐特色体验...", "stage": "recommending_experiences"}
            experiences = await self._generate_experiences(requirements, search_results)
            yield {"type": "result", "category": "experiences", "data": experiences}

            yield {
                "type": "completed",
                "message": "推荐完成！",
                "status": "success"
            }

        except Exception as e:
            logger.error(f"RecommendationAgent stream failed: {str(e)}")
            yield {
                "type": "error",
                "message": f"推荐失败: {str(e)}",
                "status": "failed"
            }

    async def _generate_recommendations(
        self,
        requirements: Dict,
        search_results: Dict
    ) -> Dict[str, Any]:
        """生成综合推荐"""
        itinerary = await self._generate_itinerary(requirements, search_results)
        budget = await self._generate_budget(requirements, search_results)
        experiences = await self._generate_experiences(requirements, search_results)

        return {
            "itinerary": itinerary,
            "budget": budget,
            "experiences": experiences,
            "summary": self._generate_summary(requirements, itinerary)
        }

    async def _generate_itinerary(
        self,
        requirements: Dict,
        search_results: Dict
    ) -> Dict:
        """生成行程规划"""
        destination = requirements.get("destination", "未知目的地")
        duration_days = requirements.get("duration_days", 5)

        # 简化版：生成每日行程
        daily_plans = []
        attractions = search_results.get("attractions", [])

        for day in range(1, duration_days + 1):
            daily_plan = {
                "day": day,
                "theme": f"探索{destination}",
                "activities": [
                    {
                        "time": "09:00-11:30",
                        "activity": attractions[day % len(attractions)].get("name", "景点游览") if attractions else "自由活动",
                        "type": "sightseeing"
                    },
                    {
                        "time": "12:00-13:30",
                        "activity": "午餐休息",
                        "type": "dining"
                    },
                    {
                        "time": "14:00-17:00",
                        "activity": attractions[(day + 1) % len(attractions)].get("name", "景点游览") if attractions else "自由活动",
                        "type": "sightseeing"
                    },
                    {
                        "time": "18:00-20:00",
                        "activity": "晚餐体验当地美食",
                        "type": "dining"
                    }
                ]
            }
            daily_plans.append(daily_plan)

        return {
            "destination": destination,
            "duration_days": duration_days,
            "daily_plans": daily_plans,
            "total_activities": len(daily_plans) * 4
        }

    async def _generate_budget(
        self,
        requirements: Dict,
        search_results: Dict
    ) -> Dict:
        """生成预算建议"""
        user_budget = requirements.get("budget", 0)
        duration_days = requirements.get("duration_days", 5)

        hotels = search_results.get("hotels", [])
        flights = search_results.get("flights", [])

        # 计算各项费用
        avg_hotel_price = sum(h.get("price_per_night", 0) for h in hotels) / len(hotels) if hotels else 400
        avg_flight_price = sum(f.get("price", 0) for f in flights) / len(flights) if flights else 1000

        accommodation_total = avg_hotel_price * duration_days
        transportation_total = avg_flight_price * 2  # 往返
        food_total = 200 * duration_days  # 每天餐饮
        activities_total = 100 * duration_days  # 每天活动

        total_budget = accommodation_total + transportation_total + food_total + activities_total

        # 如果用户提供了预算，进行调整
        if user_budget > 0:
            ratio = user_budget / total_budget
            accommodation_total *= ratio
            transportation_total *= ratio
            food_total *= ratio
            activities_total *= ratio
            total_budget = user_budget

        budget_breakdown = {
            "accommodation": {
                "amount": accommodation_total,
                "percentage": (accommodation_total / total_budget * 100) if total_budget > 0 else 0,
                "description": "住宿费用"
            },
            "transportation": {
                "amount": transportation_total,
                "percentage": (transportation_total / total_budget * 100) if total_budget > 0 else 0,
                "description": "交通费用（往返机票）"
            },
            "food": {
                "amount": food_total,
                "percentage": (food_total / total_budget * 100) if total_budget > 0 else 0,
                "description": "餐饮费用"
            },
            "activities": {
                "amount": activities_total,
                "percentage": (activities_total / total_budget * 100) if total_budget > 0 else 0,
                "description": "活动门票"
            }
        }

        return {
            "total_budget": total_budget,
            "user_budget": user_budget if user_budget > 0 else "未指定",
            "budget_breakdown": budget_breakdown,
            "currency": "CNY",
            "duration_days": duration_days
        }

    async def _generate_experiences(
        self,
        requirements: Dict,
        search_results: Dict
    ) -> List[Dict]:
        """生成特色体验推荐"""
        destination = requirements.get("destination", "未知目的地")

        experiences = [
            {
                "category": "美食体验",
                "title": f"{destination}特色美食之旅",
                "description": "品尝当地最正宗的特色菜肴",
                "estimated_duration": "3-4小时",
                "price_range": "100-300元/人"
            },
            {
                "category": "文化体验",
                "title": f"{destination}历史文化探索",
                "description": "深入了解当地的历史文化底蕴",
                "estimated_duration": "4-6小时",
                "price_range": "50-150元/人"
            },
            {
                "category": "自然体验",
                "title": f"{destination}自然风光巡游",
                "description": "欣赏壮丽的自然景观",
                "estimated_duration": "全天",
                "price_range": "200-500元/人"
            }
        ]

        return experiences

    def _generate_summary(self, requirements: Dict, itinerary: Dict) -> str:
        """生成推荐摘要"""
        destination = requirements.get("destination", "未知目的地")
        duration_days = itinerary.get("duration_days", 5)
        total_activities = itinerary.get("total_activities", 20)

        return f"""为您的{destination}之旅，我为您规划了{duration_days}天的精彩行程，共包含{total_activities}个活动。
行程涵盖了观光、美食、文化等多种体验，让您全方位感受{destination}的魅力。"""

    def _estimate_tokens(self, input_text: str, output_length: int) -> int:
        """估算 token 使用量"""
        input_tokens = len(input_text) // 4
        output_tokens = output_length // 4
        return input_tokens + output_tokens
