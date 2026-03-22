"""
【第3、4、5层】主工作流

- 第5层: DeepAgent 顶层代理
- 第4层: 主工作流 StateGraph（按顺序执行4个子代理）
- 第3层: call_subagent_node 工厂函数

集成记忆系统和Query改写功能
"""
from typing import Dict, Any, Sequence, Annotated, Optional, List
import operator
import logging

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
from workflows.subgraphs.common import merge_dicts
from deepagents import create_deep_agent
from workflows.subagents import (
    get_info_collection_agent,
    get_search_agent,
    get_recommend_agent,
    get_booking_agent,
)
from workflows.subgraphs import (
    build_collect_info_graph,
    build_search_graph,
    build_recommend_graph,
    build_booking_graph,
)
from workflows.subgraphs.collect import _route_collect_main
from conf import settings
from llm.factory import LLMFactory

# 导入记忆系统模块
try:
    from memory.memory_gateway import memory_gateway
    from memory.memory_retriever import memory_retriever
    from memory.query_rewriter import query_rewriter
    from memory.session_manager import session_manager
    MEMORY_AVAILABLE = True
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("Memory system modules not available, memory features disabled")
    MEMORY_AVAILABLE = False

logger = logging.getLogger(__name__)

# ============ MainState 定义（第4层）============

class MainState(dict):
    """主工作流状态（增强版，支持对话历史和记忆系统）"""
    messages: Sequence[BaseMessage]
    user_message: str
    collected_info: Optional[Dict]
    collection_message: Optional[str]  # ← 新增：信息收集节点的对话消息（不传递给下游）
    search_results: Optional[Dict]
    recommendations: Optional[Dict]
    booking_confirmation: Optional[Dict]
    usage: Annotated[Dict[str, int], merge_dicts]
    # usage: Annotated[Dict[str, int], operator.add]  # ← 自动累加
    final_response: Optional[str]
    need_clarification: Optional[bool]
    clarification_questions: Optional[List[str]]
    stage: Optional[str]
    conversation_history: Annotated[List[Dict], operator.add]  # ← 新增：对话历史
    # 记忆系统相关字段
    user_id: Optional[int]  # ← 新增：用户ID
    session_id: Optional[str]  # ← 新增：会话ID
    long_term_memory: Optional[Dict[str, Any]]  # ← 新增：长期记忆
    rewritten_query: Optional[str]  # ← 新增：改写后的查询


# ============ 第3层：call_subagent_node 工厂函数 ============

def call_subagent_node(subagent_getter, output_key: str):
    """
    工厂函数：创建调用子代理的节点（增强版，支持对话历史）

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

            # 获取对话历史
            conversation_history = state.get("conversation_history", [])

            input_state = {
                "messages": [HumanMessage(content=user_content)],
                "usage": {"prompt": 0, "completion": 0, "total": 0},
                "collected_info": state.get("collected_info"),
                "collection_message": state.get("collection_message"),
                "search_results": state.get("search_results"),
                "recommendations": state.get("recommendations"),
                "conversation_history": conversation_history,  # ← 传递对话历史
            }

            # 调用子代理
            result = await subagent.ainvoke(input_state)

            # 提取结果
            output = result.get("output", "")
            usage = result.get("usage", {"prompt": 0, "completion": 0, "total": 0})
            full_state = result.get("state", {})

            # 更新对话历史
            new_history = []
            # 添加用户消息
            if user_content:
                new_history.append({
                    "role": "user",
                    "content": user_content,
                    "node": output_key,
                })
            # 添加 AI 回复
            if output:
                new_history.append({
                    "role": "assistant",
                    "content": output,
                    "node": output_key,
                })

            # 返回更新
            return_dict = {
                "messages": [AIMessage(content=output)],
                "usage": usage,  # ← 自动通过 operator.add 累加
                "conversation_history": new_history,  # ← 更新对话历史
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
                "conversation_history": [],  # ← 出错时返回空历史
                output_key: {"error": str(e)}
            }

    return _node


# ============ 第4层：主工作流 StateGraph ============
_build_collect_info_graph = build_collect_info_graph()
_build_search_graph = build_search_graph()
_build_recommend_graph = build_recommend_graph()
# _build_booking_graph = build_booking_graph()


async def _memory_preprocess_node(state: MainState) -> Dict[str, Any]:
    """
    记忆系统预处理节点
    
    功能：
    1. 检索长期记忆
    2. Query改写
    3. 管理对话窗口
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    if not MEMORY_AVAILABLE:
        return {}
    
    try:
        user_id = state.get("user_id")
        session_id = state.get("session_id")
        user_message = state.get("user_message", "")
        conversation_history = state.get("conversation_history", [])
        
        if not user_id or not session_id:
            logger.warning("Missing user_id or session_id, skipping memory preprocessing")
            return {}
        
        logger.info(f"Memory preprocessing: user_id={user_id}, session_id={session_id}")
        
        updates = {}
        
        # 1. 检索长期记忆
        if settings.long_term_memory_enabled:
            try:
                long_term_memory = await memory_retriever.retrieve(
                    user_id=user_id,
                    query=user_message,
                    top_k=settings.long_term_memory_top_k,
                    use_hybrid=settings.long_term_memory_use_hybrid
                )
                updates["long_term_memory"] = {
                    "memories": long_term_memory,
                    "count": len(long_term_memory)
                }
                logger.info(f"Retrieved {len(long_term_memory)} long-term memories")
            except Exception as e:
                logger.error(f"Failed to retrieve long-term memory: {e}")
        
        # 2. Query改写
        if settings.query_rewrite_enabled:
            try:
                rewrite_result = await query_rewriter.rewrite(
                    query=user_message,
                    conversation_history=conversation_history,
                    long_term_memory=updates.get("long_term_memory")
                )
                updates["rewritten_query"] = rewrite_result.get("rewritten_query", user_message)
                
                if rewrite_result.get("needs_rewrite"):
                    logger.info(f"Query rewritten: '{user_message}' -> '{updates['rewritten_query']}'")
            except Exception as e:
                logger.error(f"Failed to rewrite query: {e}")
                updates["rewritten_query"] = user_message
        
        # 3. 管理对话窗口
        if settings.session_manager_enabled and conversation_history:
            try:
                window_result = await session_manager.manage_window(
                    user_id=user_id,
                    session_id=session_id,
                    messages=[{"role": msg.get("role"), "content": msg.get("content")} for msg in conversation_history]
                )
                
                if window_result.get("action") != "none":
                    logger.info(f"Window managed: action={window_result.get('action')}")
            except Exception as e:
                logger.error(f"Failed to manage window: {e}")
        
        return updates
    
    except Exception as e:
        logger.error(f"Memory preprocessing failed: {e}")
        return {}


async def _memory_postprocess_node(state: MainState) -> Dict[str, Any]:
    """
    记忆系统后处理节点
    
    功能：
    1. 保存对话消息
    2. 更新会话摘要
    3. 提取并保存用户偏好
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    if not MEMORY_AVAILABLE:
        return {}
    
    try:
        user_id = state.get("user_id")
        session_id = state.get("session_id")
        messages = state.get("messages", [])
        
        if not user_id or not session_id:
            return {}
        
        logger.info(f"Memory postprocessing: user_id={user_id}, session_id={session_id}")
        
        # 1. 保存对话消息
        if messages:
            for msg in messages:
                role = "user" if isinstance(msg, HumanMessage) else "assistant"
                content = msg.content
                
                await memory_gateway.save_message(
                    user_id=user_id,
                    session_id=session_id,
                    role=role,
                    content=content
                )
        
        # 2. 更新会话摘要（如果对话较长）
        if len(messages) > 5:
            try:
                conversation_text = "\n".join([msg.content for msg in messages[-10:]])
                summary = await session_manager._generate_summary(
                    [{"role": "user" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content} for msg in messages[-10:]]
                )
                
                await memory_gateway.update_session_summary(
                    user_id=user_id,
                    session_id=session_id,
                    summary=summary
                )
                
                logger.info(f"Updated session summary")
            except Exception as e:
                logger.error(f"Failed to update session summary: {e}")
        
        return {}
    
    except Exception as e:
        logger.error(f"Memory postprocessing failed: {e}")
        return {}


def build_main_graph() -> StateGraph:
    """构建主工作流图"""
    graph = StateGraph(MainState)

    # 添加记忆系统预处理节点
    if MEMORY_AVAILABLE and settings.memory_system_enabled:
        graph.add_node("memory_preprocess", _memory_preprocess_node)
    
    # 添加4个节点
    graph.add_node("collect", _build_collect_info_graph)
    graph.add_node("search", _build_search_graph)
    graph.add_node("recommend", _build_recommend_graph)
    # graph.add_node("booking", _build_booking_graph)
    
    # 添加记忆系统后处理节点
    if MEMORY_AVAILABLE and settings.memory_system_enabled:
        graph.add_node("memory_postprocess", _memory_postprocess_node)

    # 设置入口点
    if MEMORY_AVAILABLE and settings.memory_system_enabled:
        graph.set_entry_point("memory_preprocess")
        graph.add_edge("memory_preprocess", "collect")
    else:
        graph.set_entry_point("collect")

    # ✅ 使用条件边替代固定边
    graph.add_conditional_edges(
        "collect",
        _route_collect_main,
        {
            "search": "search",
            "end": END
        }
    )

    # 搜索阶段可能需要澄清
    graph.add_conditional_edges(
        "search",
        lambda state: "end" if state.get("need_clarification") else "recommend",
        {
            "recommend": "recommend",
            "end": END
        }
    )

    # 推荐阶段可能需要澄清
    # graph.add_conditional_edges(
    #     "recommend",
    #     lambda state: "end" if state.get("need_clarification") else "booking",
    #     {
    #         "booking": "booking",
    #         "end": END
    #     }
    # )
    
    # 添加记忆系统后处理节点的边
    if MEMORY_AVAILABLE and settings.memory_system_enabled:
        # 从 recommend 到 memory_postprocess
        graph.add_edge("recommend", "memory_postprocess")
        # 从 memory_postprocess 到 END
        graph.add_edge("memory_postprocess", END)
    else:
        graph.add_edge("recommend", END)

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
        llm = LLMFactory.create_model_by_tier(tier="cheap")
        
        # 构建主图
        main_runnable = build_main_graph()
        _main_agent = main_runnable
        
        logger.info("Main DeepAgent created successfully")
    
    return _main_agent


# ============ 便捷接口 ============

async def run_main_workflow_async(
    user_message: str,
    user_id: Optional[int] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    异步运行主工作流

    Args:
        user_message: 用户输入消息
        user_id: 用户ID（用于记忆系统）
        session_id: 会话ID（用于记忆系统）

    Returns:
        {
            "collected_info": {...},
            "search_results": {...},
            "recommendations": {...},
            "booking_confirmation": {...},
            "total_usage": {"prompt": ..., "completion": ..., "total": ...},
            "messages": [...],
            "conversation_history": [...],
            "long_term_memory": {...},
            "rewritten_query": "..."
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
        "need_clarification": False,
        "clarification_questions": [],
        "stage": None,
        "usage": {"prompt": 0, "completion": 0, "total": 0},
        "final_response": None,
        "conversation_history": [],  # ← 初始化对话历史
        "user_id": user_id,  # ← 新增：用户ID
        "session_id": session_id,  # ← 新增：会话ID
        "long_term_memory": None,  # ← 新增：长期记忆
        "rewritten_query": None,  # ← 新增：改写后的查询
    }

    result = await main_agent.ainvoke(initial_state)

    messages = result.get("messages") or []
    final_response = result.get("final_response")
    if not final_response and messages:
        last_msg = messages[-1]
        final_response = getattr(last_msg, "content", None)

    return {
        "collected_info": result.get("collected_info") or {},
        "search_results": result.get("search_results") or {},
        "recommendations": result.get("recommendations") or {},
        "booking_confirmation": result.get("booking_confirmation") or {},
        "need_clarification": result.get("need_clarification", False),
        "clarification_questions": result.get("clarification_questions", []),
        "stage": result.get("stage"),
        "total_usage": result.get("usage", {"prompt": 0, "completion": 0, "total": 0}),
        "messages": messages,
        "final_response": final_response,
        "conversation_history": result.get("conversation_history", []),  # ← 返回对话历史
        "long_term_memory": result.get("long_term_memory"),  # ← 返回长期记忆
        "rewritten_query": result.get("rewritten_query"),  # ← 返回改写后的查询
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
