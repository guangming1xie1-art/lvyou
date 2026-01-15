"""
搜索节点 - 处理搜索相关的任务
集成RAG知识库检索和Redis缓存
"""
from typing import Dict, Any, Optional
from ..state import ConversationState
from ...rag.knowledge_base import KnowledgeBase, TravelKnowledgeBase
from ...cache.cache_strategy import CacheStrategy
from ...llm.factory import LLMFactory, ModelTier
import logging

logger = logging.getLogger(__name__)

# 全局实例（懒加载）
_knowledge_base: Optional[KnowledgeBase] = None
_cache_strategy: Optional[CacheStrategy] = None


def get_knowledge_base() -> KnowledgeBase:
    """获取知识库实例（懒加载）"""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = TravelKnowledgeBase()
    return _knowledge_base


def get_cache_strategy() -> CacheStrategy:
    """获取缓存策略实例（懒加载）"""
    global _cache_strategy
    if _cache_strategy is None:
        _cache_strategy = CacheStrategy()
    return _cache_strategy


async def plan_search(state: ConversationState) -> ConversationState:
    """搜索规划节点：使用RAG和LLM规划搜索"""

    try:
        user_requirements = state.get("user_requirements", {})
        user_message = state.get("user_message", "")

        # 1. 尝试从缓存获取RAG上下文
        cache_strategy = get_cache_strategy()
        rag_context = cache_strategy.get_rag_context(user_message)

        if rag_context is None:
            # 2. 从知识库检索相关上下文
            knowledge_base = get_knowledge_base()
            rag_context = knowledge_base.get_relevant_context(
                user_message,
                k=5
            )

            # 3. 缓存RAG上下文
            if rag_context:
                cache_strategy.cache_rag_context(user_message, rag_context)
                logger.info(f"Cached RAG context for query: {user_message[:50]}...")
        else:
            logger.info(f"Cache HIT for RAG context: {user_message[:50]}...")

        # 4. 使用LLM规划搜索（使用标准层LLM）
        llm = LLMFactory.create_model(
            provider="deepseek",  # 使用便宜层的DeepSeek进行规划
            tier=ModelTier.CHEAP
        )

        # 构建规划提示
        planning_prompt = f"""
用户需求：{user_message}

用户偏好：
- 目的地：{user_requirements.get('destination', '待定')}
- 预算：{user_requirements.get('budget', '待定')}
- 出行人数：{user_requirements.get('travelers', 1)}
- 出行时间：{user_requirements.get('dates', '待定')}

请根据用户需求，生成具体的搜索查询计划。
返回JSON格式：
{{
    "search_query": "具体的搜索查询",
    "search_type": "flight|hotel|attraction|综合",
    "destination": "目的地",
    "additional_info": "其他需要搜索的信息"
}}
"""

        # 生成搜索查询（简化版）
        destination = user_requirements.get("destination", "旅游目的地")
        search_type = "综合"
        
        # 根据消息判断搜索类型
        if "机票" in user_message or "航班" in user_message or "飞" in user_message:
            search_type = "flight"
        elif "酒店" in user_message or "住宿" in user_message:
            search_type = "hotel"
        elif "景点" in user_message or "好玩" in user_message:
            search_type = "attraction"

        search_query = f"{destination} {search_type} 信息"

        logger.info(f"Search planning: Generated query '{search_query}' (type: {search_type})")

        return {
            **state,
            "search_query": search_query,
            "search_type": search_type,
            "destination": destination,
            "rag_context": rag_context,
            "stage": "search_planning"
        }

    except Exception as e:
        logger.error(f"Search planning failed: {str(e)}")
        return {
            **state,
            "error_message": f"搜索规划失败: {str(e)}",
            "workflow_status": "failed"
        }


async def execute_search(state: ConversationState) -> ConversationState:
    """搜索执行节点：调用搜索服务"""

    try:
        search_query = state.get("search_query", "")
        search_type = state.get("search_type", "综合")
        user_requirements = state.get("user_requirements", {})
        destination = state.get("destination", "")

        # 1. 尝试从缓存获取搜索结果
        cache_strategy = get_cache_strategy()
        cached_results = cache_strategy.get_search_results(
            search_query,
            destination=destination
        )

        if cached_results is not None:
            logger.info(f"Cache HIT for search results: {search_query}")
            return {
                **state,
                "search_results": cached_results,
                "search_executed": True,
                "stage": "search_completed",
                "cache_hit": True
            }

        # 2. 执行实际搜索（简化版：返回结构化搜索结果）
        # 实际实现应该调用真实的搜索服务API
        search_results = []

        if search_type in ["flight", "综合"]:
            search_results.append({
                "type": "flight",
                "title": f"前往 {destination} 的航班",
                "description": "搜索符合条件的航班信息",
                "details": {
                    "destination": destination,
                    "search_query": search_query
                },
                "confidence": 0.9
            })

        if search_type in ["hotel", "综合"]:
            search_results.append({
                "type": "hotel",
                "title": f"{destination} 酒店推荐",
                "description": "搜索目的地优质住宿选择",
                "details": {
                    "destination": destination,
                    "budget": user_requirements.get("budget", "")
                },
                "confidence": 0.85
            })

        if search_type in ["attraction", "综合"]:
            search_results.append({
                "type": "attraction",
                "title": f"{destination} 热门景点",
                "description": "搜索目的地必游景点",
                "details": {
                    "destination": destination,
                    "interests": user_requirements.get("interests", [])
                },
                "confidence": 0.8
            })

        # 3. 缓存搜索结果
        cache_strategy.cache_search_results(
            search_query,
            search_results,
            destination=destination
        )

        logger.info(f"Search execution: Found {len(search_results)} results for '{search_query}'")

        return {
            **state,
            "search_results": search_results,
            "search_executed": True,
            "cache_hit": False,
            "stage": "search_completed"
        }

    except Exception as e:
        logger.error(f"Search execution failed: {str(e)}")
        return {
            **state,
            "error_message": f"搜索执行失败: {str(e)}",
            "workflow_status": "failed",
            "search_executed": False
        }


async def plan_flight_search(state: ConversationState) -> ConversationState:
    """航班搜索规划节点"""
    return await plan_search(state)


async def execute_flight_search(state: ConversationState) -> ConversationState:
    """航班搜索执行节点"""

    try:
        destination = state.get("destination", "")
        user_requirements = state.get("user_requirements", {})

        # 尝试缓存
        cache_strategy = get_cache_strategy()
        cache_key = f"flight_{destination}"
        cached = cache_strategy.get_search_results(cache_key)

        if cached:
            return {
                **state,
                "flight_results": cached,
                "flight_searched": True
            }

        # 执行搜索
        flight_results = {
            "type": "flight_search",
            "destination": destination,
            "departure_date": user_requirements.get("dates", ""),
            "passengers": user_requirements.get("travelers", 1),
            "options": []
        }

        # 缓存结果
        cache_strategy.cache_search_results(cache_key, flight_results)

        return {
            **state,
            "flight_results": flight_results,
            "flight_searched": True
        }

    except Exception as e:
        logger.error(f"Flight search failed: {str(e)}")
        return {**state, "error_message": str(e), "flight_searched": False}


async def plan_hotel_search(state: ConversationState) -> ConversationState:
    """酒店搜索规划节点"""
    return await plan_search(state)


async def execute_hotel_search(state: ConversationState) -> ConversationState:
    """酒店搜索执行节点"""

    try:
        destination = state.get("destination", "")
        user_requirements = state.get("user_requirements", {})

        cache_strategy = get_cache_strategy()
        cache_key = f"hotel_{destination}"
        cached = cache_strategy.get_search_results(cache_key)

        if cached:
            return {
                **state,
                "hotel_results": cached,
                "hotel_searched": True
            }

        hotel_results = {
            "type": "hotel_search",
            "destination": destination,
            "budget": user_requirements.get("budget", ""),
            "check_in": user_requirements.get("check_in", ""),
            "check_out": user_requirements.get("check_out", ""),
            "options": []
        }

        cache_strategy.cache_search_results(cache_key, hotel_results)

        return {
            **state,
            "hotel_results": hotel_results,
            "hotel_searched": True
        }

    except Exception as e:
        logger.error(f"Hotel search failed: {str(e)}")
        return {**state, "error_message": str(e), "hotel_searched": False}
