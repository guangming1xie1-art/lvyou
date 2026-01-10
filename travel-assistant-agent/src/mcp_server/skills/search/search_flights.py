"""SearchFlightsSkill - Search for available flights"""

from typing import Any, Dict, List
from datetime import datetime, timedelta
from ..base_skill import BaseSkill


class SearchFlightsSkill(BaseSkill):
    """Search for flights between two cities
    
    This skill queries available flights for a given route and date range,
    returning flight options with pricing and schedule information.
    """
    
    name = "search_flights"
    agent_type = "search"
    description = "Search and return available flights for given route and dates"
    version = "1.0.0"
    
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
        """Search for flights
        
        Args:
            origin: Departure location
            destination: Arrival location
            departure_date: Departure date
            passengers: Number of passengers
            return_date: Return date for round trip
            cabin_class: Cabin class preference
            max_results: Maximum results to return
            
        Returns:
            Flight search results
        """
        if not self.validate_input({
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "passengers": passengers
        }):
            raise ValueError("Invalid input: origin, destination, departure_date, and passengers are required")
        
        # Mock flight data
        airlines = [
            {"name": "SkyAir", "code": "SA"},
            {"name": "Global Wings", "code": "GW"},
            {"name": "Pacific Airlines", "code": "PA"},
            {"name": "EuroFly", "code": "EF"},
            {"name": "AsiaJet", "code": "AJ"}
        ]
        
        # Generate mock outbound flights
        outbound_flights = []
        base_price = 200 if cabin_class == "economy" else 500 if cabin_class == "premium_economy" else 1200 if cabin_class == "business" else 3000
        
        for i in range(min(max_results, 5)):
            airline = airlines[i % len(airlines)]
            dep_time = f"{8 + i * 2}:00"
            duration = 180 + i * 30  # 3-4.5 hours
            stops = 0 if i < 3 else 1
            price_variation = 1.0 + (i * 0.15)  # Price increases with later flights
            
            outbound_flights.append({
                "flight_id": f"FL-{airline['code']}-{i+1:03d}",
                "airline": airline["name"],
                "flight_number": f"{airline['code']}{100 + i}",
                "departure_time": dep_time,
                "arrival_time": f"{int(dep_time.split(':')[0]) + duration // 60}:{duration % 60:02d}",
                "duration_minutes": duration,
                "stops": stops,
                "price_per_person": round(base_price * price_variation, 2),
                "total_price": round(base_price * price_variation * passengers, 2),
                "currency": "USD",
                "available_seats": 15 - i * 2,
                "cabin_class": cabin_class
            })
        
        # Generate mock return flights if round trip
        return_flights = []
        if return_date:
            for i in range(min(max_results, 5)):
                airline = airlines[i % len(airlines)]
                dep_time = f"{9 + i * 2}:00"
                duration = 180 + i * 30
                stops = 0 if i < 3 else 1
                price_variation = 1.0 + (i * 0.12)
                
                return_flights.append({
                    "flight_id": f"FL-{airline['code']}-R-{i+1:03d}",
                    "airline": airline["name"],
                    "flight_number": f"{airline['code']}{200 + i}",
                    "departure_time": dep_time,
                    "arrival_time": f"{int(dep_time.split(':')[0]) + duration // 60}:{duration % 60:02d}",
                    "duration_minutes": duration,
                    "stops": stops,
                    "price_per_person": round(base_price * price_variation, 2),
                    "total_price": round(base_price * price_variation * passengers, 2),
                    "currency": "USD",
                    "available_seats": 12 - i * 2,
                    "cabin_class": cabin_class
                })
        
        return {
            "outbound_flights": outbound_flights,
            "return_flights": return_flights if return_date else [],
            "search_metadata": {
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "return_date": return_date or "one-way",
                "passengers": passengers,
                "results_count": len(outbound_flights)
            }
        }
