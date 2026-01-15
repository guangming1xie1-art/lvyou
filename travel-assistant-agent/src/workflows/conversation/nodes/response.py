"""
响应生成节点 - 生成最终回复
"""
from typing import Dict, Any
from ..state import ConversationState
import logging

logger = logging.getLogger(__name__)


async def generate_response(state: ConversationState) -> ConversationState:
    """响应生成节点：生成最终回复"""

    try:
        intent = state.get("intent", "general")

        # 根据不同的意图生成不同的响应
        if intent == "search":
            response_text = _generate_search_response(state)
        elif intent == "recommend":
            response_text = _generate_recommend_response(state)
        elif intent == "book":
            response_text = _generate_booking_response(state)
        else:
            response_text = _generate_general_response(state)

        logger.info(f"Response generation: Generated response for intent '{intent}'")

        return {
            **state,
            "response": response_text,
            "workflow_status": "completed",
            "stage": "completed"
        }

    except Exception as e:
        logger.error(f"Response generation failed: {str(e)}")
        return {
            **state,
            "error_message": f"响应生成失败: {str(e)}",
            "workflow_status": "failed",
            "response": "抱歉，处理您的请求时出现了错误。请稍后重试。"
        }


def _generate_search_response(state: ConversationState) -> str:
    """生成搜索响应"""
    search_results = state.get("search_results", [])
    if not search_results:
        return "抱歉，没有找到相关的搜索结果。"

    response_parts = ["根据您的搜索，我为您找到了以下信息：\n"]

    for result in search_results:
        response_parts.append(f"\n**{result.get('title', '')}**\n")
        response_parts.append(f"{result.get('description', '')}\n")

    response_parts.append("\n如需更多信息或具体推荐，请告诉我！")
    return "".join(response_parts)


def _generate_recommend_response(state: ConversationState) -> str:
    """生成推荐响应"""
    recommendations = state.get("recommendations", [])
    if not recommendations:
        return "抱歉，暂时无法为您生成推荐。请提供更多详细信息。"

    response_parts = ["根据您的需求，我为您制定了以下推荐方案：\n"]

    for rec in recommendations:
        response_parts.append(f"\n**{rec.get('title', '')}**\n")
        response_parts.append(f"{rec.get('description', '')}\n")

    response_parts.append("\n如果您对这个方案满意，我可以帮您进行预订。")
    return "".join(response_parts)


def _generate_booking_response(state: ConversationState) -> str:
    """生成预订响应"""
    booking_result = state.get("booking_result", {})
    booking_confirmed = state.get("booking_confirmed", False)

    if not booking_confirmed or not booking_result:
        return "抱歉，预订未能完成。请稍后重试。"

    response = f"""预订成功！🎉

**预订编号：** {booking_result.get('booking_id', 'N/A')}
**确认码：** {booking_result.get('confirmation_code', 'N/A')}
**目的地：** {booking_result.get('destination', 'N/A')}
**出行日期：** {booking_result.get('travel_date', 'N/A')}
**总价：** ¥{booking_result.get('total_price', 0):.2f}

请保存好您的预订信息，祝您旅途愉快！
"""
    return response


def _generate_general_response(state: ConversationState) -> str:
    """生成通用响应"""
    user_message = state.get("user_message", "")

    response = """感谢您的咨询！

我可以帮您：
- 📍 搜索旅游目的地信息
- 💡 个性化行程推荐
- ✈️ 航班和酒店预订
- 🎯 旅游攻略建议

请告诉我您的具体需求，例如：
"搜索北京的景点"
"推荐5天的日本旅游行程"
"预订下个月去上海的机票"
"""
    return response
