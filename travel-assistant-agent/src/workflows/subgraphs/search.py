"""
搜索工作流 - 两阶段搜索流程：规划 → 执行
"""

from typing import Dict, Any
import json

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from utils.token_counter import TokenCounter
from llm.factory import LLMFactory
from cache.prompt_cache_manager import get_prompt_cache_manager

from .common import (
    SubState, cache_strategy, get_tools_and_skills_text, 
    build_search_tools
)
from agents.mcp_client import get_mcp_client
from rag.retriever import HybridRetriever
from .hybrid_retrieval import hybrid_rank


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
    cached = cache_strategy.get_search_results(query=f"plan_{cache_key_biz}", destination=destination)
    if cached:
        import logging
        logger = logging.getLogger(__name__)
        logger.info("🎯 业务缓存命中(search_plan)")
        return {
            "messages": [AIMessage(content=cached.get("output", ""))],
            "usage": {"prompt": 0, "completion": 0, "cached": 0, "total": 0},
            "output": cached.get("output", ""),
            "search_plan": cached.get("search_plan", {})
        }
    
    # 2️⃣ 获取 LLM（便宜层）
    llm = LLMFactory.create_model_by_tier(tier="cheap")
    
    # 3️⃣ 定义系统 prompt（固定内容，用于创建缓存）
    system_prompt = """你是旅游搜索规划专家。

    ## 职责
    1. 根据以提取到的信息(出发地、目的地、出行日期、预算、偏好等)制定搜索策略和优先级
    2. 生成用于 RAG 检索的关键词

    ## 输出格式（必须是有效的 JSON)
    {
        "search_plan": {
            "origin": "出发地",
            "destination": "目的地",
            "check_in": "入住日期",
            "check_out": "退房日期",
            "duration_days": 天数,
            "budget_range": "预算范围",
            "preferences": ["偏好1", "偏好2"],
            "search_priorities": ["hotel", "flight", "attraction"],
            "rag_search_keywords": ["关键词1", "关键词2"]
        },
        "output": "搜索计划描述"
    }"""
    
    # 4️⃣ Few-shot 示例（固定内容，用于创建缓存）
    few_shots = """## 示例 1:国内旅游
    用户:我想2025-02-01,从上海出发去杭州的西湖,3天,预算5000元,喜欢自然和文化

    输出：
    {
        "search_plan": {
            "origin": "上海",
            "destination": "杭州",
            "check_in": "2025-02-01",
            "check_out": "2025-02-04",
            "duration_days": 3,
            "budget_range": "5000元",
            "preferences": ["自然景观", "文化遗产"],
            "search_priorities": ["hotel", "attraction", "restaurant"],
            "rag_search_keywords": ["杭州西湖", "灵隐寺", "杭州美食"]
        },
        "output": "为您制定了杭州3日游搜索计划,重点搜索西湖周边酒店和文化景点。"
    }"""
    
    # 5️⃣ 工具和技能文本
    tools_text = await get_tools_and_skills_text()
    
    # 6️⃣ 获取或创建 Prompt Cache
    cache_mgr = get_prompt_cache_manager()
    prompt_cache_id = await cache_mgr.get_or_create_cache(
        cache_key="search_plan",
        llm=llm,
        system_prompt=system_prompt,
        few_shots=few_shots,
        tools_text=tools_text
    )
    
    user_query = f"""请根据以下已收集的用户信息，生成搜索计划：

    ## 用户信息
    - 出发地：{collected_info.get('origin')}
    - 目的地：{collected_info.get('destination')}
    - 出发日：{collected_info.get('dates')}
    - 周期：{collected_info.get('duration')}
    - 预算：{collected_info.get('budget', '未指定')}
    - 偏好：{', '.join(collected_info.get('preferences', [])) or '无特殊偏好'}

    ## 原始消息
    {user_content}

    返回 JSON 格式的搜索计划。"""

    if not prompt_cache_id:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("⚠️ Prompt cache creation failed, falling back to direct invocation")
        messages = [
            SystemMessage(content=f"{system_prompt}\n\n{few_shots}\n\n工具列表:\n{tools_text}"),
            HumanMessage(content=user_query)
        ]
        result = await llm.ainvoke(messages, config={"callbacks": [counter]})
        output_text = result.content
    else:
        # 7️⃣ 使用 Prompt Cache 调用 LLM
        output_text, cached_tokens = await cache_mgr.invoke_with_cache(
            llm=llm,
            cache_id=prompt_cache_id,
            user_query=user_query,
            counter=counter
        )
    
    if output_text is None:
        return {
            "messages": [AIMessage(content="Error: LLM invocation failed")],
            "usage": counter.dump(),
            "output": "Error: LLM invocation failed",
            "search_plan": {"error": "LLM invocation failed"}
        }
        
    # 解析搜索计划
    try:
        data = json.loads(output_text)
        search_plan = data.get("search_plan", {})
        desc = data.get("output", output_text)
    except:
        search_plan = {"raw": output_text, "destination": destination}
        desc = output_text
    
    # 缓存结果到业务缓存
    cache_strategy.cache_search_results(
        query=f"plan_{cache_key_biz}",
        results={"search_plan": search_plan, "output": desc},
        destination=destination
    )
    
    return {
        "messages": [AIMessage(content=output_text)],
        "usage": counter.dump(),
        "output": desc,
        "search_plan": search_plan
    }


async def search_execute_agent_node(state: SubState) -> Dict[str, Any]:
    """搜索执行节点 - ReAct Agent + Prompt Cache"""
    counter = TokenCounter()
    
    search_plan = state.get("search_plan", {})
    collected_info = state.get("collected_info", {})
    last_msg = state.get("messages", [])[-1] if state.get("messages") else None
    user_content = last_msg.content if last_msg else ""
    
    destination = search_plan.get("destination", "unknown")
    cache_key_biz = f"search_exec:{user_content[:50]}:{destination}"
    
    # 1️⃣ 业务缓存
    cached = cache_strategy.get_search_results(query=user_content, destination=destination)
    if cached:
        import logging
        logger = logging.getLogger(__name__)
        logger.info("🎯 业务缓存命中（search_execute）")
        return {
            "messages": [AIMessage(content=cached.get("output", ""))],
            "usage": {"prompt": 0, "completion": 0, "cached": 0, "total": 0},
            "output": cached.get("output", ""),
            "search_results": cached.get("search_results", {})
        }

    # 2️⃣ 获取 LLM（标准层）
    llm = LLMFactory.create_model_by_tier(tier="standard")
    
    # 3️⃣ 系统 Prompt (ReAct)
    system_prompt = """你是旅游搜索执行专家，负责利用各种工具获取详细的旅游信息。

## 职责
1. 根据搜索计划，调用 RAG、Java API 或其他工具进行深度搜索
2. 获取具体的酒店、航班、景点和价格信息
3. 综合多方数据，形成完整的搜索结果报告
4. 必须输出有效的 JSON 结构

## 工具使用策略
- 优先使用 RAG 检索知识库中的旅游攻略和常识
- 使用 Java API (MCP) 获取实时的酒店、航班数据
- 使用 Agent Skills 进行特定的搜索任务

## 输出格式（JSON）
{
    "output": "综合搜索结果文本描述",
    "search_results": {
        "destinations": [...],
        "hotels": [...],
        "flights": [...],
        "attractions": [...],
        "rag_sources_used": [...],
        "tools_used": [...]
    }
}"""

    few_shots = "## 示例：请通过调用工具获取杭州的酒店和景点信息，并返回 JSON。"
    tools_text = await get_tools_and_skills_text()
    
    # 4️⃣ Prompt Cache
    cache_mgr = get_prompt_cache_manager()
    prompt_cache_id = await cache_mgr.get_or_create_cache(
        cache_key="search_execute",
        llm=llm,
        system_prompt=system_prompt,
        few_shots=few_shots,
        tools_text=tools_text
    )
    
    # 5️⃣ 构建工具
    tools = await build_search_tools(search_plan)

    # 6️⃣ 执行逻辑
    # Step 1: Java MCP 查询原始数据
    mcp_client = get_mcp_client()
    raw_hotels_resp = await mcp_client.call_tool(
        "search_hotels",
        destination=search_plan.get("destination"),
        price_min=collected_info.get("budget_min", 0),
        price_max=collected_info.get("budget_max", 1000000),
        rating_min=4.0
    )
    raw_hotels = raw_hotels_resp.get("data", []) if isinstance(raw_hotels_resp.get("data"), list) else []

    # Step 2: RAG 混合检索
    hybrid_retriever = HybridRetriever()
    rag_query = f"{search_plan.get('destination')} {', '.join(search_plan.get('rag_search_keywords', []))}"
    rag_docs = await hybrid_retriever.aretrieve(rag_query, k=50)

    # Step 3: 混合排序
    ranked_hotels = hybrid_rank(raw_hotels, rag_docs, search_plan)

    user_query = f"""请执行以下搜索任务：

## 搜索计划
- 目的地：{search_plan.get('destination')}
- 入住日期：{search_plan.get('check_in')}
- 退房日期：{search_plan.get('check_out')}
- 住宿天数：{search_plan.get('duration_days')}
- 搜索优先级：{', '.join(search_plan.get('search_priorities', []))}

## 用户信息
- 目的地：{collected_info.get('destination')}
- 出发日：{collected_info.get('dates')}
- 周期：{collected_info.get('duration')}
- 预算：{collected_info.get('budget', '未指定')}
- 偏好：{', '.join(collected_info.get('preferences', [])) or '无特殊偏好'}

## 用户原始请求
{user_content}

## 已获取的优质酒店（经过混合排序）
{json.dumps(ranked_hotels[:5], ensure_ascii=False)}
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
            query=user_content,
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
        import logging
        logger = logging.getLogger(__name__)
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
    
    # 设置边：规划 -> 执行 -> 结束
    graph.add_edge("search_plan", "search_execute")
    graph.add_edge("search_execute", END)
    
    # 设置入口点
    graph.set_entry_point("search_plan")
    
    return graph.compile()


__all__ = ["build_search_graph"]
