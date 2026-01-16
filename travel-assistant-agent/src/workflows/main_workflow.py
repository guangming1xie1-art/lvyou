"""
【第3、4、5层】主工作流

架构层次：
- 第5层：DeepAgent 顶层代理
- 第4层：主工作流 StateGraph
- 第3层：call_subagent_node 工厂函数
"""
from typing import TypedDict, Dict, Any, Optional, List, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage
from collections import Counter
import operator
import logging

from deepagents import create_deep_agent

from src.workflows.subagents import (
    get_info_collection_agent,
    get_search_agent,
    get_recommend_agent,
    get_booking_agent,
)
from src.llm import LLMFactory

logger = logging.getLogger(__name__)


# ============ 【第4层】主工作流状态定义 ============

class MainState(TypedDict):
    """
    主工作流状态
    使用 Annotated[Dict, operator.add] 实现 usage 自动累加
    """
    # 输入
    messages: Sequence[BaseMessage]
    user_message: str
    
    # 中间结果（从子代理传递）
    collected_info: Optional[Dict[str, Any]]
    search_results: Optional[Dict[str, Any]]
    recommendations: Optional[List[Dict[str, Any]]]
    booking_confirmation: Optional[Dict[str, Any]]
    
    # Token 用量累加器（自动累加）
    usage: Annotated[Dict[str, int], operator.add]
    
    # 最终输出
    final_response: Optional[str]


# ============ 【第3层】call_subagent_node 工厂函数 ============

def call_subagent_node(subagent_name: str):
    """
    工厂函数，创建调用子代理的节点函数
    
    Args:
        subagent_name: 子代理名称 ("info_collection", "search", "recommend", "booking")
    
    Returns:
        节点函数，接受 MainState 并返回更新
    """
    def _node(state: MainState) -> Dict[str, Any]:
        """
        节点函数：调用指定的 CompiledSubAgent
        
        Args:
            state: 主工作流状态
        
        Returns:
            更新的状态字段（messages, usage, 以及对应的结果字段）
        """
        # 获取最后一条用户消息
        user_message = state.get("user_message", "")
        if not user_message and state.get("messages"):
            last_msg = state["messages"][-1]
            user_message = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
        
        logger.info(f"[call_subagent_node] Calling subagent: {subagent_name}")
        
        # 获取对应的 CompiledSubAgent
        if subagent_name == "info_collection":
            agent = get_info_collection_agent()
            result_key = "collected_info"
            
            # 构建输入状态
            input_state = {
                "user_message": user_message,
                "collected_info": None,
                "usage": {"prompt": 0, "completion": 0, "total": 0}
            }
        
        elif subagent_name == "search":
            agent = get_search_agent()
            result_key = "search_results"
            
            input_state = {
                "user_message": user_message,
                "collected_info": state.get("collected_info", {}),
                "search_results": None,
                "usage": {"prompt": 0, "completion": 0, "total": 0}
            }
        
        elif subagent_name == "recommend":
            agent = get_recommend_agent()
            result_key = "recommendations"
            
            input_state = {
                "user_message": user_message,
                "collected_info": state.get("collected_info", {}),
                "search_results": state.get("search_results", {}),
                "recommendations": None,
                "usage": {"prompt": 0, "completion": 0, "total": 0}
            }
        
        elif subagent_name == "booking":
            agent = get_booking_agent()
            result_key = "booking_confirmation"
            
            input_state = {
                "user_message": user_message,
                "collected_info": state.get("collected_info", {}),
                "recommendations": state.get("recommendations", []),
                "booking_confirmation": None,
                "usage": {"prompt": 0, "completion": 0, "total": 0}
            }
        
        else:
            raise ValueError(f"Unknown subagent: {subagent_name}")
        
        # 调用 CompiledSubAgent 的 invoke() 方法
        try:
            res = agent.invoke(input_state)
            
            # 提取结果
            output = res["output"]
            usage = Counter(res.get("usage") or {})
            if usage.get("total", 0) == 0:
                usage["total"] = usage.get("prompt", 0) + usage.get("completion", 0)
            full_state = res["state"]
            
            # 返回更新（usage 会通过 operator.add 自动累加）
            update = {
                "messages": [HumanMessage(content=output)],
                "usage": usage,  # ← 自动通过 operator.add 累加（Counter 支持 +）
            }
            
            # 添加结果到对应的字段
            if result_key in full_state:
                update[result_key] = full_state[result_key]
            
            logger.info(f"[call_subagent_node] {subagent_name} completed, usage: {usage}")
            
            return update
        
        except Exception as e:
            logger.error(f"[call_subagent_node] {subagent_name} error: {e}")
            
            # 返回错误信息
            return {
                "messages": [HumanMessage(content=f"Error in {subagent_name}: {str(e)}")],
                "usage": Counter({"prompt": 0, "completion": 0, "total": 0}),
            }
    
    return _node


# ============ 【第4层】构建主工作流图 ============

def build_main_graph() -> Any:
    """
    构建主工作流 StateGraph
    
    执行顺序: collect → search → recommend → booking → END
    
    Returns:
        编译后的 StateGraph (CompiledGraph)
    """
    graph = StateGraph(MainState)
    
    # 添加 4 个节点，每个都调用一个 CompiledSubAgent
    graph.add_node("collect", call_subagent_node("info_collection"))
    graph.add_node("search", call_subagent_node("search"))
    graph.add_node("recommend", call_subagent_node("recommend"))
    graph.add_node("booking", call_subagent_node("booking"))
    
    # 设置边（顺序执行）
    graph.set_entry_point("collect")
    graph.add_edge("collect", "search")
    graph.add_edge("search", "recommend")
    graph.add_edge("recommend", "booking")
    graph.add_edge("booking", END)
    
    logger.info("Main workflow graph built")
    
    return graph.compile()


# ============ 【第5层】DeepAgent 顶层代理 ============

_main_agent = None


def get_or_create_main_agent():
    """
    获取或创建 DeepAgent 主代理（单例）
    
    Returns:
        DeepAgent 实例
    """
    global _main_agent
    
    if _main_agent is None:
        # 创建 LLM（使用默认模型）
        try:
            llm = LLMFactory.create_model()
        except Exception as e:
            logger.warning(f"Failed to create LLM: {e}, using None")
            llm = None
        
        # 获取 4 个子代理
        subagents = [
            get_info_collection_agent(),
            get_search_agent(),
            get_recommend_agent(),
            get_booking_agent(),
        ]
        
        # 构建主工作流图
        main_runnable = build_main_graph()
        
        # 创建 DeepAgent
        _main_agent = create_deep_agent(
            model=llm,
            subagents=subagents,
            runnable=main_runnable,
            system_prompt="你是旅游协调员，按顺序调用子代理并完成预订。"
        )
        
        logger.info("Main DeepAgent created")
    
    return _main_agent


# ============ 便捷调用函数 ============

async def run_main_workflow(user_message: str) -> Dict[str, Any]:
    """
    异步运行主工作流的便捷函数
    
    Args:
        user_message: 用户消息
        
    Returns:
        {
            "collected_info": {...},
            "search_results": {...},
            "recommendations": [...],
            "booking_confirmation": {...},
            "total_usage": {"prompt": X, "completion": Y, "total": Z},
            "status": "success"
        }
    """
    main_agent = get_or_create_main_agent()
    
    # 初始状态
    initial_state = {
        "messages": [HumanMessage(content=user_message)],
        "user_message": user_message,
        "collected_info": None,
        "search_results": None,
        "recommendations": None,
        "booking_confirmation": None,
        "usage": {"prompt": 0, "completion": 0, "total": 0},
        "final_response": None
    }
    
    # 调用 DeepAgent
    logger.info(f"Running main workflow for: {user_message[:50]}...")
    result = await main_agent.ainvoke(initial_state)
    
    # 构建最终响应
    final_response = {
        "collected_info": result.get("collected_info"),
        "search_results": result.get("search_results"),
        "recommendations": result.get("recommendations"),
        "booking_confirmation": result.get("booking_confirmation"),
        "total_usage": result.get("usage", {"prompt": 0, "completion": 0, "total": 0}),
        "status": "success"
    }
    
    return final_response


def run_main_workflow_sync(user_message: str) -> Dict[str, Any]:
    """
    同步运行主工作流
    
    Args:
        user_message: 用户消息
        
    Returns:
        包含所有结果和总用量的字典
    """
    main_agent = get_or_create_main_agent()
    
    # 初始状态
    initial_state = {
        "messages": [HumanMessage(content=user_message)],
        "user_message": user_message,
        "collected_info": None,
        "search_results": None,
        "recommendations": None,
        "booking_confirmation": None,
        "usage": {"prompt": 0, "completion": 0, "total": 0},
        "final_response": None
    }
    
    # 调用 DeepAgent（同步）
    logger.info(f"Running main workflow (sync) for: {user_message[:50]}...")
    result = main_agent.invoke(initial_state)
    
    # 构建最终响应
    final_response = {
        "collected_info": result.get("collected_info"),
        "search_results": result.get("search_results"),
        "recommendations": result.get("recommendations"),
        "booking_confirmation": result.get("booking_confirmation"),
        "total_usage": result.get("usage", {"prompt": 0, "completion": 0, "total": 0}),
        "status": "success"
    }
    
    return final_response


# ============ 导出 ============

__all__ = [
    "MainState",
    "call_subagent_node",
    "build_main_graph",
    "get_or_create_main_agent",
    "run_main_workflow",
    "run_main_workflow_sync",
]
