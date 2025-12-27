"""Skills module for MCP Server

This module exports all available skills for the MCP protocol.
"""

from typing import Dict, List
from .base_skill import BaseSkill
from .destination import SearchDestinationSkill
from .pricing import QueryPricesSkill
from .reviews import GetDestinationReviewsSkill
from .weather import GetWeatherSkill
from .planning import CreateTravelPlanSkill


# Registry of all available skills
SKILL_REGISTRY: Dict[str, BaseSkill] = {
    "search_destination": SearchDestinationSkill(),
    "query_prices": QueryPricesSkill(),
    "get_destination_reviews": GetDestinationReviewsSkill(),
    "get_weather": GetWeatherSkill(),
    "create_travel_plan": CreateTravelPlanSkill(),
}


def get_all_skills() -> List[BaseSkill]:
    """Get list of all registered skills"""
    return list(SKILL_REGISTRY.values())


def get_skill_names() -> List[str]:
    """Get list of all skill names"""
    return list(SKILL_REGISTRY.keys())


def get_skill(name: str) -> BaseSkill:
    """Get a specific skill by name"""
    return SKILL_REGISTRY.get(name)


def get_skills_by_category(category: str) -> List[BaseSkill]:
    """Get skills filtered by category"""
    return [s for s in SKILL_REGISTRY.values() if s.category == category]


def get_skill_definitions() -> List[Dict]:
    """Get all skill definitions for MCP registration"""
    return [skill.to_definition() for skill in SKILL_REGISTRY.values()]


__all__ = [
    "BaseSkill",
    "SearchDestinationSkill",
    "QueryPricesSkill",
    "GetDestinationReviewsSkill",
    "GetWeatherSkill",
    "CreateTravelPlanSkill",
    "SKILL_REGISTRY",
    "get_all_skills",
    "get_skill_names",
    "get_skill",
    "get_skills_by_category",
    "get_skill_definitions",
]
