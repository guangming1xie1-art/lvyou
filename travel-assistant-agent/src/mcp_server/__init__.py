"""
MCP Server package initialization

This package provides Claude Skills integration via MCP (Model Context Protocol)
for the Travel Assistant Agent.

Skills are now organized by Agent responsibility:
- info_collection: User preference collection and validation
- search: Flight and hotel search
- recommendation: Destination info, attractions, weather, reviews
- booking: Booking creation, payment, confirmation
"""

from .config import MCPServerConfig, MCPClientConfig, SkillDefinition
from .server import MCPServer, get_mcp_server, init_mcp_server
from .skill_registry import SkillRegistry, get_skill_registry
from .skills import (
    BaseSkill,
    # Legacy exports for backward compatibility
    get_all_skills,
    get_skill,
    get_skill_names,
    get_skill_definitions,
    SKILL_REGISTRY,
    # New skills organized by agent type
    GetUserPreferencesSkill,
    ValidateUserInputSkill,
    SuggestDestinationsSkill,
    SearchFlightsSkill,
    SearchHotelsSkill,
    CompareResultsSkill,
    FilterByBudgetSkill,
    GetDestinationInfoSkill,
    GetAttractionsSkill,
    GetWeatherForecastSkill,
    GetDestinationReviewsSkill,
    CreateBookingSkill,
    ProcessPaymentSkill,
    ConfirmBookingSkill,
    GetBookingStatusSkill,
)

__version__ = "2.0.0"  # Updated to 2.0.0 for major refactoring

__all__ = [
    # Config
    "MCPServerConfig",
    "MCPClientConfig",
    "SkillDefinition",
    
    # Server
    "MCPServer",
    "get_mcp_server",
    "init_mcp_server",
    
    # Registry
    "SkillRegistry",
    "get_skill_registry",
    
    # Base
    "BaseSkill",
    
    # Legacy support
    "get_all_skills",
    "get_skill",
    "get_skill_names",
    "get_skill_definitions",
    "SKILL_REGISTRY",
    
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
]
