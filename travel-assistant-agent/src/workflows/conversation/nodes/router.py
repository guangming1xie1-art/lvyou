"""
意图识别节点 - 识别用户意图并路由到相应的处理流程
"""
import json
import re
from typing import Dict, Any
from ..state import ConversationState
import logging

logger = logging.getLogger(__name__)


async def route_intent(state: ConversationState) -> ConversationState:
    """意图识别节点"""

    try:
        # 尝试使用 LLM 进行意图识别
        from llm import LLMFactory

        llm = LLMFactory.create_model()

        # 构建意图识别prompt
        prompt = f"""根据用户消息识别用户意图和需求。

用户消息：{state["user_message"]}

请返回JSON格式（仅返回JSON，不要有其他文字）：
{{
    "intent": "search|recommend|book|general",
    "requirements": {{
        "destination": "目的地字符串 or null",
        "start_date": "开始日期字符串 or null",
        "end_date": "结束日期字符串 or null",
        "budget": "预算数值 or null",
        "preferences": {{}}
    }}
}}

要求：
1. intent 字段必须是以下值之一：search, recommend, book, general
2. 提取所有可见的旅游相关信息
3. 对于缺失的信息，设置为 null
"""

        # 调用LLM
        response = await llm.ainvoke(prompt)

        # 解析响应
        content = response.content if hasattr(response, 'content') else str(response)

        # 提取 JSON 部分
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            json_str = json_match.group()
            result = json.loads(json_str)

            intent = result.get("intent", "general")
            requirements = result.get("requirements", {})

            logger.info(f"Intent router: Detected intent '{intent}'")
            return {
                **state,
                "intent": intent,
                "user_requirements": requirements
            }
        else:
            # 无法解析 JSON，使用默认值
            logger.warning(f"Intent router: Could not parse JSON from response: {content[:200]}")
            return {
                **state,
                "intent": "general",
                "user_requirements": {}
            }

    except Exception as e:
        # LLM 调用失败，使用简单规则匹配
        logger.error(f"Intent router: LLM call failed, using fallback: {str(e)}")

        message = state["user_message"].lower()

        # 简单规则匹配
        if any(keyword in message for keyword in ["搜索", "search", "查找", "find"]):
            intent = "search"
        elif any(keyword in message for keyword in ["推荐", "recommend", "建议", "suggest"]):
            intent = "recommend"
        elif any(keyword in message for keyword in ["预订", "book", "预定", "订购"]):
            intent = "book"
        else:
            intent = "general"

        logger.info(f"Intent router: Fallback to intent '{intent}'")
        return {
            **state,
            "intent": intent,
            "user_requirements": {}
        }


def should_route(state: ConversationState) -> str:
    """路由逻辑：返回下一个节点"""

    intent = state.get("intent", "general")

    if intent == "search":
        return "search_planning"
    elif intent == "recommend":
        return "recommend_planning"
    elif intent == "book":
        return "booking_planning"
    else:
        return "response_generation"
