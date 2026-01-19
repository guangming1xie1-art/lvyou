"""Gradio UI Package for Travel Assistant Agent

使用新的 deepagents CompiledSubAgent 架构

工作流程：
1. 信息收集 (collect) → 2. 搜索 (search) → 3. 推荐 (recommend) → 4. 预订 (booking)
"""

__version__ = "2.0.0"
__author__ = "Travel Assistant Team"

from .app import create_app
from .agent_bridge import AgentBridge, agent_bridge, get_agent_bridge
from .utils import (
    MediaHandler,
    format_agent_response,
    validate_multimedia_file,
    create_chat_message
)

__all__ = [
    "create_app",
    "AgentBridge",
    "agent_bridge",
    "get_agent_bridge",
    "MediaHandler",
    "format_agent_response",
    "validate_multimedia_file",
    "create_chat_message"
]
