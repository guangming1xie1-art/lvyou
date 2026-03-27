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
from prompts.prompt_loader import prompt_loader
from prompts.prompt_renderer import prompt_renderer

from .common import SubState, cache_strategy, get_tools_and_skills_text, mcp_client


async def booking_node(state: SubState) -> Dict[str, Any]:
    """预订节点（便宜层 + 缓存）- 支持 Memory-First 架构"""
    counter = TokenCounter()

    # === Memory-First 架构支持 ===
    # 1. 优先使用意图识别提取的信息
    extracted_info = state.get("extracted_info", {})
    memory = state.get("memory", {})
    rewritten_query = state.get("rewritten_query")
    
    # 2. 获取传统方式的信息
    recommendations = state.get("recommendations", {})
    collected_info = state.get("collected_info", {})
    
    # 3. 合并信息（extracted_info 优先级更高）
    merged_info = {**collected_info, **extracted_info}
    
    last_msg = state.get("messages", [])[-1] if state.get("messages") else None
    user_content = rewritten_query if rewritten_query else (last_msg.content if last_msg else "")

    # 获取工具文本
    tools_text = await get_tools_and_skills_text()

    base_prompt = await prompt_loader.get_prompt("booking", "system_prompt")
    
    system_prompt = prompt_renderer.render(base_prompt, {
        "recommendations": recommendations,
        "tools_text": tools_text,
        "user_profile": memory.get("user_profile", {}) if memory else {},
        "extracted_info": extracted_info
    })


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
