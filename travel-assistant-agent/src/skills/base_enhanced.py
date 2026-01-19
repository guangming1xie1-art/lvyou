"""
Enhanced Skill Base Classes with Pydantic Support

This module provides enhanced base classes for agent skills with:
- Type-safe input/output using Pydantic models
- Input validation and conversion
- Dynamic cost calculation
- Dependency management support
"""

from typing import Dict, Any, Optional, List, Type, TypeVar
from pydantic import BaseModel, Field
import logging
import time
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)  # Type variable for Pydantic models


class SkillInput(BaseModel):
    """Base Skill Input"""
    pass


class SkillOutput(BaseModel):
    """Base Skill Output"""
    success: bool = Field(default=True, description="Whether execution was successful")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class EnhancedSkill(ABC):
    """
    Enhanced Agent Skill Base Class with Pydantic Support
    
    Features:
    - Type-safe input/output validation using Pydantic
    - Dynamic cost calculation based on actual usage
    - Input validation and conversion methods
    - Output validation and format enforcement
    """
    
    # Class-level type hints for input/output models
    input_model: Optional[Type[BaseModel]] = None
    output_model: Optional[Type[BaseModel]] = None
    
    def __init__(
        self,
        name: str,
        description: str,
        version: str = "1.0.0",
        enabled: bool = True,
        cost_estimate: float = 0.0,
        category: str = "general",
        dependencies: Optional[List[str]] = None,
        cost_config: Optional[Dict[str, Any]] = None
    ):
        """Initialize enhanced skill
        
        Args:
            name: Unique skill name
            description: Skill description
            version: Skill version
            enabled: Whether skill is enabled
            cost_estimate: Estimated cost per execution (USD)
            category: Skill category
            dependencies: List of skill names this skill depends on
            cost_config: Dynamic cost calculation configuration
        """
        self.name = name
        self.description = description
        self.version = version
        self.enabled = enabled
        self.cost_estimate = cost_estimate
        self.category = category
        self.dependencies = dependencies or []
        self.cost_config = cost_config or {}
        
        # Statistics
        self.invocation_count = 0
        self.total_cost = 0.0
        self.total_execution_time = 0.0
        self.success_count = 0
        self.failure_count = 0
        
        logger.info(
            f"Initialized enhanced skill: {name} (v{version}, enabled={enabled}, cost=${cost_estimate:.4f})"
        )
    
    @abstractmethod
    async def execute(self, input_data: BaseModel) -> BaseModel:
        """
        Execute the skill with type-safe input/output
        
        Args:
            input_data: Validated Pydantic input model
            
        Returns:
            Validated Pydantic output model
            
        Raises:
            Exception: If execution fails
        """
        raise NotImplementedError(f"Skill {self.name} must implement execute method")
    
    async def validate_input(self, input_dict: Dict[str, Any]) -> BaseModel:
        """
        Validate and convert input dictionary to Pydantic model
        
        Args:
            input_dict: Raw input dictionary
            
        Returns:
            Validated Pydantic input model
            
        Raises:
            ValueError: If input validation fails
        """
        if not self.input_model:
            logger.warning(f"Skill {self.name} has no input_model defined, skipping validation")
            # Create a generic model for the input
            from pydantic import create_model
            return create_model(f"{self.name}Input", **{k: (type(v), v) for k, v in input_dict.items()})
        
        try:
            return self.input_model(**input_dict)
        except Exception as e:
            logger.error(f"Input validation failed for skill {self.name}: {e}")
            raise ValueError(f"Invalid input for skill {self.name}: {e}")
    
    async def validate_output(self, output_dict: Dict[str, Any]) -> BaseModel:
        """
        Validate and convert output dictionary to Pydantic model
        
        Args:
            output_dict: Raw output dictionary
            
        Returns:
            Validated Pydantic output model
            
        Raises:
            ValueError: If output validation fails
        """
        if not self.output_model:
            logger.warning(f"Skill {self.name} has no output_model defined, skipping validation")
            # Create a generic model for the output
            from pydantic import create_model
            return create_model(f"{self.name}Output", **{k: (type(v), v) for k, v in output_dict.items()})
        
        try:
            return self.output_model(**output_dict)
        except Exception as e:
            logger.error(f"Output validation failed for skill {self.name}: {e}")
            raise ValueError(f"Invalid output from skill {self.name}: {e}")
    
    def calculate_cost(
        self,
        input_data: BaseModel,
        output_data: BaseModel
    ) -> float:
        """
        Dynamic cost calculation based on input/output
        
        Default implementation returns cost_estimate.
        Subclasses can override for dynamic calculation.
        
        Args:
            input_data: Validated input model
            output_data: Validated output model
            
        Returns:
            Actual cost in USD
        """
        # Check if cost_config has a formula
        if self.cost_config:
            formula = self.cost_config.get("formula")
            if formula and "per_result" in self.cost_config:
                try:
                    # Extract results count from output_data if available
                    results_count = 0
                    if hasattr(output_data, 'results'):
                        results_count = len(output_data.results)
                    elif 'results' in output_data.model_dump():
                        results_count = len(output_data.model_dump()['results'])
                    
                    base = float(self.cost_config.get("base", 0))
                    per_result = float(self.cost_config.get("per_result", 0))
                    
                    # Calculate based on formula: "base + min(results_count, 100) * per_result"
                    import math
                    actual_cost = base + min(results_count, 100) * per_result
                    return actual_cost
                except Exception as e:
                    logger.warning(f"Cost calculation failed for {self.name}: {e}, using estimate")
        
        return self.cost_estimate
    
    def can_execute(self, input_dict: Dict[str, Any]) -> bool:
        """Check if skill can be executed with given input
        
        Args:
            input_dict: Raw input parameters
            
        Returns:
            True if skill can execute, False otherwise
        """
        if not self.enabled:
            return False
        
        # Try validation
        try:
            if self.input_model:
                self.input_model.model_validate(input_dict)
            return True
        except Exception:
            return False
    
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
            "cost_config": self.cost_config,
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
            f"Enhanced skill {self.name} executed successfully "
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
        
        logger.error(f"Enhanced skill {self.name} failed: {error} (time: {execution_time*1000:.2f}ms)")
    
    def reset_statistics(self):
        """Reset skill statistics"""
        self.invocation_count = 0
        self.total_cost = 0.0
        self.total_execution_time = 0.0
        self.success_count = 0
        self.failure_count = 0
        logger.info(f"Reset statistics for enhanced skill: {self.name}")
    
    def enable(self):
        """Enable the skill"""
        self.enabled = True
        logger.info(f"Enabled enhanced skill: {self.name}")
    
    def disable(self):
        """Disable the skill"""
        self.enabled = False
        logger.info(f"Disabled enhanced skill: {self.name}")
    
    async def execute_raw(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute skill with raw dictionary input (for backward compatibility)
        
        Args:
            input_dict: Raw input parameters
            
        Returns:
            Execution result as dictionary
            
        Raises:
            RuntimeError: If skill cannot be executed
        """
        if not self.can_execute(input_dict):
            raise RuntimeError(f"Enhanced skill {self.name} cannot be executed with given input: {input_dict}")
        
        start_time = time.time()
        
        try:
            # Validate and convert input
            validated_input = await self.validate_input(input_dict)
            
            # Execute with typed model
            output = await self.execute(validated_input)
            
            # Calculate cost based on actual usage
            actual_cost = self.calculate_cost(validated_input, output)
            
            execution_time = time.time() - start_time
            await self.on_success(execution_time, actual_cost)
            
            # Return raw dict for backward compatibility
            return output.model_dump()
        
        except Exception as e:
            execution_time = time.time() - start_time
            await self.on_failure(str(e), execution_time)
            raise


__all__ = [
    "EnhancedSkill",
    "SkillInput", 
    "SkillOutput",
]