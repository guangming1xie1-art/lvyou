"""
主工作流图
使用 LangGraph StateGraph 构建主图，按顺序调用 4 个子图
支持 Token 用量自动累加
"""
from typing import TypedDict, Dict, Any, Optional, List, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
import operator
import logging

from src.workflows.subgraphs import (
    build_collect_info_graph,
    build_search_graph,
    build_recommend_graph,
    build_booking_graph,
)

logger = logging.getLogger(__name__)


# ============ 主工作流状态定义 ============

class MainWorkflowState(TypedDict):
    """
    主工作流状态
    使用 Annotated[Dict, operator.add] 实现 usage 自动累加
    """
    # 输入
    messages: Sequence[BaseMessage]
    user_message: str
    
    # 中间结果
    collected_info: Optional[Dict[str, Any]]
    search_results: Optional[Dict[str, Any]]
    recommendations: Optional[List[Dict[str, Any]]]
    booking_confirmation: Optional[Dict[str, Any]]
    
    # Token 用量累加器（自动累加）
    usage: Annotated[Dict[str, int], operator.add]
    
    # 最终输出
    final_response: Optional[Dict[str, Any]]


# ============ 预编译子图实例（单例模式） ============

_collect_info_graph = None
_search_graph = None
_recommend_graph = None
_booking_graph = None


def get_collect_info_graph():
    """获取信息收集子图（懒加载）"""
    global _collect_info_graph
    if _collect_info_graph is None:
        _collect_info_graph = build_collect_info_graph()
    return _collect_info_graph


def get_search_graph():
    """获取搜索子图（懒加载）"""
    global _search_graph
    if _search_graph is None:
        _search_graph = build_search_graph()
    return _search_graph


def get_recommend_graph():
    """获取推荐子图（懒加载）"""
    global _recommend_graph
    if _recommend_graph is None:
        _recommend_graph = build_recommend_graph()
    return _recommend_graph


def get_booking_graph():
    """获取预订子图（懒加载）"""
    global _booking_graph
    if _booking_graph is None:
        _booking_graph = build_booking_graph()
    return _booking_graph


# ============ 主工作流节点 ============

def collect_node(state: MainWorkflowState) -> Dict[str, Any]:
    """
    信息收集节点
    调用 collect_info_graph 子图
    """
    user_message = state.get("user_message", "")
    
    logger.info(f"[Main Workflow] collect_node: processing message")
    
    # 调用子图
    subgraph = get_collect_info_graph()
    result = subgraph.invoke({
        "user_message": user_message,
        "collected_info": None,
        "usage": {"prompt": 0, "completion": 0, "total": 0}
    })
    
    # 返回结果和用量（usage 会自动累加）
    return {
        "collected_info": result.get("collected_info"),
        "usage": result.get("usage", {"prompt": 0, "completion": 0, "total": 0})
    }


def search_node(state: MainWorkflowState) -> Dict[str, Any]:
    """
    搜索节点
    调用 search_graph 子图
    """
    user_message = state.get("user_message", "")
    collected_info = state.get("collected_info", {})
    
    logger.info(f"[Main Workflow] search_node: processing with collected_info")
    
    # 调用子图
    subgraph = get_search_graph()
    result = subgraph.invoke({
        "user_message": user_message,
        "collected_info": collected_info,
        "search_results": None,
        "usage": {"prompt": 0, "completion": 0, "total": 0}
    })
    
    return {
        "search_results": result.get("search_results"),
        "usage": result.get("usage", {"prompt": 0, "completion": 0, "total": 0})
    }


def recommend_node(state: MainWorkflowState) -> Dict[str, Any]:
    """
    推荐节点
    调用 recommend_graph 子图
    """
    user_message = state.get("user_message", "")
    collected_info = state.get("collected_info", {})
    search_results = state.get("search_results", {})
    
    logger.info(f"[Main Workflow] recommend_node: generating recommendations")
    
    # 调用子图
    subgraph = get_recommend_graph()
    result = subgraph.invoke({
        "user_message": user_message,
        "collected_info": collected_info,
        "search_results": search_results,
        "recommendations": None,
        "usage": {"prompt": 0, "completion": 0, "total": 0}
    })
    
    return {
        "recommendations": result.get("recommendations", []),
        "usage": result.get("usage", {"prompt": 0, "completion": 0, "total": 0})
    }


def booking_node(state: MainWorkflowState) -> Dict[str, Any]:
    """
    预订节点
    调用 booking_graph 子图
    """
    user_message = state.get("user_message", "")
    collected_info = state.get("collected_info", {})
    recommendations = state.get("recommendations", [])
    
    logger.info(f"[Main Workflow] booking_node: processing booking")
    
    # 调用子图
    subgraph = get_booking_graph()
    result = subgraph.invoke({
        "user_message": user_message,
        "collected_info": collected_info,
        "recommendations": recommendations,
        "booking_confirmation": None,
        "usage": {"prompt": 0, "completion": 0, "total": 0}
    })
    
    return {
        "booking_confirmation": result.get("booking_confirmation"),
        "usage": result.get("usage", {"prompt": 0, "completion": 0, "total": 0})
    }


def finalize_node(state: MainWorkflowState) -> Dict[str, Any]:
    """
    最终化节点
    生成最终响应，包含所有中间结果和总用量
    """
    logger.info(f"[Main Workflow] finalize_node: generating final response")
    
    final_response = {
        "collected_info": state.get("collected_info"),
        "search_results": state.get("search_results"),
        "recommendations": state.get("recommendations"),
        "booking_confirmation": state.get("booking_confirmation"),
        "total_usage": state.get("usage", {"prompt": 0, "completion": 0, "total": 0}),
        "status": "success"
    }
    
    return {
        "final_response": final_response
    }


# ============ 构建主工作流图 ============

def build_main_workflow():
    """
    构建主工作流图
    执行顺序: collect → search → recommend → booking → finalize → END
    """
    graph = StateGraph(MainWorkflowState)
    
    # 添加节点
    graph.add_node("collect", collect_node)
    graph.add_node("search", search_node)
    graph.add_node("recommend", recommend_node)
    graph.add_node("booking", booking_node)
    graph.add_node("finalize", finalize_node)
    
    # 设置边（顺序执行）
    graph.set_entry_point("collect")
    graph.add_edge("collect", "search")
    graph.add_edge("search", "recommend")
    graph.add_edge("recommend", "booking")
    graph.add_edge("booking", "finalize")
    graph.add_edge("finalize", END)
    
    return graph.compile()


# ============ 主工作流单例 ============

_main_workflow = None


def get_main_workflow():
    """获取主工作流实例（懒加载单例）"""
    global _main_workflow
    if _main_workflow is None:
        logger.info("Building main workflow...")
        _main_workflow = build_main_workflow()
        logger.info("Main workflow built successfully")
    return _main_workflow


# ============ 便捷调用函数 ============

async def run_main_workflow(user_message: str) -> Dict[str, Any]:
    """
    运行主工作流的便捷函数
    
    Args:
        user_message: 用户消息
        
    Returns:
        包含所有结果和总用量的字典
    """
    workflow = get_main_workflow()
    
    # 初始状态
    initial_state = {
        "messages": [],
        "user_message": user_message,
        "collected_info": None,
        "search_results": None,
        "recommendations": None,
        "booking_confirmation": None,
        "usage": {"prompt": 0, "completion": 0, "total": 0},
        "final_response": None
    }
    
    # 执行工作流
    logger.info(f"Running main workflow for message: {user_message[:50]}...")
    result = await workflow.ainvoke(initial_state)
    
    return result.get("final_response", {})


def run_main_workflow_sync(user_message: str) -> Dict[str, Any]:
    """
    同步运行主工作流
    
    Args:
        user_message: 用户消息
        
    Returns:
        包含所有结果和总用量的字典
    """
    workflow = get_main_workflow()
    
    # 初始状态
    initial_state = {
        "messages": [],
        "user_message": user_message,
        "collected_info": None,
        "search_results": None,
        "recommendations": None,
        "booking_confirmation": None,
        "usage": {"prompt": 0, "completion": 0, "total": 0},
        "final_response": None
    }
    
    # 执行工作流
    logger.info(f"Running main workflow (sync) for message: {user_message[:50]}...")
    result = workflow.invoke(initial_state)
    
    return result.get("final_response", {})


# ============ 导出 ============

__all__ = [
    "MainWorkflowState",
    "build_main_workflow",
    "get_main_workflow",
    "run_main_workflow",
    "run_main_workflow_sync",
]
