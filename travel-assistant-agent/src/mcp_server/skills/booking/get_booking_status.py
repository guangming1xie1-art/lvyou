"""GetBookingStatusSkill - Check booking status"""

from typing import Any, Dict
from datetime import datetime
from ..base_skill import BaseSkill


class GetBookingStatusSkill(BaseSkill):
    """Get current status of a booking
    
    This skill retrieves the current status, details, and any updates
    for an existing booking using the booking ID or confirmation number.
    """
    
    name = "get_booking_status"
    agent_type = "booking"
    description = "Check current status and details of a booking"
    version = "1.0.0"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "booking_id": {
                    "type": "string",
                    "description": "Booking ID or confirmation number"
                },
                "customer_email": {
                    "type": "string",
                    "description": "Customer email for verification (optional)"
                },
                "include_details": {
                    "type": "boolean",
                    "description": "Include full booking details",
                    "default": True
                }
            },
            "required": ["booking_id"]
        }
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "booking_id": {"type": "string"},
                "status": {
                    "type": "string",
                    "enum": ["confirmed", "pending_payment", "cancelled", "completed", "in_progress"]
                },
                "booking_date": {"type": "string"},
                "last_updated": {"type": "string"},
                "customer_info": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string"}
                    }
                },
                "trip_details": {
                    "type": "object",
                    "properties": {
                        "destination": {"type": "string"},
                        "departure_date": {"type": "string"},
                        "return_date": {"type": "string"},
                        "travelers": {"type": "integer"},
                        "days_until_trip": {"type": "integer"}
                    }
                },
                "payment_info": {
                    "type": "object",
                    "properties": {
                        "amount_paid": {"type": "number"},
                        "currency": {"type": "string"},
                        "payment_status": {"type": "string"},
                        "transaction_id": {"type": "string"}
                    }
                },
                "flight_details": {"type": "object"},
                "hotel_details": {"type": "object"},
                "updates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "timestamp": {"type": "string"},
                            "type": {"type": "string"},
                            "message": {"type": "string"}
                        }
                    }
                },
                "available_actions": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["booking_id", "status", "trip_details"]
        }
    
    async def execute(
        self,
        booking_id: str,
        customer_email: str = None,
        include_details: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Get booking status
        
        Args:
            booking_id: Booking or confirmation number
            customer_email: Email for verification
            include_details: Include full details
            
        Returns:
            Booking status and details
        """
        if not self.validate_input({"booking_id": booking_id}):
            raise ValueError("Invalid input: booking_id is required")
        
        # Mock booking status lookup
        # In production, this would query the database
        
        # Simulate different booking statuses
        now = datetime.now()
        
        # Parse booking to determine mock status
        if "FAILED" in booking_id.upper():
            status = "cancelled"
        elif "PENDING" in booking_id.upper():
            status = "pending_payment"
        else:
            status = "confirmed"
        
        booking_date = now.replace(day=now.day - 5).isoformat()
        last_updated = now.isoformat()
        
        # Mock trip details
        from datetime import timedelta
        departure_date = (now + timedelta(days=30)).strftime("%Y-%m-%d")
        return_date = (now + timedelta(days=37)).strftime("%Y-%m-%d")
        days_until_trip = 30
        
        trip_details = {
            "destination": "Tokyo, Japan",
            "departure_date": departure_date,
            "return_date": return_date,
            "travelers": 2,
            "days_until_trip": days_until_trip
        }
        
        # Payment info
        payment_info = {
            "amount_paid": 2850.00 if status == "confirmed" else 0,
            "currency": "USD",
            "payment_status": "completed" if status == "confirmed" else "pending",
            "transaction_id": f"TXN-{booking_id.split('-')[-1]}" if status == "confirmed" else None
        }
        
        # Updates timeline
        updates = [
            {
                "timestamp": booking_date,
                "type": "booking_created",
                "message": "Booking created successfully"
            }
        ]
        
        if status == "confirmed":
            updates.append({
                "timestamp": booking_date,
                "type": "payment_received",
                "message": "Payment processed successfully"
            })
            updates.append({
                "timestamp": booking_date,
                "type": "booking_confirmed",
                "message": "Booking confirmed - confirmation email sent"
            })
        elif status == "pending_payment":
            updates.append({
                "timestamp": now.isoformat(),
                "type": "payment_pending",
                "message": "Awaiting payment - booking will expire in 24 hours"
            })
        elif status == "cancelled":
            updates.append({
                "timestamp": last_updated,
                "type": "booking_cancelled",
                "message": "Booking was cancelled"
            })
        
        # Available actions based on status
        available_actions = []
        if status == "pending_payment":
            available_actions = ["complete_payment", "cancel_booking"]
        elif status == "confirmed":
            if days_until_trip > 7:
                available_actions = ["modify_booking", "cancel_booking", "add_services"]
            else:
                available_actions = ["view_details", "download_documents"]
        
        result = {
            "booking_id": booking_id,
            "status": status,
            "booking_date": booking_date,
            "last_updated": last_updated,
            "customer_info": {
                "name": "John Doe",
                "email": customer_email or "customer@example.com"
            },
            "trip_details": trip_details,
            "payment_info": payment_info,
            "updates": updates,
            "available_actions": available_actions
        }
        
        # Add detailed booking info if requested
        if include_details and status == "confirmed":
            result["flight_details"] = {
                "outbound": {
                    "airline": "SkyAir",
                    "flight_number": "SA101",
                    "departure": "10:00 AM",
                    "arrival": "2:30 PM",
                    "date": departure_date
                },
                "return": {
                    "airline": "SkyAir",
                    "flight_number": "SA202",
                    "departure": "3:00 PM",
                    "arrival": "9:30 PM",
                    "date": return_date
                }
            }
            result["hotel_details"] = {
                "name": "Grand Plaza Hotel",
                "check_in": departure_date,
                "check_out": return_date,
                "room_type": "Deluxe King Room",
                "nights": 7
            }
        
        return result
