"""
Enhanced Recommend Skill Implementation with Pydantic Support
基于用户偏好和搜索结果生成个性化旅游推荐方案
"""
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from src.skills.base_enhanced import EnhancedSkill
from src.skills.recommend.models import (
    RecommendInput, RecommendOutput, RecommendationItem, 
    ItineraryDay, ActivityInfo, TotalCost, CostBreakdown
)
from src.agents.mcp_client import get_mcp_client

logger = logging.getLogger(__name__)


class RecommendSkill(EnhancedSkill):
    """推荐技能 - 基于 Pydantic 的个性化旅游推荐"""
    
    input_model = RecommendInput
    output_model = RecommendOutput
    
    def __init__(self):
        super().__init__(
            name="recommend",
            description="基于用户偏好和搜索结果生成个性化旅游推荐方案",
            version="1.0.0",
            enabled=True,
            cost_estimate=0.08,
            category="recommendation",
            cost_config={
                "base": 0.02,
                "per_recommendation": 0.02,
                "formula": "base + min(num_recommendations, 5) * per_recommendation",
                "max_cost": 0.15
            },
            dependencies=["info_collection", "search"]
        )
        self.mcp_client = None
    
    async def _ensure_mcp_client(self):
        """确保 MCP Client 已初始化"""
        if self.mcp_client is None:
            self.mcp_client = get_mcp_client()
            if self.mcp_client and not self.mcp_client.is_connected():
                try:
                    await self.mcp_client.connect()
                    logger.info("MCP client connected successfully")
                except Exception as e:
                    logger.warning(f"Failed to connect MCP client: {e}")
    
    async def execute(self, input_data: RecommendInput) -> RecommendOutput:
        """
        执行推荐生成 - 类型安全版本
        
        Args:
            input_data: 已验证的 RecommendInput 模型
            
        Returns:
            RecommendOutput 模型包含推荐方案
            
        Raises:
            ValueError: 如果输入数据不足以生成推荐
            RuntimeError: 如果推荐生成失败
        """
        user_prefs = input_data.user_prefs
        search_results = input_data.search_results or []
        num_recommendations = min(input_data.num_recommendations, 5)
        
        logger.info(
            f"Generating {num_recommendations} recommendations for " 
            f"destination={user_prefs.budget}, dates={user_prefs.dates}"
        )
        
        # Validate required data
        if not user_prefs.budget or not user_prefs.dates:
            raise ValueError("User preferences must include budget and dates")
        
        # Ensure MCP Client
        await self._ensure_mcp_client()
        
        try:
            # Generate recommendations based on user prefs and search results
            recommendations = await self._generate_recommendations(
                user_prefs, search_results, num_recommendations
            )
            
            return RecommendOutput(
                recommendations=recommendations,
                selected_recommendation_id=None
            )
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}", exc_info=True)
            # Fallback to mock recommendations
            return self._generate_mock_recommendations(user_prefs, search_results, num_recommendations)
    
    async def _generate_recommendations(
        self,
        user_prefs: Dict[str, Any],
        search_results: List[Dict],
        num_recommendations: int
    ) -> List[RecommendationItem]:
        """生成个性化推荐方案"""
        recommendations = []
        
        # Extract destinations from search results or use popular defaults
        if search_results and len(search_results) > 0:
            destinations = self._extract_destinations_from_results(search_results)
        else:
            # Use popular destinations based on user preferences
            destinations = self._get_default_destinations(user_prefs)
        
        # Generate recommendation for each destination
        for i, dest in enumerate(destinations[:num_recommendations]):
            try:
                rec = await self._create_recommendation_item(
                    dest, user_prefs, search_results, i + 1
                )
                if rec:
                    recommendations.append(rec)
            except Exception as e:
                logger.warning(f"Failed to create recommendation for {dest}: {e}")
                continue
        
        # If no recommendations generated, create mock ones
        if not recommendations:
            return self._generate_mock_recommendations(user_prefs, search_results, num_recommendations)
        
        return recommendations
    
    def _extract_destinations_from_results(self, search_results: List[Dict]) -> List[Dict]:
        """从搜索结果中提取目的地"""
        destinations = []
        
        for result in search_results:
            if isinstance(result, dict):
                # Extract destination type results
                if result.get("type") == "destination":
                    destinations.append(result)
                # Also include hotels as they contain location info
                elif result.get("type") == "hotel" and result.get("name"):
                    # Create a synthetic destination from hotel info
                    destinations.append({
                        "id": f"dest_from_hotel_{result.get('id', '')}",
                        "name": result.get("location", f"Hotel in {result.get('name')}"),
                        "type": "destination",
                        "description": f"Destination featuring {result.get('name')}",
                        "rating": result.get("rating", 4.0),
                        "price_range": result.get("price_range", {"min": 500, "max": 2000})
                    })
        
        return destinations
    
    def _get_default_destinations(self, user_prefs: Dict[str, Any]) -> List[Dict]:
        """根据用户偏好获取默认目的地"""
        prefs = user_prefs.preferences or []
        budget_max = user_prefs.budget.max if user_prefs.budget and user_prefs.budget.max else 10000
        
        # Popular destinations by preference
        destinations = [
            {
                "id": "tokyo_001",
                "name": "东京",
                "type": "destination",
                "description": "现代化大都市，融合传统与现代文化",
                "rating": 4.7,
                "price_range": {"min": 8000, "max": 15000}
            },
            {
                "id": "paris_001",
                "name": "巴黎",
                "type": "destination",
                "description": "浪漫之都，艺术与文化的中心",
                "rating": 4.8,
                "price_range": {"min": 10000, "max": 18000}
            },
            {
                "id": "bali_001",
                "name": "巴厘岛",
                "type": "destination",
                "description": "热带天堂，完美的度假胜地",
                "rating": 4.6,
                "price_range": {"min": 6000, "max": 12000}
            },
            {
                "id": "newyork_001",
                "name": "纽约",
                "type": "destination",
                "description": "世界金融中心，不夜城",
                "rating": 4.5,
                "price_range": {"min": 12000, "max": 20000}
            }
        ]
        
        # Filter by budget
        filtered = [d for d in destinations if d["price_range"]["max"] <= budget_max * 1.5]
        return filtered[:3]  # Return top 3
    
    async def _create_recommendation_item(
        self,
        destination: Dict,
        user_prefs: Dict[str, Any],
        search_results: List[Dict],
        index: int
    ) -> Optional[RecommendationItem]:
        """创建单个推荐方案"""
        try:
            # Calculate trip duration
            trip_days = self._calculate_trip_duration(user_prefs.dates)
            
            # Create itinerary
            itinerary = self._create_itinerary(destination, trip_days, user_prefs)
            
            # Calculate total cost
            total_cost = self._calculate_total_cost(destination, trip_days, user_prefs)
            
            # Determine confidence based on data availability
            confidence = self._calculate_confidence(destination, search_results, user_prefs)
            
            # Create highlights based on destination and preferences
            highlights = self._create_highlights(destination, user_prefs)
            
            return RecommendationItem(
                id=f"rec_{index:03d}",
                title=f"{destination['name']} {trip_days}日游",
                description=destination['description'],
                confidence=confidence,
                total_cost=total_cost,
                itinerary=itinerary,
                highlights=highlights,
                estimated_duration_days=trip_days
            )
        except Exception as e:
            logger.error(f"Error creating recommendation item: {e}")
            return None
    
    def _calculate_trip_duration(self, dates: Dict[str, Any]) -> int:
        """计算旅行天数"""
        try:
            if dates.departure and dates.return_date:
                dep = datetime.strptime(dates.departure, "%Y-%m-%d")
                ret = datetime.strptime(dates.return_date, "%Y-%m-%d")
                duration = (ret - dep).days
                return max(1, duration)
        except:
            pass
        
        # Default to 5 days if cannot calculate
        return 5
    
    def _create_itinerary(self, destination: Dict, trip_days: int, user_prefs: Dict) -> List[ItineraryDay]:
        """创建行程计划"""
        itinerary = []
        
        prefs = user_prefs.preferences or []
        pace = user_prefs.pace or "moderate"
        
        # Activities per day based on pace
        activities_per_day = {
            "relaxed": 2,
            "moderate": 3,
            "packed": 4
        }.get(pace, 3)
        
        for day in range(1, min(trip_days + 1, 8)):  # Max 7 days
            activities = []
            
            # Morning activity
            activities.append(ActivityInfo(
                time="09:00",
                activity=f"探索{destination['name']}主要景点",
                location="市中心",
                duration="3h"
            ))
            
            # Afternoon activity
            if activities_per_day >= 2:
                activities.append(ActivityInfo(
                    time="14:00",
                    activity=f"体验当地文化活动",
                    location="文化区",
                    duration="2h"
                ))
            
            # Evening activity
            if activities_per_day >= 3:
                activities.append(ActivityInfo(
                    time="19:00",
                    activity=f"品尝当地美食",
                    location="推荐餐厅",
                    duration="2h"
                ))
            
            # Flexible activity based on preferences
            if activities_per_day >= 4 and prefs:
                activities.append(ActivityInfo(
                    time="Flexible",
                    activity=f"根据个人兴趣: {', '.join(prefs[:2])}",
                    location="自选",
                    duration=None
                ))
            
            itinerary.append(ItineraryDay(
                day=day,
                title=f"第{day}天 - {destination['name']}探索",
                activities=activities
            ))
        
        return itinerary
    
    def _calculate_total_cost(
        self, 
        destination: Dict, 
        trip_days: int, 
        user_prefs: Dict
    ) -> TotalCost:
        """计算总费用"""
        currency = user_prefs.budget.currency if user_prefs.budget else "CNY"
        
        # Base costs from destination price range
        price_range = destination.get("price_range", {"min": 5000, "max": 10000})
        base_cost = (price_range["min"] + price_range["max"]) / 2
        
        # Adjust for trip duration (rough estimate)
        daily_multiplier = trip_days / 5  # Assume 5 days baseline
        
        total_amount = base_cost * daily_multiplier
        
        # Create cost breakdown
        breakdown = CostBreakdown(
            flights=round(total_amount * 0.4, 2),
            accommodation=round(total_amount * 0.35, 2),
            activities=round(total_amount * 0.15, 2),
            meals=round(total_amount * 0.1, 2)
        )
        
        return TotalCost(
            amount=round(total_amount, 2),
            currency=currency,
            breakdown=breakdown
        )
    
    def _calculate_confidence(self, destination: Dict, search_results: List, user_prefs: Dict) -> float:
        """计算推荐置信度"""
        confidence = 0.7  # Base confidence
        
        # Increase if destination from search results
        if any(r.get("id") == destination.get("id") for r in search_results):
            confidence += 0.2
        
        # Increase if destination matches budget
        if user_prefs.budget and destination.get("price_range"):
            dest_max = destination["price_range"].get("max", 0) or 0
            user_max = user_prefs.budget.max or 100000
            if dest_max <= user_max:
                confidence += 0.1
        
        # Increase if matches preferences
        if user_prefs.preferences:
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _create_highlights(self, destination: Dict, user_prefs: Dict) -> List[str]:
        """创建亮点标签"""
        highlights = []
        
        # Add destination highlights
        if destination.get("popular_attractions"):
            highlights.extend(destination["popular_attractions"][:2])
        
        # Add based on preferences
        prefs = user_prefs.preferences or []
        if "culture" in prefs:
            highlights.append("文化体验")
        if "food" in prefs:
            highlights.append("美食探索")
        if "beach" in prefs:
            highlights.append("海滩度假")
        
        # Ensure unique highlights
        return list(set(highlights))[:5]
    
    def calculate_cost(
        self,
        input_data: RecommendInput,
        output_data: RecommendOutput
    ) -> float:
        """
        动态成本计算 - 基于推荐数量
        
        Args:
            input_data: RecommendInput model
            output_data: RecommendOutput model
            
        Returns:
            Actual cost in USD
        """
        base_cost = 0.02
        per_rec_cost = 0.02
        max_cost = 0.15
        
        # Calculate based on number of recommendations generated
        num_recommendations = len(output_data.recommendations)
        actual_cost = base_cost + min(num_recommendations, 5) * per_rec_cost
        actual_cost = min(actual_cost, max_cost)
        
        return round(actual_cost, 4)
    
    def _generate_mock_recommendations(
        self,
        user_prefs: Dict,
        search_results: List,
        num_recommendations: int
    ) -> List[RecommendationItem]:
        """生成模拟推荐方案作为降级方案"""
        logger.warning("Generating mock recommendations due to error")
        
        mock_recommendations = []
        trip_days = 5  # Default
        
        for i in range(min(num_recommendations, 3)):
            mock_rec = RecommendationItem(
                id=f"mock_rec_{i+1:03d}",
                title=f"模拟推荐方案 {i+1}",
                description="基于用户偏好的旅游推荐方案（模拟数据）",
                confidence=0.6,
                total_cost=TotalCost(
                    amount=8000.0,
                    currency="CNY",
                    breakdown=CostBreakdown(
                        flights=3200.0,
                        accommodation=2800.0,
                        activities=1200.0,
                        meals=800.0
                    )
                ),
                itinerary=[
                    ItineraryDay(
                        day=1,
                        title="抵达与初探",
                        activities=[
                            ActivityInfo(
                                time="14:00",
                                activity="办理入住",
                                location="酒店",
                                duration="1h"
                            )
                        ]
                    )
                ],
                highlights=["文化", "美食", "休闲"],
                estimated_duration_days=trip_days
            )
            mock_recommendations.append(mock_rec)
        
        return mock_recommendations


__all__ = ["RecommendSkill"]
