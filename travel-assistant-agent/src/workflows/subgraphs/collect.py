"""
信息收集工作流 - 单节点工作流，收集用户的旅游需求信息
"""

from typing import Dict, Any
import json

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from utils.token_counter import TokenCounter
from llm.factory import LLMFactory

from .common import SubState, cache_strategy

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
        # 从 common 导入的 logger
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Collection cache HIT")
        return {
            "messages": [AIMessage(content=cached.get("output", ""))],
            "usage": {"prompt": 0, "completion": 0, "total": 0},
            "output": cached.get("output", ""),
            "collected_info": cached.get("collected_info", {}),
            "collection_message": cached.get("collection_message", "")
        }

    # 系统提示词
    system_prompt = f"""你是信息收集员，负责与用户交互收集旅游需求。

    你的核心任务：
    1. 分析用户的旅游需求
    2. 识别关键信息：目的地、时间、预算、偏好等
    3. ⚠️ 【重要】严格验证信息的合法性和完整性：
    - 日期必须合法（检查月份天数、日期格式等）
    - 检查月份范围: 1-12月
    - 检查日期范围：根据月份的实际天数(如2月最多29天)
    - 关键信息（目的地、日期）不能缺失
    4. 如果信息有问题或不足，生成友好的澄清提问

    🔴 【critical】complete 字段的含义（这个字段直接影响后续工作流）：
    - complete = true: ✅ 所有关键信息都有效且完整，工作流将进入搜索阶段
    - complete = false: ❌ 发现信息错误或不足，工作流停止，用户需要澄清

    【重点】如果发现任何信息错误（日期无效、信息缺失等），你必须：
    1. 设置 complete = false
    2. 在回复中清楚地指出问题
    3. 提供修正建议和追问

    之前的对话历史：
    {history_text if history_text else "（无历史记录）"}

    返回格式（必须是有效的 JSON):
    {{
        "destination": "目的地（如北京）",
        "duration": "天数（整数或描述）",
        "budget": "预算范围(如5000-10000元)",
        "preferences": ["偏好1", "偏好2"],
        "dates": "出发时间(YYYY-MM-DD格式或描述)",
        "complete": true or false,
        "message": "你对用户的回复（澄清问题或确认信息）"
    }}

    注意:message 字段将单独存储用于对话展示，不会传递给下游搜索和推荐流程。

    【规则 1】设置 complete=true 的条件：
    ✅ 目的地明确
    ✅ 日期有效且合法（特别注意月份天数）
    ✅ 出行时长清晰
    ✅ 足以进行搜索

    【规则 2】设置 complete=false 的条件：
    ❌ 日期错误(如2月30号、13月等)
    ❌ 日期格式不清楚或模糊
    ❌ 缺少关键信息（目的地、日期）
    ❌ 信息逻辑矛盾
    ❌ 其他需要用户确认的问题

    【示例 1】完整输入 - complete=true:
    用户输入:我现在在大连,2026年2月28号出发,想去北京玩3天
    返回：
    {{
        "origin":"大连",
        "destination": "北京",
        "duration": "3天",
        "budget": "4000-6000元",
        "preferences": ["喜欢博物馆"],
        "dates": "2026-02-28",
        "complete": true,
        "message": "客户计划在2026年2月28日从大连出发去北京,游玩3天,预算在4000-6000元内,偏好是喜欢博物馆,请为客户搜索合适的酒店、航班和景点推荐。"
    }}

    【示例 2】错误输入 - complete=false:
    用户输入:我现在在大连,2026年2月30号,想去北京玩3天
    返回：
    {{
        "origin":"大连",
        "destination": "北京",
        "duration": "3天",
        "budget": "未指定",
        "preferences": ["无偏好"],
        "dates": "2026-02-30(❌ 无效)",
        "complete": false,
        "message": "我注意到您提供的信息中有一个小问题需要澄清。2026年2月30日这个日期是不存在的,因为2月份最多只有29天(闰年)。\\n\\n请问您是想在以下哪个日期出发呢?\\n- 2026年2月29日\\n- 2026年3月1日\\n- 或其他时间？"
    }}

    说明：以上返回中的 message 字段将被提取并单独存储为 collection_message,用于对话展示;其他字段作为 collected_info 传递给下游流程。
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
        try:
            # 去除可能的 Markdown 代码块标记
            cleaned_text = output_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]  # 去掉 ```json
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]  # 去掉 ```
            
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]  # 去掉结尾的 ```
            
            cleaned_text = cleaned_text.strip()
            
            collected_info = json.loads(cleaned_text)
        except:
            collected_info = {"raw": output_text, "complete": False}

        # 提取 collection_message（对话消息）和 collected_info（结构化数据）
        collection_message = collected_info.pop("message", "") if isinstance(collected_info, dict) else ""

        # 缓存结果
        cache_strategy.cache_user_preferences(cache_key, {
            "output": output_text,
            "collected_info": collected_info,
            "collection_message": collection_message
        })

        return {
            "messages": [result],
            "usage": counter.dump(),
            "output": output_text,
            "collected_info": collected_info,
            "collection_message": collection_message
        }

    except Exception as e:
        # 从 common 导入的 logger
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"collect_info_node failed: {e}")
        return {
            "messages": [AIMessage(content=f"Error: {e}")],
            "usage": {"prompt": 0, "completion": 0, "total": 0},
            "output": f"Error: {e}",
            "collected_info": {"error": str(e)}
        }


def _route_collect_main(state: SubState) -> str:
    """
    主工作流使用的路由函数（在 main_workflow.py 中调用）

    根据信息完整性决定工作流分支
    """
    collected_info = state.get("collected_info", {})
    is_complete = collected_info.get("complete", False)

    import logging
    logger = logging.getLogger(__name__)

    if is_complete:
        logger.info("✅ Info complete, routing to search stage")
        return "search"
    else:
        logger.info("❌ Info incomplete, routing to END (user needs to clarify)")
        return "end"


def build_collect_info_graph() -> StateGraph:
    """构建信息收集子图（简单的单节点图）"""
    graph = StateGraph(SubState)
    graph.add_node("collect", collect_info_node)
    graph.add_edge("collect", END)
    graph.set_entry_point("collect")
    return graph.compile()


__all__ = ["build_collect_info_graph", "_route_collect_main"]
