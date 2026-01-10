"""Gradio UI Package for Travel Assistant Agent

这个包提供了基于Gradio的用户界面，让用户能够通过聊天方式与旅行助手Agent交互。
支持多媒体交互，包括文字、图片、语音和视频文件。
"""

__version__ = "1.0.0"
__author__ = "Travel Assistant Team"

from .app import create_app
from .agent_bridge import AgentBridge
from .utils import (
    process_uploaded_file,
    format_agent_response,
    validate_multimedia_file,
    create_chat_message
)

__all__ = [
    "create_app",
    "AgentBridge", 
    "process_uploaded_file",
    "format_agent_response",
    "validate_multimedia_file",
    "create_chat_message"
]