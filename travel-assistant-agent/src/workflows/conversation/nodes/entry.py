"""
入口节点 - 验证输入并初始化对话上下文
"""
from typing import Dict, Any
from ..state import ConversationState
from langchain_core.messages import HumanMessage
import logging

logger = logging.getLogger(__name__)


async def process_entry(state: ConversationState) -> ConversationState:
    """入口节点：验证输入，初始化对话上下文"""

    # 验证输入
    if not state.get("user_message") or not state["user_message"].strip():
        error_msg = "Empty user message"
        logger.warning("Entry node: Empty user message")
        return {
            **state,
            "workflow_status": "failed",
            "error_message": error_msg
        }

    # 创建Message对象
    human_message = HumanMessage(content=state["user_message"])

    # 更新历史和messages
    new_history = state.get("conversation_history", []) + [
        {"role": "user", "content": state["user_message"]}
    ]
    new_messages = state.get("messages", []) + [human_message]

    logger.info(f"Entry node: Processed message '{state['user_message'][:50]}...'")

    return {
        **state,
        "conversation_history": new_history,
        "messages": new_messages,
        "workflow_status": "active"
    }
