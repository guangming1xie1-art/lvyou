"""
搜索工作流 - 两阶段搜索流程：规划 → 执行
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
    build_search_tools
)
from agents.mcp_client import get_mcp_client
from rag.retriever import HybridRetriever
from .hybrid_retrieval import hybrid_rank
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
    
    # 3️⃣ 定义系统 prompt（固定内容，用于创建缓存）
    system_prompt = """你是旅游搜索战略专家。你的工作不仅是重复用户信息，而是：

    1. 深度理解用户的真实需求
       - 识别用户的核心诉求和隐含偏好
       - 判断时间与预算的限制条件
    2. 识别信息缺口
       - 标注缺失的关键字段以及影响
       - 需要时提出澄清问题
    3. 制定清晰的搜索战略
       - 分阶段搜索策略
       - 优先级配置
       - RAG关键词优化
    4. 指导执行阶段
       - 输出可直接用于执行阶段的搜索指导

    ## 输出格式（必须是有效的 JSON)
    {
        "user_intent_analysis": {
            "core_needs": "核心需求描述",
            "user_interpretation": {
                "possible_focus": ["可能类型1", "可能类型2"],
                "time_pressure": "时间紧张度判断",
                "budget_flexibility": "预算弹性判断"
            },
            "potential_concerns": ["潜在问题1", "潜在问题2"]
        },
        "search_strategy": {
            "phase1_hot_spots": {
                "priority": "高/中/低",
                "focus": "阶段目标",
                "keywords": ["关键词1", "关键词2"]
            },
            "phase2_special_interests": {
                "priority": "高/中/低",
                "focus": "阶段目标",
                "keywords": ["关键词1", "关键词2"]
            },
            "phase3_accommodation": {
                "priority": "高/中/低",
                "focus": "阶段目标",
                "recommendations": "住宿策略"
            },
            "phase4_logistics": {
                "priority": "高/中/低",
                "focus": "阶段目标",
                "recommendations": "交通策略"
            }
        },
        "clarification_questions": ["问题1", "问题2"],
        "information_gaps": {
            "budget": "缺口说明",
            "travel_style": "缺口说明"
        },
        "search_configuration": {
            "priorities": {"attractions": 0.5, "hotels": 0.3, "flights": 0.2},
            "rag_search_keywords": ["关键词1", "关键词2"],
            "hotel_strategy": "住宿策略",
            "flight_strategy": "交通策略"
        },
        "search_plan": {
            "origin": "出发地",
            "destination": "目的地",
            "check_in": "入住日期",
            "check_out": "退房日期",
            "duration_days": 天数,
            "budget_range": "预算范围",
            "preferences": ["偏好1", "偏好2"]
        },
        "output": "搜索战略说明"
    }"""

    # 4️⃣ Few-shot 示例（固定内容，用于创建缓存）
    few_shots = """## 示例1: 信息相对完整
    输入: 杭州3天游,预算5000元,喜欢自然风景

    规划输出:
    {
        "user_intent_analysis": {
            "core_needs": "3天内体验杭州自然风景",
            "user_interpretation": {
                "possible_focus": ["自然景观", "湖景", "轻徒步"],
                "time_pressure": "时间较紧，需要优先排序",
                "budget_flexibility": "预算有限，需要控制成本"
            },
            "potential_concerns": []
        },
        "search_strategy": {
            "phase1_hot_spots": {
                "priority": "高",
                "focus": "西湖与灵隐寺等高评价景点",
                "keywords": ["杭州必去景点", "西湖游玩攻略"]
            },
            "phase2_special_interests": {
                "priority": "中",
                "focus": "西溪湿地等自然景观",
                "keywords": ["西溪湿地门票", "杭州自然景点推荐"]
            },
            "phase3_accommodation": {
                "priority": "中",
                "focus": "西湖周边经济型酒店",
                "recommendations": "优先西湖或黄龙附近酒店"
            },
            "phase4_logistics": {
                "priority": "低",
                "focus": "高铁与市内交通",
                "recommendations": "建议早到晚走，提升游玩时间"
            }
        },
        "clarification_questions": [],
        "information_gaps": {},
        "search_configuration": {
            "priorities": {"attractions": 0.5, "hotels": 0.3, "flights": 0.2},
            "rag_search_keywords": ["杭州自然景点推荐", "西湖3日游路线"],
            "hotel_strategy": "优先西湖周边",
            "flight_strategy": "高铁优先"
        },
        "search_plan": {
            "origin": "",
            "destination": "杭州",
            "check_in": "",
            "check_out": "",
            "duration_days": 3,
            "budget_range": "5000元",
            "preferences": ["自然风景"]
        },
        "output": "已制定杭州3日游搜索战略,优先景点与住宿,并控制预算。"
    }

    ## 示例2: 信息不完整
    输入: 北京游，偏好好玩的场所

    规划输出:
    {
        "user_intent_analysis": {
            "core_needs": "探索北京好玩的场所",
            "user_interpretation": {
                "possible_focus": ["景点景区", "主题乐园", "美食街区", "文化场所"],
                "time_pressure": "时间未知，需确认",
                "budget_flexibility": "预算未指定，范围较宽"
            },
            "potential_concerns": ["信息不足，需要补充预算和时间"]
        },
        "search_strategy": {
            "phase1_hot_spots": {
                "priority": "高",
                "focus": "北京必游景点",
                "keywords": ["北京热门景点排行", "北京必去"]
            },
            "phase2_special_interests": {
                "priority": "高",
                "focus": "娱乐场所与特色体验",
                "keywords": ["北京主题乐园", "北京娱乐景点"]
            },
            "phase3_accommodation": {
                "priority": "中",
                "focus": "市中心便捷酒店",
                "recommendations": "优先朝阳区或东城区"
            },
            "phase4_logistics": {
                "priority": "低",
                "focus": "交通时间优化",
                "recommendations": "需确认出发日期"
            }
        },
        "clarification_questions": ["请提供预算范围", "计划出行几天"],
        "information_gaps": {"budget": "未提供", "duration": "未提供"},
        "search_configuration": {
            "priorities": {"attractions": 0.5, "hotels": 0.3, "flights": 0.2},
            "rag_search_keywords": ["北京好玩景点排行", "北京主题乐园推荐"],
            "hotel_strategy": "优先朝阳区与东城区",
            "flight_strategy": "确认出发时间后优化"
        },
        "search_plan": {
            "origin": "",
            "destination": "北京",
            "check_in": "",
            "check_out": "",
            "duration_days": 0,
            "budget_range": "未指定",
            "preferences": ["好玩的场所"]
        },
        "output": "信息不足，需要补充预算与出行时长后再执行搜索。"
    }"""
    
    # 5️⃣ 工具和技能文本
    tools_text = await get_tools_and_skills_text()
    
    user_query = f"""请根据以下已收集的用户信息，生成搜索战略：

    ## 用户信息
    - 出发地：{collected_info.get('origin')}
    - 目的地：{collected_info.get('destination')}
    - 出发日：{collected_info.get('dates')}
    - 周期：{collected_info.get('duration')}
    - 预算：{collected_info.get('budget', '未指定')}
    - 偏好：{', '.join(collected_info.get('preferences', [])) or '无特殊偏好'}

    ## 原始消息
    {user_content}

    返回 JSON 格式的搜索战略。"""

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
            "messages": [AIMessage(content=desc)],
            "usage": counter.dump(),
            "output": clarification_prompt,
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

   # 3️⃣ 正确的系统提示词，指导Agent按策略执行
    system_prompt = f"""你是旅游搜索执行专家，负责根据搜索策略使用工具获取旅游信息。

    ## 执行策略
    1. 必须按顺序执行以下三个步骤，每个步骤都要实际调用对应工具：
    - 步骤1: 调用工具获取景点信息 (search_attractions)
    - 步骤2: 调用工具获取酒店信息 (search_hotels) 
    - 步骤3: 调用工具获取交通信息 (search_flights)
    2. 每个步骤完成后，在中间结果中确认该步骤已完成
    3. 最终汇总所有结果

    ## 搜索策略
    - 阶段1(热门景点): {search_plan.get('search_strategy', {}).get('phase1_hot_spots', {})}
    - 阶段2(特殊兴趣): {search_plan.get('search_strategy', {}).get('phase2_special_interests', {})}
    - 阶段3(住宿): {search_plan.get('search_strategy', {}).get('phase3_accommodation', {})}
    - 阶段4(交通): {search_plan.get('search_strategy', {}).get('phase4_logistics', {})}

    ## 参数信息
    - 目的地: {plan_payload.get('destination', '')}
    - 出发地: {plan_payload.get('origin', '')}
    - 入住日期: {plan_payload.get('check_in', '')}
    - 退房日期: {plan_payload.get('check_out', '')}
    - 预算范围: {plan_payload.get('budget_range', '')}

    ## 工具使用策略
    - 必须调用search_attractions获取景点数据
    - 必须调用search_hotels获取住宿数据
    - 必须调用search_flights获取交通数据
    - 可选使用RAG工具获取背景信息

    ## 输出格式(JSON)
    {{
        "output": "综合搜索结果文本描述",
        "search_results": {{
            "destinations": [],
            "hotels": [],
            "flights": [],
            "attractions": [],
            "rag_sources_used": [],
            "tools_used": []
        }}
    }}"""

    user_query = f"""请按执行策略完成搜索任务：

    ## 用户信息
    - 目的地：{collected_info.get('destination')}
    - 出发日：{collected_info.get('dates')}
    - 周期：{collected_info.get('duration')}
    - 预算：{collected_info.get('budget', '未指定')}
    - 偏好：{', '.join(collected_info.get('preferences', [])) or '无特殊偏好'}

    ## 用户原始请求
    {user_content}

    请严格按照执行策略调用所有必需工具并汇总结果。
    """

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
