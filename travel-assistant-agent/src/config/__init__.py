"""
配置模块
提供 LLM 配置和管理功能
"""

import importlib.util
from pathlib import Path

from .llm_config import (
    LLMFactory,
    MODEL_CONFIGS,
    LLMProvider,
    ModelConfig,
    ModelTier,
)

# 导入 settings 从父目录的 config.py
parent_dir = Path(__file__).parent.parent
config_py_path = parent_dir / "config.py"
if config_py_path.exists():
    spec = importlib.util.spec_from_file_location("config_settings", config_py_path)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    settings = config_module.settings
else:
    # 降级：使用空的 settings
    from pydantic_settings import BaseSettings

    settings = BaseSettings()

__all__ = [
    "settings",
    "ModelTier",
    "LLMProvider",
    "ModelConfig",
    "MODEL_CONFIGS",
    "LLMFactory",
]
