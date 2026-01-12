"""SearchHotelsSkill - Search for available hotels"""

from typing import Any, Dict, List
from datetime import datetime
from ..base_skill import BaseSkill
from src.utils.java_api_client import java_api_client, JavaAPIError
from src.utils.logger import app_logger


class SearchHotelsSkill(BaseSkill):
    """Search for hotels at a destination
    
    This skill queries available hotels for a given destination and date range,
    returning hotel options with pricing, amenities, and ratings.
    
    Version 2.0.0: Refactored to call Java API instead of local mock implementation.
    """
    
    name = "search_hotels"
    agent_type = "search"
    description = "Search and return available hotels for given destination and dates"
    version = "2.0.0"
    
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
        """Search for hotels by calling Java API
        
        Args:
            destination: Destination location
            check_in_date: Check-in date
            check_out_date: Check-out date
            guests: Number of guests
            rooms: Number of rooms
            min_rating: Minimum rating filter
            max_results: Maximum results to return
            
        Returns:
            Hotel search results with hotels list and search_metadata
        """
        if not self.validate_input({
            "destination": destination,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date
        }):
            raise ValueError("Invalid input: destination, check_in_date, and check_out_date are required")
        
        # Calculate nights
        try:
            check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
            check_out = datetime.strptime(check_out_date, "%Y-%m-%d")
            nights = (check_out - check_in).days
        except:
            nights = 3  # Default
        
        app_logger.info(f"SearchHotelsSkill: Searching hotels in {destination} for {nights} nights")
        
        try:
            # Call Java API to search hotels
            result = await java_api_client.search_hotels(
                destination=destination,
                check_in=check_in_date,
                check_out=check_out_date,
                guests=guests,
                rooms=rooms
            )
            
            # Get hotels from API response
            hotels = result.get("hotels", [])
            
            # Apply min_rating filter if specified (client-side filtering)
            if min_rating > 0:
                hotels = [h for h in hotels if h.get("rating", 0) >= min_rating]
            
            # Apply max_results limit
            if max_results and len(hotels) > max_results:
                hotels = hotels[:max_results]
            
            app_logger.info(f"SearchHotelsSkill: Found {len(hotels)} hotels")
            
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
            
        except JavaAPIError as e:
            app_logger.error(f"SearchHotelsSkill: Java API error - {e}")
            return {
                "hotels": [],
                "search_metadata": {
                    "destination": destination,
                    "check_in": check_in_date,
                    "check_out": check_out_date,
                    "nights": nights,
                    "guests": guests,
                    "results_count": 0
                },
                "error": {
                    "code": "JAVA_API_ERROR",
                    "message": str(e),
                    "status_code": getattr(e, "status_code", None)
                }
            }
        except Exception as e:
            app_logger.error(f"SearchHotelsSkill: Unexpected error - {e}")
            return {
                "hotels": [],
                "search_metadata": {
                    "destination": destination,
                    "check_in": check_in_date,
                    "check_out": check_out_date,
                    "nights": nights,
                    "guests": guests,
                    "results_count": 0
                },
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }
