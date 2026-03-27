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
import json

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
from workflows.subgraphs.common import merge_dicts

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
    user_id: Optional[int]  # ← 新增：用户 ID
    session_id: Optional[str]  # ← 新增：会话 ID
    memory: Optional[Dict[str, Any]]  # ← 新增：记忆上下文（包含 long_term, short_term, user_profile）
    rewritten_query: Optional[str]  # ← 新增：改写后的查询
    intent: Optional[str]  # ← 新增：意图类型
    extracted_info: Optional[Dict[str, Any]]  # ← 新增：提取的信息
    tools_needed: Optional[List[str]]  # ← 新增：需要的工具
    next_step: Optional[str]  # ← 新增：下一步路由目标


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
            
            # 获取记忆系统相关字段（Memory-First 架构）
            memory = state.get("memory", {})
            rewritten_query = state.get("rewritten_query")
            extracted_info = state.get("extracted_info", {})

            input_state = {
                "messages": [HumanMessage(content=user_content)],
                "usage": {"prompt": 0, "completion": 0, "total": 0},
                "collected_info": state.get("collected_info"),
                "collection_message": state.get("collection_message"),
                "search_results": state.get("search_results"),
                "recommendations": state.get("recommendations"),
                "conversation_history": conversation_history,  # ← 传递对话历史
                "memory": memory,  # ← 传递记忆上下文
                "rewritten_query": rewritten_query,  # ← 传递改写后的查询
                "extracted_info": extracted_info,  # ← 传递提取的信息
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
    记忆预处理节点（Memory-First 架构的入口节点）
    
    功能：
    1. 从向量数据库读取长期记忆（用户画像、偏好）
    2. 从 Redis 读取短期记忆（会话上下文）
    3. 提取用户画像
    4. 填充到 state.memory
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态（包含 memory 字段）
    """
    if not MEMORY_AVAILABLE:
        return {}
    
    try:
        user_id = state.get("user_id")
        session_id = state.get("session_id")
        
        if not user_id or not session_id:
            logger.warning("Missing user_id or session_id, skipping memory loading")
            return {}
        
        logger.info(f"🧠 Memory Loader: user_id={user_id}, session_id={session_id}")
        
        # 1. 读取长期记忆（向量数据库）
        long_term_memory = {}
        if settings.long_term_memory_enabled:
            try:
                long_term_memory = await memory_retriever.retrieve(
                    user_id=str(user_id),
                    k=5
                )
                logger.info(f"✅ Retrieved {len(long_term_memory)} long-term memories")
            except Exception as e:
                logger.error(f"Failed to retrieve long-term memory: {e}")
        
        # 2. 读取短期记忆（Redis）
        short_term_memory = {}
        try:
            short_term_memory = await session_manager.get_memory(session_id=session_id)
            logger.info(f"✅ Retrieved short-term memory")
        except Exception as e:
            logger.error(f"Failed to retrieve short-term memory: {e}")
        
        # 3. 提取用户画像
        user_profile = {
            "preferred_hotel_chain": long_term_memory.get("hotel_chain"),
            "dietary_restrictions": long_term_memory.get("dietary"),
            "budget_range": long_term_memory.get("budget"),
            "travel_style": long_term_memory.get("travel_style"),
            "recent_searches": short_term_memory.get("recent_searches", []),
            "last_destination": short_term_memory.get("last_destination")
        }
        
        # 4. 填充到 memory 字段
        memory = {
            "long_term": long_term_memory,
            "short_term": short_term_memory,
            "user_profile": user_profile
        }
        
        logger.info(f"✅ Memory loaded successfully")
        
        return {
            "memory": memory
        }
    
    except Exception as e:
        logger.error(f"❌ Memory loader failed: {e}")
        return {}


async def _query_rewriter_node(state: MainState) -> Dict[str, Any]:
    """
    查询改写节点（Memory-First 架构的第二节点）
    
    功能：
    1. 结合长期记忆和短期记忆
    2. 将模糊查询改写为语义完整的查询
    3. 处理代词指代和省略信息
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态（包含 rewritten_query 字段）
    """
    if not MEMORY_AVAILABLE:
        return {}
    
    try:
        user_message = state.get("user_message", "")
        memory = state.get("memory", {})
        conversation_history = state.get("conversation_history", [])
        
        logger.info(f"📝 Query Rewriter: '{user_message}'")
        
        # 调用查询改写器
        rewritten_query = await query_rewriter.rewrite(
            user_query=user_message,
            memory=memory,
            conversation_history=conversation_history
        )
        
        logger.info(f"✅ Query rewritten: '{user_message}' → '{rewritten_query}'")
        
        return {
            "rewritten_query": rewritten_query
        }
    
    except Exception as e:
        logger.error(f"❌ Query rewriter failed: {e}")
        return {"rewritten_query": user_message}


async def _intent_recognizer_node(state: MainState) -> Dict[str, Any]:
    """
    意图识别节点（Memory-First 架构的第三节点）
    
    功能：
    1. 基于改写后的查询进行意图识别（更准确）
    2. 提取实体信息
    3. 选择需要的工具
    4. 决定路由目标
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态（包含 intent, extracted_info, tools_needed, next_step 字段）
    """
    try:
        # 1. 获取改写后的查询（关键！）
        rewritten_query = state.get("rewritten_query", "")
        
        # 2. 获取记忆上下文
        memory = state.get("memory", {})
        user_profile = memory.get("user_profile", {})
        
        # 3. 调用 LLM 分析
        llm = LLMFactory.create_llm(model=settings.model_name, temperature=0)
        
        prompt = f"""
你是智能旅游助手的意图识别专家。基于改写后的查询，分析用户意图。

## 改写后的查询
{rewritten_query}

## 用户画像（辅助判断）
- 预算范围：{user_profile.get("budget_range", "无")}
- 旅行风格：{user_profile.get("travel_style", "无")}
- 偏好：{user_profile.get("preferred_hotel_chain", "无")}

## 意图类型定义

1. **search** - 搜索查询
   - 用户想了解信息或搜索特定内容
   - 示例："大理都有啥好玩的？"、"北京到上海的航班有哪些？"
   - 路由：search → recommend（或 booking）

2. **recommend** - 推荐建议
   - 用户需要推荐或比较
   - 示例："帮我推荐几个本地好吃的"、"航班和高铁哪个快？"
   - 路由：search → recommend

3. **booking** - 直接预订
   - 用户有明确的预订指令
   - 示例："帮我订今天晚上最快的一班飞机去大理"
   - 路由：search → booking

## 输出格式（必须是有效的 JSON）
{{
    "intent": "意图类型",
    "extracted_info": {{
        "destination": "目的地",
        "origin": "出发地",
        "date": "日期",
        "search_target": "搜索目标（景点/美食/航班/酒店/高铁）",
        "preference": "偏好",
        "budget": "预算"
    }},
    "tools_needed": ["工具 1", "工具 2"],
    "next_step": "search/recommend/booking"
}}

## 工具映射参考
| 搜索目标 | 需要的工具 |
|---------|-----------|
| 景点 | attraction_search, map_service |
| 美食 | food_search, map_service |
| 飞机 | date_parser, flight_search |
| 酒店 | date_parser, hotel_search |
| 高铁 | date_parser, train_search |
"""
        
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        
        # 4. 解析结果
        try:
            result = json.loads(response.content)
        except:
            # 降级处理
            result = {
                "intent": "search",
                "extracted_info": {},
                "tools_needed": ["attraction_search"],
                "next_step": "search"
            }
        
        logger.info(f"🎯 Intent recognized: intent={result['intent']}, next_step={result['next_step']}")
        
        return {
            "intent": result["intent"],
            "extracted_info": result["extracted_info"],
            "tools_needed": result["tools_needed"],
            "next_step": result["next_step"]
        }
    
    except Exception as e:
        logger.error(f"❌ Intent recognition failed: {e}")
        return {
            "intent": "search",
            "extracted_info": {},
            "tools_needed": ["attraction_search"],
            "next_step": "search"
        }


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
        extracted_info = state.get("extracted_info", {})
        
        if not user_id or not session_id:
            return {}
        
        logger.info(f"💾 Memory Postprocess: user_id={user_id}, session_id={session_id}")
        
        # 1. 更新短期记忆（Redis）
        if messages:
            last_msg = messages[-1] if messages else None
            user_input = state.get("user_message", "")
            ai_response = last_msg.content if last_msg else ""
            
            await session_manager.update_memory(
                session_id=session_id,
                user_input=user_input,
                ai_response=ai_response,
                extracted_info=extracted_info
            )
            
            logger.info(f"✅ Session memory updated")
        
        return {}
    
    except Exception as e:
        logger.error(f"❌ Memory postprocess failed: {e}")
        return {}


def build_main_graph() -> StateGraph:
    """构建主工作流图（Memory-First Architecture）"""
    graph = StateGraph(MainState)

    # === 阶段 1：记忆系统预处理节点 ===
    if MEMORY_AVAILABLE and settings.memory_system_enabled:
        graph.add_node("memory_preprocess", _memory_preprocess_node)
    
    # === 阶段 2：查询改写节点 ===
    if MEMORY_AVAILABLE and settings.memory_system_enabled:
        graph.add_node("query_rewriter", _query_rewriter_node)
    
    # === 阶段 3：意图识别节点 ===
    if MEMORY_AVAILABLE and settings.memory_system_enabled:
        graph.add_node("intent_recognizer", _intent_recognizer_node)
    
    # === 阶段 4：核心业务节点 ===
    graph.add_node("collect", _build_collect_info_graph)
    graph.add_node("search", _build_search_graph)
    graph.add_node("recommend", _build_recommend_graph)
    # graph.add_node("booking", _build_booking_graph)
    
    # === 阶段 5：记忆系统后处理节点 ===
    if MEMORY_AVAILABLE and settings.memory_system_enabled:
        graph.add_node("memory_postprocess", _memory_postprocess_node)

    # === 设置入口点和流程 ===
    if MEMORY_AVAILABLE and settings.memory_system_enabled:
        # Memory-First 架构流程：
        # memory_preprocess -> query_rewriter -> intent_recognizer -> collect -> search -> recommend -> memory_postprocess
        graph.set_entry_point("memory_preprocess")
        graph.add_edge("memory_preprocess", "query_rewriter")
        graph.add_edge("query_rewriter", "intent_recognizer")
        graph.add_edge("intent_recognizer", "collect")
    else:
        # 传统流程
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
        "user_id": user_id,  # ← 新增：用户 ID
        "session_id": session_id,  # ← 新增：会话 ID
        "memory": None,  # ← 新增：记忆上下文
        "rewritten_query": None,  # ← 新增：改写后的查询
        "intent": None,  # ← 新增：意图类型
        "extracted_info": None,  # ← 新增：提取的信息
        "tools_needed": None,  # ← 新增：需要的工具
        "next_step": None,  # ← 新增：下一步路由目标
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
        "memory": result.get("memory"),  # ← 返回记忆上下文
        "rewritten_query": result.get("rewritten_query"),  # ← 返回改写后的查询
        "intent": result.get("intent"),  # ← 返回意图类型
        "extracted_info": result.get("extracted_info"),  # ← 返回提取的信息
        "tools_needed": result.get("tools_needed"),  # ← 返回需要的工具
        "next_step": result.get("next_step"),  # ← 返回下一步路由目标
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
