"""GetUserPreferencesSkill - Collect user travel preferences and requirements"""

from typing import Any, Dict
from ..base_skill import BaseSkill


class GetUserPreferencesSkill(BaseSkill):
    """Collect and structure user travel preferences from conversation context
    
    This skill extracts structured travel requirements from user input including
    destination preferences, dates, budget, group size, and travel interests.
    """
    
    name = "get_user_preferences"
    agent_type = "info_collection"
    description = "Collect user travel information including destination, dates, budget, group size, and preferences"
    version = "1.0.0"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "user_message": {
                    "type": "string",
                    "description": "The user's input message describing their travel needs"
                },
                "conversation_history": {
                    "type": "array",
                    "description": "Optional conversation history for context",
                    "items": {"type": "string"},
                    "default": []
                }
            },
            "required": ["user_message"]
        }
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "Desired destination or 'unspecified'"
                },
                "departure_date": {
                    "type": "string",
                    "description": "Departure date (YYYY-MM-DD format) or 'unspecified'"
                },
                "return_date": {
                    "type": "string",
                    "description": "Return date (YYYY-MM-DD format) or 'unspecified'"
                },
                "duration_days": {
                    "type": "integer",
                    "description": "Trip duration in days, or null if unspecified"
                },
                "budget": {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "number"},
                        "currency": {"type": "string"},
                        "range": {"type": "string"}
                    }
                },
                "group_size": {
                    "type": "integer",
                    "description": "Number of travelers"
                },
                "preferences": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Travel preferences (e.g., 'culture', 'food', 'nature', 'shopping')"
                },
                "special_requirements": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Special requirements (e.g., 'wheelchair accessible', 'vegetarian')"
                },
                "confidence": {
                    "type": "string",
                    "description": "Confidence level of extraction (high, medium, low)"
                },
                "missing_info": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of information that still needs to be collected"
                }
            },
            "required": ["destination", "confidence", "missing_info"]
        }
    
    async def execute(self, user_message: str, conversation_history: list = None, **kwargs) -> Dict[str, Any]:
        """Extract structured preferences from user message
        
        Args:
            user_message: User's input describing travel needs
            conversation_history: Optional previous conversation context
            
        Returns:
            Structured user preferences object
        """
        if not self.validate_input({"user_message": user_message}):
            raise ValueError("Invalid input: user_message is required")
        
        # Mock implementation - in production, this would use NLP/LLM to extract info
        # For demo, we'll do simple keyword matching
        message_lower = user_message.lower()
        
        preferences = []
        if any(word in message_lower for word in ["culture", "cultural", "history", "museum"]):
            preferences.append("culture")
        if any(word in message_lower for word in ["food", "cuisine", "restaurant", "dining"]):
            preferences.append("food")
        if any(word in message_lower for word in ["nature", "hiking", "mountain", "beach", "outdoor"]):
            preferences.append("nature")
        if any(word in message_lower for word in ["shopping", "market", "mall"]):
            preferences.append("shopping")
        if any(word in message_lower for word in ["adventure", "extreme", "sport"]):
            preferences.append("adventure")
        
        # Mock destination extraction
        destination = "unspecified"
        for city in ["tokyo", "paris", "bali", "new york", "london", "beijing", "shanghai"]:
            if city in message_lower:
                destination = city.title()
                break
        
        # Mock budget extraction
        budget = {"amount": None, "currency": "USD", "range": "unspecified"}
        if "budget" in message_lower:
            if "cheap" in message_lower or "budget" in message_lower:
                budget = {"amount": 1000, "currency": "USD", "range": "budget"}
            elif "luxury" in message_lower or "expensive" in message_lower:
                budget = {"amount": 5000, "currency": "USD", "range": "luxury"}
            else:
                budget = {"amount": 2500, "currency": "USD", "range": "moderate"}
        
        # Mock group size
        group_size = 1
        if "family" in message_lower:
            group_size = 4
        elif "couple" in message_lower or "two" in message_lower:
            group_size = 2
        
        # Determine missing info
        missing_info = []
        if destination == "unspecified":
            missing_info.append("destination")
        if "date" not in message_lower and "when" not in message_lower:
            missing_info.append("travel_dates")
        if budget["range"] == "unspecified":
            missing_info.append("budget")
        
        confidence = "high" if len(missing_info) == 0 else "medium" if len(missing_info) <= 2 else "low"
        
        return {
            "destination": destination,
            "departure_date": "unspecified",
            "return_date": "unspecified",
            "duration_days": None,
            "budget": budget,
            "group_size": group_size,
            "preferences": preferences if preferences else ["general"],
            "special_requirements": [],
            "confidence": confidence,
            "missing_info": missing_info
        }
