"""
Built-in Booking Skills

This module provides booking-related skills for the Travel Assistant Agent.
"""

from typing import Dict, Any, List
import logging
from ..base import Skill

logger = logging.getLogger(__name__)


class BookFlightSkill(Skill):
    """Book a flight"""
    
    def __init__(self):
        super().__init__(
            name="book_flight",
            description="Book a flight for the user",
            version="1.0.0",
            enabled=True,
            cost_estimate=0.005,
            category="booking"
        )
    
    def get_required_fields(self) -> list:
        return ["flight_id", "user_id", "passengers"]
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute flight booking"""
        flight_id = input_data.get("flight_id")
        user_id = input_data.get("user_id")
        passengers = input_data.get("passengers", [])
        
        # Mock implementation
        booking_id = f"FLB{flight_id}{user_id[:4]}"
        result = {
            "booking_id": booking_id,
            "flight_id": flight_id,
            "user_id": user_id,
            "passengers_count": len(passengers),
            "status": "confirmed",
            "total_price": 500 * len(passengers),  # Mock pricing
            "confirmation_code": f"CNF{booking_id.upper()}",
            "timestamp": "2024-01-15T10:00:00Z"
        }
        
        logger.info(f"Flight booked: {booking_id} for user {user_id}")
        return result


class BookHotelSkill(Skill):
    """Book a hotel room"""
    
    def __init__(self):
        super().__init__(
            name="book_hotel",
            description="Book a hotel room for the user",
            version="1.0.0",
            enabled=True,
            cost_estimate=0.005,
            category="booking"
        )
    
    def get_required_fields(self) -> list:
        return ["hotel_id", "user_id", "check_in", "check_out"]
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute hotel booking"""
        hotel_id = input_data.get("hotel_id")
        user_id = input_data.get("user_id")
        check_in = input_data.get("check_in")
        check_out = input_data.get("check_out")
        rooms = input_data.get("rooms", 1)
        guest_info = input_data.get("guest_info", {})
        
        # Mock implementation
        booking_id = f"HTB{hotel_id}{user_id[:4]}"
        result = {
            "booking_id": booking_id,
            "hotel_id": hotel_id,
            "user_id": user_id,
            "check_in": check_in,
            "check_out": check_out,
            "rooms": rooms,
            "status": "confirmed",
            "total_price": 100 * rooms,  # Mock pricing
            "confirmation_code": f"CNF{booking_id.upper()}",
            "timestamp": "2024-01-15T10:00:00Z"
        }
        
        logger.info(f"Hotel booked: {booking_id} for user {user_id}")
        return result


class GetBookingStatusSkill(Skill):
    """Get booking status"""
    
    def __init__(self):
        super().__init__(
            name="get_booking_status",
            description="Get the status of a booking",
            version="1.0.0",
            enabled=True,
            cost_estimate=0.001,
            category="booking"
        )
    
    def get_required_fields(self) -> list:
        return ["booking_id"]
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute booking status check"""
        booking_id = input_data.get("booking_id")
        
        # Mock implementation
        result = {
            "booking_id": booking_id,
            "status": "confirmed",
            "confirmed_at": "2024-01-15T10:00:00Z",
            "is_active": True,
            "details": {
                "type": "flight" if booking_id.startswith("FLB") else "hotel",
                "reference": booking_id
            }
        }
        
        logger.info(f"Retrieved status for booking: {booking_id}")
        return result


class CancelBookingSkill(Skill):
    """Cancel a booking"""
    
    def __init__(self):
        super().__init__(
            name="cancel_booking",
            description="Cancel a booking",
            version="1.0.0",
            enabled=True,
            cost_estimate=0.005,
            category="booking"
        )
    
    def get_required_fields(self) -> list:
        return ["booking_id"]
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute booking cancellation"""
        booking_id = input_data.get("booking_id")
        reason = input_data.get("reason", "User requested")
        
        # Mock implementation
        result = {
            "booking_id": booking_id,
            "status": "cancelled",
            "cancelled_at": "2024-01-15T12:00:00Z",
            "reason": reason,
            "refund_status": "processing",
            "refund_amount": 500  # Mock refund amount
        }
        
        logger.info(f"Booking cancelled: {booking_id}")
        return result


__all__ = [
    "BookFlightSkill",
    "BookHotelSkill",
    "GetBookingStatusSkill",
    "CancelBookingSkill",
]
