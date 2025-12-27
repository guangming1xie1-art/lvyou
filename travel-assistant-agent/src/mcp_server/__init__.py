"""
MCP Server package initialization

This package provides Claude Skills integration via MCP (Model Context Protocol)
for the Travel Assistant Agent.
"""

from .config import MCPServerConfig, MCPClientConfig, SkillDefinition
from .server import MCPServer, get_mcp_server, init_mcp_server
from .skills import (
    BaseSkill,
    SearchDestinationSkill,
    QueryPricesSkill,
    GetDestinationReviewsSkill,
    GetWeatherSkill,
    CreateTravelPlanSkill,
    get_all_skills,
    get_skill,
    get_skill_names,
    get_skill_definitions,
    SKILL_REGISTRY
)

__version__ = "1.0.0"

__all__ = [
    # Config
    "MCPServerConfig",
    "MCPClientConfig",
    "SkillDefinition",
    
    # Server
    "MCPServer",
    "get_mcp_server",
    "init_mcp_server",
    
    # Skills
    "BaseSkill",
    "SearchDestinationSkill",
    "QueryPricesSkill",
    "GetDestinationReviewsSkill",
    "GetWeatherSkill",
    "CreateTravelPlanSkill",
    "get_all_skills",
    "get_skill",
    "get_skill_names",
    "get_skill_definitions",
    "SKILL_REGISTRY",
]
