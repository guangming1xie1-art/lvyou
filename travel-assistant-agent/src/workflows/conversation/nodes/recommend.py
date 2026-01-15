"""
推荐节点 - 处理推荐相关的任务
"""
from typing import Dict, Any
from ..state import ConversationState
import logging

logger = logging.getLogger(__name__)


async def plan_recommend(state: ConversationState) -> ConversationState:
    """推荐规划节点"""

    try:
        user_requirements = state.get("user_requirements", {})

        # 生成推荐参数
        recommend_parameters = {
            "destination": user_requirements.get("destination", "未知目的地"),
            "budget": user_requirements.get("budget", None),
            "preferences": user_requirements.get("preferences", {}),
            "travel_date": user_requirements.get("start_date", None)
        }

        logger.info(f"Recommend planning: Generated parameters")

        return {
            **state,
            "recommend_parameters": recommend_parameters,
            "stage": "recommend_planning"
        }

    except Exception as e:
        logger.error(f"Recommend planning failed: {str(e)}")
        return {
            **state,
            "error_message": f"推荐规划失败: {str(e)}",
            "workflow_status": "failed"
        }


async def execute_recommend(state: ConversationState) -> ConversationState:
    """推荐执行节点"""

    try:
        recommend_parameters = state.get("recommend_parameters", {})
        search_results = state.get("search_results", [])

        # 简化版：生成推荐结果
        # 实际实现应该使用 RecommendationAgent 进行智能推荐
        recommendations = [
            {
                "type": "itinerary",
                "title": "推荐行程",
                "description": f"根据您的需求定制的 {recommend_parameters.get('destination', '')} 之旅",
                "details": {
                    "days": 5,
                    "highlights": ["景点A", "景点B", "景点C"]
                }
            },
            {
                "type": "budget_breakdown",
                "title": "预算分配",
                "description": "合理的费用分配建议",
                "details": {
                    "accommodation": 40,
                    "transportation": 30,
                    "food": 20,
                    "activities": 10
                }
            }
        ]

        logger.info(f"Recommend execution: Generated {len(recommendations)} recommendations")

        return {
            **state,
            "recommendations": recommendations,
            "recommend_executed": True,
            "stage": "recommend_completed"
        }

    except Exception as e:
        logger.error(f"Recommend execution failed: {str(e)}")
        return {
            **state,
            "error_message": f"推荐执行失败: {str(e)}",
            "workflow_status": "failed",
            "recommend_executed": False
        }
