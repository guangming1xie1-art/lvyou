"""QueryPricesSkill - Query hotel and flight prices for destinations"""

from typing import Any, Dict, List
from .base_skill import BaseSkill


class QueryPricesSkill(BaseSkill):
    """Skill for querying hotel and flight prices"""
    
    name = "query_prices"
    description = "Get pricing information for hotels and flights to help travelers plan their budget"
    category = "pricing"
    version = "1.0.0"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "Name of the destination"
                },
                "check_in": {
                    "type": "string",
                    "description": "Check-in date (YYYY-MM-DD)"
                },
                "check_out": {
                    "type": "string",
                    "description": "Check-out date (YYYY-MM-DD)"
                },
                "guests": {
                    "type": "integer",
                    "description": "Number of guests",
                    "default": 2
                },
                "rooms": {
                    "type": "integer",
                    "description": "Number of rooms needed",
                    "default": 1
                },
                "flight_class": {
                    "type": "string",
                    "description": "Flight class (economy, business, first)",
                    "default": "economy"
                }
            },
            "required": ["destination"]
        }
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "destination": {"type": "string"},
                "dates": {
                    "type": "object",
                    "properties": {
                        "check_in": {"type": "string"},
                        "check_out": {"type": "string"},
                        "nights": {"type": "integer"}
                    }
                },
                "hotels": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "rating": {"type": "number"},
                            "price_per_night": {"type": "number"},
                            "total_price": {"type": "number"},
                            "amenities": {"type": "array", "items": {"type": "string"}},
                            "location": {"type": "string"}
                        }
                    }
                },
                "flights": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "airline": {"type": "string"},
                            "price": {"type": "number"},
                            "duration": {"type": "string"},
                            "stops": {"type": "integer"},
                            "class": {"type": "string"}
                        }
                    }
                },
                "total_budget_estimate": {
                    "type": "object",
                    "properties": {
                        "budget": {"type": "string"},
                        "hotel_total": {"type": "number"},
                        "flight_total": {"type": "number"},
                        "daily_budget": {"type": "number"}
                    }
                }
            },
            "required": ["destination"]
        }
    
    async def execute(
        self,
        destination: str,
        check_in: str = None,
        check_out: str = None,
        guests: int = 2,
        rooms: int = 1,
        flight_class: str = "economy"
    ) -> Dict[str, Any]:
        """Execute price query with mock data"""
        
        # Calculate nights if dates provided
        nights = 5  # default
        if check_in and check_out:
            try:
                from datetime import datetime
                start = datetime.strptime(check_in, "%Y-%m-%d")
                end = datetime.strptime(check_out, "%Y-%m-%d")
                nights = max(1, (end - start).days)
            except:
                pass
        
        # Mock hotel data
        hotels = [
            {
                "name": "Grand Plaza Hotel",
                "rating": 4.5,
                "price_per_night": 250,
                "total_price": 250 * nights * rooms,
                "amenities": ["WiFi", "Pool", "Gym", "Restaurant", "Room Service"],
                "location": "City Center"
            },
            {
                "name": "Seaside Resort",
                "rating": 4.8,
                "price_per_night": 400,
                "total_price": 400 * nights * rooms,
                "amenities": ["WiFi", "Beach Access", "Spa", "Multiple Restaurants", "Concierge"],
                "location": "Beachfront"
            },
            {
                "name": "Budget Inn Express",
                "rating": 3.8,
                "price_per_night": 90,
                "total_price": 90 * nights * rooms,
                "amenities": ["WiFi", "Breakfast", "Parking"],
                "location": "Near Airport"
            }
        ]
        
        # Mock flight data based on destination
        flight_multipliers = {
            "tokyo": {"base": 800, "duration": "12-14 hours"},
            "paris": {"base": 700, "duration": "8-10 hours"},
            "bali": {"base": 1100, "duration": "18-22 hours"},
        }
        
        dest_lower = destination.lower().strip()
        flight_info = flight_multipliers.get(dest_lower, {"base": 1000, "duration": "10-12 hours"})
        
        class_multipliers = {"economy": 1.0, "business": 3.0, "first": 5.0}
        multiplier = class_multipliers.get(flight_class, 1.0)
        
        flights = [
            {
                "airline": "Major Airline",
                "price": int(flight_info["base"] * multiplier * guests),
                "duration": flight_info["duration"],
                "stops": 0 if dest_lower in ["tokyo", "paris", "bali"] else 1,
                "class": flight_class
            },
            {
                "airline": "Budget Carrier",
                "price": int(flight_info["base"] * 0.7 * multiplier * guests),
                "duration": f"{int(flight_info['duration'].split('-')[0]) + 4}-{int(flight_info['duration'].split('-')[1].split()[0]) + 4} hours",
                "stops": 1,
                "class": flight_class
            }
        ]
        
        # Calculate budget estimate
        hotel_total = hotels[0]["total_price"]
        flight_total = flights[0]["price"]
        total_estimate = hotel_total + flight_total
        
        return {
            "destination": destination,
            "dates": {
                "check_in": check_in or "TBD",
                "check_out": check_out or "TBD",
                "nights": nights
            },
            "hotels": hotels,
            "flights": flights,
            "total_budget_estimate": {
                "budget": "mid-range",
                "hotel_total": hotel_total,
                "flight_total": flight_total,
                "daily_budget": total_estimate // nights if nights > 0 else total_estimate
            }
        }
