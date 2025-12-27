"""GetWeatherSkill - Check weather for destinations"""

from typing import Any, Dict, List
from .base_skill import BaseSkill


class GetWeatherSkill(BaseSkill):
    """Skill for checking weather forecasts for destinations"""
    
    name = "get_weather"
    description = "Get current weather and forecast for travel destinations to help with packing and planning"
    category = "weather"
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
                "start_date": {
                    "type": "string",
                    "description": "Start date of travel (YYYY-MM-DD)"
                },
                "end_date": {
                    "type": "string",
                    "description": "End date of travel (YYYY-MM-DD)"
                },
                "include_forecast": {
                    "type": "boolean",
                    "description": "Include daily forecast for travel dates",
                    "default": True
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
                "current": {
                    "type": "object",
                    "properties": {
                        "temperature": {"type": "number"},
                        "condition": {"type": "string"},
                        "humidity": {"type": "number"},
                        "wind_speed": {"type": "number"},
                        "uv_index": {"type": "number"}
                    }
                },
                "forecast": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string"},
                            "temperature_high": {"type": "number"},
                            "temperature_low": {"type": "number"},
                            "condition": {"type": "string"},
                            "precipitation_chance": {"type": "number"}
                        }
                    }
                },
                "packing_recommendations": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "best_activities": {
                    "type": "object",
                    "properties": {
                        "indoor": {"type": "array", "items": {"type": "string"}},
                        "outdoor": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "required": ["destination"]
        }
    
    async def execute(
        self,
        destination: str,
        start_date: str = None,
        end_date: str = None,
        include_forecast: bool = True
    ) -> Dict[str, Any]:
        """Execute weather check with mock data"""
        
        # Weather data by destination
        weather_data = {
            "tokyo": {
                "current": {
                    "temperature": 18,
                    "condition": "Partly Cloudy",
                    "humidity": 65,
                    "wind_speed": 12,
                    "uv_index": 5
                },
                "packing_recommendations": [
                    "Light layers",
                    "Compact umbrella (rainy season: Jun-Jul)",
                    "Comfortable walking shoes",
                    "Light jacket for evenings"
                ],
                "best_activities": {
                    "indoor": ["Museums", "Shopping malls", "Temples", "Anime districts"],
                    "outdoor": ["Cherry blossom viewing (Mar-Apr)", "Parks", "Rooftop bars"]
                }
            },
            "paris": {
                "current": {
                    "temperature": 15,
                    "condition": "Sunny",
                    "humidity": 55,
                    "wind_speed": 8,
                    "uv_index": 4
                },
                "packing_recommendations": [
                    "Light sweaters",
                    "Elegant casual wear for dining",
                    "Comfortable shoes for cobblestones",
                    "Light rain jacket",
                    "Adapter for European outlets"
                ],
                "best_activities": {
                    "indoor": ["Louvre", "Musée d'Orsay", "Cafés", "Wine bars"],
                    "outdoor": ["Seine walks", "Jardin du Luxembourg", "Montmartre"]
                }
            },
            "bali": {
                "current": {
                    "temperature": 29,
                    "condition": "Sunny",
                    "humidity": 80,
                    "wind_speed": 10,
                    "uv_index": 9
                },
                "packing_recommendations": [
                    "Light, breathable clothing",
                    "Swimwear",
                    "Sunscreen (high SPF)",
                    "Insect repellent",
                    "Raincoat (wet season: Nov-Mar)",
                    "Modest clothing for temples"
                ],
                "best_activities": {
                    "indoor": ["Spa treatments", "Cooking classes", "Temple visits"],
                    "outdoor": ["Beach", "Surfing", "Rice terrace treks", "Waterfalls"]
                }
            }
        }
        
        dest_lower = destination.lower().strip()
        result = weather_data.get(dest_lower, {
            "current": {
                "temperature": 22,
                "condition": "Clear",
                "humidity": 60,
                "wind_speed": 10,
                "uv_index": 6
            },
            "packing_recommendations": [
                "Check local weather before packing",
                "Bring comfortable walking shoes",
                "Pack layers"
            ],
            "best_activities": {
                "indoor": ["Local museums", "Markets"],
                "outdoor": ["Explore local parks", "Walking tours"]
            }
        })
        
        # Add destination name
        result["destination"] = destination
        
        # Generate forecast if requested
        if include_forecast:
            forecast = []
            num_days = 7  # Default forecast days
            
            if start_date and end_date:
                try:
                    from datetime import datetime, timedelta
                    start = datetime.strptime(start_date, "%Y-%m-%d")
                    end = datetime.strptime(end_date, "%Y-%m-%d")
                    num_days = min((end - start).days + 1, 14)  # Max 14 days
                except:
                    pass
            
            conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Light Rain", "Clear"]
            
            for i in range(num_days):
                date_str = f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}"  # Mock dates
                condition = conditions[i % len(conditions)]
                
                temp_base = result["current"]["temperature"]
                forecast.append({
                    "date": date_str,
                    "temperature_high": temp_base + (i % 5),
                    "temperature_low": temp_base - (5 - i % 5),
                    "condition": condition,
                    "precipitation_chance": 20 if "Rain" in condition else 10
                })
            
            result["forecast"] = forecast
        
        return result
