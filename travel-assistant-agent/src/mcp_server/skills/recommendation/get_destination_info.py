"""GetDestinationInfoSkill - Fetch general destination information"""

from typing import Any, Dict
from ..base_skill import BaseSkill
from src.utils.java_api_client import java_api_client, JavaAPIError
from src.utils.logger import app_logger


class GetDestinationInfoSkill(BaseSkill):
    """Get general information about a travel destination

    This skill provides comprehensive destination information including
    description, currency, language, visa requirements, and travel tips.

    Version 2.0.0: Refactored to call Java API instead of local mock implementation.
    """

    name = "get_destination_info"
    agent_type = "recommendation"
    description = "Fetch general destination information including description, currency, language, and visa requirements"
    version = "2.0.0"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "Name of the destination (city, country, or region)"
                },
                "language": {
                    "type": "string",
                    "description": "Preferred language for information",
                    "default": "en"
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
                "country": {"type": "string"},
                "region": {"type": "string"},
                "description": {"type": "string"},
                "best_time_to_visit": {"type": "string"},
                "average_duration": {"type": "string"},
                "currency": {"type": "string"},
                "language": {"type": "string"},
                "visa_info": {"type": "string"},
                "local_tips": {"type": "array", "items": {"type": "string"}},
                "timezone": {"type": "string"},
                "emergency_number": {"type": "string"}
            },
            "required": ["destination", "country", "description"]
        }
    
    async def execute(self, destination: str, language: str = "en", **kwargs) -> Dict[str, Any]:
        """Get destination information by calling Java API

        Args:
            destination: Destination name
            language: Preferred language (passed to Java API for localization)

        Returns:
            Comprehensive destination information
        """
        if not self.validate_input({"destination": destination}):
            raise ValueError("Invalid input: destination is required")

        app_logger.info(f"GetDestinationInfoSkill: Fetching destination info for {destination}")

        try:
            # Call Java API to get destination info
            result = await java_api_client.get_destination_info(destination=destination)

            app_logger.info(f"GetDestinationInfoSkill: Successfully fetched info for {destination}")

            # Transform Java API response to match skill output schema
            # JavaAPIClient returns: {"destination": ..., "info": {...}}
            # We need to flatten the structure
            api_info = result.get("info", {})

            # If Java API returns data in expected format, return it
            if "country" in api_info or "description" in api_info:
                return {
                    "destination": api_info.get("name") or api_info.get("destination") or destination,
                    "country": api_info.get("country", "Unknown"),
                    "region": api_info.get("region", "Unknown"),
                    "description": api_info.get("description", ""),
                    "best_time_to_visit": api_info.get("best_season", api_info.get("best_time_to_visit", "")),
                    "average_duration": api_info.get("average_duration", ""),
                    "currency": api_info.get("currency", ""),
                    "language": api_info.get("language", ""),
                    "visa_info": api_info.get("visa_info", ""),
                    "local_tips": api_info.get("local_tips", api_info.get("highlights", [])),
                    "timezone": api_info.get("time_zone", api_info.get("timezone", "")),
                    "emergency_number": api_info.get("emergency_number", "")
                }

            # Fallback: return as-is if format doesn't match expected structure
            return api_info

        except JavaAPIError as e:
            app_logger.error(f"GetDestinationInfoSkill: Java API error - {e}")
            return {
                "destination": destination,
                "country": "Unknown",
                "region": "Unknown",
                "description": f"Unable to fetch information for {destination}",
                "best_time_to_visit": "",
                "average_duration": "",
                "currency": "",
                "language": "",
                "visa_info": "",
                "local_tips": [],
                "timezone": "",
                "emergency_number": "",
                "error": {
                    "code": "JAVA_API_ERROR",
                    "message": str(e),
                    "status_code": getattr(e, "status_code", None)
                }
            }
        except Exception as e:
            app_logger.error(f"GetDestinationInfoSkill: Unexpected error - {e}")
            return {
                "destination": destination,
                "country": "Unknown",
                "region": "Unknown",
                "description": f"Error fetching information for {destination}",
                "best_time_to_visit": "",
                "average_duration": "",
                "currency": "",
                "language": "",
                "visa_info": "",
                "local_tips": [],
                "timezone": "",
                "emergency_number": "",
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }
