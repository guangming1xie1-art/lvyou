"""
Agent Skills Framework

This module provides a comprehensive framework for managing agent skills,
including skill discovery, registration, dynamic loading, and execution.
"""

from .base import Skill, SkillInput, SkillOutput
from .registry import SkillRegistry

__version__ = "1.0.0"

__all__ = [
    # Base classes
    "Skill",
    "SkillInput",
    "SkillOutput",
    
    # Registry
    "SkillRegistry",
]
