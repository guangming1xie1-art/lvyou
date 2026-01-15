"""
Agent Skill Loader

This module provides dynamic skill loading capabilities,
allowing skills to be discovered and loaded at runtime.
"""

from typing import Dict, List, Optional, Type, Any
import importlib
import inspect
import logging
from pathlib import Path
from .base import Skill
from .registry import SkillRegistry

logger = logging.getLogger(__name__)


class SkillLoader:
    """Skill Dynamic Loader
    
    Loads skills from modules and packages at runtime.
    Supports both explicit loading and automatic discovery.
    """
    
    def __init__(self, registry: Optional[SkillRegistry] = None):
        """Initialize skill loader
        
        Args:
            registry: Optional skill registry (uses global if not provided)
        """
        from .registry import get_skill_registry
        self.registry = registry or get_skill_registry()
    
    def load_from_module(
        self,
        module_path: str,
        skill_classes: Optional[List[str]] = None
    ) -> List[Skill]:
        """Load skills from a module
        
        Args:
            module_path: Python module path (e.g., "travel_assistant_agent.src.skills.builtins.search")
            skill_classes: Optional list of class names to load (loads all Skill subclasses if None)
            
        Returns:
            List of loaded skill instances
        """
        loaded_skills = []
        
        try:
            module = importlib.import_module(module_path)
            
            # Find all Skill subclasses in the module
            if skill_classes is None:
                skill_classes = []
                for name, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj) and
                        issubclass(obj, Skill) and
                        obj is not Skill and
                        not obj.__name__.startswith('_')
                    ):
                        skill_classes.append(obj.__name__)
            
            # Load specified skill classes
            for class_name in skill_classes:
                try:
                    SkillClass = getattr(module, class_name)
                    
                    # Verify it's a Skill subclass
                    if not (inspect.isclass(SkillClass) and issubclass(SkillClass, Skill)):
                        logger.warning(
                            f"Class {class_name} in {module_path} is not a Skill subclass"
                        )
                        continue
                    
                    # Instantiate and register the skill
                    skill = SkillClass()
                    self.registry.register(skill)
                    loaded_skills.append(skill)
                    
                    logger.info(
                        f"Loaded skill: {class_name} from {module_path}"
                    )
                
                except AttributeError:
                    logger.error(f"Class {class_name} not found in {module_path}")
                except Exception as e:
                    logger.error(
                        f"Failed to load skill {class_name} from {module_path}: {e}"
                    )
        
        except ImportError as e:
            logger.error(f"Failed to import module {module_path}: {e}")
        except Exception as e:
            logger.error(f"Error loading skills from {module_path}: {e}")
        
        return loaded_skills
    
    def load_from_directory(
        self,
        directory_path: str,
        package_prefix: str,
        recursive: bool = True
    ) -> List[Skill]:
        """Load skills from all Python modules in a directory
        
        Args:
            directory_path: Directory path to scan
            package_prefix: Package prefix for imported modules
            recursive: Whether to recursively scan subdirectories
            
        Returns:
            List of loaded skill instances
        """
        loaded_skills = []
        directory = Path(directory_path)
        
        if not directory.exists():
            logger.error(f"Directory not found: {directory_path}")
            return loaded_skills
        
        # Find Python files
        pattern = "**/*.py" if recursive else "*.py"
        py_files = directory.glob(pattern)
        
        for py_file in py_files:
            # Skip __pycache__ and __init__.py
            if (
                "__pycache__" in str(py_file) or
                py_file.name == "__init__.py" or
                py_file.name.startswith("_")
            ):
                continue
            
            # Convert file path to module path
            rel_path = py_file.relative_to(directory)
            module_path = str(rel_path.with_suffix('')).replace('/', '.')
            full_module_path = f"{package_prefix}.{module_path}"
            
            # Load skills from module
            skills = self.load_from_module(full_module_path)
            loaded_skills.extend(skills)
        
        logger.info(
            f"Loaded {len(loaded_skills)} skills from directory {directory_path}"
        )
        
        return loaded_skills
    
    def load_all_builtin_skills(self) -> List[Skill]:
        """Load all built-in skills
        
        Returns:
            List of loaded skill instances
        """
        loaded_skills = []
        
        # Try to load from builtins directory
        try:
            builtins_path = Path(__file__).parent / "builtins"
            if builtins_path.exists():
                skills = self.load_from_directory(
                    str(builtins_path),
                    "travel_assistant_agent.src.skills.builtins"
                )
                loaded_skills.extend(skills)
        except Exception as e:
            logger.warning(f"Failed to load from builtins directory: {e}")
        
        # Try to load from mcp_server skills (backward compatibility)
        try:
            skills = self.load_from_module(
                "travel_assistant_agent.src.mcp_server.skills",
                skill_classes=None  # Load all skills
            )
            # Note: These are already registered in mcp_server, so we just track them
            loaded_skills.extend(skills)
        except Exception as e:
            logger.warning(f"Failed to load from mcp_server skills: {e}")
        
        logger.info(f"Loaded {len(loaded_skills)} built-in skills")
        
        return loaded_skills
    
    def load_skills_from_config(self, config: Dict[str, Any]) -> List[Skill]:
        """Load skills based on configuration
        
        Args:
            config: Configuration dictionary with skill loading rules
            
        Returns:
            List of loaded skill instances
        """
        loaded_skills = []
        
        # Load from configured modules
        modules = config.get("modules", [])
        for module_config in modules:
            if isinstance(module_config, str):
                # Simple module path
                skills = self.load_from_module(module_config)
                loaded_skills.extend(skills)
            elif isinstance(module_config, dict):
                # Detailed module config
                module_path = module_config.get("path")
                skill_classes = module_config.get("skills")
                if module_path:
                    skills = self.load_from_module(module_path, skill_classes)
                    loaded_skills.extend(skills)
        
        # Load from configured directories
        directories = config.get("directories", [])
        for dir_config in directories:
            dir_path = dir_config.get("path")
            package_prefix = dir_config.get("package", "")
            recursive = dir_config.get("recursive", True)
            
            if dir_path:
                skills = self.load_from_directory(dir_path, package_prefix, recursive)
                loaded_skills.extend(skills)
        
        logger.info(f"Loaded {len(loaded_skills)} skills from config")
        
        return loaded_skills
    
    def reload_skill(self, skill_name: str) -> Optional[Skill]:
        """Reload a specific skill
        
        Args:
            skill_name: Name of the skill to reload
            
        Returns:
            Reloaded skill instance or None if not found
        """
        # Get current skill
        skill = self.registry.get(skill_name)
        if not skill:
            logger.warning(f"Cannot reload skill {skill_name}: not found")
            return None
        
        # Get the skill's module
        skill_module = inspect.getmodule(skill)
        if not skill_module:
            logger.warning(f"Cannot reload skill {skill_name}: no module")
            return None
        
        # Reload the module
        try:
            importlib.reload(skill_module)
            
            # Re-instantiate the skill
            SkillClass = type(skill)
            new_skill = SkillClass()
            
            # Re-register
            self.registry.register(new_skill)
            
            logger.info(f"Reloaded skill: {skill_name}")
            return new_skill
        
        except Exception as e:
            logger.error(f"Failed to reload skill {skill_name}: {e}")
            return None
    
    def unload_skill(self, skill_name: str) -> bool:
        """Unload a specific skill
        
        Args:
            skill_name: Name of the skill to unload
            
        Returns:
            True if successful, False otherwise
        """
        if skill_name in self.registry.skills:
            del self.registry.skills[skill_name]
            
            # Update category index
            for category_skills in self.registry._categories.values():
                category_skills.discard(skill_name)
            
            logger.info(f"Unloaded skill: {skill_name}")
            return True
        
        logger.warning(f"Cannot unload skill {skill_name}: not found")
        return False


__all__ = [
    "SkillLoader",
]
