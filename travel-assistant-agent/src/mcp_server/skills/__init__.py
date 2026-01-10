"""Skills module for MCP Server

This module exports all available skills organized by agent type.
Each skill is an independent tool unit that belongs to a specific agent.
"""

from typing import Dict, List
from .base_skill import BaseSkill

# Import all skills by agent type
from .info_collection import (
    GetUserPreferencesSkill,
    ValidateUserInputSkill,
    SuggestDestinationsSkill,
)
from .search import (
    SearchFlightsSkill,
    SearchHotelsSkill,
    CompareResultsSkill,
    FilterByBudgetSkill,
)
from .recommendation import (
    GetDestinationInfoSkill,
    GetAttractionsSkill,
    GetWeatherForecastSkill,
    GetDestinationReviewsSkill,
)
from .booking import (
    CreateBookingSkill,
    ProcessPaymentSkill,
    ConfirmBookingSkill,
    GetBookingStatusSkill,
)


# Legacy support - will be deprecated
# Use SkillRegistry instead
SKILL_REGISTRY: Dict[str, BaseSkill] = {}


def _init_legacy_registry():
    """Initialize legacy registry for backward compatibility"""
    global SKILL_REGISTRY
    
    # Info Collection Skills
    SKILL_REGISTRY["get_user_preferences"] = GetUserPreferencesSkill()
    SKILL_REGISTRY["validate_user_input"] = ValidateUserInputSkill()
    SKILL_REGISTRY["suggest_destinations"] = SuggestDestinationsSkill()
    
    # Search Skills
    SKILL_REGISTRY["search_flights"] = SearchFlightsSkill()
    SKILL_REGISTRY["search_hotels"] = SearchHotelsSkill()
    SKILL_REGISTRY["compare_results"] = CompareResultsSkill()
    SKILL_REGISTRY["filter_by_budget"] = FilterByBudgetSkill()
    
    # Recommendation Skills
    SKILL_REGISTRY["get_destination_info"] = GetDestinationInfoSkill()
    SKILL_REGISTRY["get_attractions"] = GetAttractionsSkill()
    SKILL_REGISTRY["get_weather_forecast"] = GetWeatherForecastSkill()
    SKILL_REGISTRY["get_destination_reviews"] = GetDestinationReviewsSkill()
    
    # Booking Skills
    SKILL_REGISTRY["create_booking"] = CreateBookingSkill()
    SKILL_REGISTRY["process_payment"] = ProcessPaymentSkill()
    SKILL_REGISTRY["confirm_booking"] = ConfirmBookingSkill()
    SKILL_REGISTRY["get_booking_status"] = GetBookingStatusSkill()


_init_legacy_registry()


def get_all_skills() -> List[BaseSkill]:
    """Get list of all registered skills (legacy support)"""
    return list(SKILL_REGISTRY.values())


def get_skill_names() -> List[str]:
    """Get list of all skill names (legacy support)"""
    return list(SKILL_REGISTRY.keys())


def get_skill(name: str) -> BaseSkill:
    """Get a specific skill by name (legacy support)"""
    return SKILL_REGISTRY.get(name)


def get_skills_by_category(category: str) -> List[BaseSkill]:
    """Get skills filtered by agent type (updated to use agent_type)"""
    # Map old 'category' to new 'agent_type'
    return [s for s in SKILL_REGISTRY.values() if s.agent_type == category]


def get_skill_definitions() -> List[Dict]:
    """Get all skill definitions for MCP registration (legacy support)"""
    return [skill.to_definition() for skill in SKILL_REGISTRY.values()]


__all__ = [
    # Base class
    "BaseSkill",
    
    # Info Collection Skills
    "GetUserPreferencesSkill",
    "ValidateUserInputSkill",
    "SuggestDestinationsSkill",
    
    # Search Skills
    "SearchFlightsSkill",
    "SearchHotelsSkill",
    "CompareResultsSkill",
    "FilterByBudgetSkill",
    
    # Recommendation Skills
    "GetDestinationInfoSkill",
    "GetAttractionsSkill",
    "GetWeatherForecastSkill",
    "GetDestinationReviewsSkill",
    
    # Booking Skills
    "CreateBookingSkill",
    "ProcessPaymentSkill",
    "ConfirmBookingSkill",
    "GetBookingStatusSkill",
    
    # Legacy support
    "SKILL_REGISTRY",
    "get_all_skills",
    "get_skill_names",
    "get_skill",
    "get_skills_by_category",
    "get_skill_definitions",
]
