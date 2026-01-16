"""
【第1层】4 个子图 StateGraph

每个子图独立执行，返回 {"output": str, "usage": Dict}
使用 TokenCounter 统计单个 LLM 调用的 token
"""
from typing import Dict, Any, Sequence, Annotated, Optional
import operator
import logging

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.utils.token_counter import TokenCounter
from src.agents.mcp_client import get_mcp_client
from src.skills.registry import SkillRegistry
from src.config import settings

logger = logging.getLogger(__name__)


# ============ SubState 定义 ============

class SubState(dict):
    """子图状态"""
    messages: Sequence[BaseMessage]
    usage: Annotated[Dict[str, int], operator.add]
    output: str
    collected_info: Optional[Dict]
    search_results: Optional[Dict]
    recommendations: Optional[Dict]
    booking_confirmation: Optional[Dict]


# ============ LLM 实例 ============

# 便宜层：用于简单任务（信息收集、预订）
cheap_llm = ChatOpenAI(
    model=settings.llm_model_cheap if hasattr(settings, 'llm_model_cheap') else "deepseek-chat",
    temperature=0,
    api_key=settings.deepseek_api_key if hasattr(settings, 'deepseek_api_key') else None,
    base_url=settings.deepseek_base_url if hasattr(settings, 'deepseek_base_url') else None,
)

# 标准层：用于复杂任务（搜索、推荐）
standard_llm = ChatOpenAI(
    model=settings.llm_model if hasattr(settings, 'llm_model') else "qwen-turbo",
    temperature=0,
    api_key=settings.dashscope_api_key if hasattr(settings, 'dashscope_api_key') else None,
    base_url=settings.dashscope_base_url if hasattr(settings, 'dashscope_base_url') else None,
)


# ============ MCP Client 和 Skills ============

mcp_client = get_mcp_client()


def get_tools_and_skills_text() -> str:
    """获取所有工具和技能的文本摘要"""
    try:
        tools_text = mcp_client.get_tool_summaries_text()
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


# ============ 1. 信息收集子图 ============

async def collect_info_node(state: SubState) -> Dict[str, Any]:
    """信息收集节点"""
    counter = TokenCounter()
    
    # 获取用户消息
    last_msg = state.get("messages", [])[-1] if state.get("messages") else None
    user_content = last_msg.content if last_msg else ""
    
    # 系统提示词
    system_prompt = """你是信息收集员，负责与用户交互收集旅游需求。

你的任务：
1. 分析用户的旅游需求
2. 识别关键信息：目的地、时间、预算、偏好等
3. 如果信息不足，生成友好的追问
4. 最终返回结构化的需求摘要

返回格式（JSON）：
{
    "destination": "目的地",
    "duration": "天数",
    "budget": "预算范围",
    "preferences": ["偏好1", "偏好2"],
    "dates": "出发时间",
    "complete": true/false  # 信息是否完整
}
"""
    
    # 调用 LLM
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]
        
        result = await cheap_llm.ainvoke(
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


# ============ 2. 搜索子图 ============

async def search_node(state: SubState) -> Dict[str, Any]:
    """搜索节点"""
    counter = TokenCounter()
    
    # 获取已收集的信息
    collected_info = state.get("collected_info", {})
    last_msg = state.get("messages", [])[-1] if state.get("messages") else None
    user_content = last_msg.content if last_msg else ""
    
    # 系统提示词
    system_prompt = f"""你是搜索员，负责根据用户需求搜索旅游目的地、酒店、航班等信息。

你的任务：
1. 分析用户需求和已收集的信息
2. 使用可用的工具搜索相关信息
3. 返回结构化的搜索结果

已收集的用户需求：
{collected_info}

可用工具：
{get_tools_and_skills_text()}

返回格式（JSON）：
{{
    "destinations": [...],
    "hotels": [...],
    "flights": [...],
    "total_results": 数量
}}
"""
    
    # 获取工具
    try:
        tools = mcp_client.get_tools()
    except Exception as e:
        logger.warning(f"Failed to get tools: {e}")
        tools = []
    
    # 调用 LLM
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]
        
        # 如果有工具，使用 tool calling
        if tools:
            result = await standard_llm.ainvoke(
                messages,
                tools=tools,
                config={"callbacks": [counter]}
            )
        else:
            result = await standard_llm.ainvoke(
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


# ============ 3. 推荐子图 ============

async def recommend_node(state: SubState) -> Dict[str, Any]:
    """推荐节点"""
    counter = TokenCounter()
    
    # 获取前面步骤的信息
    collected_info = state.get("collected_info", {})
    search_results = state.get("search_results", {})
    last_msg = state.get("messages", [])[-1] if state.get("messages") else None
    user_content = last_msg.content if last_msg else ""
    
    # 系统提示词
    system_prompt = f"""你是推荐员，负责根据用户需求和搜索结果生成个性化旅游推荐方案。

你的任务：
1. 综合分析用户需求和搜索结果
2. 生成3-5个个性化推荐方案
3. 每个方案包含详细的行程安排、预算估算、亮点介绍

用户需求：
{collected_info}

搜索结果：
{search_results}

可用工具：
{get_tools_and_skills_text()}

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
            "confidence": 0.9
        }}
    ]
}}
"""
    
    # 获取工具
    try:
        tools = mcp_client.get_tools()
    except Exception as e:
        logger.warning(f"Failed to get tools: {e}")
        tools = []
    
    # 调用 LLM
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]
        
        if tools:
            result = await standard_llm.ainvoke(
                messages,
                tools=tools,
                config={"callbacks": [counter]}
            )
        else:
            result = await standard_llm.ainvoke(
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


# ============ 4. 预订子图 ============

async def booking_node(state: SubState) -> Dict[str, Any]:
    """预订节点"""
    counter = TokenCounter()
    
    # 获取前面步骤的信息
    recommendations = state.get("recommendations", {})
    last_msg = state.get("messages", [])[-1] if state.get("messages") else None
    user_content = last_msg.content if last_msg else ""
    
    # 系统提示词
    system_prompt = f"""你是预订员，负责完成用户选定的旅游预订。

你的任务：
1. 确认用户选择的推荐方案
2. 使用 create_booking 工具创建预订
3. 返回预订确认信息

推荐方案：
{recommendations}

可用工具：
{get_tools_and_skills_text()}

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
        tools = mcp_client.get_tools()
    except Exception as e:
        logger.warning(f"Failed to get tools: {e}")
        tools = []
    
    # 调用 LLM
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]
        
        if tools:
            result = await cheap_llm.ainvoke(
                messages,
                tools=tools,
                config={"callbacks": [counter]}
            )
        else:
            result = await cheap_llm.ainvoke(
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
