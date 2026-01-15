"""
推荐工具模块
提供行程规划、预算计算、特色体验推荐的具体实现
"""
from typing import List, Dict, Any
from langchain_core.tools import tool
import logging

logger = logging.getLogger(__name__)


@tool
async def generate_itinerary(
    destination: str,
    duration_days: int = 5,
    preferences: Dict = None
) -> Dict:
    """
    生成旅游行程规划

    Args:
        destination: 目的地
        duration_days: 行程天数
        preferences: 用户偏好

    Returns:
        行程规划
    """
    if preferences is None:
        preferences = {}

    logger.info(f"Generating itinerary for {destination} ({duration_days} days)")

    # 生成每日行程
    daily_plans = []
    for day in range(1, duration_days + 1):
        daily_plan = {
            "day": day,
            "theme": f"探索{destination} - 第{day}天",
            "activities": [
                {
                    "time": "09:00-11:30",
                    "activity": "景点游览",
                    "type": "sightseeing",
                    "location": f"{destination}著名景点"
                },
                {
                    "time": "12:00-13:30",
                    "activity": "午餐休息",
                    "type": "dining",
                    "recommendation": "当地特色餐厅"
                },
                {
                    "time": "14:00-17:00",
                    "activity": "文化体验",
                    "type": "culture",
                    "location": "历史文化场所"
                },
                {
                    "time": "18:00-20:00",
                    "activity": "晚餐体验",
                    "type": "dining",
                    "recommendation": "夜景餐厅"
                }
            ]
        }
        daily_plans.append(daily_plan)

    return {
        "destination": destination,
        "duration_days": duration_days,
        "daily_plans": daily_plans,
        "total_activities": len(daily_plans) * 4,
        "highlights": [
            f"{destination}必游景点",
            "当地特色美食",
            "文化历史体验"
        ]
    }


@tool
async def calculate_budget(
    destination: str,
    duration_days: int = 5,
    budget: float = 0,
    preferences: Dict = None
) -> Dict:
    """
    计算旅游预算

    Args:
        destination: 目的地
        duration_days: 行程天数
        budget: 用户预算（0表示未指定）
        preferences: 用户偏好

    Returns:
        预算明细
    """
    if preferences is None:
        preferences = {}

    logger.info(f"Calculating budget for {destination} ({duration_days} days)")

    # 基础费用估算
    accommodation_per_night = 500.0  # 平均每晚住宿费
    flight_round_trip = 2000.0  # 往返机票
    food_per_day = 200.0  # 每天餐饮
    activities_per_day = 150.0  # 每天活动

    accommodation_total = accommodation_per_night * duration_days
    transportation_total = flight_round_trip
    food_total = food_per_day * duration_days
    activities_total = activities_per_day * duration_days

    total_budget = accommodation_total + transportation_total + food_total + activities_total

    # 如果用户提供了预算，按比例调整
    if budget > 0:
        ratio = budget / total_budget
        accommodation_total *= ratio
        transportation_total *= ratio
        food_total *= ratio
        activities_total *= ratio
        total_budget = budget

    budget_breakdown = {
        "accommodation": {
            "amount": round(accommodation_total, 2),
            "percentage": round(accommodation_total / total_budget * 100, 1) if total_budget > 0 else 0,
            "description": "住宿费用"
        },
        "transportation": {
            "amount": round(transportation_total, 2),
            "percentage": round(transportation_total / total_budget * 100, 1) if total_budget > 0 else 0,
            "description": "交通费用"
        },
        "food": {
            "amount": round(food_total, 2),
            "percentage": round(food_total / total_budget * 100, 1) if total_budget > 0 else 0,
            "description": "餐饮费用"
        },
        "activities": {
            "amount": round(activities_total, 2),
            "percentage": round(activities_total / total_budget * 100, 1) if total_budget > 0 else 0,
            "description": "活动门票"
        }
    }

    return {
        "destination": destination,
        "duration_days": duration_days,
        "total_budget": round(total_budget, 2),
        "user_budget": round(budget, 2) if budget > 0 else "未指定",
        "budget_breakdown": budget_breakdown,
        "currency": "CNY",
        "tips": [
            "提前预订可享受折扣",
            "避开旺季出行可节省费用",
            "当地公共交通比出租车更经济"
        ]
    }


@tool
async def recommend_experiences(
    destination: str,
    interests: List[str] = None
) -> List[Dict]:
    """
    推荐特色体验

    Args:
        destination: 目的地
        interests: 兴趣爱好

    Returns:
        特色体验列表
    """
    if interests is None:
        interests = []

    logger.info(f"Recommending experiences for {destination}")

    # 根据兴趣推荐体验
    experiences = []

    if not interests or "美食" in interests or "food" in interests:
        experiences.append({
            "category": "美食体验",
            "title": f"{destination}特色美食之旅",
            "description": "品尝当地最正宗的特色菜肴，包括街头小吃、传统名菜",
            "estimated_duration": "3-4小时",
            "price_range": "100-300元/人",
            "highlights": ["当地名菜", "街头小吃", "特色甜品"]
        })

    if not interests or "文化" in interests or "culture" in interests:
        experiences.append({
            "category": "文化体验",
            "title": f"{destination}历史文化探索",
            "description": "深入了解当地的历史文化底蕴，参观博物馆、古迹",
            "estimated_duration": "4-6小时",
            "price_range": "50-150元/人",
            "highlights": ["历史古迹", "文化博物馆", "传统工艺"]
        })

    if not interests or "自然" in interests or "nature" in interests:
        experiences.append({
            "category": "自然体验",
            "title": f"{destination}自然风光巡游",
            "description": "欣赏壮丽的自然景观，体验户外活动",
            "estimated_duration": "全天",
            "price_range": "200-500元/人",
            "highlights": ["自然风光", "户外活动", "摄影机会"]
        })

    # 默认添加一些通用体验
    if len(experiences) < 3:
        experiences.append({
            "category": "购物体验",
            "title": f"{destination}特色购物",
            "description": "探索当地的购物中心、特色市集，购买纪念品",
            "estimated_duration": "2-3小时",
            "price_range": "视购买情况而定",
            "highlights": ["特色商品", "纪念品", "当地特产"]
        })

    return experiences
