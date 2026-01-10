"""Skill Registry - Central registry for all MCP skills

This module manages skill registration, discovery, and retrieval
organized by agent type.
"""

from typing import Dict, List, Optional
from .skills.base_skill import BaseSkill

# Import all skills by agent type
from .skills.info_collection import (
    GetUserPreferencesSkill,
    ValidateUserInputSkill,
    SuggestDestinationsSkill,
)
from .skills.search import (
    SearchFlightsSkill,
    SearchHotelsSkill,
    CompareResultsSkill,
    FilterByBudgetSkill,
)
from .skills.recommendation import (
    GetDestinationInfoSkill,
    GetAttractionsSkill,
    GetWeatherForecastSkill,
    GetDestinationReviewsSkill,
)
from .skills.booking import (
    CreateBookingSkill,
    ProcessPaymentSkill,
    ConfirmBookingSkill,
    GetBookingStatusSkill,
)


class SkillRegistry:
    """Registry for managing all available skills"""
    
    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}
        self._register_all_skills()
    
    def _register_all_skills(self):
        """Register all available skills"""
        
        # Info Collection Skills
        self.register(GetUserPreferencesSkill())
        self.register(ValidateUserInputSkill())
        self.register(SuggestDestinationsSkill())
        
        # Search Skills
        self.register(SearchFlightsSkill())
        self.register(SearchHotelsSkill())
        self.register(CompareResultsSkill())
        self.register(FilterByBudgetSkill())
        
        # Recommendation Skills
        self.register(GetDestinationInfoSkill())
        self.register(GetAttractionsSkill())
        self.register(GetWeatherForecastSkill())
        self.register(GetDestinationReviewsSkill())
        
        # Booking Skills
        self.register(CreateBookingSkill())
        self.register(ProcessPaymentSkill())
        self.register(ConfirmBookingSkill())
        self.register(GetBookingStatusSkill())
    
    def register(self, skill: BaseSkill):
        """Register a skill
        
        Args:
            skill: Skill instance to register
        """
        self._skills[skill.name] = skill
    
    def get(self, skill_name: str) -> Optional[BaseSkill]:
        """Get a skill by name
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Skill instance or None if not found
        """
        return self._skills.get(skill_name)
    
    def get_all(self) -> List[BaseSkill]:
        """Get all registered skills
        
        Returns:
            List of all skills
        """
        return list(self._skills.values())
    
    def get_by_agent_type(self, agent_type: str) -> List[BaseSkill]:
        """Get all skills for a specific agent type
        
        Args:
            agent_type: Agent type (info_collection, search, recommendation, booking)
            
        Returns:
            List of skills for that agent
        """
        return [skill for skill in self._skills.values() if skill.agent_type == agent_type]
    
    def get_skill_names(self) -> List[str]:
        """Get list of all skill names
        
        Returns:
            List of skill names
        """
        return list(self._skills.keys())
    
    def get_skill_definitions(self, agent_type: Optional[str] = None) -> List[Dict]:
        """Get skill definitions for MCP protocol
        
        Args:
            agent_type: Optional filter by agent type
            
        Returns:
            List of skill definitions
        """
        skills = self.get_by_agent_type(agent_type) if agent_type else self.get_all()
        return [skill.to_definition() for skill in skills]
    
    def count(self) -> int:
        """Get total number of registered skills
        
        Returns:
            Number of skills
        """
        return len(self._skills)
    
    def count_by_agent_type(self) -> Dict[str, int]:
        """Get count of skills per agent type
        
        Returns:
            Dictionary of agent types to skill counts
        """
        counts = {}
        for skill in self._skills.values():
            counts[skill.agent_type] = counts.get(skill.agent_type, 0) + 1
        return counts


# Global registry instance
_registry: Optional[SkillRegistry] = None


def get_skill_registry() -> SkillRegistry:
    """Get the global skill registry instance
    
    Returns:
        Global SkillRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = SkillRegistry()
    return _registry


def reset_registry():
    """Reset the global registry (useful for testing)"""
    global _registry
    _registry = None


__all__ = [
    "SkillRegistry",
    "get_skill_registry",
    "reset_registry",
]
