"""Base Skill class for all MCP Skills"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import json


class BaseSkill(ABC):
    """Base class for all Claude Skills"""
    
    name: str = "base_skill"
    description: str = "Base skill class"
    category: str = "general"
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
    
    def to_definition(self) -> Dict[str, Any]:
        """Convert skill to MCP definition format"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
            "outputSchema": self.output_schema,
            "category": self.category,
            "version": self.version
        }
    
    def format_output(self, result: Dict[str, Any]) -> str:
        """Format result as readable string for agent"""
        return json.dumps(result, indent=2, ensure_ascii=False)
