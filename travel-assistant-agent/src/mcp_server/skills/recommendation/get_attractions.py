"""GetAttractionsSkill - Get popular attractions and activities"""

from typing import Any, Dict, List
from ..base_skill import BaseSkill
from src.utils.java_api_client import java_api_client, JavaAPIError
from src.utils.logger import app_logger


class GetAttractionsSkill(BaseSkill):
    """Get popular attractions and activities at a destination

    This skill provides a list of must-see attractions, activities,
    and experiences at a given destination.

    Version 2.0.0: Refactored to call Java API instead of local mock implementation.
    """

    name = "get_attractions"
    agent_type = "recommendation"
    description = "Get popular attractions, activities, and experiences at a destination"
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
                "category": {
                    "type": "string",
                    "description": "Filter by category",
                    "enum": ["all", "culture", "nature", "food", "entertainment", "adventure"],
                    "default": "all"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 10
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
                "attractions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "category": {"type": "string"},
                            "description": {"type": "string"},
                            "rating": {"type": "number"},
                            "estimated_duration": {"type": "string"},
                            "best_time_to_visit": {"type": "string"},
                            "entrance_fee": {"type": "string"},
                            "must_see": {"type": "boolean"}
                        }
                    }
                },
                "total_count": {"type": "integer"}
            },
            "required": ["destination", "attractions", "total_count"]
        }
    
    async def execute(
        self,
        destination: str,
        category: str = "all",
        max_results: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """Get attractions for destination by calling Java API

        Args:
            destination: Destination name
            category: Filter by category (all, culture, nature, food, entertainment, adventure)
            max_results: Maximum results

        Returns:
            List of attractions and activities
        """
        if not self.validate_input({"destination": destination}):
            raise ValueError("Invalid input: destination is required")

        app_logger.info(f"GetAttractionsSkill: Fetching attractions for {destination} (category: {category})")

        try:
            # Call Java API to get attractions
            result = await java_api_client.get_attractions(
                destination=destination,
                category=category if category != "all" else None,
                sort_by="rating"
            )

            attractions = result.get("attractions", [])

            app_logger.info(f"GetAttractionsSkill: Found {len(attractions)} attractions in {destination}")

            # Transform Java API response to match skill output schema
            # JavaAPIClient returns attractions with fields like: attraction_id, name, category, rating, etc.
            # Skill output schema expects: name, category, description, rating, estimated_duration, best_time_to_visit, entrance_fee, must_see
            transformed_attractions = []
            for attraction in attractions[:max_results]:
                transformed = {
                    "name": attraction.get("name", ""),
                    "category": attraction.get("category", "culture"),
                    "description": attraction.get("description", ""),
                    "rating": attraction.get("rating", 0.0),
                    "estimated_duration": f"{attraction.get('duration_hours', 2)} hours",
                    "best_time_to_visit": attraction.get("opening_hours", "Anytime"),
                    "entrance_fee": f"${attraction.get('ticket_price', 0)}" if attraction.get("ticket_price", 0) > 0 else "Free",
                    "must_see": attraction.get("rating", 0) >= 4.5  # Mark high-rated attractions as must-see
                }
                transformed_attractions.append(transformed)

            return {
                "destination": destination,
                "attractions": transformed_attractions,
                "total_count": len(transformed_attractions)
            }

        except JavaAPIError as e:
            app_logger.error(f"GetAttractionsSkill: Java API error - {e}")
            return {
                "destination": destination,
                "attractions": [],
                "total_count": 0,
                "error": {
                    "code": "JAVA_API_ERROR",
                    "message": str(e),
                    "status_code": getattr(e, "status_code", None)
                }
            }
        except Exception as e:
            app_logger.error(f"GetAttractionsSkill: Unexpected error - {e}")
            return {
                "destination": destination,
                "attractions": [],
                "total_count": 0,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }
