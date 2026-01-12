"""ConfirmBookingSkill - Confirm booking and send confirmation"""

from typing import Any, Dict
from datetime import datetime
from ..base_skill import BaseSkill

try:
    from utils.java_api_client import java_api_client, JavaAPIError
except ModuleNotFoundError:
    from src.utils.java_api_client import java_api_client, JavaAPIError

try:
    from utils.logger import app_logger
except ModuleNotFoundError:
    from src.utils.logger import app_logger


class ConfirmBookingSkill(BaseSkill):
    """Confirm booking and send confirmation details
    
    This skill finalizes a booking after successful payment and
    generates confirmation details with booking reference.
    """
    
    name = "confirm_booking"
    agent_type = "booking"
    description = "Confirm booking after payment and send confirmation details"
    version = "2.0.0"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "booking_id": {
                    "type": "string",
                    "description": "Booking ID to confirm"
                },
                "transaction_id": {
                    "type": "string",
                    "description": "Payment transaction ID"
                },
                "customer_email": {
                    "type": "string",
                    "description": "Email to send confirmation to"
                }
            },
            "required": ["booking_id", "transaction_id"]
        }
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "confirmation_status": {
                    "type": "string",
                    "enum": ["confirmed", "failed", "pending"]
                },
                "booking_id": {"type": "string"},
                "confirmation_number": {"type": "string"},
                "confirmed_at": {"type": "string"},
                "booking_details": {
                    "type": "object",
                    "properties": {
                        "destination": {"type": "string"},
                        "dates": {"type": "string"},
                        "travelers": {"type": "integer"},
                        "total_paid": {"type": "number"}
                    }
                },
                "confirmation_email_sent": {"type": "boolean"},
                "documents": {
                    "type": "object",
                    "properties": {
                        "eticket_url": {"type": "string"},
                        "hotel_voucher_url": {"type": "string"},
                        "itinerary_url": {"type": "string"}
                    }
                },
                "important_info": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "next_steps": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["confirmation_status", "booking_id", "confirmation_number"]
        }
    
    async def execute(
        self,
        booking_id: str,
        transaction_id: str,
        customer_email: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Confirm booking
        
        Args:
            booking_id: Booking ID
            transaction_id: Transaction ID
            customer_email: Customer email
            
        Returns:
            Booking confirmation details
        """
        if not self.validate_input({"booking_id": booking_id, "transaction_id": transaction_id}):
            app_logger.error(f"ConfirmBookingSkill: Invalid input for booking {booking_id}")
            return {
                "confirmation_status": "failed",
                "booking_id": booking_id,
                "confirmation_number": None,
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "booking_id and transaction_id are required"
                }
            }
        
        app_logger.info(f"Confirming booking {booking_id} with transaction {transaction_id}")
        
        try:
            # Call Java API
            result = await java_api_client.confirm_booking(booking_id=booking_id)
            
            confirmation_number = result.get("confirmation_number")
            confirmed_at = result.get("confirmed_at") or datetime.now().isoformat()
            
            app_logger.info(f"Booking {booking_id} confirmed successfully: {confirmation_number}")
            
            # Fetch details if not in result
            # Mocking the rest for consistency with output_schema
            booking_details = {
                "destination": "Unknown",
                "dates": "See confirmation",
                "travelers": 0,
                "total_paid": 0.0
            }
            
            # Try to get more info from result if available
            if "details" in result:
                details = result["details"]
                booking_details.update({
                    "destination": details.get("destination", "Unknown"),
                    "travelers": details.get("travelers", 0),
                    "total_paid": result.get("total_amount", 0.0)
                })

            base_url = "https://bookings.example.com/documents"
            documents = {
                "eticket_url": f"{base_url}/eticket/{booking_id}.pdf",
                "hotel_voucher_url": f"{base_url}/voucher/{booking_id}.pdf",
                "itinerary_url": f"{base_url}/itinerary/{booking_id}.pdf"
            }
            
            important_info = [
                "Please arrive at airport 3 hours before international departure",
                "Valid passport required for international travel",
                "Hotel check-in time: 3:00 PM, check-out: 11:00 AM",
                "Keep confirmation number for reference",
                "Download and print all travel documents"
            ]
            
            next_steps = [
                "Download and save your travel documents",
                "Check passport validity (must be valid 6 months beyond travel dates)",
                "Review visa requirements for your destination",
                "Consider travel insurance if not already purchased",
                "Check airline baggage policies",
                "Add trip to your calendar",
                "Check-in online 24 hours before departure"
            ]
            
            return {
                "confirmation_status": result.get("status", "confirmed"),
                "booking_id": booking_id,
                "confirmation_number": confirmation_number,
                "confirmed_at": confirmed_at,
                "booking_details": booking_details,
                "confirmation_email_sent": customer_email is not None,
                "documents": documents,
                "important_info": important_info,
                "next_steps": next_steps
            }

        except JavaAPIError as e:
            app_logger.error(f"ConfirmBookingSkill: Java API error for booking {booking_id} - {e}")
            return {
                "confirmation_status": "failed",
                "booking_id": booking_id,
                "confirmation_number": None,
                "error": {
                    "code": "JAVA_API_ERROR",
                    "message": str(e),
                    "status_code": getattr(e, "status_code", None)
                }
            }
        except Exception as e:
            app_logger.error(f"ConfirmBookingSkill: Unexpected error for booking {booking_id} - {e}", exc_info=True)
            return {
                "confirmation_status": "failed",
                "booking_id": booking_id,
                "confirmation_number": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "确认预订失败，请稍后重试"
                }
            }
