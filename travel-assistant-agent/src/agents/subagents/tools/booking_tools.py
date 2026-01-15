"""
预订工具模块
提供航班、酒店、门票预订的具体实现
"""
from typing import Dict, Any
from langchain_core.tools import tool
import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def _generate_booking_id(prefix: str) -> str:
    """生成预订ID"""
    timestamp = int(datetime.now().timestamp())
    random_num = random.randint(1000, 9999)
    return f"{prefix}{timestamp}{random_num}"


@tool
async def book_flight(
    destination: str,
    departure_date: str = "2024-06-01",
    passengers: int = 1
) -> Dict:
    """
    预订航班

    Args:
        destination: 目的地
        departure_date: 出发日期
        passengers: 乘客人数

    Returns:
        预订结果
    """
    booking_id = _generate_booking_id("FL")

    logger.info(f"Booking flight {booking_id} to {destination} for {passengers} passenger(s)")

    # 简化版：返回模拟预订结果
    # 实际实现应该调用真实的航班预订 API
    return {
        "booking_id": booking_id,
        "type": "flight",
        "airline": "中国航空",
        "flight_number": "CA1234",
        "destination": destination,
        "departure_date": departure_date,
        "arrival_date": departure_date,  # 简化，实际应该是返回日期
        "passengers": passengers,
        "price": 1200.0 * passengers,
        "currency": "CNY",
        "status": "confirmed",
        "booking_date": datetime.now().strftime("%Y-%m-%d"),
        "confirmation_code": f"FL{random.randint(10000, 99999)}"
    }


@tool
async def book_hotel(
    destination: str,
    check_in: str = "2024-06-01",
    check_out: str = "2024-06-10",
    rooms: int = 1
) -> Dict:
    """
    预订酒店

    Args:
        destination: 目的地
        check_in: 入住日期
        check_out: 退房日期
        rooms: 房间数量

    Returns:
        预订结果
    """
    booking_id = _generate_booking_id("HT")

    # 计算住宿天数
    try:
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
        nights = (check_out_date - check_in_date).days
    except ValueError:
        nights = 5  # 默认5天

    logger.info(f"Booking hotel {booking_id} in {destination} for {nights} night(s)")

    price_per_night = 600.0
    total_price = price_per_night * nights * rooms

    # 简化版：返回模拟预订结果
    return {
        "booking_id": booking_id,
        "type": "hotel",
        "hotel_name": "豪华大酒店",
        "destination": destination,
        "check_in_date": check_in,
        "check_out_date": check_out,
        "nights": nights,
        "rooms": rooms,
        "price_per_night": price_per_night,
        "total_price": total_price,
        "currency": "CNY",
        "status": "confirmed",
        "booking_date": datetime.now().strftime("%Y-%m-%d"),
        "confirmation_code": f"HT{random.randint(10000, 99999)}"
    }


@tool
async def book_ticket(
    attraction: str,
    visit_date: str = "2024-06-01",
    visitors: int = 1
) -> Dict:
    """
    预订景点门票

    Args:
        attraction: 景点名称
        visit_date: 参观日期
        visitors: 参观人数

    Returns:
        预订结果
    """
    booking_id = _generate_booking_id("TK")

    logger.info(f"Booking ticket {booking_id} for {attraction} on {visit_date}")

    ticket_price = 100.0
    total_price = ticket_price * visitors

    # 简化版：返回模拟预订结果
    return {
        "booking_id": booking_id,
        "type": "ticket",
        "attraction_name": attraction,
        "visit_date": visit_date,
        "visitors": visitors,
        "ticket_price": ticket_price,
        "total_price": total_price,
        "currency": "CNY",
        "status": "confirmed",
        "booking_date": datetime.now().strftime("%Y-%m-%d"),
        "confirmation_code": f"TK{random.randint(10000, 99999)}",
        "ticket_type": "成人票",
        "validity": "参观当天有效"
    }
