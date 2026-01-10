"""SuggestDestinationsSkill - Suggest popular destinations based on preferences"""

from typing import Any, Dict, List
from ..base_skill import BaseSkill


class SuggestDestinationsSkill(BaseSkill):
    """Suggest travel destinations based on user preferences
    
    This skill recommends popular destinations that match the user's
    travel preferences, budget, and interests.
    """
    
    name = "suggest_destinations"
    agent_type = "info_collection"
    description = "Suggest popular destinations based on user preferences and constraints"
    version = "1.0.0"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "preferences": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "User's travel preferences (e.g., 'culture', 'nature', 'food')"
                },
                "budget_range": {
                    "type": "string",
                    "description": "Budget range: 'budget', 'moderate', or 'luxury'",
                    "enum": ["budget", "moderate", "luxury"]
                },
                "duration_days": {
                    "type": "integer",
                    "description": "Preferred trip duration in days"
                },
                "season": {
                    "type": "string",
                    "description": "Preferred travel season",
                    "enum": ["spring", "summer", "autumn", "winter", "any"]
                },
                "max_suggestions": {
                    "type": "integer",
                    "description": "Maximum number of suggestions to return",
                    "default": 5
                }
            },
            "required": ["preferences"]
        }
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "suggestions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "destination": {"type": "string"},
                            "country": {"type": "string"},
                            "match_score": {"type": "number"},
                            "matched_preferences": {"type": "array", "items": {"type": "string"}},
                            "short_description": {"type": "string"},
                            "estimated_budget": {"type": "string"},
                            "best_season": {"type": "string"},
                            "highlights": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                },
                "total_matches": {"type": "integer"}
            },
            "required": ["suggestions", "total_matches"]
        }
    
    async def execute(
        self,
        preferences: List[str],
        budget_range: str = "moderate",
        duration_days: int = None,
        season: str = "any",
        max_suggestions: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """Suggest destinations based on preferences
        
        Args:
            preferences: List of user preferences
            budget_range: Budget category
            duration_days: Preferred duration
            season: Preferred season
            max_suggestions: Max number to return
            
        Returns:
            List of destination suggestions with match scores
        """
        if not self.validate_input({"preferences": preferences}):
            raise ValueError("Invalid input: preferences are required")
        
        # Mock destination database with preferences tags
        destinations_db = [
            {
                "destination": "Tokyo",
                "country": "Japan",
                "tags": ["culture", "food", "shopping", "adventure"],
                "budget": "moderate",
                "best_season": "spring",
                "description": "A vibrant blend of tradition and modernity",
                "highlights": ["Temples", "Sushi", "Technology", "Cherry Blossoms"],
                "estimated_budget": "$2000-3500"
            },
            {
                "destination": "Paris",
                "country": "France",
                "tags": ["culture", "food", "shopping", "romance"],
                "budget": "luxury",
                "best_season": "spring",
                "description": "The city of light and romance",
                "highlights": ["Eiffel Tower", "Louvre", "French Cuisine", "Fashion"],
                "estimated_budget": "$3000-5000"
            },
            {
                "destination": "Bali",
                "country": "Indonesia",
                "tags": ["nature", "culture", "beach", "wellness"],
                "budget": "budget",
                "best_season": "summer",
                "description": "Tropical paradise with spiritual culture",
                "highlights": ["Beaches", "Temples", "Rice Terraces", "Yoga"],
                "estimated_budget": "$1000-2000"
            },
            {
                "destination": "Barcelona",
                "country": "Spain",
                "tags": ["culture", "food", "beach", "architecture"],
                "budget": "moderate",
                "best_season": "summer",
                "description": "Mediterranean charm with stunning architecture",
                "highlights": ["Sagrada Familia", "Tapas", "Beach", "Gaudi"],
                "estimated_budget": "$2000-3500"
            },
            {
                "destination": "Iceland",
                "country": "Iceland",
                "tags": ["nature", "adventure", "photography"],
                "budget": "luxury",
                "best_season": "winter",
                "description": "Land of fire and ice with dramatic landscapes",
                "highlights": ["Northern Lights", "Waterfalls", "Glaciers", "Hot Springs"],
                "estimated_budget": "$3500-5500"
            },
            {
                "destination": "Thailand",
                "country": "Thailand",
                "tags": ["food", "culture", "beach", "budget"],
                "budget": "budget",
                "best_season": "winter",
                "description": "Affordable paradise with rich culture",
                "highlights": ["Street Food", "Temples", "Islands", "Markets"],
                "estimated_budget": "$800-1500"
            },
            {
                "destination": "New York",
                "country": "USA",
                "tags": ["culture", "shopping", "food", "entertainment"],
                "budget": "luxury",
                "best_season": "autumn",
                "description": "The city that never sleeps",
                "highlights": ["Broadway", "Museums", "Shopping", "Diverse Cuisine"],
                "estimated_budget": "$3000-5000"
            },
            {
                "destination": "New Zealand",
                "country": "New Zealand",
                "tags": ["nature", "adventure", "photography", "outdoor"],
                "budget": "moderate",
                "best_season": "summer",
                "description": "Breathtaking landscapes and outdoor adventures",
                "highlights": ["Mountains", "Hiking", "Lord of the Rings Sites", "Wildlife"],
                "estimated_budget": "$2500-4000"
            }
        ]
        
        # Calculate match scores
        suggestions = []
        for dest in destinations_db:
            # Calculate preference match
            matched_prefs = [pref for pref in preferences if pref.lower() in dest["tags"]]
            match_score = len(matched_prefs) / max(len(preferences), 1)
            
            # Adjust score based on budget match
            if dest["budget"] == budget_range:
                match_score += 0.2
            
            # Adjust score based on season match
            if season != "any" and dest["best_season"] == season:
                match_score += 0.1
            
            if match_score > 0:
                suggestions.append({
                    "destination": dest["destination"],
                    "country": dest["country"],
                    "match_score": round(min(match_score, 1.0), 2),
                    "matched_preferences": matched_prefs,
                    "short_description": dest["description"],
                    "estimated_budget": dest["estimated_budget"],
                    "best_season": dest["best_season"],
                    "highlights": dest["highlights"]
                })
        
        # Sort by match score
        suggestions.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Limit results
        suggestions = suggestions[:max_suggestions]
        
        return {
            "suggestions": suggestions,
            "total_matches": len(suggestions)
        }
