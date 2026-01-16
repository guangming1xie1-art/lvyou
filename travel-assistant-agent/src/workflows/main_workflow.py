"""
【第3、4、5层】主工作流

- 第5层: DeepAgent 顶层代理
- 第4层: 主工作流 StateGraph（按顺序执行4个子代理）
- 第3层: call_subagent_node 工厂函数
"""
from typing import Dict, Any, Sequence, Annotated, Optional
import operator
import logging

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
from langchain_openai import ChatOpenAI

from deepagents import create_deep_agent
from src.workflows.subagents import (
    get_info_collection_agent,
    get_search_agent,
    get_recommend_agent,
    get_booking_agent,
)
from src.config import settings

logger = logging.getLogger(__name__)


# ============ MainState 定义（第4层）============

class MainState(dict):
    """主工作流状态"""
    messages: Sequence[BaseMessage]
    user_message: str
    collected_info: Optional[Dict]
    search_results: Optional[Dict]
    recommendations: Optional[Dict]
    booking_confirmation: Optional[Dict]
    usage: Annotated[Dict[str, int], operator.add]  # ← 自动累加
    final_response: Optional[str]


# ============ 第3层：call_subagent_node 工厂函数 ============

def call_subagent_node(subagent_getter, output_key: str):
    """
    工厂函数：创建调用子代理的节点
    
    Args:
        subagent_getter: 获取子代理的函数（懒加载）
        output_key: 输出数据存储的键名
    
    Returns:
        节点函数
    """
    async def _node(state: MainState) -> Dict[str, Any]:
        try:
            # 获取子代理
            subagent = subagent_getter()
            
            # 准备输入状态
            last_msg = state.get("messages", [])[-1] if state.get("messages") else None
            user_content = last_msg.content if last_msg else state.get("user_message", "")
            
            input_state = {
                "messages": [HumanMessage(content=user_content)],
                "usage": {"prompt": 0, "completion": 0, "total": 0},
                "collected_info": state.get("collected_info"),
                "search_results": state.get("search_results"),
                "recommendations": state.get("recommendations"),
            }
            
            # 调用子代理
            result = await subagent.ainvoke(input_state)
            
            # 提取结果
            output = result.get("output", "")
            usage = result.get("usage", {"prompt": 0, "completion": 0, "total": 0})
            full_state = result.get("state", {})
            
            # 返回更新
            return_dict = {
                "messages": [AIMessage(content=output)],
                "usage": usage,  # ← 自动通过 operator.add 累加
            }
            
            # 根据 output_key 存储特定数据
            if output_key == "collected_info":
                return_dict["collected_info"] = full_state.get("collected_info", {})
            elif output_key == "search_results":
                return_dict["search_results"] = full_state.get("search_results", {})
            elif output_key == "recommendations":
                return_dict["recommendations"] = full_state.get("recommendations", {})
            elif output_key == "booking_confirmation":
                return_dict["booking_confirmation"] = full_state.get("booking_confirmation", {})
            
            logger.info(f"Node '{output_key}' completed, usage: {usage}")
            return return_dict
        
        except Exception as e:
            logger.error(f"Node '{output_key}' failed: {e}")
            return {
                "messages": [AIMessage(content=f"Error in {output_key}: {e}")],
                "usage": {"prompt": 0, "completion": 0, "total": 0},
                output_key: {"error": str(e)}
            }
    
    return _node


# ============ 第4层：主工作流 StateGraph ============

def build_main_graph() -> StateGraph:
    """构建主工作流图"""
    graph = StateGraph(MainState)
    
    # 添加4个节点
    graph.add_node("collect", call_subagent_node(get_info_collection_agent, "collected_info"))
    graph.add_node("search", call_subagent_node(get_search_agent, "search_results"))
    graph.add_node("recommend", call_subagent_node(get_recommend_agent, "recommendations"))
    graph.add_node("booking", call_subagent_node(get_booking_agent, "booking_confirmation"))
    
    # 定义顺序执行
    graph.add_edge("collect", "search")
    graph.add_edge("search", "recommend")
    graph.add_edge("recommend", "booking")
    graph.add_edge("booking", END)
    
    # 设置入口点
    graph.set_entry_point("collect")
    
    return graph.compile()


# ============ 第5层：DeepAgent 顶层代理 ============

_main_agent: Optional[Any] = None


def get_or_create_main_agent() -> Any:
    """
    获取或创建主代理（全局单例）
    
    Returns:
        CompiledStateGraph 实例
    """
    global _main_agent
    if _main_agent is None:
        logger.info("Creating main DeepAgent...")
        
        # 获取 LLM（可选，主要用于元数据）
        llm = ChatOpenAI(
            model=settings.llm_model if hasattr(settings, 'llm_model') else "qwen-turbo",
            temperature=0,
            api_key=settings.dashscope_api_key if hasattr(settings, 'dashscope_api_key') else None,
            base_url=settings.dashscope_base_url if hasattr(settings, 'dashscope_base_url') else None,
        )
        
        # 构建主图
        main_runnable = build_main_graph()
        
        # 创建 DeepAgent
        _main_agent = create_deep_agent(
            model=llm,
            subagents=[
                get_info_collection_agent(),
                get_search_agent(),
                get_recommend_agent(),
                get_booking_agent(),
            ],
            system_prompt="""你是旅游协调员，负责协调4个子代理完成用户的旅游预订需求。

工作流程：
1. 信息收集员：收集用户的旅游需求（目的地、时间、预算等）
2. 搜索员：搜索相关的目的地、酒店、航班信息
3. 推荐员：生成个性化旅游推荐方案
4. 预订员：完成用户选定的预订

你的职责是确保整个流程顺利进行，并向用户提供最终的预订确认。
"""
        )
        
        logger.info("Main DeepAgent created successfully")
    
    return _main_agent


# ============ 便捷接口 ============

async def run_main_workflow_async(user_message: str) -> Dict[str, Any]:
    """
    异步运行主工作流
    
    Args:
        user_message: 用户输入消息
    
    Returns:
        {
            "collected_info": {...},
            "search_results": {...},
            "recommendations": {...},
            "booking_confirmation": {...},
            "total_usage": {"prompt": ..., "completion": ..., "total": ...},
            "messages": [...]
        }
    """
    main_agent = get_or_create_main_agent()
    
    initial_state = {
        "messages": [HumanMessage(content=user_message)],
        "user_message": user_message,
        "collected_info": None,
        "search_results": None,
        "recommendations": None,
        "booking_confirmation": None,
        "usage": {"prompt": 0, "completion": 0, "total": 0},
        "final_response": None,
    }
    
    result = await main_agent.ainvoke(initial_state)
    
    return {
        "collected_info": result.get("collected_info"),
        "search_results": result.get("search_results"),
        "recommendations": result.get("recommendations"),
        "booking_confirmation": result.get("booking_confirmation"),
        "total_usage": result.get("usage", {"prompt": 0, "completion": 0, "total": 0}),
        "messages": result.get("messages", []),
        "final_response": result.get("final_response"),
    }


def run_main_workflow_sync(user_message: str) -> Dict[str, Any]:
    """
    同步运行主工作流（仅用于测试）
    
    Args:
        user_message: 用户输入消息
    
    Returns:
        同 run_main_workflow_async
    """
    import asyncio
    return asyncio.run(run_main_workflow_async(user_message))


__all__ = [
    "MainState",
    "build_main_graph",
    "get_or_create_main_agent",
    "run_main_workflow_async",
    "run_main_workflow_sync",
]
