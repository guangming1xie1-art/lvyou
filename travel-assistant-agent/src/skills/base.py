"""
Agent Skill Base Classes

This module provides base classes for agent skills, including
skill definition, execution interface, and metadata management.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import logging
import time
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class SkillInput(BaseModel):
    """Base Skill Input"""
    pass


class SkillOutput(BaseModel):
    """Base Skill Output"""
    success: bool = Field(default=True, description="Whether execution was successful")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class Skill(ABC):
    """Agent Skill Base Class
    
    All agent skills should inherit from this class and implement
    the execute method.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        version: str = "1.0.0",
        enabled: bool = True,
        cost_estimate: float = 0.0,
        category: str = "general",
        dependencies: Optional[List[str]] = None
    ):
        """Initialize skill
        
        Args:
            name: Unique skill name
            description: Skill description
            version: Skill version
            enabled: Whether skill is enabled
            cost_estimate: Estimated cost per execution (USD)
            category: Skill category
            dependencies: List of skill names this skill depends on
        """
        self.name = name
        self.description = description
        self.version = version
        self.enabled = enabled
        self.cost_estimate = cost_estimate
        self.category = category
        self.dependencies = dependencies or []
        
        # Statistics
        self.invocation_count = 0
        self.total_cost = 0.0
        self.total_execution_time = 0.0
        self.success_count = 0
        self.failure_count = 0
        
        logger.info(
            f"Initialized skill: {name} (v{version}, enabled={enabled}, cost=${cost_estimate:.4f})"
        )
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the skill
        
        Args:
            input_data: Skill input parameters
            
        Returns:
            Skill execution result
            
        Raises:
            Exception: If execution fails
        """
        raise NotImplementedError(f"Skill {self.name} must implement execute method")
    
    def can_execute(self, input_data: Dict[str, Any]) -> bool:
        """Check if skill can be executed with given input
        
        Args:
            input_data: Skill input parameters
            
        Returns:
            True if skill can execute, False otherwise
        """
        if not self.enabled:
            return False
        
        # Check if required fields are present
        required = self.get_required_fields()
        if not required:
            return True
        
        return all(field in input_data for field in required)
    
    def get_required_fields(self) -> List[str]:
        """Get list of required input fields
        
        Returns:
            List of required field names
        """
        # Subclasses can override this
        return []
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get skill metadata
        
        Returns:
            Dictionary containing skill metadata
        """
        avg_execution_time = (
            self.total_execution_time / self.invocation_count
            if self.invocation_count > 0 else 0.0
        )
        
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "enabled": self.enabled,
            "category": self.category,
            "cost_estimate": self.cost_estimate,
            "dependencies": self.dependencies,
            "invocation_count": self.invocation_count,
            "total_cost": self.total_cost,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": (
                self.success_count / self.invocation_count
                if self.invocation_count > 0 else 0.0
            ),
            "avg_execution_time_ms": avg_execution_time * 1000,
            "total_execution_time_ms": self.total_execution_time * 1000
        }
    
    async def on_success(self, execution_time: float, actual_cost: Optional[float] = None):
        """Called after successful execution
        
        Args:
            execution_time: Execution time in seconds
            actual_cost: Actual cost if different from estimate
        """
        self.invocation_count += 1
        self.success_count += 1
        self.total_execution_time += execution_time
        
        cost = actual_cost if actual_cost is not None else self.cost_estimate
        self.total_cost += cost
        
        logger.info(
            f"Skill {self.name} executed successfully "
            f"(cost: ${cost:.4f}, time: {execution_time*1000:.2f}ms)"
        )
    
    async def on_failure(self, error: str, execution_time: float):
        """Called after failed execution
        
        Args:
            error: Error message
            execution_time: Execution time in seconds
        """
        self.invocation_count += 1
        self.failure_count += 1
        self.total_execution_time += execution_time
        
        logger.error(f"Skill {self.name} failed: {error} (time: {execution_time*1000:.2f}ms)")
    
    def reset_statistics(self):
        """Reset skill statistics"""
        self.invocation_count = 0
        self.total_cost = 0.0
        self.total_execution_time = 0.0
        self.success_count = 0
        self.failure_count = 0
        logger.info(f"Reset statistics for skill: {self.name}")
    
    def enable(self):
        """Enable the skill"""
        self.enabled = True
        logger.info(f"Enabled skill: {self.name}")
    
    def disable(self):
        """Disable the skill"""
        self.enabled = False
        logger.info(f"Disabled skill: {self.name}")
    
    async def __call__(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convenience method to execute skill
        
        Args:
            input_data: Skill input parameters
            
        Returns:
            Skill execution result
        """
        if not self.can_execute(input_data):
            raise RuntimeError(f"Skill {self.name} cannot be executed with given input")
        
        start_time = time.time()
        
        try:
            result = await self.execute(input_data)
            execution_time = time.time() - start_time
            await self.on_success(execution_time)
            return result
        
        except Exception as e:
            execution_time = time.time() - start_time
            await self.on_failure(str(e), execution_time)
            raise


__all__ = [
    "Skill",
    "SkillInput",
    "SkillOutput",
]
