"""
搜索工作流 - 两阶段搜索流程：规划 → 执行
"""

from typing import Dict, Any
import json
import logging

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from utils.token_counter import TokenCounter
from llm.factory import LLMFactory
from prompts.prompt_loader import prompt_loader
from prompts.prompt_renderer import prompt_renderer

from .common import (
    SubState, cache_strategy, get_tools_and_skills_text, 
    build_search_tools
)
from agents.mcp_client import get_mcp_client
import re

logger = logging.getLogger(__name__)

async def search_plan_node(state: SubState) -> Dict[str, Any]:
    """搜索规划节点 - 利用 Prompt Cache 优化成本"""
    counter = TokenCounter()
    
    # 获取已收集的信息
    collected_info = state.get("collected_info", {})
    last_msg = state.get("messages", [])[-1] if state.get("messages") else None
    user_content = last_msg.content if last_msg else ""
    
    # 1️⃣ 检查业务缓存（快速路径）
    destination = collected_info.get("destination", "unknown")
    cache_key_biz = f"search_plan:{user_content[:50]}:{destination}"
    cached = cache_strategy.get_search_results(query=cache_key_biz, destination=destination)
    if cached:
        logger.info("🎯 业务缓存命中(search_plan)")
        need_clarification = cached.get("need_clarification", False)
        return {
            "messages": [AIMessage(content=cached.get("output", ""))],
            "usage": {"prompt": 0, "completion": 0, "cached": 0, "total": 0},
            "output": cached.get("output", ""),
            "search_plan": cached.get("search_plan", {}),
            "need_clarification": need_clarification,
            "clarification_questions": cached.get("clarification_questions", []),
            "stage": cached.get("stage")
        }
    
    # 2️⃣ 获取 LLM（便宜层）
    llm = LLMFactory.create_model_by_tier(tier="cheap")
    
    system_prompt = await prompt_loader.get_prompt("search_plan", "system_prompt")
    few_shots = await prompt_loader.get_prompt("search_plan", "few_shots")
    user_query_template = await prompt_loader.get_prompt("search_plan", "user_query")
    
    tools_text = await get_tools_and_skills_text()
    
    user_query = await prompt_renderer.render(
        user_query_template,
        origin=collected_info.get('origin'),
        destination=collected_info.get('destination'),
        dates=collected_info.get('dates'),
        duration=collected_info.get('duration'),
        budget=collected_info.get('budget', '未指定'),
        preferences=', '.join(collected_info.get('preferences', [])) or '无特殊偏好',
        user_content=user_content
    )

    messages = [
        SystemMessage(content=f"{system_prompt}\n\n{few_shots}\n\n工具列表:\n{tools_text}"),
        HumanMessage(content=user_query)
    ]
    result = await llm.ainvoke(messages, config={"callbacks": [counter]})
    output_text = result.content
    
    if output_text is None:
        return {
            "messages": [AIMessage(content="Error: LLM invocation failed")],
            "usage": counter.dump(),
            "output": "Error: LLM invocation failed",
            "search_plan": {"error": "LLM invocation failed"}
        }
        
    # 解析搜索计划
    try:
        cleaned_text = output_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        elif cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]

        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]

        cleaned_text = cleaned_text.strip()
        data = json.loads(cleaned_text)
        search_plan = data
        desc = data.get("output", output_text)
        clarification_questions = data.get("clarification_questions", []) or []
        need_clarification = len(clarification_questions) > 0
    except Exception:
        search_plan = {"raw": output_text, "search_plan": {"destination": destination}}
        desc = output_text
        clarification_questions = []
        need_clarification = False

    # 缓存结果到业务缓存
    cache_strategy.cache_search_results(
        query=cache_key_biz,
        results={
            "search_plan": search_plan,
            "output": desc,
            "need_clarification": need_clarification,
            "clarification_questions": clarification_questions,
            "stage": "awaiting_clarification" if need_clarification else "ready_for_execution"
        },
        destination=destination
    )

    if need_clarification:
        # 不再使用 LLM 的 output，而是构造一个清晰的澄清请求
        clarification_prompt = "为了更好地为您规划行程，请您回答以下问题：\n"
        for i, q in enumerate(clarification_questions, 1):
            clarification_prompt += f"{i}. {q}\n"
        clarification_prompt += "\n请回复您的答案,我会根据您的反馈继续为您推荐。"
        return {
            "messages": [AIMessage(content=clarification_prompt)],
            "usage": counter.dump(),
            "output": clarification_prompt,
            "search_results": clarification_prompt,
            "need_clarification": True,
            "clarification_questions": clarification_questions,
            "search_plan": None,
            "stage": "awaiting_clarification"
        }

    return {
        "messages": [AIMessage(content=desc)],
        "usage": counter.dump(),
        "output": desc,
        "search_plan": search_plan,
        "need_clarification": False,
        "clarification_questions": [],
        "stage": "ready_for_execution"
    }

async def search_execute_agent_node(state: SubState) -> Dict[str, Any]:
    """搜索执行节点 - ReAct Agent + Prompt Cache"""
    counter = TokenCounter()
    
    search_plan = state.get("search_plan", {})
    collected_info = state.get("collected_info", {})
    last_msg = state.get("messages", [])[-1] if state.get("messages") else None
    user_content = last_msg.content if last_msg else ""

    plan_payload = search_plan.get("search_plan", {}) if isinstance(search_plan, dict) else {}
    destination = plan_payload.get("destination", search_plan.get("destination", "unknown"))
    cache_key_biz = f"search_exec:{user_content[:50]}:{destination}"
    
    # 1️⃣ 业务缓存
    cached = cache_strategy.get_search_results(query=cache_key_biz, destination=destination)
    if cached:
        logger.info("🎯 业务缓存命中（search_execute）")
        return {
            "messages": [AIMessage(content=cached.get("output", ""))],
            "usage": {"prompt": 0, "completion": 0, "cached": 0, "total": 0},
            "output": cached.get("output", ""),
            "search_results": cached.get("search_results", {})
        }

    # 2️⃣ 获取 LLM（标准层）
    llm = LLMFactory.create_model_by_tier(tier="cheap")
    
    # 5️⃣ 构建工具
    tools = await build_search_tools(search_plan)
    
    # # 记录工具信息
    tool_names = [getattr(t, 'name', str(t)) for t in tools]
    logger.info(f"[Search Execute] 🔧 Tools available: {tool_names}")

    # 6️⃣ 执行逻辑
    strategy = search_plan.get("search_strategy", {})
    search_config = search_plan.get("search_configuration", {})
    rag_keywords = search_config.get("rag_search_keywords", []) or search_plan.get("rag_search_keywords", [])
    priorities = search_config.get("priorities", {})

    # Step 1: Java MCP 查询原始数据
    budgetTmp=re.findall(r'\d+\.?\d*', plan_payload.get("budget_range", "1000000"))
    if len(budgetTmp)>1:
        minPrice=budgetTmp[0]
        maxPrice=budgetTmp[1]
    else:
        minPrice=0
        maxPrice=budgetTmp[0]
    mcp_client = get_mcp_client()

    base_prompt = await prompt_loader.get_prompt("search_execute", "system_prompt")
    
    system_prompt = prompt_renderer.render(base_prompt, {
        "search_strategy_phase1": search_plan.get('search_strategy', {}).get('phase1_hot_spots', {}),
        "search_strategy_phase2": search_plan.get('search_strategy', {}).get('phase2_special_interests', {}),
        "search_strategy_phase3": search_plan.get('search_strategy', {}).get('phase3_accommodation', {}),
        "search_strategy_phase4": search_plan.get('search_strategy', {}).get('phase4_logistics', {}),
        "destination": plan_payload.get('destination', ''),
        "origin": plan_payload.get('origin', ''),
        "check_in": plan_payload.get('check_in', ''),
        "check_out": plan_payload.get('check_out', ''),
        "budget_range": plan_payload.get('budget_range', '')
    })

    user_query_template = await prompt_loader.get_prompt("search_execute", "user_query")
    user_query = await prompt_renderer.render(
        user_query_template,
        destination=collected_info.get('destination'),
        dates=collected_info.get('dates'),
        duration=collected_info.get('duration'),
        budget=collected_info.get('budget', '未指定'),
        preferences=', '.join(collected_info.get('preferences', [])) or '无特殊偏好',
        user_content=user_content
    )

    try:
        # 创建 ReAct Agent（绑定真正的工具）
        logger.info(f"[Search Execute] 🤖 Creating ReAct agent with {len(tools)} tools")
        agent = create_react_agent(llm, tools)
        
        invoke_kwargs = {"callbacks": [counter]}
        
        logger.info(f"[Search Execute] 🚀 Starting agent execution...")
        result = await agent.ainvoke(
            {"messages": [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_query)
            ]},
            config=invoke_kwargs
        )
        logger.info(f"[Search Execute] ✅ Agent execution completed")
        
        # 获取最后的消息作为响应内容
        last_msg = result["messages"][-1]
        output_text = last_msg.content
        
        # 尝试从回复中提取 JSON
        try:
            # 兼容有些 LLM 会在回复中包含 ```json ... ```
            clean_text = output_text
            if "```json" in output_text:
                clean_text = output_text.split("```json")[1].split("```")[0].strip()
            elif "```" in output_text:
                clean_text = output_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(clean_text)
            search_results = data.get("search_results", data)
            desc = data.get("output", output_text)
        except:
            search_results = {"raw": output_text}
            desc = output_text
            
        # 缓存结果到业务缓存
        cache_strategy.cache_search_results(
            query=cache_key_biz,
            results={"search_results": search_results, "output": desc},
            destination=destination
        )
        
        return {
            "messages": [last_msg],
            "usage": counter.dump(),
            "output": desc,
            "search_results": search_results
        }
        
    except Exception as e:
        
        logger.error(f"❌ search_execute_agent_node failed: {e}")
        return {
            "messages": [AIMessage(content=f"Error: {e}")],
            "usage": counter.dump(),
            "output": f"Error: {e}",
            "search_results": {"error": str(e)}
        }

def build_search_graph() -> StateGraph:
    """构建搜索子图（两阶段流程）"""
    graph = StateGraph(SubState)
    
    # 添加两个节点：规划 + 执行
    graph.add_node("search_plan", search_plan_node)
    graph.add_node("search_execute", search_execute_agent_node)
    
    # 设置边：规划 -> 执行/结束
    graph.add_conditional_edges(
        "search_plan",
        lambda state: "end" if state.get("need_clarification") else "search_execute",
        {
            "search_execute": "search_execute",
            "end": END
        }
    )
    graph.add_edge("search_execute", END)
    
    # 设置入口点
    graph.set_entry_point("search_plan")
    
    return graph.compile()


__all__ = ["build_search_graph"]
