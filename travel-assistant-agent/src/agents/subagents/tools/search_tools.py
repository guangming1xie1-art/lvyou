"""
搜索工具模块
提供航班、酒店、景点搜索的具体实现
"""
from typing import List, Dict, Any
from langchain_core.tools import tool
import logging

logger = logging.getLogger(__name__)


@tool
async def search_flights(destination: str, departure_date: str = "2024-06-01") -> List[Dict]:
    """
    搜索航班信息

    Args:
        destination: 目的地
        departure_date: 出发日期

    Returns:
        航班列表
    """
    logger.info(f"Searching flights to {destination} on {departure_date}")

    # 简化版：返回模拟数据
    # 实际实现应该调用真实的航班搜索 API
    return [
        {
            "id": "FL001",
            "airline": "中国航空",
            "flight_number": "CA1234",
            "departure_time": "08:00",
            "arrival_time": "10:30",
            "price": 1200.0,
            "currency": "CNY",
            "stops": 0,
            "duration": "2h 30m",
            "aircraft": "Boeing 737"
        },
        {
            "id": "FL002",
            "airline": "东方航空",
            "flight_number": "MU5678",
            "departure_time": "14:00",
            "arrival_time": "16:45",
            "price": 980.0,
            "currency": "CNY",
            "stops": 0,
            "duration": "2h 45m",
            "aircraft": "Airbus A320"
        }
    ]


@tool
async def search_hotels(
    destination: str,
    check_in: str = "2024-06-01",
    check_out: str = "2024-06-10"
) -> List[Dict]:
    """
    搜索酒店信息

    Args:
        destination: 目的地
        check_in: 入住日期
        check_out: 退房日期

    Returns:
        酒店列表
    """
    logger.info(f"Searching hotels in {destination} from {check_in} to {check_out}")

    # 简化版：返回模拟数据
    return [
        {
            "id": "HT001",
            "name": "豪华大酒店",
            "rating": 5.0,
            "price_per_night": 600.0,
            "currency": "CNY",
            "amenities": ["WiFi", "健身房", "游泳池", "餐厅", "SPA"],
            "location": "市中心",
            "room_types": ["标准间", "豪华间", "套房"]
        },
        {
            "id": "HT002",
            "name": "舒适酒店",
            "rating": 4.0,
            "price_per_night": 350.0,
            "currency": "CNY",
            "amenities": ["WiFi", "早餐", "停车场", "会议室"],
            "location": "交通便利",
            "room_types": ["标准间", "大床房"]
        }
    ]


@tool
async def search_attractions(destination: str) -> List[Dict]:
    """
    搜索景点信息

    Args:
        destination: 目的地

    Returns:
        景点列表
    """
    logger.info(f"Searching attractions in {destination}")

    # 简化版：返回模拟数据
    return [
        {
            "id": "AT001",
            "name": "著名景点 A",
            "category": "自然景观",
            "rating": 4.8,
            "ticket_price": 100.0,
            "currency": "CNY",
            "description": "绝佳的自然风光，值得一看",
            "opening_hours": "08:00-18:00",
            "recommended_duration": "3-4小时"
        },
        {
            "id": "AT002",
            "name": "历史古迹 B",
            "category": "历史文化",
            "rating": 4.6,
            "ticket_price": 50.0,
            "currency": "CNY",
            "description": "深厚的历史文化底蕴",
            "opening_hours": "09:00-17:00",
            "recommended_duration": "2-3小时"
        }
    ]
