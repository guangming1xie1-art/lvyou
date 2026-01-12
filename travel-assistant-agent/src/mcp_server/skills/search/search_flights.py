"""SearchFlightsSkill - Search for available flights"""

from typing import Any, Dict, List
from datetime import datetime, timedelta
from ..base_skill import BaseSkill
from src.utils.java_api_client import java_api_client, JavaAPIError
from src.utils.logger import app_logger


class SearchFlightsSkill(BaseSkill):
    """Search for flights between two cities
    
    This skill queries available flights for a given route and date range,
    returning flight options with pricing and schedule information.
    
    Version 2.0.0: Refactored to call Java API instead of local mock implementation.
    """
    
    name = "search_flights"
    agent_type = "search"
    description = "Search and return available flights for given route and dates"
    version = "2.0.0"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "Departure city or airport code"
                },
                "destination": {
                    "type": "string",
                    "description": "Arrival city or airport code"
                },
                "departure_date": {
                    "type": "string",
                    "description": "Departure date (YYYY-MM-DD)"
                },
                "return_date": {
                    "type": "string",
                    "description": "Return date (YYYY-MM-DD) for round trip",
                    "default": None
                },
                "passengers": {
                    "type": "integer",
                    "description": "Number of passengers",
                    "default": 1
                },
                "cabin_class": {
                    "type": "string",
                    "description": "Cabin class preference",
                    "enum": ["economy", "premium_economy", "business", "first"],
                    "default": "economy"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 10
                }
            },
            "required": ["origin", "destination", "departure_date", "passengers"]
        }
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "outbound_flights": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "flight_id": {"type": "string"},
                            "airline": {"type": "string"},
                            "flight_number": {"type": "string"},
                            "departure_time": {"type": "string"},
                            "arrival_time": {"type": "string"},
                            "duration_minutes": {"type": "integer"},
                            "stops": {"type": "integer"},
                            "price_per_person": {"type": "number"},
                            "total_price": {"type": "number"},
                            "currency": {"type": "string"},
                            "available_seats": {"type": "integer"},
                            "cabin_class": {"type": "string"}
                        }
                    }
                },
                "return_flights": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Return flights if round trip"
                },
                "search_metadata": {
                    "type": "object",
                    "properties": {
                        "origin": {"type": "string"},
                        "destination": {"type": "string"},
                        "departure_date": {"type": "string"},
                        "return_date": {"type": "string"},
                        "passengers": {"type": "integer"},
                        "results_count": {"type": "integer"}
                    }
                }
            },
            "required": ["outbound_flights", "search_metadata"]
        }
    
    async def execute(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        passengers: int,
        return_date: str = None,
        cabin_class: str = "economy",
        max_results: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """Search for flights by calling Java API"""
        try:
            if not self.validate_input({
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "passengers": passengers
            }):
                raise ValueError("Invalid input: origin, destination, departure_date, and passengers are required")
            
            app_logger.info(f"Executing {self.name}", origin=origin, destination=destination)
            
            # Call Java API to search flights
            trip_type = "roundtrip" if return_date else "oneway"
            result = await java_api_client.search_flights(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                passengers=passengers,
                return_date=return_date,
                cabin_class=cabin_class,
                trip_type=trip_type
            )
            
            # Transform Java API response to match skill output schema
            outbound_flights = result.get("outbound_flights", [])
            return_flights = result.get("return_flights", [])
            
            app_logger.info(f"Success: {self.name}", count=len(outbound_flights))
            
            return {
                "outbound_flights": outbound_flights,
                "return_flights": return_flights,
                "search_metadata": {
                    "origin": origin,
                    "destination": destination,
                    "departure_date": departure_date,
                    "return_date": return_date or "one-way",
                    "passengers": passengers,
                    "results_count": len(outbound_flights)
                }
            }
            
        except JavaAPIError as e:
            app_logger.error(f"API Error in {self.name}", exception=e)
            return {
                "outbound_flights": [],
                "return_flights": [],
                "search_metadata": {
                    "origin": origin,
                    "destination": destination,
                    "departure_date": departure_date,
                    "return_date": return_date or "one-way",
                    "passengers": passengers,
                    "results_count": 0
                },
                "error": e.to_dict()
            }
        except Exception as e:
            app_logger.error(f"Unexpected error in {self.name}", exception=e)
            return {
                "outbound_flights": [],
                "return_flights": [],
                "search_metadata": {
                    "origin": origin,
                    "destination": destination,
                    "departure_date": departure_date,
                    "return_date": return_date or "one-way",
                    "passengers": passengers,
                    "results_count": 0
                },
                "error": {"code": "INTERNAL_ERROR", "message": str(e)}
            }
