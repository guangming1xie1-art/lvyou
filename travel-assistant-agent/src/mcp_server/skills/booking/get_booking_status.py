"""GetBookingStatusSkill - Check booking status"""

from typing import Any, Dict
from datetime import datetime, timedelta
from ..base_skill import BaseSkill

try:
    from utils.java_api_client import java_api_client, JavaAPIError
except ModuleNotFoundError:
    from src.utils.java_api_client import java_api_client, JavaAPIError

try:
    from utils.logger import app_logger
except ModuleNotFoundError:
    from src.utils.logger import app_logger


class GetBookingStatusSkill(BaseSkill):
    """Get current status of a booking
    
    This skill retrieves the current status, details, and any updates
    for an existing booking using the booking ID or confirmation number.
    """
    
    name = "get_booking_status"
    agent_type = "booking"
    description = "Check current status and details of a booking"
    version = "2.0.0"
    
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
            app_logger.error("GetBookingStatusSkill: Invalid input - booking_id is required")
            return {
                "booking_id": booking_id,
                "status": "unknown",
                "trip_details": {},
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "booking_id is required"
                }
            }
        
        app_logger.info(f"Fetching status for booking {booking_id}")
        
        try:
            # Call Java API
            result = await java_api_client.get_booking_status(booking_id=booking_id)
            
            status = result.get("status", "unknown")
            app_logger.info(f"Booking {booking_id} status: {status}")
            
            # Enrich and transform result to match output_schema
            booking_date = result.get("created_at") or datetime.now().isoformat()
            last_updated = result.get("updated_at") or datetime.now().isoformat()
            
            # Use data from result or provide sensible defaults
            details = result.get("details", {})
            trip_info = details.get("trip_details", {})
            
            departure_date = trip_info.get("departure_date") or (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            return_date = trip_info.get("return_date") or (datetime.now() + timedelta(days=37)).strftime("%Y-%m-%d")
            
            trip_details = {
                "destination": trip_info.get("destination", "Unknown"),
                "departure_date": departure_date,
                "return_date": return_date,
                "travelers": trip_info.get("travelers", 1),
                "days_until_trip": trip_info.get("days_until_trip", 30)
            }
            
            payment_info = {
                "amount_paid": result.get("total_amount", 0.0) if status == "confirmed" else 0.0,
                "currency": result.get("currency", "USD"),
                "payment_status": "completed" if status == "confirmed" else "pending",
                "transaction_id": result.get("transaction_id")
            }
            
            updates = result.get("updates", [
                {
                    "timestamp": booking_date,
                    "type": "booking_created",
                    "message": "Booking created successfully"
                }
            ])
            
            available_actions = []
            if status == "pending_payment":
                available_actions = ["complete_payment", "cancel_booking"]
            elif status == "confirmed":
                available_actions = ["view_details", "modify_booking", "cancel_booking"]
            
            output = {
                "booking_id": booking_id,
                "status": status,
                "booking_date": booking_date,
                "last_updated": last_updated,
                "customer_info": {
                    "name": details.get("customer_info", {}).get("name", "Valued Customer"),
                    "email": customer_email or details.get("customer_info", {}).get("email", "customer@example.com")
                },
                "trip_details": trip_details,
                "payment_info": payment_info,
                "updates": updates,
                "available_actions": available_actions
            }
            
            if include_details and status == "confirmed":
                output["flight_details"] = details.get("selected_flight")
                output["hotel_details"] = details.get("selected_hotel")
                
            return output

        except JavaAPIError as e:
            app_logger.error(f"GetBookingStatusSkill: Java API error for booking {booking_id} - {e}")
            return {
                "booking_id": booking_id,
                "status": "unknown",
                "trip_details": {},
                "error": {
                    "code": "JAVA_API_ERROR",
                    "message": str(e),
                    "status_code": getattr(e, "status_code", None)
                }
            }
        except Exception as e:
            app_logger.error(f"GetBookingStatusSkill: Unexpected error for booking {booking_id} - {e}", exc_info=True)
            return {
                "booking_id": booking_id,
                "status": "unknown",
                "trip_details": {},
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "查询预订状态失败，请稍后重试"
                }
            }
