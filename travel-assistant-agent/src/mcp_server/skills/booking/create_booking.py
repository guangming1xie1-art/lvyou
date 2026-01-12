"""CreateBookingSkill - Create initial booking order"""

from typing import Any, Dict, List
from datetime import datetime
import random
import string
from ..base_skill import BaseSkill

try:
    from utils.java_api_client import java_api_client, JavaAPIError
except ModuleNotFoundError:
    from src.utils.java_api_client import java_api_client, JavaAPIError

try:
    from utils.logger import app_logger
except ModuleNotFoundError:
    from src.utils.logger import app_logger


class CreateBookingSkill(BaseSkill):
    """Create a new booking order for selected travel options
    
    This skill initiates a booking by creating an order that includes
    flights, hotels, and any additional services.
    """
    
    name = "create_booking"
    agent_type = "booking"
    description = "Create initial booking order for trip details and selected options"
    version = "2.0.0"
    
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
            app_logger.error("CreateBookingSkill: Invalid input - customer_info and trip_details are required")
            return {
                "booking_id": None,
                "status": "failed",
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "customer_info and trip_details are required"
                },
                "price_breakdown": {"total": 0, "currency": "USD"},
                "next_steps": ["Check your input and try again"]
            }
        
        app_logger.info(f"Creating booking for {customer_info.get('email')} to {trip_details.get('destination')}")
        
        try:
            # Prepare data for Java API
            booking_payload = {
                "customer_info": customer_info,
                "trip_details": trip_details,
                "selected_flight": selected_flight,
                "selected_hotel": selected_hotel,
                "additional_services": additional_services or [],
                "user_id": customer_info.get("email") # Using email as user_id
            }
            
            # Call Java API
            result = await java_api_client.create_booking(booking_data=booking_payload)
            
            booking_id = result.get("booking_id")
            app_logger.info(f"Successfully created booking: {booking_id}")
            
            # Transform and enrich response to match output_schema
            # Some fields might be missing in API response if it's simplified
            created_at = result.get("created_at") or datetime.now().isoformat()
            
            # Calculate pricing if not returned by API (as fallback)
            price_breakdown = result.get("details", {}).get("price_breakdown")
            if not price_breakdown:
                flight_total = selected_flight.get("total_price", 0) if selected_flight else 0
                hotel_total = selected_hotel.get("total_price", 0) if selected_hotel else 0
                services_total = sum(s.get("price", 0) for s in (additional_services or []))
                subtotal = flight_total + hotel_total + services_total
                taxes_and_fees = round(subtotal * 0.12, 2)
                total = round(subtotal + taxes_and_fees, 2)
                price_breakdown = {
                    "flights_total": flight_total,
                    "hotels_total": hotel_total,
                    "services_total": services_total,
                    "subtotal": subtotal,
                    "taxes_and_fees": taxes_and_fees,
                    "total": total,
                    "currency": "USD"
                }

            # Generate expires_at if missing (24h hold)
            expires_at = result.get("expires_at")
            if not expires_at:
                dt_created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                dt_expires = dt_created.replace(hour=(dt_created.hour + 24) % 24)
                expires_at = dt_expires.isoformat()

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
                "Complete payment within 24 hours or booking will be released",
                "After payment, you'll receive confirmation email"
            ]

            return {
                "booking_id": booking_id,
                "status": result.get("status", "pending_payment"),
                "created_at": created_at,
                "expires_at": expires_at,
                "customer_info": {
                    "name": customer_info.get("name"),
                    "email": customer_info.get("email"),
                    "phone": customer_info.get("phone", "Not provided")
                },
                "trip_summary": trip_summary,
                "price_breakdown": price_breakdown,
                "payment_required": True,
                "next_steps": next_steps
            }

        except JavaAPIError as e:
            app_logger.error(f"CreateBookingSkill: Java API error - {e}")
            return {
                "booking_id": None,
                "status": "failed",
                "error": {
                    "code": "JAVA_API_ERROR",
                    "message": str(e),
                    "status_code": getattr(e, "status_code", None)
                },
                "price_breakdown": {"total": 0, "currency": "USD"},
                "next_steps": ["Please try again later or contact support"]
            }
        except Exception as e:
            app_logger.error(f"CreateBookingSkill: Unexpected error - {e}", exc_info=True)
            return {
                "booking_id": None,
                "status": "error",
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "创建预订失败，请稍后重试"
                },
                "price_breakdown": {"total": 0, "currency": "USD"},
                "next_steps": ["Please try again later"]
            }
