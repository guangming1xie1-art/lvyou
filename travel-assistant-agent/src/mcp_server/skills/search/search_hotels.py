"""SearchHotelsSkill - Search for available hotels"""

from typing import Any, Dict, List
from ..base_skill import BaseSkill


class SearchHotelsSkill(BaseSkill):
    """Search for hotels at a destination
    
    This skill queries available hotels for a given destination and date range,
    returning hotel options with pricing, amenities, and ratings.
    """
    
    name = "search_hotels"
    agent_type = "search"
    description = "Search and return available hotels for given destination and dates"
    version = "1.0.0"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "Destination city or region"
                },
                "check_in_date": {
                    "type": "string",
                    "description": "Check-in date (YYYY-MM-DD)"
                },
                "check_out_date": {
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
                    "description": "Number of rooms",
                    "default": 1
                },
                "min_rating": {
                    "type": "number",
                    "description": "Minimum hotel rating (1-5 stars)",
                    "default": 0
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 10
                }
            },
            "required": ["destination", "check_in_date", "check_out_date"]
        }
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "hotels": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "hotel_id": {"type": "string"},
                            "name": {"type": "string"},
                            "rating": {"type": "number"},
                            "review_count": {"type": "integer"},
                            "review_score": {"type": "number"},
                            "address": {"type": "string"},
                            "distance_to_center": {"type": "string"},
                            "amenities": {"type": "array", "items": {"type": "string"}},
                            "room_type": {"type": "string"},
                            "price_per_night": {"type": "number"},
                            "total_price": {"type": "number"},
                            "currency": {"type": "string"},
                            "cancellation_policy": {"type": "string"},
                            "breakfast_included": {"type": "boolean"}
                        }
                    }
                },
                "search_metadata": {
                    "type": "object",
                    "properties": {
                        "destination": {"type": "string"},
                        "check_in": {"type": "string"},
                        "check_out": {"type": "string"},
                        "nights": {"type": "integer"},
                        "guests": {"type": "integer"},
                        "results_count": {"type": "integer"}
                    }
                }
            },
            "required": ["hotels", "search_metadata"]
        }
    
    async def execute(
        self,
        destination: str,
        check_in_date: str,
        check_out_date: str,
        guests: int = 2,
        rooms: int = 1,
        min_rating: float = 0,
        max_results: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """Search for hotels
        
        Args:
            destination: Destination location
            check_in_date: Check-in date
            check_out_date: Check-out date
            guests: Number of guests
            rooms: Number of rooms
            min_rating: Minimum rating filter
            max_results: Maximum results to return
            
        Returns:
            Hotel search results
        """
        if not self.validate_input({
            "destination": destination,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date
        }):
            raise ValueError("Invalid input: destination, check_in_date, and check_out_date are required")
        
        # Calculate nights
        from datetime import datetime
        try:
            check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
            check_out = datetime.strptime(check_out_date, "%Y-%m-%d")
            nights = (check_out - check_in).days
        except:
            nights = 3  # Default
        
        # Mock hotel data
        hotel_templates = [
            {
                "name": "Grand Plaza Hotel",
                "rating": 5,
                "review_score": 9.2,
                "review_count": 1250,
                "distance": "0.5 km",
                "amenities": ["Pool", "Spa", "Gym", "Restaurant", "WiFi", "Parking"],
                "base_price": 250,
                "room": "Deluxe King Room"
            },
            {
                "name": "Cozy Inn Downtown",
                "rating": 4,
                "review_score": 8.5,
                "review_count": 850,
                "distance": "0.8 km",
                "amenities": ["WiFi", "Breakfast", "Gym", "Restaurant"],
                "base_price": 120,
                "room": "Standard Double Room"
            },
            {
                "name": "Sunset Resort & Spa",
                "rating": 5,
                "review_score": 9.5,
                "review_count": 2100,
                "distance": "3.2 km",
                "amenities": ["Beach Access", "Pool", "Spa", "Multiple Restaurants", "WiFi", "Kids Club"],
                "base_price": 320,
                "room": "Ocean View Suite"
            },
            {
                "name": "Budget Stay Express",
                "rating": 3,
                "review_score": 7.8,
                "review_count": 450,
                "distance": "2.1 km",
                "amenities": ["WiFi", "Parking"],
                "base_price": 65,
                "room": "Economy Room"
            },
            {
                "name": "Heritage Boutique Hotel",
                "rating": 4,
                "review_score": 9.0,
                "review_count": 620,
                "distance": "1.2 km",
                "amenities": ["WiFi", "Restaurant", "Rooftop Bar", "Concierge"],
                "base_price": 180,
                "room": "Classic Room"
            },
            {
                "name": "Modern Tower Suites",
                "rating": 4,
                "review_score": 8.8,
                "review_count": 980,
                "distance": "1.5 km",
                "amenities": ["Pool", "Gym", "WiFi", "Kitchen", "Parking"],
                "base_price": 150,
                "room": "Studio Suite"
            }
        ]
        
        # Generate hotel results
        hotels = []
        for i, template in enumerate(hotel_templates):
            if template["rating"] < min_rating:
                continue
                
            price_per_night = template["base_price"] * rooms
            total_price = price_per_night * nights
            
            hotels.append({
                "hotel_id": f"HTL-{destination[:3].upper()}-{i+1:03d}",
                "name": template["name"],
                "rating": template["rating"],
                "review_count": template["review_count"],
                "review_score": template["review_score"],
                "address": f"{i+1}00 Main Street, {destination}",
                "distance_to_center": template["distance"],
                "amenities": template["amenities"],
                "room_type": template["room"],
                "price_per_night": price_per_night,
                "total_price": total_price,
                "currency": "USD",
                "cancellation_policy": "Free cancellation up to 24 hours before check-in" if template["rating"] >= 4 else "Non-refundable",
                "breakfast_included": template["rating"] >= 4
            })
            
            if len(hotels) >= max_results:
                break
        
        return {
            "hotels": hotels,
            "search_metadata": {
                "destination": destination,
                "check_in": check_in_date,
                "check_out": check_out_date,
                "nights": nights,
                "guests": guests,
                "results_count": len(hotels)
            }
        }
