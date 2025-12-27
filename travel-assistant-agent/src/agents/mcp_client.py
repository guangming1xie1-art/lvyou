"""
MCP Client for Agent Integration

This module provides an MCP client that allows the Agent to discover
and invoke skills via the MCP protocol.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MCPSkillCategory(Enum):
    """Skill categories for filtering"""
    DESTINATION = "destination"
    PRICING = "pricing"
    REVIEWS = "reviews"
    WEATHER = "weather"
    PLANNING = "planning"


@dataclass
class MCPSkill:
    """Represents an available MCP skill"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    category: str
    version: str = "1.0.0"
    
    @classmethod
    def from_definition(cls, definition: Dict) -> "MCPSkill":
        """Create from MCP definition format"""
        return cls(
            name=definition["name"],
            description=definition["description"],
            input_schema=definition.get("inputSchema", {}),
            output_schema=definition.get("outputSchema", {}),
            category=definition.get("category", "general"),
            version=definition.get("version", "1.0.0")
        )


@dataclass
class MCPSkillResult:
    """Result from a skill execution"""
    success: bool
    skill_name: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class MCPClient:
    """
    MCP Client for Travel Assistant Agent.
    
    This client provides methods for:
    - Discovering available skills
    - Invoking skills with parameters
    - Managing skill calls
    """
    
    def __init__(self, server_url: str = None):
        self.server_url = server_url
        self._skills_cache: List[MCPSkill] = []
        self._connected = False
    
    async def connect(self) -> bool:
        """Connect to MCP server"""
        self._connected = True
        logger.info("MCP Client connected (simulated)")
        await self._discover_skills()
        return self._connected
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        self._connected = False
        self._skills_cache = []
        logger.info("MCP Client disconnected")
    
    async def _discover_skills(self):
        """Discover available skills from server"""
        # In a real implementation, this would call the server's list_skills endpoint
        # For demo, we use the skills module directly
        from mcp_server.skills import get_skill_definitions, get_all_skills
        
        definitions = get_skill_definitions()
        self._skills_cache = [MCPSkill.from_definition(d) for d in definitions]
        logger.info(f"Discovered {len(self._skills_cache)} skills")
    
    def list_skills(self) -> List[MCPSkill]:
        """List all available skills"""
        return self._skills_cache.copy()
    
    def list_skill_names(self) -> List[str]:
        """List names of all available skills"""
        return [s.name for s in self._skills_cache]
    
    def get_skill(self, name: str) -> Optional[MCPSkill]:
        """Get a specific skill by name"""
        for skill in self._skills_cache:
            if skill.name == name:
                return skill
        return None
    
    def get_skills_by_category(self, category: MCPSkillCategory) -> List[MCPSkill]:
        """Get skills filtered by category"""
        return [s for s in self._skills_cache if s.category == category.value]
    
    async def call_skill(
        self,
        skill_name: str,
        parameters: Dict[str, Any]
    ) -> MCPSkillResult:
        """
        Execute a skill with the given parameters.
        
        Args:
            skill_name: Name of the skill to execute
            parameters: Input parameters for the skill
            
        Returns:
            MCPSkillResult with execution result
        """
        try:
            from mcp_server.skills import get_skill
            skill = get_skill(skill_name)
            
            if not skill:
                return MCPSkillResult(
                    success=False,
                    skill_name=skill_name,
                    error=f"Skill '{skill_name}' not found"
                )
            
            # Execute the skill
            result = await skill.execute(**parameters)
            
            logger.info(f"Skill '{skill_name}' executed successfully")
            
            return MCPSkillResult(
                success=True,
                skill_name=skill_name,
                result=result
            )
            
        except Exception as e:
            logger.error(f"Error executing skill '{skill_name}': {e}")
            return MCPSkillResult(
                success=False,
                skill_name=skill_name,
                error=str(e)
            )
    
    async def call_skills_parallel(
        self,
        calls: List[Dict[str, Any]]
    ) -> List[MCPSkillResult]:
        """
        Execute multiple skills in parallel.
        
        Args:
            calls: List of {"skill": skill_name, "parameters": params} dictionaries
            
        Returns:
            List of MCPSkillResult objects
        """
        tasks = []
        for call in calls:
            skill_name = call.get("skill") or call.get("name")
            parameters = call.get("parameters") or {}
            tasks.append(self.call_skill(skill_name, parameters))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                call = calls[i]
                skill_name = call.get("skill") or call.get("name")
                processed_results.append(MCPSkillResult(
                    success=False,
                    skill_name=skill_name,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def call_skills_sequential(
        self,
        calls: List[Dict[str, Any]],
        pass_previous_outputs: bool = True
    ) -> List[MCPSkillResult]:
        """
        Execute multiple skills sequentially, passing outputs to next calls.
        
        Args:
            calls: List of {"skill": skill_name, "parameters": params} dictionaries
            pass_previous_outputs: Whether to include previous results in next call parameters
            
        Returns:
            List of MCPSkillResult objects in order
        """
        results = []
        accumulated_data = {}
        
        for call in calls:
            skill_name = call.get("skill") or call.get("name")
            parameters = call.get("parameters") or {}
            
            # Optionally merge accumulated data into parameters
            if pass_previous_outputs and accumulated_data:
                parameters = {**parameters, **accumulated_data}
            
            result = await self.call_skill(skill_name, parameters)
            results.append(result)
            
            if result.success and result.result:
                accumulated_data.update(result.result)
        
        return results
    
    def is_connected(self) -> bool:
        """Check if client is connected to server"""
        return self._connected
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "connected": self._connected,
            "skills_count": len(self._skills_cache),
            "skills": self.list_skill_names()
        }


# Singleton instance
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """Get the global MCP client instance"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client


async def init_mcp_client(server_url: str = None) -> MCPClient:
    """Initialize and connect the global MCP client"""
    global _mcp_client
    _mcp_client = MCPClient(server_url)
    await _mcp_client.connect()
    return _mcp_client


__all__ = [
    "MCPClient",
    "MCPSkill",
    "MCPSkillResult",
    "MCPSkillCategory",
    "get_mcp_client",
    "init_mcp_client",
]
