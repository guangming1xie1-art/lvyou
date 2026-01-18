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
from typing import Dict, Any, Sequence, Annotated, Optional, List
import operator
import logging

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage, SystemMessage
import json

from src.utils.token_counter import TokenCounter
from src.agents.mcp_client import get_mcp_client
from src.skills.registry import SkillRegistry
from src.config import settings
from src.llm.factory import LLMFactory
from src.cache.cache_strategy import CacheStrategy
from src.rag.knowledge_base import KnowledgeBase
from src.cache.prompt_cache_manager import get_prompt_cache_manager

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


# ============ 2. 搜索子图（两阶段流程） ============

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
        logger.info("🎯 业务缓存命中（search_plan）")
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
1. 分析用户的旅游需求（从信息收集中提取）
2. 识别关键信息：目的地、出行日期、预算、偏好
3. 制定搜索策略和优先级
4. 生成用于 RAG 检索的关键词

## 输出格式（必须是有效的 JSON）
{
    "search_plan": {
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
    few_shots = """## 示例 1：国内旅游
用户：我想去杭州，3天，预算5000元，喜欢自然和文化

输出：
{
    "search_plan": {
        "destination": "杭州",
        "check_in": "2025-02-01",
        "check_out": "2025-02-04",
        "duration_days": 3,
        "budget_range": "5000元",
        "preferences": ["自然景观", "文化遗产"],
        "search_priorities": ["hotel", "attraction", "restaurant"],
        "rag_search_keywords": ["杭州西湖", "灵隐寺", "杭州美食"]
    },
    "output": "为您制定了杭州3日游搜索计划，重点搜索西湖周边酒店和文化景点。"
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
{json.dumps(collected_info, ensure_ascii=False, indent=2)}

## 原始消息
{user_content}

返回 JSON 格式的搜索计划。"""

    if not prompt_cache_id:
        logger.warning("⚠️ Prompt cache creation failed, falling back to direct invocation")
        messages = [
            SystemMessage(content=f"{system_prompt}\n\n{few_shots}\n\n工具列表：\n{tools_text}"),
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
    user_query = f"""请执行以下搜索任务：
搜索计划：{json.dumps(search_plan, ensure_ascii=False)}
用户信息：{json.dumps(collected_info, ensure_ascii=False)}
用户原始请求：{user_content}"""

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


# ============ 3. 推荐子图（两阶段流程） ============

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
    
    cache_mgr = get_prompt_cache_manager()
    prompt_cache_id = await cache_mgr.get_or_create_cache(
        cache_key="recommend_execute",
        llm=llm,
        system_prompt=system_prompt,
        few_shots=few_shots,
        tools_text=tools_text
    )
    
    tools = await build_recommend_tools(recommend_plan)
    
    user_query = f"""请生成旅游方案：
推荐计划：{json.dumps(recommend_plan, ensure_ascii=False)}
搜索结果摘要：{str(search_results)[:2000]}
用户信息：{json.dumps(collected_info, ensure_ascii=False)}
用户原始请求：{user_content}"""

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
