"""CreateBookingSkill - Create initial booking order"""

from typing import Any, Dict, List
from datetime import datetime
import random
import string
from ..base_skill import BaseSkill


class CreateBookingSkill(BaseSkill):
    """Create a new booking order for selected travel options
    
    This skill initiates a booking by creating an order that includes
    flights, hotels, and any additional services.
    """
    
    name = "create_booking"
    agent_type = "booking"
    description = "Create initial booking order for trip details and selected options"
    version = "1.0.0"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "customer_info": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"}
                    },
                    "required": ["name", "email"]
                },
                "trip_details": {
                    "type": "object",
                    "properties": {
                        "destination": {"type": "string"},
                        "departure_date": {"type": "string"},
                        "return_date": {"type": "string"},
                        "travelers": {"type": "integer"}
                    },
                    "required": ["destination", "departure_date", "travelers"]
                },
                "selected_flight": {
                    "type": "object",
                    "description": "Selected flight details"
                },
                "selected_hotel": {
                    "type": "object",
                    "description": "Selected hotel details"
                },
                "additional_services": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Additional services (insurance, tours, etc.)",
                    "default": []
                }
            },
            "required": ["customer_info", "trip_details"]
        }
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "booking_id": {"type": "string"},
                "status": {"type": "string"},
                "created_at": {"type": "string"},
                "expires_at": {"type": "string"},
                "customer_info": {"type": "object"},
                "trip_summary": {"type": "object"},
                "price_breakdown": {
                    "type": "object",
                    "properties": {
                        "flights_total": {"type": "number"},
                        "hotels_total": {"type": "number"},
                        "services_total": {"type": "number"},
                        "subtotal": {"type": "number"},
                        "taxes_and_fees": {"type": "number"},
                        "total": {"type": "number"},
                        "currency": {"type": "string"}
                    }
                },
                "payment_required": {"type": "boolean"},
                "next_steps": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["booking_id", "status", "price_breakdown", "next_steps"]
        }
    
    async def execute(
        self,
        customer_info: Dict[str, Any],
        trip_details: Dict[str, Any],
        selected_flight: Dict[str, Any] = None,
        selected_hotel: Dict[str, Any] = None,
        additional_services: List[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a booking
        
        Args:
            customer_info: Customer details
            trip_details: Trip information
            selected_flight: Selected flight
            selected_hotel: Selected hotel
            additional_services: Additional services
            
        Returns:
            Booking confirmation with booking ID
        """
        if not self.validate_input({"customer_info": customer_info, "trip_details": trip_details}):
            raise ValueError("Invalid input: customer_info and trip_details are required")
        
        # Generate booking ID
        booking_id = self._generate_booking_id()
        
        # Calculate pricing
        flight_total = selected_flight.get("total_price", 0) if selected_flight else 0
        hotel_total = selected_hotel.get("total_price", 0) if selected_hotel else 0
        services_total = sum(s.get("price", 0) for s in (additional_services or []))
        
        subtotal = flight_total + hotel_total + services_total
        taxes_and_fees = round(subtotal * 0.12, 2)  # 12% taxes/fees
        total = round(subtotal + taxes_and_fees, 2)
        
        # Create booking
        created_at = datetime.now()
        expires_at = created_at.replace(hour=created_at.hour + 24)  # 24 hour hold
        
        trip_summary = {
            "destination": trip_details.get("destination"),
            "departure_date": trip_details.get("departure_date"),
            "return_date": trip_details.get("return_date"),
            "travelers": trip_details.get("travelers"),
            "flight_included": selected_flight is not None,
            "hotel_included": selected_hotel is not None,
            "additional_services_count": len(additional_services or [])
        }
        
        next_steps = [
            "Review booking details carefully",
            "Proceed to payment to confirm booking",
            f"Complete payment by {expires_at.strftime('%Y-%m-%d %H:%M')} or booking will be released",
            "After payment, you'll receive confirmation email"
        ]
        
        return {
            "booking_id": booking_id,
            "status": "pending_payment",
            "created_at": created_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "customer_info": {
                "name": customer_info.get("name"),
                "email": customer_info.get("email"),
                "phone": customer_info.get("phone", "Not provided")
            },
            "trip_summary": trip_summary,
            "price_breakdown": {
                "flights_total": flight_total,
                "hotels_total": hotel_total,
                "services_total": services_total,
                "subtotal": subtotal,
                "taxes_and_fees": taxes_and_fees,
                "total": total,
                "currency": "USD"
            },
            "payment_required": True,
            "next_steps": next_steps
        }
    
    def _generate_booking_id(self) -> str:
        """Generate a unique booking ID"""
        timestamp = datetime.now().strftime("%Y%m%d")
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"BKG-{timestamp}-{random_chars}"
