"""
MCP Server Implementation

This module provides a simple MCP (Model Context Protocol) server implementation
that wraps travel assistant skills for agent integration.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from .config import MCPServerConfig, SkillDefinition
from .skills import get_skill, get_skill_definitions, get_skill_names, get_skills_by_category

try:
    from utils.logger import app_logger
except ModuleNotFoundError:
    from src.utils.logger import app_logger

class MCPServer:
    """
    Simple MCP Server implementation for Travel Assistant Skills.
    
    This server provides an interface for agents to discover and invoke
    travel-related skills via the MCP protocol.
    """
    
    def __init__(self, config: MCPServerConfig = None):
        self.config = config or MCPServerConfig()
        self.running = False
        self.call_history: List[Dict] = []
        
    async def start(self):
        """Start the MCP server"""
        self.running = True
        app_logger.info(f"MCP Server started on {self.config.host}:{self.config.port}")
    
    async def stop(self):
        """Stop the MCP server"""
        self.running = False
        app_logger.info("MCP Server stopped")
    
    def list_skills(self, agent_type: Optional[str] = None) -> List[Dict]:
        """List all available skills with their definitions
        
        Args:
            agent_type: Optional filter by agent type (info_collection, search, recommendation, booking)
            
        Returns:
            List of skill definitions
        """
        if agent_type:
            skills = get_skills_by_category(agent_type)
            definitions = [skill.to_definition() for skill in skills]
            app_logger.info(f"Listing {len(definitions)} skills for agent_type '{agent_type}'")
        else:
            definitions = get_skill_definitions()
            app_logger.info(f"Listing {len(definitions)} skills")
        return definitions
    
    def get_skill_info(self, skill_name: str) -> Optional[Dict]:
        """Get detailed information about a specific skill"""
        skill = get_skill(skill_name)
        if skill:
            return {
                "definition": skill.to_definition(),
                "agentType": skill.agent_type,
                "version": skill.version
            }
        return None
    
    async def call_skill(self, skill_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a skill with the given parameters.
        
        Args:
            skill_name: Name of the skill to execute
            parameters: Input parameters for the skill
            
        Returns:
            Skill execution result
        """
        start_time = datetime.now()
        
        try:
            skill = get_skill(skill_name)
            if not skill:
                return {
                    "success": False,
                    "error": f"Skill '{skill_name}' not found",
                    "available_skills": get_skill_names()
                }
            
            # Validate required parameters
            input_schema = skill.input_schema
            required = input_schema.get("required", [])
            missing = [p for p in required if p not in parameters]
            
            if missing:
                return {
                    "success": False,
                    "error": f"Missing required parameters: {missing}",
                    "skill_name": skill_name,
                    "required_params": required
                }
            
            # Execute skill
            result = await skill.execute_with_error_handling(**parameters)
            
            # Record call
            call_record = {
                "timestamp": start_time.isoformat(),
                "skill_name": skill_name,
                "parameters": parameters,
                "success": "error" not in result if isinstance(result, dict) else True,
                "execution_time_ms": (datetime.now() - start_time).total_seconds() * 1000
            }
            self.call_history.append(call_record)
            
            return {
                "success": True,
                "skill_name": skill_name,
                "result": result
            }
            
        except Exception as e:
            app_logger.error(f"Error executing skill {skill_name}: {e}")
            call_record = {
                "timestamp": start_time.isoformat(),
                "skill_name": skill_name,
                "parameters": parameters,
                "success": False,
                "error": str(e),
                "execution_time_ms": (datetime.now() - start_time).total_seconds() * 1000
            }
            self.call_history.append(call_record)
            
            return {
                "success": False,
                "skill_name": skill_name,
                "error": str(e)
            }
    
    async def call_skills_batch(self, calls: List[Dict]) -> List[Dict]:
        """
        Execute multiple skills in batch.
        
        Args:
            calls: List of {"skill": skill_name, "parameters": params} dictionaries
            
        Returns:
            List of execution results
        """
        results = []
        for call in calls:
            skill_name = call.get("skill") or call.get("name")
            parameters = call.get("parameters") or call.get("input", {})
            
            result = await self.call_skill(skill_name, parameters)
            results.append(result)
        
        return results
    
    def get_call_history(self) -> List[Dict]:
        """Get history of all skill calls"""
        return self.call_history
    
    def clear_history(self):
        """Clear the call history"""
        self.call_history = []


# Singleton instance for easy access
_mcp_server: Optional[MCPServer] = None


def get_mcp_server() -> MCPServer:
    """Get the global MCP server instance"""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MCPServer()
    return _mcp_server


def init_mcp_server(config: MCPServerConfig = None) -> MCPServer:
    """Initialize the global MCP server"""
    global _mcp_server
    _mcp_server = MCPServer(config)
    return _mcp_server


__all__ = [
    "MCPServer",
    "get_mcp_server",
    "init_mcp_server",
]
