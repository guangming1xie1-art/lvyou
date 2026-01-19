"""
Skill Prompt Generator

Automatically generates LLM prompts based on YAML skill schemas.
Creates system prompts with skill catalogs, input/output formats, and examples.
"""

import json
import logging
from typing import Dict, Any, List, Optional
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)


class SkillPromptGenerator:
    """为 LLM 自动生成 skill 清单和系统提示"""
    
    @staticmethod
    def load_yaml_schema(schema_path: Path) -> Dict[str, Any]:
        """加载 YAML schema 文件"""
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load YAML schema from {schema_path}: {e}")
            return {}
    
    @staticmethod
    def format_input_schema(input_schema: Dict[str, Any]) -> str:
        """将输入 schema 转换为可读格式"""
        if not input_schema:
            return "No input schema defined"
        
        lines = []
        required_fields = input_schema.get("required", [])
        properties = input_schema.get("properties", {})
        
        for prop_name, prop_def in properties.items():
            req_str = "✅ Required" if prop_name in required_fields else "⚠️ Optional"
            prop_type = prop_def.get("type", "object")
            description = prop_def.get("description", "")
            
            lines.append(f"- `{prop_name}` ({prop_type}): {description} [{req_str}]")
            
            # Add nested properties for objects
            if prop_type == "object" and "properties" in prop_def:
                nested_props = prop_def["properties"]
                for nested_name, nested_def in nested_props.items():
                    nested_type = nested_def.get("type", "object")
                    nested_desc = nested_def.get("description", "")
                    lines.append(f"  - `{nested_name}` ({nested_type}): {nested_desc}")
            
            # Add item type for arrays
            elif prop_type == "array":
                items = prop_def.get("items", {})
                item_type = items.get("type", "object")
                lines.append(f"  - Item type: {item_type}")
        
        return "\n".join(lines) if lines else "No input parameters"
    
    @staticmethod
    def format_output_schema(output_schema: Dict[str, Any]) -> str:
        """将输出 schema 转换为可读格式"""
        if not output_schema:
            return "No output schema defined"
        
        lines = []
        required_fields = output_schema.get("required", [])
        properties = output_schema.get("properties", {})
        
        for prop_name, prop_def in properties.items():
            prop_type = prop_def.get("type", "object")
            description = prop_def.get("description", "")
            req_str = "✅" if prop_name in required_fields else "⚠️"
            
            lines.append(f"- {req_str} `{prop_name}` ({prop_type}): {description}")
            
            # Handle nested properties
            if prop_type == "object" and "properties" in prop_def:
                nested_props = prop_def["properties"]
                for nested_name, nested_def in nested_props.items():
                    nested_type = nested_def.get("type", "object")
                    nested_desc = nested_def.get("description", "")
                    lines.append(f"  - `{nested_name}` ({nested_type}): {nested_desc}")
            
            elif prop_type == "array" and "items" in prop_def:
                items = prop_def["items"]
                if isinstance(items, dict) and "properties" in items:
                    lines.append(f"  - Array items:")
                    item_props = items["properties"]
                    for item_name, item_def in item_props.items():
                        item_type = item_def.get("type", "object")
                        item_desc = item_def.get("description", "")
                        lines.append(f"    - `{item_name}` ({item_type}): {item_desc}")
        
        return "\n".join(lines) if lines else "No output fields"
    
    @staticmethod
    def format_examples(examples: List[Dict[str, Any]]) -> str:
        """格式化示例为可读文本"""
        if not examples:
            return "No examples available"
        
        lines = []
        for i, example in enumerate(examples[:3], 1):  # Show max 3 examples
            input_data = example.get("input", {})
            output_data = example.get("output", {})
            
            lines.append(f"Example {i}:")
            lines.append("Input:")
            try:
                input_str = json.dumps(input_data, ensure_ascii=False, indent=2)
                lines.append(f"```json\n{input_str}\n```")
            except:
                lines.append(f"```json\n{input_data}\n```")
            
            lines.append("Output:")
            try:
                output_str = json.dumps(output_data, ensure_ascii=False, indent=2)
                lines.append(f"```json\n{output_str}\n```")
            except:
                lines.append(f"```json\n{output_data}\n```")
            
            lines.append("")  # Empty line between examples
        
        return "\n".join(lines).strip()
    
    @staticmethod
    def generate_system_prompt(skills_dir: Path, skill_names: Optional[List[str]] = None) -> str:
        """
        生成包含所有 skill 信息的系统提示
        
        Args:
            skills_dir: Skill 目录路径
            skill_names: 可选，指定要包含的技能列表，如果为 None 则包含所有
            
        Returns:
            系统提示字符串
        """
        # Discover skills
        if skill_names is None:
            skill_names = []
            for item in skills_dir.iterdir():
                if item.is_dir() and not item.name.startswith("_"):
                    schema_file = item / "SKILL.yaml"
                    if schema_file.exists():
                        skill_names.append(item.name)
        
        catalog_parts = []
        total_skills = len(skill_names)
        
        for skill_name in skill_names:
            schema_file = skills_dir / skill_name / "SKILL.yaml"
            if not schema_file.exists():
                continue
            
            try:
                schema = SkillPromptGenerator.load_yaml_schema(schema_file)
                if not schema:
                    continue
                
                # Build skill section
                skill_lines = []
                skill_lines.append(f"\n## Skill: {schema.get('name', skill_name)}\n")
                
                # Version and category
                version = schema.get('version', '1.0.0')
                category = schema.get('category', 'general')
                enabled = schema.get('enabled', True)
                status = "✅ Available" if enabled else "❌ Disabled"
                
                skill_lines.append(f"**版本**: {version} | **分类**: {category} | **状态**: {status}\n")
                
                # Description
                description = schema.get('description', '').strip()
                if description:
                    skill_lines.append(f"**描述**: {description}\n")
                
                # LLM Hint
                llm_hint = schema.get('llm_hint', '').strip()
                if llm_hint:
                    skill_lines.append(f"**使用场景**: {llm_hint}\n")
                
                # Input schema
                input_schema = schema.get('input_schema', {})
                if input_schema:
                    skill_lines.append("**必需参数**:")
                    skill_lines.append(SkillPromptGenerator.format_input_schema(input_schema))
                    skill_lines.append("")
                
                # Output schema
                output_schema = schema.get('output_schema', {})
                if output_schema:
                    skill_lines.append("**返回格式**:")
                    skill_lines.append(SkillPromptGenerator.format_output_schema(output_schema))
                    skill_lines.append("")
                
                # Cost
                cost = schema.get('cost', {})
                if cost:
                    formula = cost.get('formula', cost.get('base', 'unknown'))
                    description = cost.get('description', '')
                    skill_lines.append(f"**成本估计**: ${formula}")
                    if description:
                        skill_lines.append(f"*{description}*")
                    skill_lines.append("")
                
                # Examples
                examples = schema.get('examples', [])
                if examples:
                    skill_lines.append("**使用示例**:")
                    skill_lines.append(SkillPromptGenerator.format_examples(examples))
                    skill_lines.append("")
                
                catalog_parts.append("\n".join(skill_lines))
                
            except Exception as e:
                logger.error(f"Failed to process skill '{skill_name}': {e}")
                continue
        
        # Build system prompt
        system_prompt_parts = []
        system_prompt_parts.append(f"""You are an intelligent travel assistant with access to {total_skills} specialized tools (skills).

Your goal is to help users plan their trips by analyzing their needs and using the appropriate tools.

## Important Guidelines

1. **Understand First**: Always try to understand the user's complete needs before selecting tools
2. **Tool Selection**: Choose the most appropriate tool(s) based on the user's request
3. **Input Validation**: Ensure all required parameters are provided before calling a tool
4. **Cost Awareness**: Each tool call has a cost - be efficient and avoid unnecessary calls
5. **Dependency Management**: Some tools depend on others - ensure prerequisites are met
6. **Error Handling**: If a tool fails, explain what happened and suggest alternatives
""")
        
        # Add cost awareness section
        system_prompt_parts.append("""
## Cost Awareness

- Each tool call has an associated cost (shown in USD)
- When multiple tools can accomplish the task, prefer lower-cost options
- Minimize unnecessary tool calls by caching results when possible
- The total cost will be tracked and reported to the user
""")
        
        # Add available skills
        system_prompt_parts.append("\n## Available Skills\n")
        system_prompt_parts.extend(catalog_parts)
        
        # Add usage instructions
        system_prompt_parts.append("""
## How to Use Skills

When you need to use a skill, follow this format:

1. Analyze the user's request to identify required skills
2. Check if all required parameters are available
3. If parameters are missing, ask the user for clarification
4. When ready, execute the skill with proper parameters
5. Interpret the results and explain them to the user
6. If the result suggests follow-up actions, proceed accordingly

## Response Style

- Be helpful, friendly, and professional
- Explain your reasoning when selecting tools
- Clearly communicate what information you're missing
- Provide actionable suggestions based on tool results
- Keep the conversation natural and engaging
""")
        
        return "\n".join(system_prompt_parts)
    
    @staticmethod
    def generate_skill_prompt(skills_dir: Path, skill_name: str) -> Optional[str]:
        """
        为单个 skill 生成详细提示
        
        Args:
            skills_dir: Skill 目录路径
            skill_name: 技能名称
            
        Returns:
            技能详细提示字符串，如果加载失败返回 None
        """
        schema_file = skills_dir / skill_name / "SKILL.yaml"
        if not schema_file.exists():
            return None
        
        try:
            schema = SkillPromptGenerator.load_yaml_schema(schema_file)
            if not schema:
                return None
            
            lines = []
            lines.append(f"### {schema.get('name', skill_name).upper()} ###\n")
            
            # Basic info
            lines.append(f"Category: {schema.get('category', 'general')}")
            lines.append(f"Version: {schema.get('version', '1.0.0')}")
            lines.append(f"Enabled: {'Yes' if schema.get('enabled', True) else 'No'}")
            lines.append("")
            
            # Description
            desc = schema.get('description', '').strip()
            if desc:
                lines.append(f"Description: {desc}")
                lines.append("")
            
            # LLM Hint
            hint = schema.get('llm_hint', '').strip()
            if hint:
                lines.append(f"When to use: {hint}")
                lines.append("")
            
            # Input schema
            input_schema = schema.get('input_schema', {})
            if input_schema:
                lines.append("INPUT SCHEMA:")
                lines.append(SkillPromptGenerator.format_input_schema(input_schema))
                lines.append("")
            
            # Output schema
            output_schema = schema.get('output_schema', {})
            if output_schema:
                lines.append("OUTPUT SCHEMA:")
                lines.append(SkillPromptGenerator.format_output_schema(output_schema))
                lines.append("")
            
            # Cost
            cost = schema.get('cost', {})
            if cost:
                lines.append(f"Cost: {cost.get('formula', cost.get('base', 'unknown'))}")
                if cost.get('description'):
                    lines.append(f"Note: {cost['description']}")
                lines.append("")
            
            # Performance
            performance = schema.get('performance', {})
            if performance:
                avg_time = performance.get('avg_execution_time_ms', 'unknown')
                lines.append(f"Average execution time: {avg_time}ms")
                lines.append("")
            
            # Examples
            examples = schema.get('examples', [])
            if examples:
                lines.append("EXAMPLES:")
                lines.append(SkillPromptGenerator.format_examples(examples))
                lines.append("")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Failed to generate prompt for skill '{skill_name}': {e}")
            return None
    
    @staticmethod
    def generate_summary_table(skills_dir: Path) -> str:
        """
        生成 skill 摘要表格（用于快速参考）
        
        Args:
            skills_dir: Skill 目录路径
            
        Returns:
            Markdown 格式的表格字符串
        """
        # Collect all skills
        skills_info = []
        
        for item in skills_dir.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                schema_file = item / "SKILL.yaml"
                if schema_file.exists():
                    try:
                        schema = SkillPromptGenerator.load_yaml_schema(schema_file)
                        if schema:
                            skills_info.append({
                                "name": schema.get("name", item.name),
                                "category": schema.get("category", "general"),
                                "description": schema.get("description", "").strip().split("\n")[0],
                                "cost": schema.get("cost", {}).get("formula", schema.get("cost", {}).get("base", "unknown")),
                                "enabled": schema.get("enabled", True),
                                "dependencies": len(schema.get("dependencies", []))
                            })
                    except Exception as e:
                        logger.error(f"Failed to load schema for {item.name}: {e}")
                        continue
        
        # Build markdown table
        lines = []
        lines.append("| Skill | Category | Description | Cost | Status | Dependencies |")
        lines.append("|-------|----------|-------------|------|--------|--------------|")
        
        for skill in sorted(skills_info, key=lambda x: x["category"]):
            status = "✅" if skill["enabled"] else "❌"
            deps = skill["dependencies"]
            lines.append(
                f"| {skill['name']} | {skill['category']} | {skill['description'][:50]}... | "
                f"${skill['cost']} | {status} | {deps} |")
        
        return "\n".join(lines)


__all__ = ["SkillPromptGenerator"]