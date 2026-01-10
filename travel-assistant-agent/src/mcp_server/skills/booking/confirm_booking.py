"""ConfirmBookingSkill - Confirm booking and send confirmation"""

from typing import Any, Dict
from datetime import datetime
from ..base_skill import BaseSkill


class ConfirmBookingSkill(BaseSkill):
    """Confirm booking and send confirmation details
    
    This skill finalizes a booking after successful payment and
    generates confirmation details with booking reference.
    """
    
    name = "confirm_booking"
    agent_type = "booking"
    description = "Confirm booking after payment and send confirmation details"
    version = "1.0.0"
    
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
            raise ValueError("Invalid input: booking_id and transaction_id are required")
        
        # Generate confirmation number
        confirmation_number = f"CONF-{booking_id.split('-')[-1]}"
        confirmed_at = datetime.now()
        
        # Mock booking details retrieval
        # In production, this would fetch actual booking data from database
        booking_details = {
            "destination": "Tokyo, Japan",
            "dates": "2024-05-01 to 2024-05-07",
            "travelers": 2,
            "total_paid": 2850.00
        }
        
        # Generate document URLs (mock)
        base_url = "https://bookings.example.com/documents"
        documents = {
            "eticket_url": f"{base_url}/eticket/{booking_id}.pdf",
            "hotel_voucher_url": f"{base_url}/voucher/{booking_id}.pdf",
            "itinerary_url": f"{base_url}/itinerary/{booking_id}.pdf"
        }
        
        # Important information
        important_info = [
            "Please arrive at airport 3 hours before international departure",
            "Valid passport required for international travel",
            "Hotel check-in time: 3:00 PM, check-out: 11:00 AM",
            "Keep confirmation number for reference",
            "Download and print all travel documents"
        ]
        
        # Next steps
        next_steps = [
            "Download and save your travel documents",
            "Check passport validity (must be valid 6 months beyond travel dates)",
            "Review visa requirements for your destination",
            "Consider travel insurance if not already purchased",
            "Check airline baggage policies",
            "Add trip to your calendar",
            "Check-in online 24 hours before departure"
        ]
        
        # Simulate sending confirmation email
        email_sent = customer_email is not None
        
        return {
            "confirmation_status": "confirmed",
            "booking_id": booking_id,
            "confirmation_number": confirmation_number,
            "confirmed_at": confirmed_at.isoformat(),
            "booking_details": booking_details,
            "confirmation_email_sent": email_sent,
            "documents": documents,
            "important_info": important_info,
            "next_steps": next_steps
        }
