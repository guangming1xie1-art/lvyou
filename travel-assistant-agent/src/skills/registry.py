"""
Agent Skill Registry

This module provides a centralized registry for managing agent skills,
including registration, discovery, and execution.
"""

from typing import Dict, List, Optional, Set
import logging
import asyncio
from .base import Skill

logger = logging.getLogger(__name__)


class SkillRegistry:
    """Agent Skill Registry
    
    Manages skill registration, discovery, and execution.
    Provides a central interface for working with all registered skills.
    """
    
    def __init__(self):
        """Initialize skill registry"""
        self.skills: Dict[str, Skill] = {}
        self._categories: Dict[str, Set[str]] = {}
        self._execution_lock = asyncio.Lock()
    
    def register(self, skill: Skill):
        """Register a skill
        
        Args:
            skill: Skill instance to register
            
        Raises:
            ValueError: If a skill with the same name is already registered
        """
        if skill.name in self.skills:
            logger.warning(f"Skill {skill.name} is already registered, overwriting")
        
        self.skills[skill.name] = skill
        
        # Update category index
        if skill.category not in self._categories:
            self._categories[skill.category] = set()
        self._categories[skill.category].add(skill.name)
        
        logger.info(
            f"Registered skill: {skill.name} "
            f"(category: {skill.category}, enabled: {skill.enabled})"
        )
    
    def get(self, name: str) -> Optional[Skill]:
        """Get a skill by name
        
        Args:
            name: Skill name
            
        Returns:
            Skill instance or None if not found
        """
        return self.skills.get(name)
    
    def has(self, name: str) -> bool:
        """Check if a skill exists
        
        Args:
            name: Skill name
            
        Returns:
            True if skill exists, False otherwise
        """
        return name in self.skills
    
    def list_all(self) -> List[Dict]:
        """List all skills
        
        Returns:
            List of skill metadata dictionaries
        """
        return [skill.get_metadata() for skill in self.skills.values()]
    
    def list_enabled(self) -> List[Dict]:
        """List all enabled skills
        
        Returns:
            List of enabled skill metadata dictionaries
        """
        return [
            skill.get_metadata()
            for skill in self.skills.values()
            if skill.enabled
        ]
    
    def list_by_category(self, category: str) -> List[Dict]:
        """List skills by category
        
        Args:
            category: Skill category
            
        Returns:
            List of skill metadata in the category
        """
        if category not in self._categories:
            return []
        
        return [
            self.skills[name].get_metadata()
            for name in self._categories[category]
            if self.skills[name].enabled
        ]
    
    def get_categories(self) -> List[str]:
        """Get all categories
        
        Returns:
            List of category names
        """
        return list(self._categories.keys())
    
    def enable(self, name: str):
        """Enable a skill
        
        Args:
            name: Skill name
            
        Raises:
            ValueError: If skill not found
        """
        if name not in self.skills:
            raise ValueError(f"Unknown skill: {name}")
        
        self.skills[name].enable()
    
    def disable(self, name: str):
        """Disable a skill
        
        Args:
            name: Skill name
            
        Raises:
            ValueError: If skill not found
        """
        if name not in self.skills:
            raise ValueError(f"Unknown skill: {name}")
        
        self.skills[name].disable()
    
    async def execute(
        self,
        name: str,
        input_data: Dict,
        timeout: Optional[float] = None
    ) -> Dict:
        """Execute a skill
        
        Args:
            name: Skill name
            input_data: Skill input parameters
            timeout: Optional timeout in seconds
            
        Returns:
            Skill execution result
            
        Raises:
            ValueError: If skill not found
            RuntimeError: If skill cannot be executed
            asyncio.TimeoutError: If execution times out
        """
        skill = self.get(name)
        if skill is None:
            raise ValueError(f"Unknown skill: {name}")
        
        if not skill.can_execute(input_data):
            raise RuntimeError(f"Skill {name} cannot be executed with given input")
        
        if timeout:
            try:
                result = await asyncio.wait_for(
                    skill(input_data),
                    timeout=timeout
                )
                return result
            except asyncio.TimeoutError:
                logger.error(f"Skill {name} execution timed out after {timeout}s")
                await skill.on_failure("Execution timeout", timeout)
                raise
        else:
            result = await skill(input_data)
            return result
    
    async def execute_parallel(
        self,
        calls: List[Dict],
        timeout: Optional[float] = None
    ) -> List[Dict]:
        """Execute multiple skills in parallel
        
        Args:
            calls: List of {"name": skill_name, "input": input_data} dictionaries
            timeout: Optional timeout in seconds
            
        Returns:
            List of results in the same order as calls
        """
        async def execute_call(call: Dict) -> Dict:
            skill_name = call.get("name")
            input_data = call.get("input", {})
            return {
                "name": skill_name,
                "result": await self.execute(skill_name, input_data, timeout)
            }
        
        tasks = [execute_call(call) for call in calls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        final_results = []
        for call, result in zip(calls, results):
            if isinstance(result, Exception):
                final_results.append({
                    "name": call["name"],
                    "error": str(result),
                    "success": False
                })
            else:
                final_results.append(result)
        
        return final_results
    
    async def execute_sequence(
        self,
        calls: List[Dict],
        stop_on_error: bool = True,
        timeout: Optional[float] = None
    ) -> List[Dict]:
        """Execute multiple skills in sequence
        
        Args:
            calls: List of {"name": skill_name, "input": input_data} dictionaries
            stop_on_error: Whether to stop on first error
            timeout: Optional timeout in seconds
            
        Returns:
            List of results in the same order as calls
        """
        results = []
        
        for call in calls:
            skill_name = call.get("name")
            input_data = call.get("input", {})
            
            try:
                result = await self.execute(skill_name, input_data, timeout)
                results.append({
                    "name": skill_name,
                    "result": result,
                    "success": True
                })
            except Exception as e:
                results.append({
                    "name": skill_name,
                    "error": str(e),
                    "success": False
                })
                
                if stop_on_error:
                    break
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics
        
        Returns:
            Dictionary with statistics
        """
        total_invocations = sum(
            skill.invocation_count
            for skill in self.skills.values()
        )
        total_cost = sum(
            skill.total_cost
            for skill in self.skills.values()
        )
        total_success = sum(
            skill.success_count
            for skill in self.skills.values()
        )
        
        return {
            "total_skills": len(self.skills),
            "enabled_skills": len([s for s in self.skills.values() if s.enabled]),
            "categories": len(self._categories),
            "total_invocations": total_invocations,
            "total_cost": total_cost,
            "total_success": total_success,
            "overall_success_rate": (
                total_success / total_invocations
                if total_invocations > 0 else 0.0
            )
        }
    
    def reset_all_statistics(self):
        """Reset statistics for all skills"""
        for skill in self.skills.values():
            skill.reset_statistics()
        logger.info("Reset statistics for all skills")


# Global registry instance
_global_registry: Optional[SkillRegistry] = None


def get_skill_registry() -> SkillRegistry:
    """Get the global skill registry instance
    
    Returns:
        Global SkillRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = SkillRegistry()
    return _global_registry


def init_skill_registry(registry: SkillRegistry) -> SkillRegistry:
    """Initialize the global skill registry
    
    Args:
        registry: SkillRegistry instance to use as global
        
    Returns:
        The registry instance
    """
    global _global_registry
    _global_registry = registry
    return registry


__all__ = [
    "SkillRegistry",
    "get_skill_registry",
    "init_skill_registry",
]
