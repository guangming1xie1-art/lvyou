"""
信息收集工作流 - 单节点工作流，收集用户的旅游需求信息
"""

from typing import Dict, Any
import json

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from utils.token_counter import TokenCounter
from llm.factory import LLMFactory
from prompts.prompt_loader import prompt_loader
from prompts.prompt_renderer import prompt_renderer

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
            "collected_info": cached.get("collected_info", {}),
            "collection_message": cached.get("collection_message", "")
        }

    # 加载系统提示词
    system_prompt = await prompt_loader.get_prompt("collect", "system_prompt")
    
    history_text = "\n".join([f"{msg.type}: {msg.content}" for msg in messages[:-1]])
    rendered_prompt = prompt_renderer.render(system_prompt, {"history_text": history_text})

    try:
        llm = LLMFactory.create_model_by_tier(tier="cheap")

        messages = [
            SystemMessage(content=rendered_prompt),
            HumanMessage(content=user_content)
        ]

        result = await llm.ainvoke(
            messages,
            config={"callbacks": [counter]}
        )

        output_text = result.content

        # 尝试解析为 JSON
        try:
            # 去除可能的 Markdown 代码块标记
            cleaned_text = output_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]  # 去掉 ```json
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]  # 去掉 ```
            
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]  # 去掉结尾的 ```
            
            cleaned_text = cleaned_text.strip()
            
            collected_info = json.loads(cleaned_text)
        except:
            collected_info = {"raw": output_text, "complete": False}

        # 提取 collection_message（对话消息）和 collected_info（结构化数据）
        collection_message = collected_info.pop("message", "") if isinstance(collected_info, dict) else ""

        # 缓存结果
        cache_strategy.cache_user_preferences(cache_key, {
            "output": output_text,
            "collected_info": collected_info,
            "collection_message": collection_message
        })

        return {
            "messages": [result],
            "usage": counter.dump(),
            "output": output_text,
            "collected_info": collected_info,
            "collection_message": collection_message
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


def _route_collect_main(state: SubState) -> str:
    """
    主工作流使用的路由函数（在 main_workflow.py 中调用）

    根据信息完整性决定工作流分支
    """
    collected_info = state.get("collected_info", {})
    is_complete = collected_info.get("complete", False)

    import logging
    logger = logging.getLogger(__name__)

    if is_complete:
        logger.info("✅ Info complete, routing to search stage")
        return "search"
    else:
        logger.info("❌ Info incomplete, routing to END (user needs to clarify)")
        return "end"


def build_collect_info_graph() -> StateGraph:
    """构建信息收集子图（简单的单节点图）"""
    graph = StateGraph(SubState)
    graph.add_node("collect", collect_info_node)
    graph.add_edge("collect", END)
    graph.set_entry_point("collect")
    return graph.compile()


__all__ = ["build_collect_info_graph", "_route_collect_main"]
