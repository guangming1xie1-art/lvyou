"""Base Skill class for all MCP Skills with enhanced error handling and logging"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import json
from src.utils.logger import app_logger, log_execution
from src.agents.error_handler import AgentErrorHandler


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
    
    @log_execution
    async def execute_with_error_handling(self, **kwargs) -> Dict[str, Any]:
        """Execute the skill with unified error handling and logging"""
        try:
            app_logger.info(
                f"Executing skill {self.name}",
                skill=self.name,
                agent_type=self.agent_type,
                input_params=kwargs
            )
            
            result = await self.execute(**kwargs)
            
            app_logger.info(
                f"Skill {self.name} completed successfully",
                skill=self.name,
                has_error="error" in result if isinstance(result, dict) else False
            )
            
            return result
            
        except Exception as e:
            return AgentErrorHandler.handle_skill_error(
                skill_name=self.name,
                error=e,
                agent_type=self.agent_type,
                input_params=kwargs
            )
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the skill main logic"""
        raise NotImplementedError
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data against input schema
        
        Args:
            data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required = self.input_schema.get("required", [])
        for field in required:
            if field not in data:
                app_logger.warning(
                    f"Missing required field {field}",
                    skill=self.name,
                    field=field
                )
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
