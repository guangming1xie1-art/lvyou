"""Base Skill class for all MCP Skills"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import json


class BaseSkill(ABC):
    """Base class for all Claude Skills
    
    Each skill should be an independent tool unit that belongs to a specific agent.
    Skills are organized by which Agent uses them (agent_type).
    """
    
    name: str = "base_skill"
    description: str = "Base skill class"
    agent_type: str = "general"  # Which agent uses this skill (info_collection, search, recommendation, booking)
    version: str = "1.0.0"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        """Define input parameters using JSON Schema format"""
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        """Define output format using JSON Schema format"""
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the skill with given parameters"""
        raise NotImplementedError
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data against input schema
        
        Args:
            data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation - check required fields
        required = self.input_schema.get("required", [])
        for field in required:
            if field not in data:
                return False
        return True
    
    def to_definition(self) -> Dict[str, Any]:
        """Convert skill to MCP definition format"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
            "outputSchema": self.output_schema,
            "agentType": self.agent_type,
            "version": self.version
        }
    
    def format_output(self, result: Dict[str, Any]) -> str:
        """Format result as readable string for agent"""
        return json.dumps(result, indent=2, ensure_ascii=False)
