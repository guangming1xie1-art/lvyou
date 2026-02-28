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
    
    system_prompt = """你是旅游推荐规划专家。你的工作不是简单复述搜索结果，而是：

    ## 职责
    1. 分析用户需求与搜索结果，洞察用户偏好与行程节奏
    2. 制定推荐框架：构建多方案策略，明确不同方案定位与满意度预期
    3. 识别信息缺口，提出澄清问题
    4. 为推荐执行阶段提供可操作的指导

    ## 输出格式(JSON)
    {
        "user_profile_analysis": {
            "trip_characteristics": {
                "duration": "行程时长",
                "destination_type": "目的地类型",
                "travel_pace": "行程节奏",
                "interest_focus": "兴趣焦点"
            },
            "recommendation_considerations": ["考虑点1", "考虑点2"]
        },
        "recommendation_framework": {
            "plan_1": {
                "name": "方案名称",
                "target": "目标人群",
                "focus": ["景点1", "景点2"],
                "characteristics": "方案特点",
                "estimated_satisfaction": 0.8
            }
        },
        "information_gaps": {
            "missing_inputs": ["缺失信息1"],
            "impact": "缺失影响"
        },
        "clarification_questions": ["问题1", "问题2"],
        "recommend_plan": {
            "themes": ["主题1", "主题2"],
            "num_plans": 3,
            "focus_points": ["侧重点1", "侧重点2"],
            "weights": {"budget": 0.3, "experience": 0.4, "convenience": 0.3}
        },
        "output": "推荐计划描述"
    }"""

    few_shots = """## 示例1: 信息相对完整
    用户:杭州3天,预算5000元,喜欢自然。
    搜索结果：包含西湖、灵隐寺、西溪湿地。

    输出：
    {
        "user_profile_analysis": {
            "trip_characteristics": {
                "duration": "3天",
                "destination_type": "城市自然+文化",
                "travel_pace": "适中",
                "interest_focus": "自然风景"
            },
            "recommendation_considerations": ["需要兼顾自然与文化体验"]
        },
        "recommendation_framework": {
            "plan_1": {
                "name": "经典自然版",
                "target": "首次到杭州",
                "focus": ["西湖", "灵隐寺"],
                "characteristics": "经典、景点集中",
                "estimated_satisfaction": 0.85
            },
            "plan_2": {
                "name": "湿地深度版",
                "target": "喜欢轻徒步",
                "focus": ["西溪湿地", "九溪"],
                "characteristics": "生态、放松",
                "estimated_satisfaction": 0.8
            }
        },
        "information_gaps": {
            "missing_inputs": [],
            "impact": ""
        },
        "clarification_questions": [],
        "recommend_plan": {
            "themes": ["自然山水", "文化寻踪"],
            "num_plans": 2,
            "focus_points": ["西湖十景", "湿地生态"],
            "weights": {"budget": 0.2, "experience": 0.6, "convenience": 0.2}
        },
        "output": "为您规划了以自然景观为主的推荐策略。"
    }

    ## 示例2: 信息不完整
    用户：北京游，偏好好玩的场所。
    搜索结果：基础景点信息有限。

    输出：
    {
        "user_profile_analysis": {
            "trip_characteristics": {
                "duration": "未知",
                "destination_type": "城市娱乐+文化",
                "travel_pace": "未知",
                "interest_focus": "好玩的场所"
            },
            "recommendation_considerations": ["缺少预算与行程节奏信息"]
        },
        "recommendation_framework": {
            "plan_1": {
                "name": "热门景点精选版",
                "target": "首次来北京",
                "focus": ["故宫", "长城"],
                "characteristics": "经典、可靠",
                "estimated_satisfaction": 0.8
            }
        },
        "information_gaps": {
            "missing_inputs": ["预算范围", "出行风格"],
            "impact": "影响酒店等级与行程强度"
        },
        "clarification_questions": ["您的预算范围是多少？", "偏好紧凑还是悠闲行程？"],
        "recommend_plan": {
            "themes": ["热门景点"],
            "num_plans": 1,
            "focus_points": ["经典景点"],
            "weights": {"budget": 0.3, "experience": 0.4, "convenience": 0.3}
        },
        "output": "信息不足，需要补充预算和行程风格后优化推荐。"
    }"""

    tools_text = await get_tools_and_skills_text()
    
    user_query = f"""请制定推荐策略：

    ## 用户信息
    - 目的地：{collected_info.get('destination')}
    - 出发日：{collected_info.get('dates')}
    - 周期：{collected_info.get('duration')}
    - 预算：{collected_info.get('budget', '未指定')}
    - 偏好：{', '.join(collected_info.get('preferences', [])) or '无特殊偏好'}

    ## 搜索结果摘要
    {str(search_results)[:1000]}

    ## 用户原始请求
    {user_content}

    返回 JSON 格式的推荐策略。"""

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
        return {
            "messages": [AIMessage(content=desc)],
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
    """推荐执行节点 - ReAct Agent + Prompt Cache"""
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
        # import logging
        # logger = logging.getLogger(__name__)
        logger.info("🎯 业务缓存命中(recommend_execute)")
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

    ## 输出格式(JSON)
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
    # cache_mgr = get_prompt_cache_manager()
    # prompt_cache_id = await cache_mgr.get_or_create_cache(
    #     cache_key="recommend_execute",
    #     llm=llm,
    #     system_prompt=system_prompt,
    #     few_shots=few_shots,
    #     tools_text=tools_text
    # )
    
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
    
    # 记录工具信息
    tool_names = [getattr(t, 'name', str(t)) for t in tools]
    logger.info(f"[Recommend Execute] 🔧 Tools available: {tool_names}")
    
    user_profile = recommend_plan.get("user_profile_analysis", {})
    framework = recommend_plan.get("recommendation_framework", {})
    gaps = recommend_plan.get("information_gaps", {})

    plan_config = recommend_plan.get("recommend_plan", {})

    user_query = f"""请生成个性化旅游推荐方案：

    ## 推荐策略分析
    - 用户画像：{user_profile}
    - 方案框架：{framework}
    - 信息缺口：{gaps}

    ## 推荐计划
    - 主题：{', '.join(plan_config.get('themes', []))}
    - 方案数量：{plan_config.get('num_plans', 3)}
    - 侧重点：{', '.join(plan_config.get('focus_points', []))}
    - 权重：{plan_config.get('weights', {})}

    ## 用户信息
    - 目的地：{collected_info.get('destination')}
    - 出发日：{collected_info.get('dates')}
    - 周期：{collected_info.get('duration')}
    - 预算：{collected_info.get('budget', '未指定')}
    - 偏好：{', '.join(collected_info.get('preferences', [])) or '无特殊偏好'}

    ## 搜索结果摘要
    {str(search_results)[:1000]}

    ## 基础推荐数据(Java MCP)
    {json.dumps(rec_base.get('user', {}), ensure_ascii=False)}

    ## 优质备选酒店(RAG 混合排序)
    {json.dumps(ranked_hotels[:5], ensure_ascii=False)}
    """

    try:
        # 创建 ReAct Agent（绑定真正的工具）
        logger.info(f"[Recommend Execute] 🤖 Creating ReAct agent with {len(tools)} tools")
        agent = create_react_agent(llm, tools)
        
        invoke_kwargs = {"callbacks": [counter]}
        if prompt_cache_id:
            invoke_kwargs["extra_body"] = {"cache_id": prompt_cache_id}
        
        logger.info(f"[Recommend Execute] 🚀 Starting agent execution...")
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=user_query)]},
            config=invoke_kwargs
        )
        logger.info(f"[Recommend Execute] ✅ Agent execution completed")
        
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
            user_id=cache_key_biz,
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
        # import logging
        # logger = logging.getLogger(__name__)
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
