"""
推荐工作流 - 两阶段推荐流程：规划 → 执行
"""

from typing import Dict, Any
import json

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from ....utils.token_counter import TokenCounter
from ....llm.factory import LLMFactory
from ....cache.prompt_cache_manager import get_prompt_cache_manager

from .common import (
    SubState, cache_strategy, get_tools_and_skills_text, 
    build_recommend_tools
)
from ....agents.mcp_client import get_mcp_client
from ....rag.retriever import HybridRetriever
from .hybrid_retrieval import hybrid_rank


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
        user_id=f"plan_{destination}",
        interests=collected_info.get("preferences", []),
        budget=collected_info.get("budget")
    )
    if cached:
        import logging
        logger = logging.getLogger(__name__)
        logger.info("🎯 业务缓存命中（recommend_plan）")
        return {
            "messages": [AIMessage(content=cached.get("output", ""))],
            "usage": {"prompt": 0, "completion": 0, "cached": 0, "total": 0},
            "output": cached.get("output", ""),
            "recommend_plan": cached.get("recommend_plan", {})
        }
        
    llm = LLMFactory.create_model_by_tier(tier="cheap")
    
    system_prompt = """你是旅游推荐规划专家。

## 职责
1. 分析用户需求和已有的搜索结果
2. 制定推荐策略：包括主题、方案数量、侧重点和评分权重
3. 确保推荐方案的多样性和针对性

## 输出格式（JSON）
{
    "recommend_plan": {
        "themes": ["主题1", "主题2"],
        "num_plans": 3,
        "focus_points": ["侧重点1", "侧重点2"],
        "weights": {"budget": 0.3, "experience": 0.4, "convenience": 0.3}
    },
    "output": "推荐计划描述"
}"""

    few_shots = """## 示例
用户：想去杭州，喜欢自然。
搜索结果：包含西湖、灵隐寺、西溪湿地。

输出：
{
    "recommend_plan": {
        "themes": ["自然山水", "文化寻踪"],
        "num_plans": 2,
        "focus_points": ["西湖十景", "湿地生态"],
        "weights": {"budget": 0.2, "experience": 0.6, "convenience": 0.2}
    },
    "output": "为您规划了以自然景观为主的推荐策略。"
}"""

    tools_text = await get_tools_and_skills_text()
    cache_mgr = get_prompt_cache_manager()
    prompt_cache_id = await cache_mgr.get_or_create_cache(
        cache_key="recommend_plan",
        llm=llm,
        system_prompt=system_prompt,
        few_shots=few_shots,
        tools_text=tools_text
    )
    
    user_query = f"""请制定推荐计划：
用户信息：{json.dumps(collected_info, ensure_ascii=False)}
搜索结果摘要：{str(search_results)[:1000]}
用户原始请求：{user_content}"""

    if not prompt_cache_id:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("⚠️ Prompt cache creation failed, falling back to direct invocation")
        messages = [
            SystemMessage(content=f"{system_prompt}\n\n{few_shots}\n\n工具列表：\n{tools_text}"),
            HumanMessage(content=user_query)
        ]
        result = await llm.ainvoke(messages, config={"callbacks": [counter]})
        output_text = result.content
    else:
        output_text, cached_tokens = await cache_mgr.invoke_with_cache(
            llm=llm,
            cache_id=prompt_cache_id,
            user_query=user_query,
            counter=counter
        )
        
    try:
        data = json.loads(output_text)
        recommend_plan = data.get("recommend_plan", {})
        desc = data.get("output", output_text)
    except:
        recommend_plan = {"raw": output_text}
        desc = output_text
        
    # 缓存
    cache_strategy.cache_recommendations(
        user_id=f"plan_{destination}",
        results={"recommend_plan": recommend_plan, "output": desc},
        interests=collected_info.get("preferences", []),
        budget=collected_info.get("budget")
    )
    
    return {
        "messages": [AIMessage(content=output_text)],
        "usage": counter.dump(),
        "output": desc,
        "recommend_plan": recommend_plan
    }


async def recommend_execute_agent_node(state: SubState) -> Dict[str, Any]:
    """推荐执行节点 - ReAct Agent + Prompt Cache"""
    counter = TokenCounter()
    
    recommend_plan = state.get("recommend_plan", {})
    collected_info = state.get("collected_info", {})
    search_results = state.get("search_results", {})
    last_msg = state.get("messages", [])[-1] if state.get("messages") else None
    user_content = last_msg.content if last_msg else ""
    
    destination = collected_info.get("destination", "unknown")
    
    # 1️⃣ 业务缓存
    cached = cache_strategy.get_recommendations(
        user_id=f"exec_{destination}",
        interests=collected_info.get("preferences", []),
        budget=collected_info.get("budget")
    )
    if cached:
        import logging
        logger = logging.getLogger(__name__)
        logger.info("🎯 业务缓存命中（recommend_execute）")
        return {
            "messages": [AIMessage(content=cached.get("output", ""))],
            "usage": {"prompt": 0, "completion": 0, "cached": 0, "total": 0},
            "output": cached.get("output", ""),
            "recommendations": cached.get("recommendations", {})
        }
        
    llm = LLMFactory.create_model_by_tier(tier="standard")
    
    system_prompt = """你是旅游推荐执行专家，负责生成个性化的旅游方案。

## 职责
1. 根据推荐计划和搜索结果，生成具体的旅游行程方案
2. 包含每日行程、推荐酒店、预估预算和亮点介绍
3. 使用工具获取额外的推荐建议或进行价格校验
4. 必须输出有效的 JSON 结构

## 输出格式（JSON）
{
    "recommendations": {
        "plans": [
            {
                "id": "plan_1",
                "title": "方案标题",
                "itinerary": [...],
                "budget": {...},
                "highlights": [...]
            }
        ]
    },
    "output": "方案概览描述"
}"""

    few_shots = "## 示例：根据杭州搜索结果生成一个西湖深度游方案。"
    tools_text = await get_tools_and_skills_text()
    
    # 4️⃣ Prompt Cache
    cache_mgr = get_prompt_cache_manager()
    prompt_cache_id = await cache_mgr.get_or_create_cache(
        cache_key="recommend_execute",
        llm=llm,
        system_prompt=system_prompt,
        few_shots=few_shots,
        tools_text=tools_text
    )
    
    # Step 1: Java MCP 获取推荐基础数据
    mcp_client = get_mcp_client()
    rec_base_resp = await mcp_client.call_tool(
        "get_recommendation_base",
        email=collected_info.get("email", "guest@example.com"),
        destination=destination
    )
    rec_base = rec_base_resp.get("data", {})
    raw_hotels = rec_base.get("hotels", [])
    
    # Step 2: RAG 混合检索
    hybrid_retriever = HybridRetriever()
    rag_query = f"recommendations for {destination} with preferences {', '.join(collected_info.get('preferences', []))}"
    rag_docs = await hybrid_retriever.aretrieve(rag_query, k=50)
    
    # Step 3: 混合排序
    ranked_hotels = hybrid_rank(raw_hotels, rag_docs, recommend_plan)

    tools = await build_recommend_tools(recommend_plan)
    
    user_query = f"""请生成个性化旅游推荐方案：
推荐计划：{json.dumps(recommend_plan, ensure_ascii=False)}
用户信息：{json.dumps(collected_info, ensure_ascii=False)}
搜索结果摘要：{str(search_results)[:1000]}

## 基础推荐数据（Java MCP）:
{json.dumps(rec_base.get('user', {}), ensure_ascii=False)}

## 优质备选酒店（RAG 混合排序）:
{json.dumps(ranked_hotels[:5], ensure_ascii=False, indent=2)}
"""

    try:
        agent = create_react_agent(llm, tools)
        
        invoke_kwargs = {"callbacks": [counter]}
        if prompt_cache_id:
            invoke_kwargs["extra_body"] = {"cache_id": prompt_cache_id}
            
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=user_query)]},
            config=invoke_kwargs
        )
        
        last_msg = result["messages"][-1]
        output_text = last_msg.content
        
        try:
            # 兼容处理 JSON 回复
            clean_text = output_text
            if "```json" in output_text:
                clean_text = output_text.split("```json")[1].split("```")[0].strip()
            elif "```" in output_text:
                clean_text = output_text.split("```")[1].split("```")[0].strip()
                
            data = json.loads(clean_text)
            recommendations = data.get("recommendations", data)
            desc = data.get("output", output_text)
        except:
            recommendations = {"raw": output_text}
            desc = output_text
            
        # 缓存
        cache_strategy.cache_recommendations(
            user_id=f"exec_{destination}",
            results={"recommendations": recommendations, "output": desc},
            interests=collected_info.get("preferences", []),
            budget=collected_info.get("budget")
        )
        
        return {
            "messages": [last_msg],
            "usage": counter.dump(),
            "output": desc,
            "recommendations": recommendations
        }
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
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
    
    # 设置边：规划 -> 执行 -> 结束
    graph.add_edge("recommend_plan", "recommend_execute")
    graph.add_edge("recommend_execute", END)
    
    # 设置入口点
    graph.set_entry_point("recommend_plan")
    
    return graph.compile()


__all__ = ["build_recommend_graph"]
