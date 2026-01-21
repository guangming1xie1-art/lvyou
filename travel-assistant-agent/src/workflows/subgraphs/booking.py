"""
预订工作流 - 单节点工作流，处理用户选定方案的预订
"""

from typing import Dict, Any
import json

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from utils.token_counter import TokenCounter
from llm.factory import LLMFactory
from agents.mcp_client import get_mcp_client

from .common import SubState, cache_strategy, get_tools_and_skills_text, mcp_client


async def booking_node(state: SubState) -> Dict[str, Any]:
    """预订节点（便宜层 + 缓存）"""
    counter = TokenCounter()

    # 获取前面步骤的信息
    recommendations = state.get("recommendations", {})
    last_msg = state.get("messages", [])[-1] if state.get("messages") else None
    user_content = last_msg.content if last_msg else ""

    # 获取工具文本
    tools_text = await get_tools_and_skills_text()

    # 系统提示词
    system_prompt = f"""你是预订员，负责完成用户选定的旅游预订。

你的任务：
1. 确认用户选择的推荐方案
2. 使用 create_booking 工具创建预订
3. 返回预订确认信息

推荐方案：
{recommendations}

可用工具：
{tools_text}

返回格式（JSON）：
{{
    "booking_id": "预订ID",
    "status": "confirmed/pending",
    "details": {{...}},
    "confirmation_message": "确认信息"
}}
"""

    # 获取工具
    try:
        tools = await mcp_client.get_tools()
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to get tools: {e}")
        tools = []

    # 调用 LLM（便宜层）
    try:
        # 使用 LLMFactory 创建便宜层模型
        llm = LLMFactory.create_model_by_tier(tier="cheap")

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]

        if tools:
            result = await llm.ainvoke(
                messages,
                tools=tools,
                config={"callbacks": [counter]}
            )
        else:
            result = await llm.ainvoke(
                messages,
                config={"callbacks": [counter]}
            )

        output_text = result.content

        # 尝试解析为 JSON
        try:
            booking_confirmation = json.loads(output_text)
        except:
            booking_confirmation = {"raw": output_text, "status": "pending"}

        # 预订信息通常缓存较短时间
        if booking_confirmation.get("booking_id"):
            cache_key = f"booking:{booking_confirmation['booking_id']}"
            cache_strategy.cache_destination_info(cache_key, booking_confirmation)

        return {
            "messages": [result],
            "usage": counter.dump(),
            "output": output_text,
            "booking_confirmation": booking_confirmation
        }

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"booking_node failed: {e}")
        return {
            "messages": [AIMessage(content=f"Error: {e}")],
            "usage": {"prompt": 0, "completion": 0, "total": 0},
            "output": f"Error: {e}",
            "booking_confirmation": {"error": str(e)}
        }


def build_booking_graph() -> StateGraph:
    """构建预订子图"""
    graph = StateGraph(SubState)
    graph.add_node("booking", booking_node)
    graph.add_edge("booking", END)
    graph.set_entry_point("booking")
    return graph.compile()


__all__ = ["build_booking_graph"]
