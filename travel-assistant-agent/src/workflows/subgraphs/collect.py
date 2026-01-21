"""
信息收集工作流 - 单节点工作流，收集用户的旅游需求信息
"""

from typing import Dict, Any
import json

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from utils.token_counter import TokenCounter
from llm.factory import LLMFactory

from .common import SubState, cache_strategy


async def collect_info_node(state: SubState) -> Dict[str, Any]:
    """信息收集节点（便宜层 + 缓存）"""
    counter = TokenCounter()

    # 获取用户消息
    last_msg = state.get("messages", [])[-1] if state.get("messages") else None
    user_content = last_msg.content if last_msg else ""

    # 获取对话历史
    conversation_history = state.get("conversation_history", [])
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-6:]])

    # 尝试从缓存获取（基于用户消息）
    cache_key = f"collect:{user_content[:100]}"
    cached = cache_strategy.get_user_preferences(cache_key)
    if cached:
        # 从 common 导入的 logger
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Collection cache HIT")
        return {
            "messages": [AIMessage(content=cached.get("output", ""))],
            "usage": {"prompt": 0, "completion": 0, "total": 0},
            "output": cached.get("output", ""),
            "collected_info": cached.get("collected_info", {})
        }

    # 系统提示词
    system_prompt = f"""你是信息收集员，负责与用户交互收集旅游需求。

你的任务：
1. 分析用户的旅游需求
2. 识别关键信息：目的地、时间、预算、偏好等
3. 如果信息不足，生成友好的追问
4. 最终返回结构化的需求摘要

之前的对话历史：
{history_text if history_text else "（无历史记录）"}

返回格式（JSON）：
{{
    "destination": "目的地",
    "duration": "天数",
    "budget": "预算范围",
    "preferences": ["偏好1", "偏好2"],
    "dates": "出发时间",
    "complete": true/false  # 信息是否完整
}}
"""

    # 调用 LLM（便宜层）
    try:
        # 使用 LLMFactory 创建便宜层模型
        llm = LLMFactory.create_model_by_tier(tier="cheap")

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]

        result = await llm.ainvoke(
            messages,
            config={"callbacks": [counter]}
        )

        output_text = result.content

        # 尝试解析为 JSON
        try:
            collected_info = json.loads(output_text)
        except:
            collected_info = {"raw": output_text, "complete": False}

        # 缓存结果
        cache_strategy.cache_user_preferences(cache_key, {
            "output": output_text,
            "collected_info": collected_info
        })

        return {
            "messages": [result],
            "usage": counter.dump(),
            "output": output_text,
            "collected_info": collected_info
        }

    except Exception as e:
        # 从 common 导入的 logger
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"collect_info_node failed: {e}")
        return {
            "messages": [AIMessage(content=f"Error: {e}")],
            "usage": {"prompt": 0, "completion": 0, "total": 0},
            "output": f"Error: {e}",
            "collected_info": {"error": str(e)}
        }


def build_collect_info_graph() -> StateGraph:
    """构建信息收集子图"""
    graph = StateGraph(SubState)
    graph.add_node("collect", collect_info_node)
    graph.add_edge("collect", END)
    graph.set_entry_point("collect")
    return graph.compile()


__all__ = ["build_collect_info_graph"]
