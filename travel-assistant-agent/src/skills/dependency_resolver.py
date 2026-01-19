"""
Skill Dependency Resolver

Handles dependency validation, resolution, and execution for skills.
Supports dependency chains, cycles detection, and optional dependencies.
"""

from typing import Dict, Any, Set, List, Optional
import logging
from collections import deque

logger = logging.getLogger(__name__)


class DependencyResolver:
    """Skill 依赖解析和执行工具类"""
    
    @classmethod
    def validate_dependencies(cls, skill_name: str, schema_loader) -> bool:
        """
        检测依赖链是否有循环
        
        Args:
            skill_name: 要验证的技能名称
            schema_loader: 用于加载 skill schema 的函数/方法
            
        Returns:
            True 如果没有循环依赖，False 如果有
        """
        visited = set()
        stack = set()
        
        def has_cycle(name: str) -> bool:
            """递归检测循环"""
            if name in stack:
                logger.error(f"Circular dependency detected: {name} is already in dependency stack")
                return True
            if name in visited:
                return False
            
            visited.add(name)
            stack.add(name)
            
            try:
                # Load schema to get dependencies
                schema = schema_loader(name)
                for dep in schema.get("dependencies", []):
                    dep_name = dep.get("name")
                    if dep_name and has_cycle(dep_name):
                        return True
            except Exception as e:
                logger.warning(f"Could not load schema for {name}: {e}")
            
            stack.remove(name)
            return False
        
        return not has_cycle(skill_name)
    
    @classmethod
    async def resolve_dependencies(
        cls,
        skill_name: str,
        input_data: Dict[str, Any],
        skill_loader,
        schema_loader
    ) -> Dict[str, Any]:
        """
        解析并执行所有依赖
        
        Args:
            skill_name: 主技能名称
            input_data: 主技能输入数据
            skill_loader: 异步函数用于加载和执行技能
            schema_loader: 函数用于加载技能 schema
            
        Returns:
            {dep_name: dep_output, ...}
        """
        try:
            schema = schema_loader(skill_name)
        except Exception as e:
            logger.error(f"Failed to load schema for {skill_name}: {e}")
            return {}
        
        dependencies = schema.get("dependencies", [])
        if not dependencies:
            logger.debug(f"Skill '{skill_name}' has no dependencies")
            return {}
        
        results = {}
        logger.info(f"Resolving {len(dependencies)} dependencies for skill '{skill_name}'")
        
        for dep_config in dependencies:
            dep_name = dep_config.get("name")
            is_optional = dep_config.get("optional", False)
            
            if not dep_name:
                logger.warning(f"Invalid dependency config: {dep_config}")
                continue
            
            try:
                logger.info(f"Resolving dependency: {dep_name} (optional={is_optional})")
                
                # Recursively resolve dependencies first
                dep_deps_results = await cls.resolve_dependencies(
                    dep_name, input_data, skill_loader, schema_loader
                )
                
                # Merge dependency results into input data if needed
                enriched_input = {**input_data}
                for dep_result_name, dep_result_value in dep_deps_results.items():
                    if dep_result_value and isinstance(dep_result_value, dict):
                        enriched_input.update(dep_result_value)
                
                # Load and execute the dependency skill
                dep_skill = await skill_loader(dep_name)
                dep_output = await dep_skill.execute_raw(enriched_input)
                
                results[dep_name] = dep_output
                logger.info(f"Dependency '{dep_name}' resolved successfully")
                
            except Exception as e:
                error_msg = f"Dependency '{dep_name}' failed: {e}"
                if is_optional:
                    logger.warning(error_msg)
                    results[dep_name] = None
                else:
                    logger.error(error_msg)
                    raise Exception(f"Required dependency '{dep_name}' failed: {e}")
        
        return results
    
    @classmethod
    def get_dependency_graph(cls, skill_name: str, schema_loader) -> Dict[str, List[str]]:
        """
        获取依赖树（用于可视化）
        
        Args:
            skill_name: 技能名称
            schema_loader: 用于加载 skill schema 的函数
            
        Returns:
            {skill_name: [dep1, dep2, ...], ...}
        """
        try:
            schema = schema_loader(skill_name)
        except Exception as e:
            logger.error(f"Failed to load schema for {skill_name}: {e}")
            return {skill_name: []}
        
        graph = {skill_name: []}
        
        for dep_config in schema.get("dependencies", []):
            dep_name = dep_config.get("name")
            if dep_name:
                graph[skill_name].append(dep_name)
                
                # 递归获取子依赖
                try:
                    sub_graph = cls.get_dependency_graph(dep_name, schema_loader)
                    graph.update(sub_graph)
                except Exception as e:
                    logger.warning(f"Could not get sub-dependencies for {dep_name}: {e}")
        
        return graph
    
    @classmethod
    def get_execution_order(
        cls,
        skill_name: str,
        schema_loader
    ) -> List[str]:
        """
        获取依赖的执行顺序（拓扑排序）
        
        Args:
            skill_name: 技能名称
            schema_loader: 用于加载 skill schema 的函数
            
        Returns:
            按执行顺序排列的技能名称列表
        """
        # Build dependency graph
        graph = cls.get_dependency_graph(skill_name, schema_loader)
        
        # Build adjacency list and in-degree counter
        adjacency = {name: deps.copy() for name, deps in graph.items()}
        in_degree = {name: 0 for name in graph.keys()}
        
        # Calculate in-degrees
        for name, deps in adjacency.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        # Topological sort using Kahn's algorithm
        queue = deque([name for name, degree in in_degree.items() if degree == 0])
        execution_order = []
        
        while queue:
            current = queue.popleft()
            execution_order.append(current)
            
            for neighbor in adjacency.get(current, []):
                if neighbor in in_degree:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
        
        # Check for cycles
        if len(execution_order) != len(graph):
            logger.error(f"Circular dependency detected in skill graph for {skill_name}")
            raise ValueError(f"Circular dependency detected in skill graph for {skill_name}")
        
        # Remove the main skill itself from dependencies
        if skill_name in execution_order:
            execution_order.remove(skill_name)
        
        return execution_order
    
    @classmethod
    def get_required_dependencies(cls, skill_name: str, schema_loader) -> List[str]:
        """
        获取必需依赖列表（不包括可选依赖）
        
        Args:
            skill_name: 技能名称
            schema_loader: 用于加载 skill schema 的函数
            
        Returns:
            必需依赖名称列表
        """
        try:
            schema = schema_loader(skill_name)
        except Exception as e:
            logger.error(f"Failed to load schema for {skill_name}: {e}")
            return []
        
        required_deps = []
        for dep in schema.get("dependencies", []):
            dep_name = dep.get("name")
            is_optional = dep.get("optional", False)
            if dep_name and not is_optional:
                required_deps.append(dep_name)
        
        return required_deps
    
    @classmethod
    def get_optional_dependencies(cls, skill_name: str, schema_loader) -> List[str]:
        """
        获取可选依赖列表
        
        Args:
            skill_name: 技能名称
            schema_loader: 用于加载 skill schema 的函数
            
        Returns:
            可选依赖名称列表
        """
        try:
            schema = schema_loader(skill_name)
        except Exception as e:
            logger.error(f"Failed to load schema for {skill_name}: {e}")
            return []
        
        optional_deps = []
        for dep in schema.get("dependencies", []):
            dep_name = dep.get("name")
            is_optional = dep.get("optional", False)
            if dep_name and is_optional:
                optional_deps.append(dep_name)
        
        return optional_deps


__all__ = ["DependencyResolver"]
