"""
工作流公共模块 - 定义共享状态、组件和工具函数
"""

from typing import Dict, Any, Sequence, Annotated, Optional, List
import operator
import logging

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage, SystemMessage
import json

from utils.token_counter import TokenCounter
from agents.mcp_client import get_mcp_client

from conf import settings
from llm.factory import LLMFactory
from cache.cache_strategy import CacheStrategy
from rag.knowledge_base import KnowledgeBase
from cache.prompt_cache_manager import get_prompt_cache_manager

logger = logging.getLogger(__name__)

# 定义字典合并函数
def merge_dicts(left: Dict[str, int], right: Dict[str, int]) -> Dict[str, int]:
    """合并两个字典，相同 key 的值相加"""
    result = left.copy()
    for key, value in right.items():
        result[key] = result.get(key, 0) + value
    return result
# ============ SubState 定义 ============

class SubState(dict):
    """子图状态（增强版，支持对话历史）"""
    messages: Sequence[BaseMessage]
    usage: Annotated[Dict[str, int], merge_dicts]
    # usage: Annotated[Dict[str, int], operator.add]  # ← 自动累加
    output: str
    collected_info: Optional[Dict]
    collection_message: Optional[str]  # ← 新增：信息收集节点的对话消息（不传递给下游）
    search_plan: Optional[Dict]
    search_results: Optional[Dict]
    recommend_plan: Optional[Dict]
    recommendations: Optional[Dict]
    booking_confirmation: Optional[Dict]
    need_clarification: Optional[bool]
    clarification_questions: Optional[List[str]]
    stage: Optional[str]
    conversation_history: Optional[list]  # ← 新增：对话历史支持


# ============ 增强组件 ============

# 缓存策略
cache_strategy = CacheStrategy()

# 知识库
knowledge_base = KnowledgeBase()

# MCP Client
mcp_client = get_mcp_client()





async def build_search_tools(search_plan: Dict) -> List:
    """
    根据搜索计划构建搜索工具
    
    返回真正可调用的 LangChain Tool 对象列表
    
    Args:
        search_plan: 搜索计划字典
        
    Returns:
        List[BaseTool]: 真正的 LangChain Tool 对象列表
    """
    tools = []
    
    try:
        # 1. RAG 检索工具
        from langchain_core.tools import tool
        
        @tool
        def rag_search_tool(query: str) -> str:
            """使用旅游知识库进行RAG搜索"""
            rag_context = get_rag_context(query, use_cache=True)
            return f"RAG搜索结果：\n{rag_context}"
        
        tools.append(rag_search_tool)
        logger.info(f"[Build Tools] ✅ Added RAG search tool")
        
        # 2. MCP Java 工具（✅ 现在返回真正的 Tool 对象）
        mcp_tools = await mcp_client.get_tools()
        if mcp_tools:
            tools.extend(mcp_tools)
            logger.info(f"[Build Tools] ✅ Added {len(mcp_tools)} MCP Java tools")
        else:
            logger.warning(f"[Build Tools] ⚠️ No MCP tools available")
        
        # 3. SKILLS 搜索技能
        # try:
        #     search_skill = await SkillRegistry.load_skill("search")
        #     if search_skill:
        #         # 使用适配器转换为工具
        #         tools.append(skill_to_tool(search_skill))
        #         logger.info(f"[Build Tools] ✅ Added search skill tool")
        # except Exception as e:
        #     logger.warning(f"[Build Tools] ⚠️ Failed to load search skill: {e}")
        
        logger.info(f"[Build Tools] 🔧 Total tools built: {len(tools)}")
        
    except Exception as e:
        logger.error(f"[Build Tools] ❌ Failed to build search tools: {e}")
    
    return tools


async def build_recommend_tools(recommend_plan: Dict) -> List:
    """
    根据推荐策略构建推荐工具
    
    返回真正可调用的 LangChain Tool 对象列表
    
    Args:
        recommend_plan: 推荐计划字典
        
    Returns:
        List[BaseTool]: 真正的 LangChain Tool 对象列表
    """
    tools = []
    
    try:
        # 1. RAG 检索工具（用于旅游贴士和行程建议）
        from langchain_core.tools import tool
        
        @tool
        def rag_recommend_tool(query: str) -> str:
            """使用旅游知识库获取推荐建议"""
            rag_context = get_rag_context(query, use_cache=True)
            return f"RAG推荐建议：\n{rag_context}"
        
        tools.append(rag_recommend_tool)
        logger.info(f"[Build Tools] ✅ Added RAG recommend tool")
        
        # 2. MCP Java 工具（✅ 现在返回真正的 Tool 对象）
        mcp_tools = await mcp_client.get_tools()
        if mcp_tools:
            tools.extend(mcp_tools)
            logger.info(f"[Build Tools] ✅ Added {len(mcp_tools)} MCP Java tools")
        else:
            logger.warning(f"[Build Tools] ⚠️ No MCP tools available")
        
        logger.info(f"[Build Tools] 🔧 Total tools built: {len(tools)}")
        
    except Exception as e:
        logger.error(f"[Build Tools] ❌ Failed to build recommend tools: {e}")
    
    return tools


async def get_tools_and_skills_text() -> str:
    """
    获取 Java API 工具的文本摘要

    注意：只返回 Java API 工具，不包含 Agent Skills
    - Skills 是 Agent 内部流程管理，不应该作为"工具"展示给 LLM
    - Java API 工具与 Skills 存在概念重叠（如 search, recommend）
    - 这样避免 LLM 混淆应该调用哪个接口
    """
    try:
        # 异步获取 Java API 工具
        tools_summaries = await mcp_client.get_tool_summaries()
        if tools_summaries:
            tools_text = "\n".join([f"- {tool['name']}: {tool['description']}" for tool in tools_summaries])
            return f"**Java API 工具**:\n{tools_text}"
        return "暂无可用工具"
    except Exception as e:
        logger.warning(f"Failed to get MCP tools: {e}")
        return "暂无可用工具"


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


__all__ = [
    "SubState",
    "cache_strategy",
    "knowledge_base",
    "mcp_client",
    "build_search_tools",
    "build_recommend_tools",
    "get_tools_and_skills_text",
    "get_rag_context",
    "merge_dicts"
]
