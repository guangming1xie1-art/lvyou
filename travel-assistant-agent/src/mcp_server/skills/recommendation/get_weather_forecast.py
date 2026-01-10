"""GetWeatherForecastSkill - Get weather forecast for travel dates"""

from typing import Any, Dict, List
from datetime import datetime, timedelta
from ..base_skill import BaseSkill


class GetWeatherForecastSkill(BaseSkill):
    """Get weather forecast for travel destination and dates
    
    This skill provides weather forecasts including temperature, conditions,
    and packing recommendations for the travel period.
    """
    
    name = "get_weather_forecast"
    agent_type = "recommendation"
    description = "Get weather forecast for destination and travel dates with packing recommendations"
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
                }
            },
            "required": ["destination", "start_date"]
        }
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "destination": {"type": "string"},
                "forecast_period": {
                    "type": "object",
                    "properties": {
                        "start_date": {"type": "string"},
                        "end_date": {"type": "string"},
                        "days": {"type": "integer"}
                    }
                },
                "daily_forecast": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string"},
                            "day_of_week": {"type": "string"},
                            "temperature_high": {"type": "number"},
                            "temperature_low": {"type": "number"},
                            "condition": {"type": "string"},
                            "precipitation_chance": {"type": "number"},
                            "humidity": {"type": "number"},
                            "wind_speed": {"type": "number"}
                        }
                    }
                },
                "summary": {
                    "type": "object",
                    "properties": {
                        "average_high": {"type": "number"},
                        "average_low": {"type": "number"},
                        "most_common_condition": {"type": "string"},
                        "rainy_days": {"type": "integer"}
                    }
                },
                "packing_recommendations": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "weather_alerts": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["destination", "daily_forecast", "packing_recommendations"]
        }
    
    async def execute(
        self,
        destination: str,
        start_date: str,
        end_date: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Get weather forecast
        
        Args:
            destination: Destination name
            start_date: Start date
            end_date: End date (optional)
            
        Returns:
            Weather forecast with recommendations
        """
        if not self.validate_input({"destination": destination, "start_date": start_date}):
            raise ValueError("Invalid input: destination and start_date are required")
        
        # Mock weather patterns by destination
        weather_patterns = {
            "tokyo": {
                "base_temp_high": 22,
                "base_temp_low": 15,
                "conditions": ["Sunny", "Partly Cloudy", "Cloudy", "Light Rain"],
                "condition_weights": [0.4, 0.3, 0.2, 0.1],
                "rain_chance": 0.3
            },
            "paris": {
                "base_temp_high": 18,
                "base_temp_low": 11,
                "conditions": ["Cloudy", "Partly Cloudy", "Light Rain", "Sunny"],
                "condition_weights": [0.4, 0.3, 0.2, 0.1],
                "rain_chance": 0.4
            },
            "bali": {
                "base_temp_high": 30,
                "base_temp_low": 24,
                "conditions": ["Sunny", "Partly Cloudy", "Scattered Showers", "Thunderstorm"],
                "condition_weights": [0.5, 0.3, 0.15, 0.05],
                "rain_chance": 0.2
            },
            "new york": {
                "base_temp_high": 15,
                "base_temp_low": 8,
                "conditions": ["Sunny", "Cloudy", "Windy", "Rain"],
                "condition_weights": [0.35, 0.35, 0.2, 0.1],
                "rain_chance": 0.3
            }
        }
        
        # Get pattern or use default
        dest_lower = destination.lower().strip()
        pattern = weather_patterns.get(dest_lower, {
            "base_temp_high": 20,
            "base_temp_low": 12,
            "conditions": ["Sunny", "Cloudy", "Partly Cloudy"],
            "condition_weights": [0.4, 0.3, 0.3],
            "rain_chance": 0.25
        })
        
        # Parse dates
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else start + timedelta(days=3)
        except:
            start = datetime.now()
            end = start + timedelta(days=3)
        
        days = (end - start).days + 1
        
        # Generate daily forecast
        daily_forecast = []
        conditions_count = {}
        total_high = 0
        total_low = 0
        rainy_days = 0
        
        for i in range(days):
            date = start + timedelta(days=i)
            
            # Vary temperature slightly
            temp_high = pattern["base_temp_high"] + (i % 3) - 1
            temp_low = pattern["base_temp_low"] + (i % 3) - 1
            
            # Select condition (simplified random selection)
            condition = pattern["conditions"][i % len(pattern["conditions"])]
            conditions_count[condition] = conditions_count.get(condition, 0) + 1
            
            # Precipitation chance
            precip_chance = pattern["rain_chance"] * 100
            if "Rain" in condition or "Thunderstorm" in condition:
                precip_chance = min(80, precip_chance * 2)
                rainy_days += 1
            
            daily_forecast.append({
                "date": date.strftime("%Y-%m-%d"),
                "day_of_week": date.strftime("%A"),
                "temperature_high": temp_high,
                "temperature_low": temp_low,
                "condition": condition,
                "precipitation_chance": precip_chance,
                "humidity": 60 + (i % 20),
                "wind_speed": 10 + (i % 15)
            })
            
            total_high += temp_high
            total_low += temp_low
        
        # Calculate summary
        most_common_condition = max(conditions_count, key=conditions_count.get)
        avg_high = round(total_high / days, 1)
        avg_low = round(total_low / days, 1)
        
        # Generate packing recommendations
        packing_recs = []
        if avg_high > 25:
            packing_recs.extend(["Light, breathable clothing", "Sunscreen", "Hat", "Sunglasses"])
        elif avg_high > 15:
            packing_recs.extend(["Light layers", "Comfortable walking shoes", "Light jacket for evenings"])
        else:
            packing_recs.extend(["Warm layers", "Jacket or coat", "Scarf and gloves"])
        
        if rainy_days > 0 or pattern["rain_chance"] > 0.3:
            packing_recs.extend(["Umbrella", "Rain jacket", "Waterproof shoes"])
        
        # Weather alerts
        alerts = []
        if rainy_days >= days * 0.5:
            alerts.append("Expect frequent rain - plan indoor activities")
        if avg_high > 30:
            alerts.append("High temperatures - stay hydrated")
        if avg_low < 5:
            alerts.append("Cold temperatures - pack warm clothing")
        
        return {
            "destination": destination,
            "forecast_period": {
                "start_date": start_date,
                "end_date": end.strftime("%Y-%m-%d"),
                "days": days
            },
            "daily_forecast": daily_forecast,
            "summary": {
                "average_high": avg_high,
                "average_low": avg_low,
                "most_common_condition": most_common_condition,
                "rainy_days": rainy_days
            },
            "packing_recommendations": packing_recs,
            "weather_alerts": alerts
        }
