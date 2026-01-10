"""GetAttractionsSkill - Get popular attractions and activities"""

from typing import Any, Dict, List
from ..base_skill import BaseSkill


class GetAttractionsSkill(BaseSkill):
    """Get popular attractions and activities at a destination
    
    This skill provides a list of must-see attractions, activities,
    and experiences at a given destination.
    """
    
    name = "get_attractions"
    agent_type = "recommendation"
    description = "Get popular attractions, activities, and experiences at a destination"
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
        """Get attractions for destination
        
        Args:
            destination: Destination name
            category: Filter by category
            max_results: Maximum results
            
        Returns:
            List of attractions and activities
        """
        if not self.validate_input({"destination": destination}):
            raise ValueError("Invalid input: destination is required")
        
        # Mock attractions database
        mock_attractions = {
            "tokyo": [
                {
                    "name": "Senso-ji Temple",
                    "category": "culture",
                    "description": "Tokyo's oldest temple with vibrant atmosphere",
                    "rating": 4.5,
                    "estimated_duration": "1-2 hours",
                    "best_time_to_visit": "Early morning to avoid crowds",
                    "entrance_fee": "Free",
                    "must_see": True
                },
                {
                    "name": "Shibuya Crossing",
                    "category": "entertainment",
                    "description": "World's busiest pedestrian crossing",
                    "rating": 4.3,
                    "estimated_duration": "30 minutes",
                    "best_time_to_visit": "Evening for full effect",
                    "entrance_fee": "Free",
                    "must_see": True
                },
                {
                    "name": "Tsukiji Outer Market",
                    "category": "food",
                    "description": "Fresh seafood and street food paradise",
                    "rating": 4.6,
                    "estimated_duration": "2-3 hours",
                    "best_time_to_visit": "Morning (6-10 AM)",
                    "entrance_fee": "Free",
                    "must_see": True
                },
                {
                    "name": "Tokyo Skytree",
                    "category": "entertainment",
                    "description": "Tallest structure in Japan with observation decks",
                    "rating": 4.4,
                    "estimated_duration": "2 hours",
                    "best_time_to_visit": "Sunset",
                    "entrance_fee": "$25-35",
                    "must_see": False
                },
                {
                    "name": "Meiji Shrine",
                    "category": "culture",
                    "description": "Peaceful shrine in a forested area",
                    "rating": 4.5,
                    "estimated_duration": "1 hour",
                    "best_time_to_visit": "Morning",
                    "entrance_fee": "Free",
                    "must_see": True
                }
            ],
            "paris": [
                {
                    "name": "Eiffel Tower",
                    "category": "culture",
                    "description": "Iconic iron tower and Paris symbol",
                    "rating": 4.7,
                    "estimated_duration": "2-3 hours",
                    "best_time_to_visit": "Sunset",
                    "entrance_fee": "$15-30",
                    "must_see": True
                },
                {
                    "name": "Louvre Museum",
                    "category": "culture",
                    "description": "World's largest art museum",
                    "rating": 4.8,
                    "estimated_duration": "3-4 hours",
                    "best_time_to_visit": "Weekday mornings",
                    "entrance_fee": "$17",
                    "must_see": True
                },
                {
                    "name": "Seine River Cruise",
                    "category": "entertainment",
                    "description": "Scenic boat tour past major landmarks",
                    "rating": 4.5,
                    "estimated_duration": "1 hour",
                    "best_time_to_visit": "Evening",
                    "entrance_fee": "$15-25",
                    "must_see": False
                },
                {
                    "name": "Montmartre & Sacré-Cœur",
                    "category": "culture",
                    "description": "Charming hilltop neighborhood with basilica",
                    "rating": 4.6,
                    "estimated_duration": "2-3 hours",
                    "best_time_to_visit": "Morning or late afternoon",
                    "entrance_fee": "Free (basilica)",
                    "must_see": True
                }
            ],
            "bali": [
                {
                    "name": "Uluwatu Temple",
                    "category": "culture",
                    "description": "Clifftop temple with sunset Kecak dance",
                    "rating": 4.7,
                    "estimated_duration": "2-3 hours",
                    "best_time_to_visit": "Sunset",
                    "entrance_fee": "$3-5",
                    "must_see": True
                },
                {
                    "name": "Tegallalang Rice Terraces",
                    "category": "nature",
                    "description": "Stunning rice paddies with jungle swing",
                    "rating": 4.5,
                    "estimated_duration": "2 hours",
                    "best_time_to_visit": "Morning",
                    "entrance_fee": "$1-2",
                    "must_see": True
                },
                {
                    "name": "Sacred Monkey Forest",
                    "category": "nature",
                    "description": "Forest sanctuary with playful monkeys",
                    "rating": 4.4,
                    "estimated_duration": "1-2 hours",
                    "best_time_to_visit": "Morning",
                    "entrance_fee": "$5",
                    "must_see": False
                },
                {
                    "name": "Mount Batur Sunrise Trek",
                    "category": "adventure",
                    "description": "Volcano hike to watch sunrise",
                    "rating": 4.8,
                    "estimated_duration": "5-6 hours",
                    "best_time_to_visit": "Predawn start",
                    "entrance_fee": "$35-50 (guided)",
                    "must_see": True
                }
            ]
        }
        
        # Get attractions for destination
        dest_lower = destination.lower().strip()
        attractions = mock_attractions.get(dest_lower, [])
        
        # If not found, try partial match
        if not attractions:
            for key, value in mock_attractions.items():
                if dest_lower in key or key in dest_lower:
                    attractions = value
                    break
        
        # Default attractions if not found
        if not attractions:
            attractions = [
                {
                    "name": "Main City Square",
                    "category": "culture",
                    "description": "Central gathering place with local flavor",
                    "rating": 4.0,
                    "estimated_duration": "1 hour",
                    "best_time_to_visit": "Anytime",
                    "entrance_fee": "Free",
                    "must_see": True
                },
                {
                    "name": "Local Market",
                    "category": "food",
                    "description": "Traditional market with local products",
                    "rating": 4.2,
                    "estimated_duration": "1-2 hours",
                    "best_time_to_visit": "Morning",
                    "entrance_fee": "Free",
                    "must_see": False
                }
            ]
        
        # Filter by category
        if category != "all":
            attractions = [a for a in attractions if a["category"] == category]
        
        # Limit results
        attractions = attractions[:max_results]
        
        return {
            "destination": destination,
            "attractions": attractions,
            "total_count": len(attractions)
        }
