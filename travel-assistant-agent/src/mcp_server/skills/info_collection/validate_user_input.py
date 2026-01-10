"""ValidateUserInputSkill - Validate and normalize user input data"""

from typing import Any, Dict
from datetime import datetime
from ..base_skill import BaseSkill


class ValidateUserInputSkill(BaseSkill):
    """Validate and normalize raw user input data
    
    This skill ensures that collected user preferences are valid, consistent,
    and properly formatted for downstream processing.
    """
    
    name = "validate_user_input"
    agent_type = "info_collection"
    description = "Validate and normalize user input data for travel preferences"
    version = "1.0.0"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "user_preferences": {
                    "type": "object",
                    "description": "Raw user preferences object to validate"
                }
            },
            "required": ["user_preferences"]
        }
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "is_valid": {
                    "type": "boolean",
                    "description": "Whether the input is valid"
                },
                "validated_data": {
                    "type": "object",
                    "description": "Normalized and validated data"
                },
                "validation_errors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of validation errors if any"
                },
                "validation_warnings": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of validation warnings"
                },
                "suggestions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Suggestions for incomplete or invalid fields"
                }
            },
            "required": ["is_valid", "validated_data", "validation_errors"]
        }
    
    async def execute(self, user_preferences: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Validate user preferences
        
        Args:
            user_preferences: Raw user preferences object
            
        Returns:
            Validation result with normalized data
        """
        if not self.validate_input({"user_preferences": user_preferences}):
            raise ValueError("Invalid input: user_preferences is required")
        
        errors = []
        warnings = []
        suggestions = []
        validated_data = user_preferences.copy()
        
        # Validate destination
        if not user_preferences.get("destination") or user_preferences["destination"] == "unspecified":
            errors.append("Destination is required")
            suggestions.append("Please specify your desired destination")
        
        # Validate dates
        departure_date = user_preferences.get("departure_date")
        return_date = user_preferences.get("return_date")
        
        if departure_date and departure_date != "unspecified":
            try:
                dep_date = datetime.strptime(departure_date, "%Y-%m-%d")
                if dep_date < datetime.now():
                    warnings.append("Departure date is in the past")
                    suggestions.append("Consider updating the departure date to a future date")
            except ValueError:
                errors.append("Invalid departure date format (expected YYYY-MM-DD)")
        else:
            warnings.append("Departure date not specified")
            suggestions.append("Specify your preferred departure date")
        
        if return_date and return_date != "unspecified" and departure_date and departure_date != "unspecified":
            try:
                ret_date = datetime.strptime(return_date, "%Y-%m-%d")
                dep_date = datetime.strptime(departure_date, "%Y-%m-%d")
                if ret_date <= dep_date:
                    errors.append("Return date must be after departure date")
            except ValueError:
                errors.append("Invalid return date format (expected YYYY-MM-DD)")
        
        # Validate budget
        budget = user_preferences.get("budget", {})
        if not budget.get("amount") and budget.get("range") == "unspecified":
            warnings.append("Budget not specified")
            suggestions.append("Specify your budget range for better recommendations")
        elif budget.get("amount") and budget["amount"] < 0:
            errors.append("Budget amount cannot be negative")
        
        # Validate group size
        group_size = user_preferences.get("group_size", 1)
        if group_size < 1:
            errors.append("Group size must be at least 1")
        elif group_size > 20:
            warnings.append("Large group size may require special arrangements")
            
        # Normalize group size
        validated_data["group_size"] = max(1, group_size)
        
        # Validate preferences
        preferences = user_preferences.get("preferences", [])
        if not preferences or len(preferences) == 0:
            warnings.append("No travel preferences specified")
            suggestions.append("Specify your interests (e.g., culture, food, nature) for personalized recommendations")
        
        # Determine overall validity
        is_valid = len(errors) == 0
        
        return {
            "is_valid": is_valid,
            "validated_data": validated_data,
            "validation_errors": errors,
            "validation_warnings": warnings,
            "suggestions": suggestions
        }
