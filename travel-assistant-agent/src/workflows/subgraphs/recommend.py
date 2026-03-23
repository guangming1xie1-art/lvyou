"""
推荐工作流 - 两阶段推荐流程：规划 → 执行
"""

from typing import Dict, Any
import json
import logging

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from utils.token_counter import TokenCounter
from llm.factory import LLMFactory
from cache.prompt_cache_manager import get_prompt_cache_manager
from prompts.prompt_loader import prompt_loader
from prompts.prompt_renderer import prompt_renderer

from .common import (
    SubState, cache_strategy, get_tools_and_skills_text, 
    build_recommend_tools
)
from agents.mcp_client import get_mcp_client
from rag.retriever import HybridRetriever
from .hybrid_retrieval import hybrid_rank

logger = logging.getLogger(__name__)

async def recommend_plan_node(state: SubState) -> Dict[str, Any]:
    """推荐规划节点 - 利用 Prompt Cache 优化成本"""
    counter = TokenCounter()
    
    collected_info = state.get("collected_info", {})
    search_results = state.get("search_results", {})
    last_msg = state.get("messages", [])[-1] if state.get("messages") else None
    user_content = last_msg.content if last_msg else ""
    
    destination = collected_info.get("destination", "unknown")
    cache_key_biz = f"recommend_plan:{user_content[:50]}:{destination}"
    
    # 1️⃣ 业务缓存
    cached = cache_strategy.get_recommendations(
        user_id=cache_key_biz,
        interests=collected_info.get("preferences", []),
        budget=collected_info.get("budget")
    )
    if cached:
        logger.info("🎯 业务缓存命中(recommend_plan)")
        need_clarification = cached.get("need_clarification", False)
        return {
            "messages": [AIMessage(content=cached.get("output", ""))],
            "usage": {"prompt": 0, "completion": 0, "cached": 0, "total": 0},
            "output": cached.get("output", ""),
            "recommend_plan": cached.get("recommend_plan", {}),
            "need_clarification": need_clarification,
            "clarification_questions": cached.get("clarification_questions", []),
            "stage": cached.get("stage")
        }
        
    llm = LLMFactory.create_model_by_tier(tier="cheap")
    
    system_prompt = await prompt_loader.get_prompt("recommend_plan", "system_prompt")
    few_shots = await prompt_loader.get_prompt("recommend_plan", "few_shots")
    user_query_template = await prompt_loader.get_prompt("recommend_plan", "user_query")
    
    tools_text = await get_tools_and_skills_text()
    
    user_query = await prompt_renderer.render(
        user_query_template,
        destination=collected_info.get('destination'),
        dates=collected_info.get('dates'),
        duration=collected_info.get('duration'),
        budget=collected_info.get('budget', '未指定'),
        preferences=', '.join(collected_info.get('preferences', [])) or '无特殊偏好',
        search_results=str(search_results)[:1000],
        user_content=user_content
    )

    messages = [
        SystemMessage(content=f"{system_prompt}\n\n{few_shots}\n\n工具列表：\n{tools_text}"),
        HumanMessage(content=user_query)
    ]
    result = await llm.ainvoke(messages, config={"callbacks": [counter]})
    output_text = result.content

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
        recommend_plan = data
        desc = data.get("output", output_text)
        clarification_questions = data.get("clarification_questions", []) or []
        need_clarification = len(clarification_questions) > 0
    except Exception:
        recommend_plan = {"raw": output_text}
        desc = output_text
        clarification_questions = []
        need_clarification = False

    # 缓存
    cache_strategy.cache_recommendations(
        user_id=cache_key_biz,
        recommendations={
            "recommend_plan": recommend_plan,
            "output": desc,
            "need_clarification": need_clarification,
            "clarification_questions": clarification_questions,
            "stage": "awaiting_clarification" if need_clarification else "ready_for_execution"
        },
        interests=collected_info.get("preferences", []),
        budget=collected_info.get("budget")
    )

    if need_clarification:
        clarification_prompt = "为了更好地为您规划行程，请您回答以下问题：\n"
        for i, q in enumerate(clarification_questions, 1):
            clarification_prompt += f"{i}. {q}\n"
        clarification_prompt += "\n请回复您的答案,我会根据您的反馈继续为您推荐。"
        return {
            "messages": [AIMessage(content=clarification_prompt)],
            "usage": counter.dump(),
            "output": desc,
            "need_clarification": True,
            "clarification_questions": clarification_questions,
            "recommend_plan": None,
            "stage": "awaiting_clarification"
        }

    return {
        "messages": [AIMessage(content=desc)],
        "usage": counter.dump(),
        "output": desc,
        "recommend_plan": recommend_plan,
        "need_clarification": False,
        "clarification_questions": [],
        "stage": "ready_for_execution"
    }
async def recommend_execute_agent_node(state: SubState) -> Dict[str, Any]:
    """推荐执行节点 - 直接调用大模型进行推荐"""
    counter = TokenCounter()
    
    recommend_plan = state.get("recommend_plan", {})
    collected_info = state.get("collected_info", {})
    search_results = state.get("search_results", {})
    last_msg = state.get("messages", [])[-1] if state.get("messages") else None
    user_content = last_msg.content if last_msg else ""

    plan_payload = recommend_plan.get("recommend_plan", {}) if isinstance(recommend_plan, dict) else {}
    destination = plan_payload.get("destination", collected_info.get("destination", "unknown"))
    
    cache_key_biz = f"recommend_execute:{user_content[:50]}:{destination}"

    # 1️⃣ 业务缓存
    cached = cache_strategy.get_recommendations(
        user_id=cache_key_biz,
        interests=collected_info.get("preferences", []),
        budget=collected_info.get("budget")
    )
    if cached:
        logger.info("🎯 业务缓存命中(recommend_execute)")
        return {
            "messages": [AIMessage(content=cached.get("output", ""))],
            "usage": {"prompt": 0, "completion": 0, "cached": 0, "total": 0},
            "output": cached.get("output", ""),
            "recommendations": cached.get("recommendations", {})
        }
        
    llm = LLMFactory.create_model_by_tier(tier="cheap")
    
    system_prompt = await prompt_loader.get_prompt("recommend_execute", "system_prompt")
    user_query_template = await prompt_loader.get_prompt("recommend_execute", "user_query")
    
    user_profile = recommend_plan.get("user_profile_analysis", {})
    framework = recommend_plan.get("recommendation_framework", {})
    gaps = recommend_plan.get("information_gaps", {})

    plan_config = recommend_plan.get("recommend_plan", {})

    user_query = await prompt_renderer.render(
        user_query_template,
        destination=collected_info.get('destination'),
        origin=collected_info.get('origin', '未知'),
        dates=collected_info.get('dates'),
        duration=collected_info.get('duration'),
        budget=collected_info.get('budget', '未指定'),
        preferences=', '.join(collected_info.get('preferences', [])) or '无特殊偏好',
        group_size=collected_info.get('group_size', '未知'),
        special_requests=collected_info.get('special_requests', '无'),
        user_profile=json.dumps(user_profile, ensure_ascii=False),
        framework=json.dumps(framework, ensure_ascii=False),
        gaps=json.dumps(gaps, ensure_ascii=False),
        themes=', '.join(plan_config.get('themes', [])),
        num_plans=plan_config.get('num_plans', 3),
        focus_points=', '.join(plan_config.get('focus_points', [])),
        weights=plan_config.get('weights', {}),
        attractions=json.dumps(search_results.get('attractions', []), ensure_ascii=False, indent=2),
        hotels=json.dumps(search_results.get('hotels', []), ensure_ascii=False, indent=2),
        flights=json.dumps(search_results.get('flights', []), ensure_ascii=False, indent=2),
        other_info=json.dumps({k: v for k, v in search_results.items() if k not in ['attractions', 'hotels', 'flights']}, ensure_ascii=False, indent=2),
        user_content=user_content
    )

    try:
        logger.info("[Recommend Execute] 🚀 Starting direct LLM recommendation...")
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_query)
        ]
        
        result = await llm.ainvoke(messages, config={"callbacks": [counter]})
        output_text = result.content
        
        try:
            # 尝试解析 JSON 回复
            clean_text = output_text
            if "```json" in output_text:
                clean_text = output_text.split("```json")[1].split("```")[0].strip()
            elif "```" in output_text:
                clean_text = output_text.split("```")[1].split("```")[0].strip()
                
            data = json.loads(clean_text)
            recommendations = data.get("recommendations", data)
            desc = data.get("output", output_text)
        except json.JSONDecodeError:
            # 如果解析失败，创建基本结构
            recommendations = {
                "summary": "无法解析推荐结果",
                "plans": [],
                "raw_response": output_text
            }
            desc = output_text
            
        # 缓存结果
        cache_strategy.cache_recommendations(
            user_id=cache_key_biz,
            recommendations={"recommendations": recommendations, "output": desc},
            interests=collected_info.get("preferences", []),
            budget=collected_info.get("budget")
        )
        
        # 构建完整的输出文本（包含所有方案的详细描述）
        full_output = desc
        if recommendations and "plans" in recommendations:
            plans = recommendations["plans"]
            full_output += "\n\n## 详细推荐方案\n\n"
            for i, plan in enumerate(plans, 1):
                full_output += f"### 方案 {i}: {plan.get('title', '')}\n"
                full_output += f"{plan.get('subtitle', '')}\n\n"
                
                # 每日行程
                itinerary = plan.get("itinerary", [])
                for day in itinerary:
                    full_output += f"**{day.get('title', '')}**\n"
                    activities = day.get("activities", [])
                    for activity in activities:
                        full_output += f"- {activity.get('time', '')}: {activity.get('location', '')} - {activity.get('description', '')}\n"
                    full_output += "\n"
                
                # 预算和亮点
                budget = plan.get("budget_breakdown", {})
                if budget:
                    full_output += f"**预算**: 总计 {budget.get('total_budget', '')} 元\n"
                highlights = plan.get("highlights", [])
                if highlights:
                    full_output += f"**亮点**: {', '.join(highlights)}\n"
                full_output += "\n---\n\n"
        
        # 创建新的 AIMessage，包含完整内容
        full_message = AIMessage(content=full_output)
        
        return {
            "messages": [full_message],
            "usage": counter.dump(),
            "output": full_output,
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"❌ recommend_execute_agent_node failed: {e}")
        return {
            "messages": [AIMessage(content=f"Error: {e}")],
            "usage": counter.dump(),
            "output": f"Error: {e}",
            "recommendations": {"error": str(e)}
        }
def build_recommend_graph() -> StateGraph:
    """构建推荐子图（两阶段流程）"""
    graph = StateGraph(SubState)
    
    # 添加两个节点：规划 + 执行
    graph.add_node("recommend_plan", recommend_plan_node)
    graph.add_node("recommend_execute", recommend_execute_agent_node)
    
    # 设置边：规划 -> 执行/结束
    graph.add_conditional_edges(
        "recommend_plan",
        lambda state: "end" if state.get("need_clarification") else "recommend_execute",
        {
            "recommend_execute": "recommend_execute",
            "end": END
        }
    )
    graph.add_edge("recommend_execute", END)
    
    # 设置入口点
    graph.set_entry_point("recommend_plan")
    
    return graph.compile()

__all__ = ["build_recommend_graph"]
