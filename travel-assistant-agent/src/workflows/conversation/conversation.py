"""
LangGraph 对话工作流主文件
创建完整的对话工作流图
"""
from typing import Any
import logging

# 导入 LangGraph 相关模块
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not available, conversation workflow will be limited")

# 导入节点
from .nodes import (
    process_entry,
    route_intent,
    should_route,
    plan_search,
    execute_search,
    plan_recommend,
    execute_recommend,
    plan_booking,
    execute_booking,
    generate_response
)
from .state import ConversationState

logger = logging.getLogger(__name__)


def create_conversation_workflow():
    """创建完整的对话工作流"""

    if not LANGGRAPH_AVAILABLE:
        logger.warning("LangGraph is not available, cannot create workflow")
        return None

    workflow = StateGraph(ConversationState)

    # 添加节点
    workflow.add_node("entry", process_entry)
    workflow.add_node("intent_router", route_intent)
    workflow.add_node("search_planning", plan_search)
    workflow.add_node("search_execution", execute_search)
    workflow.add_node("recommend_planning", plan_recommend)
    workflow.add_node("recommend_execution", execute_recommend)
    workflow.add_node("booking_planning", plan_booking)
    workflow.add_node("booking_execution", execute_booking)
    workflow.add_node("response_generation", generate_response)

    # 设置入口和边
    workflow.set_entry_point("entry")
    workflow.add_edge("entry", "intent_router")

    # 条件路由
    workflow.add_conditional_edges(
        "intent_router",
        should_route,
        {
            "search_planning": "search_planning",
            "recommend_planning": "recommend_planning",
            "booking_planning": "booking_planning",
            "response_generation": "response_generation"
        }
    )

    # 搜索流
    workflow.add_edge("search_planning", "search_execution")
    workflow.add_edge("search_execution", "response_generation")

    # 推荐流
    workflow.add_edge("recommend_planning", "recommend_execution")
    workflow.add_edge("recommend_execution", "response_generation")

    # 预订流
    workflow.add_edge("booking_planning", "booking_execution")
    workflow.add_edge("booking_execution", "response_generation")

    # 最终响应
    workflow.add_edge("response_generation", END)

    logger.info("Conversation workflow created successfully")
    return workflow.compile()


# 全局实例
conversation_workflow = create_conversation_workflow()


class ConversationWorkflow:
    """对话工作流包装类"""

    def __init__(self):
        """初始化对话工作流"""
        self.workflow = conversation_workflow
        self.is_available = LANGGRAPH_AVAILABLE

    async def invoke(self, user_message: str) -> ConversationState:
        """
        执行对话工作流

        Args:
            user_message: 用户输入消息

        Returns:
            工作流执行结果
        """
        if not self.is_available:
            logger.error("Conversation workflow is not available")
            return {
                "user_message": user_message,
                "response": "抱歉，对话服务暂时不可用。",
                "workflow_status": "failed",
                "error_message": "LangGraph not available"
            }

        # 初始化状态
        initial_state: ConversationState = {
            "user_message": user_message,
            "conversation_history": [],
            "messages": [],
            "intent": "",
            "user_requirements": {},
            "search_query": None,
            "search_results": None,
            "search_executed": False,
            "recommend_parameters": None,
            "recommendations": None,
            "recommend_executed": False,
            "booking_details": None,
            "booking_confirmed": False,
            "booking_result": None,
            "response": "",
            "workflow_status": "active",
            "error_message": None,
            "cost_tokens": {}
        }

        # 执行工作流
        final_state = await self.workflow.ainvoke(initial_state)

        return final_state

    async def stream(self, user_message: str):
        """
        流式执行对话工作流

        Args:
            user_message: 用户输入消息

        Yields:
            工作流执行过程中的状态更新
        """
        if not self.is_available:
            yield {
                "user_message": user_message,
                "response": "抱歉，对话服务暂时不可用。",
                "workflow_status": "failed",
                "error_message": "LangGraph not available"
            }
            return

        # 初始化状态
        initial_state: ConversationState = {
            "user_message": user_message,
            "conversation_history": [],
            "messages": [],
            "intent": "",
            "user_requirements": {},
            "search_query": None,
            "search_results": None,
            "search_executed": False,
            "recommend_parameters": None,
            "recommendations": None,
            "recommend_executed": False,
            "booking_details": None,
            "booking_confirmed": False,
            "booking_result": None,
            "response": "",
            "workflow_status": "active",
            "error_message": None,
            "cost_tokens": {}
        }

        # 流式执行工作流
        async for state_update in self.workflow.astream(initial_state):
            yield state_update
