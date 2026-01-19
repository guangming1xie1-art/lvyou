"""
Skill Executor with Validation and Cost Tracking

Provides comprehensive skill execution with input validation, output validation,
dependency resolution, and cost tracking.
"""

from typing import Dict, Any, Optional
import logging
import time
import asyncio

logger = logging.getLogger(__name__)


class SkillExecutor:
    """Skill 执行器（含验证、依赖、成本追踪）"""
    
    @staticmethod
    async def execute(
        skill_name: str,
        input_params: Dict[str, Any],
        skill_loader,
        schema_loader,
        track_cost: bool = True,
        validate_input: bool = True,
        validate_output: bool = True,
        resolve_deps: bool = True
    ) -> Dict[str, Any]:
        """
        执行 skill（完整流程）
        
        1. 验证依赖
        2. 执行依赖
        3. 验证输入
        4. 执行 skill
        5. 验证输出
        6. 计算成本
        
        Args:
            skill_name: 技能名称
            input_params: 输入参数
            skill_loader: 异步函数用于加载技能
            schema_loader: 函数用于加载技能 schema
            track_cost: 是否追踪成本
            validate_input: 是否验证输入
            validate_output: 是否验证输出
            resolve_deps: 是否解析依赖
        
        Returns:
            {
                "success": True,
                "output": {...},
                "cost": 0.05,
                "execution_time_ms": 500,
                "dependencies_used": {...},
                "validation_errors": []
            }
        """
        start_time = time.time()
        execution_context = {
            "skill_name": skill_name,
            "start_time": start_time,
            "validation_errors": [],
            "dependencies_resolved": [],
            "cost_calculated": 0.0
        }
        
        try:
            logger.info(f"Starting execution of skill '{skill_name}'")
            
            # 1. 验证依赖链是否有循环
            if resolve_deps:
                logger.debug(f"Validating dependencies for '{skill_name}'")
                from src.skills.dependency_resolver import DependencyResolver
                
                if not DependencyResolver.validate_dependencies(skill_name, schema_loader):
                    raise ValueError(f"Circular dependency detected in skill '{skill_name}'")
                
                logger.debug(f"Dependencies validated for '{skill_name}'")
            
            # 2. 加载 skill
            logger.debug(f"Loading skill '{skill_name}'")
            try:
                skill = await skill_loader(skill_name)
            except Exception as e:
                raise RuntimeError(f"Failed to load skill '{skill_name}': {e}")
            
            # 3. 执行依赖
            deps_results = {}
            if resolve_deps and hasattr(skill, 'dependencies') and skill.dependencies:
                logger.info(f"Resolving {len(skill.dependencies)} dependencies for '{skill_name}'")
                from src.skills.dependency_resolver import DependencyResolver
                
                deps_results = await DependencyResolver.resolve_dependencies(
                    skill_name,
                    input_params,
                    skill_loader,
                    schema_loader
                )
                execution_context["dependencies_resolved"] = list(deps_results.keys())
                logger.info(f"Dependencies resolved: {list(deps_results.keys())}")
            
            # 4. 富集输入数据（合并依赖结果）
            enriched_input = {**input_params}
            for dep_name, dep_output in deps_results.items():
                if dep_output and isinstance(dep_output, dict):
                    # 智能合并策略：如果依赖输出包含关键信息，合并到输入
                    if "collected_info" in dep_output:
                        enriched_input["user_prefs"] = dep_output["collected_info"]
                    if "results" in dep_output:
                        enriched_input["search_results"] = dep_output["results"]
                    # 通用合并：避免覆盖已有字段
                    for key, value in dep_output.items():
                        if key not in enriched_input and value is not None:
                            enriched_input[key] = value
            
            # 5. 验证输入
            if validate_input and hasattr(skill, 'validate_input'):
                logger.debug(f"Validating input for '{skill_name}'")
                try:
                    validated_input = await skill.validate_input(enriched_input)
                    logger.debug(f"Input validated successfully for '{skill_name}'")
                except Exception as e:
                    execution_context["validation_errors"].append(f"Input validation failed: {e}")
                    logger.warning(f"Input validation failed for '{skill_name}': {e}")
                    # Still proceed, let the skill handle it
                    validated_input = enriched_input
            else:
                validated_input = enriched_input
            
            # 6. 执行 skill
            logger.debug(f"Executing skill '{skill_name}'")
            
            if hasattr(skill, 'execute_raw'):
                # Use enhanced execution path
                output = await skill.execute_raw(validated_input if not isinstance(validated_input, dict) else validated_input)
            else:
                # Fallback to legacy execution
                output = await skill.execute(validated_input if isinstance(validated_input, dict) else validated_input.model_dump())
            
            # 7. 验证输出
            if validate_output and hasattr(skill, 'validate_output'):
                logger.debug(f"Validating output for '{skill_name}'")
                try:
                    validated_output = await skill.validate_output(output)
                    output = validated_output.model_dump() if hasattr(validated_output, 'model_dump') else validated_output
                except Exception as e:
                    execution_context["validation_errors"].append(f"Output validation failed: {e}")
                    logger.warning(f"Output validation failed for '{skill_name}': {e}")
                    # Continue with raw output
            
            # 8. 计算成本
            actual_cost = 0.0
            if track_cost and hasattr(skill, 'calculate_cost'):
                try:
                    # For enhanced skills with Pydantic models
                    if hasattr(skill, 'input_model') and hasattr(skill, 'output_model'):
                        # Re-construct models if needed
                        input_model = None
                        output_model = None
                        
                        if skill.input_model and validated_input:
                            input_model = skill.input_model(**validated_input) if isinstance(validated_input, dict) else validated_input
                        
                        if skill.output_model and output:
                            output_model = skill.output_model(**output)
                        
                        if input_model and output_model:
                            actual_cost = skill.calculate_cost(input_model, output_model)
                        else:
                            actual_cost = skill.cost_estimate
                    else:
                        # Fallback to estimate
                        actual_cost = skill.cost_estimate
                    
                    execution_context["cost_calculated"] = actual_cost
                    logger.debug(f"Cost calculated for '{skill_name}': ${actual_cost:.4f}")
                except Exception as e:
                    logger.warning(f"Cost calculation failed for '{skill_name}': {e}")
                    actual_cost = getattr(skill, 'cost_estimate', 0.0)
            else:
                actual_cost = getattr(skill, 'cost_estimate', 0.0)
            
            execution_time = time.time() - start_time
            
            logger.info(
                f"Skill '{skill_name}' executed successfully. "
                f"Cost: ${actual_cost:.4f}, Time: {execution_time*1000:.2f}ms, "
                f"Dependencies: {len(deps_results)}"
            )
            
            # 9. Prepare comprehensive result
            result = {
                "success": True,
                "output": output,
                "cost": actual_cost if track_cost else None,
                "execution_time_ms": execution_time * 1000,
                "dependencies_used": deps_results,
                "validation_errors": execution_context["validation_errors"],
                "skill_metadata": skill.get_metadata() if hasattr(skill, 'get_metadata') else {}
            }
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Skill '{skill_name}' execution failed: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "cost": 0.0 if track_cost else None,
                "execution_time_ms": execution_time * 1000,
                "dependencies_used": execution_context.get("dependencies_resolved", []),
                "validation_errors": execution_context["validation_errors"]
            }
    
    @staticmethod
    async def execute_batch(
        skill_name: str,
        input_params_list: List[Dict[str, Any]],
        skill_loader,
        schema_loader,
        max_concurrent: int = 3,
        track_cost: bool = True
    ) -> List[Dict[str, Any]]:
        """
        批量执行 skill 多次
        
        Args:
            skill_name: 技能名称
            input_params_list: 输入参数列表
            skill_loader: 异步函数用于加载技能
            schema_loader: 函数用于加载技能 schema
            max_concurrent: 最大并发数
            track_cost: 是否追踪成本
        
        Returns:
            结果列表，顺序与 input_params_list 对应
        """
        logger.info(f"Starting batch execution of '{skill_name}' with {len(input_params_list)} inputs")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_single(params):
            async with semaphore:
                return await SkillExecutor.execute(
                    skill_name,
                    params,
                    skill_loader,
                    schema_loader,
                    track_cost=track_cost
                )
        
        # Execute all with concurrency limit
        results = await asyncio.gather(
            *[execute_single(params) for params in input_params_list],
            return_exceptions=True
        )
        
        # 处理异常
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch execution {i} failed: {result}")
                processed_results.append({
                    "success": False,
                    "error": str(result),
                    "cost": 0.0 if track_cost else None,
                    "execution_time_ms": 0.0
                })
            else:
                processed_results.append(result)
        
        total_cost = sum(r.get("cost", 0.0) or 0.0 for r in processed_results if r.get("success"))
        total_time = sum(r.get("execution_time_ms", 0.0) for r in processed_results)
        
        logger.info(
            f"Batch execution completed for '{skill_name}': "
            f"{len(processed_results)} tasks, "
            f"total_cost: ${total_cost:.4f}, "
            f"total_time: {total_time:.2f}ms"
        )
        
        return processed_results
    
    @staticmethod
    async def execute_with_fallback(
        primary_skill_name: str,
        fallback_skill_name: str,
        input_params: Dict[str, Any],
        skill_loader,
        schema_loader,
        track_cost: bool = True
    ) -> Dict[str, Any]:
        """
        带降级策略的技能执行
        
        Args:
            primary_skill_name: 首选技能名称
            fallback_skill_name: 降级技能名称
            input_params: 输入参数
            skill_loader: 异步函数用于加载技能
            schema_loader: 函数用于加载技能 schema
            track_cost: 是否追踪成本
        
        Returns:
            执行结果
        """
        # Try primary skill
        primary_result = await SkillExecutor.execute(
            primary_skill_name,
            input_params,
            skill_loader,
            schema_loader,
            track_cost=track_cost
        )
        
        if primary_result.get("success"):
            return primary_result
        
        # Primary failed, try fallback
        logger.warning(
            f"Primary skill '{primary_skill_name}' failed, "
            f"falling back to '{fallback_skill_name}': {primary_result.get('error')}"
        )
        
        fallback_result = await SkillExecutor.execute(
            fallback_skill_name,
            input_params,
            skill_loader,
            schema_loader,
            track_cost=track_cost
        )
        
        # Add fallback info
        fallback_result["used_fallback"] = True
        fallback_result["primary_error"] = primary_result.get("error")
        
        return fallback_result


__all__ = ["SkillExecutor"]