"""
对话工作流状态定义
使用 TypedDict 定义工作流中的状态结构
"""
from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class ConversationState(TypedDict, total=False):
    """对话工作流状态"""

    # 用户输入
    user_message: str                    # 用户原始消息

    # 对话历史
    conversation_history: List[Dict]     # 历史对话
    messages: List[Any]                  # LangChain Message对象

    # 意图识别
    intent: str                          # 意图：search/recommend/book/general
    user_requirements: Dict              # 解析的用户需求

    # 搜索阶段
    search_query: Optional[str]
    search_results: Optional[List[Dict]]
    search_executed: bool

    # 推荐阶段
    recommend_parameters: Optional[Dict]
    recommendations: Optional[List[Dict]]
    recommend_executed: bool

    # 预订阶段
    booking_details: Optional[Dict]
    booking_confirmed: bool
    booking_result: Optional[Dict]

    # 响应
    response: str                        # 最终回复

    # 元数据
    workflow_status: str                 # active/completed/failed
    error_message: Optional[str]
    cost_tokens: Dict                    # token成本追踪
