"""
【第1层】4 个子图 StateGraph（增强版）

每个子图独立执行，返回 {"output": str, "usage": Dict}
使用 TokenCounter 统计单个 LLM 调用的 token

增强功能：
- LLMFactory 多模型支持
- CacheStrategy 缓存策略
- RAG 知识库集成
- 对话历史支持
"""
from typing import Dict, Any, Sequence, Annotated, Optional
import operator
import logging

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage, SystemMessage

from src.utils.token_counter import TokenCounter
from src.agents.mcp_client import get_mcp_client
from src.skills.registry import SkillRegistry
from src.config import settings
from src.llm.factory import LLMFactory
from src.cache.cache_strategy import CacheStrategy
from src.rag.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)


# ============ SubState 定义 ============

class SubState(dict):
    """子图状态（增强版，支持对话历史）"""
    messages: Sequence[BaseMessage]
    usage: Annotated[Dict[str, int], operator.add]
    output: str
    collected_info: Optional[Dict]
    search_results: Optional[Dict]
    recommendations: Optional[Dict]
    booking_confirmation: Optional[Dict]
    conversation_history: Optional[list]  # ← 新增：对话历史支持


# ============ 增强组件 ============

# 缓存策略
cache_strategy = CacheStrategy()

# 知识库
knowledge_base = KnowledgeBase()

# MCP Client
mcp_client = get_mcp_client()


async def get_tools_and_skills_text() -> str:
    """获取所有工具和技能的文本摘要"""
    try:
        # 异步获取工具
        tools_summaries = await mcp_client.get_tool_summaries()
        tools_text = "\n".join([f"- {tool['name']}: {tool['description']}" for tool in tools_summaries])
    except Exception as e:
        logger.warning(f"Failed to get MCP tools: {e}")
        tools_text = ""

    try:
        skills_text = SkillRegistry.get_all_summaries_text()
    except Exception as e:
        logger.warning(f"Failed to get skills: {e}")
        skills_text = ""

    combined = []
    if tools_text:
        combined.append(f"**Java API 工具**:\n{tools_text}")
    if skills_text:
        combined.append(f"**Agent Skills**:\n{skills_text}")

    return "\n\n".join(combined) if combined else "暂无可用工具"


def get_rag_context(query: str, use_cache: bool = True) -> str:
    """
    获取 RAG 上下文（带缓存）

    Args:
        query: 查询文本
        use_cache: 是否使用缓存

    Returns:
        RAG 上下文字符串
    """
    if use_cache:
        # 尝试从缓存获取
        cached = cache_strategy.get_rag_context(query)
        if cached:
            logger.info(f"RAG cache HIT for query: {query[:50]}...")
            return cached

    # 从知识库检索
    try:
        rag_context = knowledge_base.get_rag_context_for_prompt(query, k=5)
        logger.info(f"RAG retrieved {len(rag_context)} chars for query: {query[:50]}...")

        # 缓存结果
        if rag_context and use_cache:
            cache_strategy.cache_rag_context(query, rag_context)

        return rag_context
    except Exception as e:
        logger.warning(f"RAG retrieval failed: {e}")
        return ""


# ============ 1. 信息收集子图（便宜层 + 缓存） ============

async def collect_info_node(state: SubState) -> Dict[str, Any]:
    """信息收集节点（便宜层 + 缓存）"""
    counter = TokenCounter()

    # 获取用户消息
    last_msg = state.get("messages", [])[-1] if state.get("messages") else None
    user_content = last_msg.content if last_msg else ""

    # 获取对话历史
    conversation_history = state.get("conversation_history", [])
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-6:]])

    # 尝试从缓存获取（基于用户消息）
    cache_key = f"collect:{user_content[:100]}"
    cached = cache_strategy.get_user_preferences(cache_key)
    if cached:
        logger.info(f"Collection cache HIT")
        return {
            "messages": [AIMessage(content=cached.get("output", ""))],
            "usage": {"prompt": 0, "completion": 0, "total": 0},
            "output": cached.get("output", ""),
            "collected_info": cached.get("collected_info", {})
        }

    # 系统提示词
    system_prompt = f"""你是信息收集员，负责与用户交互收集旅游需求。

你的任务：
1. 分析用户的旅游需求
2. 识别关键信息：目的地、时间、预算、偏好等
3. 如果信息不足，生成友好的追问
4. 最终返回结构化的需求摘要

之前的对话历史：
{history_text if history_text else "（无历史记录）"}

返回格式（JSON）：
{{
    "destination": "目的地",
    "duration": "天数",
    "budget": "预算范围",
    "preferences": ["偏好1", "偏好2"],
    "dates": "出发时间",
    "complete": true/false  # 信息是否完整
}}
"""

    # 调用 LLM（便宜层）
    try:
        # 使用 LLMFactory 创建便宜层模型
        llm = LLMFactory.create_model_by_tier(tier="cheap")

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]

        result = await llm.ainvoke(
            messages,
            config={"callbacks": [counter]}
        )

        output_text = result.content

        # 尝试解析为 JSON
        import json
        try:
            collected_info = json.loads(output_text)
        except:
            collected_info = {"raw": output_text, "complete": False}

        # 缓存结果
        cache_strategy.cache_user_preferences(cache_key, {
            "output": output_text,
            "collected_info": collected_info
        })

        return {
            "messages": [result],
            "usage": counter.dump(),
            "output": output_text,
            "collected_info": collected_info
        }

    except Exception as e:
        logger.error(f"collect_info_node failed: {e}")
        return {
            "messages": [AIMessage(content=f"Error: {e}")],
            "usage": {"prompt": 0, "completion": 0, "total": 0},
            "output": f"Error: {e}",
            "collected_info": {"error": str(e)}
        }


def build_collect_info_graph() -> StateGraph:
    """构建信息收集子图"""
    graph = StateGraph(SubState)
    graph.add_node("collect", collect_info_node)
    graph.add_edge("collect", END)
    graph.set_entry_point("collect")
    return graph.compile()


# ============ 2. 搜索子图（标准层 + RAG + 缓存） ============

async def search_node(state: SubState) -> Dict[str, Any]:
    """搜索节点（标准层 + RAG + 缓存）"""
    counter = TokenCounter()

    # 获取已收集的信息
    collected_info = state.get("collected_info", {})
    last_msg = state.get("messages", [])[-1] if state.get("messages") else None
    user_content = last_msg.content if last_msg else ""

    # 构建缓存键
    destination = collected_info.get("destination", "unknown")
    cache_key = f"{user_content[:50]}:{destination}"

    # 尝试从缓存获取搜索结果
    cached = cache_strategy.get_search_results(query=user_content, destination=destination)
    if cached:
        logger.info(f"Search cache HIT")
        return {
            "messages": [AIMessage(content=cached.get("output", ""))],
            "usage": {"prompt": 0, "completion": 0, "total": 0},
            "output": cached.get("output", ""),
            "search_results": cached.get("search_results", {})
        }

    # 获取 RAG 上下文
    rag_context = get_rag_context(user_content, use_cache=True)

    # 获取工具文本
    tools_text = await get_tools_and_skills_text()

    # 系统提示词
    system_prompt = f"""你是搜索员，负责根据用户需求搜索旅游目的地、酒店、航班等信息。

你的任务：
1. 分析用户需求和已收集的信息
2. 使用可用的工具搜索相关信息
3. 结合知识库信息提供更准确的搜索结果

已收集的用户需求：
{collected_info}

旅游知识库参考：
{rag_context if rag_context else "（暂无相关知识库信息）"}

可用工具：
{tools_text}

返回格式（JSON）：
{{
    "destinations": [...],
    "hotels": [...],
    "flights": [...],
    "total_results": 数量,
    "rag_sources_used": ["来源1", "来源2"]
}}
"""

    # 获取工具
    try:
        tools = await mcp_client.get_tools()
    except Exception as e:
        logger.warning(f"Failed to get tools: {e}")
        tools = []

    # 调用 LLM（标准层）
    try:
        # 使用 LLMFactory 创建标准层模型
        llm = LLMFactory.create_model_by_tier(tier="standard")

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]

        # 如果有工具，使用 tool calling
        if tools:
            result = await llm.ainvoke(
                messages,
                tools=tools,
                config={"callbacks": [counter]}
            )
        else:
            result = await llm.ainvoke(
                messages,
                config={"callbacks": [counter]}
            )

        output_text = result.content

        # 尝试解析为 JSON
        import json
        try:
            search_results = json.loads(output_text)
        except:
            search_results = {"raw": output_text, "destinations": []}

        # 缓存结果
        cache_strategy.cache_search_results(
            query=user_content,
            results=search_results,
            destination=destination
        )

        return {
            "messages": [result],
            "usage": counter.dump(),
            "output": output_text,
            "search_results": search_results
        }

    except Exception as e:
        logger.error(f"search_node failed: {e}")
        return {
            "messages": [AIMessage(content=f"Error: {e}")],
            "usage": {"prompt": 0, "completion": 0, "total": 0},
            "output": f"Error: {e}",
            "search_results": {"error": str(e)}
        }


def build_search_graph() -> StateGraph:
    """构建搜索子图"""
    graph = StateGraph(SubState)
    graph.add_node("search", search_node)
    graph.add_edge("search", END)
    graph.set_entry_point("search")
    return graph.compile()


# ============ 3. 推荐子图（标准层 + RAG + 缓存） ============

async def recommend_node(state: SubState) -> Dict[str, Any]:
    """推荐节点（标准层 + RAG + 缓存）"""
    counter = TokenCounter()

    # 获取前面步骤的信息
    collected_info = state.get("collected_info", {})
    search_results = state.get("search_results", {})
    last_msg = state.get("messages", [])[-1] if state.get("messages") else None
    user_content = last_msg.content if last_msg else ""

    # 构建缓存键
    destination = collected_info.get("destination", "unknown")
    interests = collected_info.get("preferences", [])
    cache_key = f"{user_content[:50]}:{destination}:{','.join(interests)}"

    # 尝试从缓存获取推荐结果
    cached = cache_strategy.get_recommendations(
        user_id="default",
        interests=interests,
        budget=collected_info.get("budget")
    )
    if cached:
        logger.info(f"Recommend cache HIT")
        return {
            "messages": [AIMessage(content=cached.get("output", ""))],
            "usage": {"prompt": 0, "completion": 0, "total": 0},
            "output": cached.get("output", ""),
            "recommendations": cached.get("recommendations", {})
        }

    # 获取 RAG 上下文
    rag_context = get_rag_context(user_content, use_cache=True)

    # 获取工具文本
    tools_text = await get_tools_and_skills_text()

    # 系统提示词
    system_prompt = f"""你是推荐员，负责根据用户需求和搜索结果生成个性化旅游推荐方案。

你的任务：
1. 综合分析用户需求和搜索结果
2. 生成3-5个个性化推荐方案
3. 每个方案包含详细的行程安排、预算估算、亮点介绍
4. 结合知识库中的旅游贴士和推荐信息

用户需求：
{collected_info}

搜索结果：
{search_results}

旅游知识库参考：
{rag_context if rag_context else "（暂无相关知识库信息）"}

可用工具：
{tools_text}

返回格式（JSON）：
{{
    "recommendations": [
        {{
            "id": "方案ID",
            "title": "方案标题",
            "description": "详细描述",
            "itinerary": [...],
            "estimated_cost": "预算",
            "highlights": [...],
            "confidence": 0.9,
            "rag_sources_used": ["来源1", "来源2"]
        }}
    ]
}}
"""

    # 获取工具
    try:
        tools = await mcp_client.get_tools()
    except Exception as e:
        logger.warning(f"Failed to get tools: {e}")
        tools = []

    # 调用 LLM（标准层）
    try:
        # 使用 LLMFactory 创建标准层模型
        llm = LLMFactory.create_model_by_tier(tier="standard")

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]

        if tools:
            result = await llm.ainvoke(
                messages,
                tools=tools,
                config={"callbacks": [counter]}
            )
        else:
            result = await llm.ainvoke(
                messages,
                config={"callbacks": [counter]}
            )

        output_text = result.content

        # 尝试解析为 JSON
        import json
        try:
            recommendations = json.loads(output_text)
        except:
            recommendations = {"raw": output_text, "recommendations": []}

        # 缓存结果
        cache_strategy.cache_recommendations(
            user_id="default",
            recommendations=recommendations,
            interests=interests,
            budget=collected_info.get("budget")
        )

        return {
            "messages": [result],
            "usage": counter.dump(),
            "output": output_text,
            "recommendations": recommendations
        }

    except Exception as e:
        logger.error(f"recommend_node failed: {e}")
        return {
            "messages": [AIMessage(content=f"Error: {e}")],
            "usage": {"prompt": 0, "completion": 0, "total": 0},
            "output": f"Error: {e}",
            "recommendations": {"error": str(e)}
        }


def build_recommend_graph() -> StateGraph:
    """构建推荐子图"""
    graph = StateGraph(SubState)
    graph.add_node("recommend", recommend_node)
    graph.add_edge("recommend", END)
    graph.set_entry_point("recommend")
    return graph.compile()


# ============ 4. 预订子图（便宜层 + 缓存） ============

async def booking_node(state: SubState) -> Dict[str, Any]:
    """预订节点（便宜层 + 缓存）"""
    counter = TokenCounter()

    # 获取前面步骤的信息
    recommendations = state.get("recommendations", {})
    last_msg = state.get("messages", [])[-1] if state.get("messages") else None
    user_content = last_msg.content if last_msg else ""

    # 获取工具文本
    tools_text = await get_tools_and_skills_text()

    # 系统提示词
    system_prompt = f"""你是预订员，负责完成用户选定的旅游预订。

你的任务：
1. 确认用户选择的推荐方案
2. 使用 create_booking 工具创建预订
3. 返回预订确认信息

推荐方案：
{recommendations}

可用工具：
{tools_text}

返回格式（JSON）：
{{
    "booking_id": "预订ID",
    "status": "confirmed/pending",
    "details": {{...}},
    "confirmation_message": "确认信息"
}}
"""

    # 获取工具
    try:
        tools = await mcp_client.get_tools()
    except Exception as e:
        logger.warning(f"Failed to get tools: {e}")
        tools = []

    # 调用 LLM（便宜层）
    try:
        # 使用 LLMFactory 创建便宜层模型
        llm = LLMFactory.create_model_by_tier(tier="cheap")

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]

        if tools:
            result = await llm.ainvoke(
                messages,
                tools=tools,
                config={"callbacks": [counter]}
            )
        else:
            result = await llm.ainvoke(
                messages,
                config={"callbacks": [counter]}
            )

        output_text = result.content

        # 尝试解析为 JSON
        import json
        try:
            booking_confirmation = json.loads(output_text)
        except:
            booking_confirmation = {"raw": output_text, "status": "pending"}

        # 预订信息通常缓存较短时间
        if booking_confirmation.get("booking_id"):
            cache_key = f"booking:{booking_confirmation['booking_id']}"
            cache_strategy.cache_destination_info(cache_key, booking_confirmation)

        return {
            "messages": [result],
            "usage": counter.dump(),
            "output": output_text,
            "booking_confirmation": booking_confirmation
        }

    except Exception as e:
        logger.error(f"booking_node failed: {e}")
        return {
            "messages": [AIMessage(content=f"Error: {e}")],
            "usage": {"prompt": 0, "completion": 0, "total": 0},
            "output": f"Error: {e}",
            "booking_confirmation": {"error": str(e)}
        }


def build_booking_graph() -> StateGraph:
    """构建预订子图"""
    graph = StateGraph(SubState)
    graph.add_node("booking", booking_node)
    graph.add_edge("booking", END)
    graph.set_entry_point("booking")
    return graph.compile()


# ============ 导出 ============

__all__ = [
    "SubState",
    "build_collect_info_graph",
    "build_search_graph",
    "build_recommend_graph",
    "build_booking_graph",
]
