"""
Skill Registry - 按需加载 Skills

提供统一的 Skill 注册、发现、加载接口
支持 YAML schema 加载和验证
"""
import os
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml
import json

logger = logging.getLogger(__name__)


class SkillRegistry:
    """
    Skill 注册表
    负责 Skill 的发现、加载、管理
    """
    
    _skills_dir = Path(__file__).parent
    _loaded_skills: Dict[str, Any] = {}
    
    @classmethod
    def list_skills(cls) -> List[Dict[str, str]]:
        """
        列出所有可用的 skills（名称 + 描述）
        不加载完整实现，只读取 SKILLS.md
        
        Returns:
            [{"name": "search", "description": "..."}, ...]
        """
        skills = []
        
        # 扫描 skills 目录
        for item in cls._skills_dir.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                skill_md = item / "SKILL.md"
                if skill_md.exists():
                    # 从 SKILL.md 提取名称和描述
                    name = item.name
                    description = cls._extract_description(skill_md)
                    skills.append({
                        "name": name,
                        "description": description
                    })
        
        return skills
    
    @classmethod
    def _extract_description(cls, skill_md_path: Path) -> str:
        """从 SKILL.md 提取描述"""
        try:
            content = skill_md_path.read_text(encoding="utf-8")
            # 查找 "## 概述" 部分
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.strip().startswith("## 概述"):
                    # 返回下一行
                    if i + 1 < len(lines):
                        return lines[i + 1].strip()
            return "No description available"
        except Exception as e:
            logger.warning(f"Failed to extract description from {skill_md_path}: {e}")
            return "No description available"
    
    @classmethod
    async def load_skill(cls, name: str):
        """
        按需加载 Skill 完整实现
        
        Args:
            name: skill 名称（如 "search"）
        
        Returns:
            Skill 实例
        """
        # 检查缓存
        if name in cls._loaded_skills:
            logger.info(f"Skill '{name}' already loaded (from cache)")
            return cls._loaded_skills[name]
        
        # 动态导入
        try:
            # 导入 skill 模块
            module_path = f"skills.{name}.skill"
            module = __import__(module_path, fromlist=[""])
            
            # 获取 Skill 类（约定类名为 {Name}Skill）
            skill_class_name = f"{name.capitalize()}Skill"
            if hasattr(module, skill_class_name):
                skill_class = getattr(module, skill_class_name)
                skill_instance = skill_class()
                
                # 缓存
                cls._loaded_skills[name] = skill_instance
                logger.info(f"Skill '{name}' loaded successfully")
                
                return skill_instance
            else:
                raise ImportError(f"Skill class '{skill_class_name}' not found in {module_path}")
        
        except Exception as e:
            logger.error(f"Failed to load skill '{name}': {e}")
            raise
    
    @classmethod
    def get_skill_summary(cls, name: str) -> Dict[str, Any]:
        """
        获取 Skill 摘要（参数、返回值格式等）
        从 SKILL.md 解析，不加载实现
        
        Args:
            name: skill 名称
        
        Returns:
            {
                "name": "search",
                "description": "...",
                "input_schema": {...},
                "output_schema": {...},
                "cost_estimate": 0.05,
                "execution_time": "500ms"
            }
        """
        skill_dir = cls._skills_dir / name
        skill_md = skill_dir / "SKILL.md"
        
        if not skill_md.exists():
            return {
                "name": name,
                "error": f"SKILL.md not found for '{name}'"
            }
        
        try:
            content = skill_md.read_text(encoding="utf-8")
            
            # 提取关键信息
            summary = {
                "name": name,
                "description": cls._extract_description(skill_md),
                "input_schema": cls._extract_section(content, "## 参数"),
                "output_schema": cls._extract_section(content, "## 返回值"),
                "usage_examples": cls._extract_section(content, "## 使用示例"),
                "cost_and_performance": cls._extract_section(content, "## 成本与性能"),
            }
            
            return summary
        
        except Exception as e:
            logger.error(f"Failed to get summary for skill '{name}': {e}")
            return {
                "name": name,
                "error": str(e)
            }
    
    @classmethod
    def _extract_section(cls, content: str, section_title: str) -> str:
        """从 markdown 提取指定章节内容"""
        lines = content.split("\n")
        in_section = False
        section_lines = []
        
        for line in lines:
            if line.strip().startswith(section_title):
                in_section = True
                continue
            
            if in_section:
                # 遇到下一个 ## 章节，结束
                if line.strip().startswith("##"):
                    break
                section_lines.append(line)
        
        return "\n".join(section_lines).strip()
    
    @classmethod
    def get_all_summaries(cls) -> List[Dict[str, Any]]:
        """
        批量获取所有 skill 摘要
        用于生成 LLM Prompt
        
        Returns:
            [{"name": "search", "description": "...", ...}, ...]
        """
        skills = cls.list_skills()
        summaries = []
        
        for skill_info in skills:
            name = skill_info["name"]
            summary = cls.get_skill_summary(name)
            summaries.append(summary)
        
        return summaries
    
    @classmethod
    def get_all_summaries_text(cls) -> str:
        """
        返回所有 skills 的摘要（文本格式，用于 LLM prompt）
        
        Returns:
            格式化的文本字符串
        """
        skills = cls.list_skills()
        summaries = []
        for skill in skills:
            summaries.append(f"- {skill['name']}: {skill['description']}")
        return "\n".join(summaries)
    
    @classmethod
    def unload_skill(cls, name: str):
        """
        卸载 Skill（释放内存）
        
        Args:
            name: skill 名称
        """
        if name in cls._loaded_skills:
            del cls._loaded_skills[name]
            logger.info(f"Skill '{name}' unloaded")
    
    @classmethod
    def unload_all(cls):
        """卸载所有 skills"""
        cls._loaded_skills.clear()
        logger.info("All skills unloaded")
    
    @classmethod
    def get_loaded_skills(cls) -> List[str]:
        """获取已加载的 skill 名称列表"""
        return list(cls._loaded_skills.keys())
    
    # ===== YAML Schema Support Methods =====
    
    @classmethod
    def load_yaml_schema(cls, name: str) -> Dict[str, Any]:
        """
        加载 YAML schema 文件
        
        Args:
            name: skill 名称
            
        Returns:
            YAML schema 字典
        """
        skill_dir = cls._skills_dir / name
        yaml_file = skill_dir / "SKILL.yaml"
        
        if not yaml_file.exists():
            raise FileNotFoundError(f"SKILL.yaml not found for skill '{name}'")
        
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                schema = yaml.safe_load(f)
            return schema
        except Exception as e:
            logger.error(f"Failed to load YAML schema for '{name}': {e}")
            raise
    
    @classmethod
    def list_skills_yaml(cls) -> List[Dict[str, Any]]:
        """
        列出所有可用的 skills（基于 YAML schema）
        
        Returns:
            包含详细信息的 skill 列表
        """
        skills = []
        
        # 扫描 skills 目录
        for item in cls._skills_dir.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                yaml_file = item / "SKILL.yaml"
                if yaml_file.exists():
                    try:
                        schema = cls.load_yaml_schema(item.name)
                        skills.append({
                            "name": item.name,
                            "description": schema.get("description", "").strip().split("\n")[0],
                            "category": schema.get("category", "general"),
                            "enabled": schema.get("enabled", True),
                            "cost": schema.get("cost", {}).get("formula", schema.get("cost", {}).get("base", 0)),
                            "dependencies": len(schema.get("dependencies", []))
                        })
                    except Exception as e:
                        logger.warning(f"Failed to load YAML schema for '{item.name}': {e}")
                        continue
        
        return skills
    
    @classmethod
    def get_skill_schema(cls, name: str) -> Dict[str, Any]:
        """
        获取 skill 的完整 schema（完整实现）
        
        Args:
            name: skill 名称
            
        Returns:
            完整的 skill schema 字典
        """
        return cls.load_yaml_schema(name)
    
    @classmethod
    def get_all_summaries_for_llm(cls) -> str:
        """
        生成 LLM prompt 中的 skill 清单
        
        Returns:
            格式化的 skill 信息文本
        """
        from skills.prompt_generator import SkillPromptGenerator
        return SkillPromptGenerator.generate_system_prompt(cls._skills_dir)
    
    @classmethod
    def _validate_skill_implementation(cls, skill, schema: Dict[str, Any]):
        """
        验证 skill 实现是否遵循 schema
        
        Args:
            skill: skill 实例
            schema: YAML schema 字典
        """
        # 验证输入 model
        if hasattr(skill, 'input_model') and skill.input_model:
            try:
                input_json_schema = skill.input_model.model_json_schema()
                yaml_input_schema = schema.get('input_schema', {})
                
                # 比较必需字段
                json_required = set(input_json_schema.get('required', []))
                yaml_required = set(yaml_input_schema.get('required', []))
                
                if json_required != yaml_required:
                    logger.warning(
                        f"Skill {skill.name}: required fields mismatch. "
                        f"Pydantic: {json_required}, YAML: {yaml_required}"
                    )
            except Exception as e:
                logger.warning(f"Could not validate input model for {skill.name}: {e}")
        
        # 验证输出 model
        if hasattr(skill, 'output_model') and skill.output_model:
            try:
                output_json_schema = skill.output_model.model_json_schema()
                yaml_output_schema = schema.get('output_schema', {})
                
                json_required = set(output_json_schema.get('required', []))
                yaml_required = set(yaml_output_schema.get('required', []))
                
                if json_required != yaml_required:
                    logger.warning(
                        f"Skill {skill.name}: output required fields mismatch. "
                        f"Pydantic: {json_required}, YAML: {yaml_required}"
                    )
            except Exception as e:
                logger.warning(f"Could not validate output model for {skill.name}: {e}")
        
        logger.debug(f"Skill {skill.name} validated against schema")
    
    @classmethod
    async def load_skill_with_validation(cls, name: str):
        """
        加载 skill 并验证与 schema 的一致性
        
        Args:
            name: skill 名称
            
        Returns:
            验证后的 skill 实例
        """
        # Load schema first
        schema = cls.load_yaml_schema(name)
        
        # Load skill
        skill = await cls.load_skill(name)
        
        # Validate against schema
        cls._validate_skill_implementation(skill, schema)
        
        return skill


__all__ = ["SkillRegistry"]
