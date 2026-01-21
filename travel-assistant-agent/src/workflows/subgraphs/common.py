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

from ....utils.token_counter import TokenCounter
from ....agents.mcp_client import get_mcp_client
from ....skills.registry import SkillRegistry
from ....config import settings
from ....llm.factory import LLMFactory
from ....cache.cache_strategy import CacheStrategy
from ....rag.knowledge_base import KnowledgeBase
from ....cache.prompt_cache_manager import get_prompt_cache_manager

logger = logging.getLogger(__name__)


# ============ SubState 定义 ============

class SubState(dict):
    """子图状态（增强版，支持对话历史）"""
    messages: Sequence[BaseMessage]
    usage: Annotated[Dict[str, int], operator.add]
    output: str
    collected_info: Optional[Dict]
    search_plan: Optional[Dict]
    search_results: Optional[Dict]
    recommend_plan: Optional[Dict]
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


# ============ 技能到工具的适配器 ============

def skill_to_tool(skill):
    """将Skill实例转换为LangChain Tool"""
    from langchain_core.tools import tool
    
    @tool
    def skill_tool(**kwargs):
        """使用技能执行任务"""
        import asyncio
        
        # 运行技能的execute方法
        try:
            result = asyncio.run(skill.execute(kwargs))
            return str(result)
        except Exception as e:
            return f"Skill execution error: {str(e)}"
    
    # 设置技能的基本信息
    skill_tool.name = skill.name
    skill_tool.description = skill.description
    
    return skill_tool


# ============ 辅助函数 ============

def create_search_plan_prompt(collected_info: Dict, conversation_history: List[Dict]) -> str:
    """生成搜索规划提示词"""
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-6:]])
    
    return f"""你是搜索规划师，负责分析用户需求并制定结构化的搜索计划。

你的任务：
1. 分析用户需求和已收集的信息
2. 提取关键搜索要素：目的地、时间、预算、偏好
3. 生成JSON格式的搜索策略

已收集的用户需求：
{collected_info}

对话历史：
{history_text if history_text else "（无历史记录）"}

返回格式（JSON）：
{{
    "search_plan": {{
        "destination": "目的地",
        "check_in": "入住日期", 
        "check_out": "退房日期",
        "budget_range": "预算范围",
        "search_priorities": ["酒店", "航班", "景点"],
        "rag_search_keywords": ["关键词1", "关键词2"]
    }},
    "output": "搜索计划描述"
}}"""


def create_recommend_plan_prompt(collected_info: Dict, search_results: Dict, conversation_history: List[Dict]) -> str:
    """生成推荐规划提示词"""
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-6:]])
    
    return f"""你是推荐规划师，负责分析用户需求和搜索结果，制定个性化推荐策略。

你的任务：
1. 综合分析用户需求和搜索结果
2. 确定推荐主题和重点
3. 生成推荐策略

用户需求：
{collected_info}

搜索结果摘要：
{str(search_results)[:500]}...

对话历史：
{history_text if history_text else "（无历史记录）"}

返回格式（JSON）：
{{
    "recommend_plan": {{
        "themes": ["主题1", "主题2", "主题3"],
        "num_plans": 3,
        "focus_points": ["重点1", "重点2"],
        "weights": {{"预算": 0.3, "体验": 0.4, "安全": 0.3}}
    }},
    "output": "推荐策略描述"
}}"""


async def build_search_tools(search_plan: Dict) -> List:
    """根据搜索计划构建搜索工具"""
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
        
        # 2. MCP Java 工具
        mcp_tools = await mcp_client.get_tools()
        tools.extend(mcp_tools)
        
        # 3. SKILLS 搜索技能
        try:
            search_skill = await SkillRegistry.load_skill("search")
            if search_skill:
                # 使用适配器转换为工具
                tools.append(skill_to_tool(search_skill))
        except Exception as e:
            logger.warning(f"Failed to load search skill: {e}")
        
    except Exception as e:
        logger.warning(f"Failed to build search tools: {e}")
    
    return tools


async def build_recommend_tools(recommend_plan: Dict) -> List:
    """根据推荐策略构建推荐工具"""
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
        
        # 2. MCP Java 工具
        mcp_tools = await mcp_client.get_tools()
        tools.extend(mcp_tools)
        
        # 3. SKILLS 推荐技能
        try:
            recommend_skill = await SkillRegistry.load_skill("recommend")
            if recommend_skill:
                # 使用适配器转换为工具
                tools.append(skill_to_tool(recommend_skill))
        except Exception as e:
            logger.warning(f"Failed to load recommend skill: {e}")
        
    except Exception as e:
        logger.warning(f"Failed to build recommend tools: {e}")
    
    return tools


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


__all__ = [
    "SubState",
    "cache_strategy",
    "knowledge_base",
    "mcp_client",
    "skill_to_tool",
    "create_search_plan_prompt",
    "create_recommend_plan_prompt",
    "build_search_tools",
    "build_recommend_tools",
    "get_tools_and_skills_text",
    "get_rag_context",
]
