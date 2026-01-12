"""GetWeatherForecastSkill - Get weather forecast for travel dates"""

from typing import Any, Dict, List
from datetime import datetime, timedelta
from ..base_skill import BaseSkill
from src.utils.java_api_client import java_api_client, JavaAPIError
from src.utils.logger import app_logger


class GetWeatherForecastSkill(BaseSkill):
    """Get weather forecast for travel destination and dates

    This skill provides weather forecasts including temperature, conditions,
    and packing recommendations for the travel period.

    Version 2.0.0: Refactored to call Java API instead of local mock implementation.
    """

    name = "get_weather_forecast"
    agent_type = "recommendation"
    description = "Get weather forecast for destination and travel dates with packing recommendations"
    version = "2.0.0"
    
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
        """Get weather forecast by calling Java API

        Args:
            destination: Destination name
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (optional, YYYY-MM-DD)

        Returns:
            Weather forecast with recommendations
        """
        if not self.validate_input({"destination": destination, "start_date": start_date}):
            raise ValueError("Invalid input: destination and start_date are required")

        app_logger.info(f"GetWeatherForecastSkill: Fetching weather for {destination} from {start_date}")

        try:
            # Parse dates and calculate number of days
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else start + timedelta(days=3)
            except Exception:
                # Fallback to default values if date parsing fails
                start = datetime.now()
                end = start + timedelta(days=3)

            days = (end - start).days + 1

            # Call Java API to get weather forecast
            result = await java_api_client.get_weather_forecast(
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                days=days
            )

            forecast = result.get("forecast", [])

            app_logger.info(f"GetWeatherForecastSkill: Found {len(forecast)} days of forecast for {destination}")

            # Transform Java API response to match skill output schema
            # JavaAPIClient returns a list of daily forecasts
            daily_forecast = []
            conditions_count = {}
            total_high = 0
            total_low = 0
            rainy_days = 0

            for day_data in forecast:
                # Parse day_data from Java API response
                day_date_str = day_data.get("date", start_date)
                try:
                    day_date = datetime.strptime(day_date_str, "%Y-%m-%d")
                    day_of_week = day_date.strftime("%A")
                except:
                    day_of_week = "Unknown"

                condition = day_data.get("weather", day_data.get("condition", "Unknown"))
                conditions_count[condition] = conditions_count.get(condition, 0) + 1

                temp_high = day_data.get("temperature_high", day_data.get("temperature", 20))
                temp_low = day_data.get("temperature_low", temp_high - 10)

                precip_chance = day_data.get("precipitation_chance", day_data.get("humidity", 50))

                if "Rain" in condition or "Rain" in str(precip_chance):
                    rainy_days += 1

                total_high += temp_high
                total_low += temp_low

                daily_forecast.append({
                    "date": day_date_str,
                    "day_of_week": day_of_week,
                    "temperature_high": temp_high,
                    "temperature_low": temp_low,
                    "condition": condition,
                    "precipitation_chance": precip_chance,
                    "humidity": day_data.get("humidity", 60),
                    "wind_speed": day_data.get("wind_speed", 10)
                })

            # Calculate summary
            if daily_forecast:
                most_common_condition = max(conditions_count, key=conditions_count.get)
                avg_high = round(total_high / len(daily_forecast), 1)
                avg_low = round(total_low / len(daily_forecast), 1)
            else:
                most_common_condition = "Unknown"
                avg_high = 0
                avg_low = 0

            # Generate packing recommendations
            packing_recs = []
            if avg_high > 25:
                packing_recs.extend(["Light, breathable clothing", "Sunscreen", "Hat", "Sunglasses"])
            elif avg_high > 15:
                packing_recs.extend(["Light layers", "Comfortable walking shoes", "Light jacket for evenings"])
            else:
                packing_recs.extend(["Warm layers", "Jacket or coat", "Scarf and gloves"])

            if rainy_days > 0 or avg_high > 20:
                packing_recs.extend(["Umbrella", "Rain jacket"])

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

        except JavaAPIError as e:
            app_logger.error(f"GetWeatherForecastSkill: Java API error - {e}")
            return {
                "destination": destination,
                "forecast_period": {
                    "start_date": start_date,
                    "end_date": end_date or start_date,
                    "days": 1
                },
                "daily_forecast": [],
                "summary": {
                    "average_high": 0,
                    "average_low": 0,
                    "most_common_condition": "Unknown",
                    "rainy_days": 0
                },
                "packing_recommendations": [],
                "weather_alerts": [],
                "error": {
                    "code": "JAVA_API_ERROR",
                    "message": str(e),
                    "status_code": getattr(e, "status_code", None)
                }
            }
        except Exception as e:
            app_logger.error(f"GetWeatherForecastSkill: Unexpected error - {e}")
            return {
                "destination": destination,
                "forecast_period": {
                    "start_date": start_date,
                    "end_date": end_date or start_date,
                    "days": 1
                },
                "daily_forecast": [],
                "summary": {
                    "average_high": 0,
                    "average_low": 0,
                    "most_common_condition": "Unknown",
                    "rainy_days": 0
                },
                "packing_recommendations": [],
                "weather_alerts": [],
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }
