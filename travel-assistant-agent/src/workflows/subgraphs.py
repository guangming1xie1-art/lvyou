"""
LangGraph 子图定义
4 个独立的子图：信息收集、搜索、推荐、预订
每个子图都是独立的 StateGraph，支持 Token 统计
"""
from typing import TypedDict, Dict, Any, Optional, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
import logging

from src.utils.token_counter import TokenCounter
from src.llm import LLMFactory

logger = logging.getLogger(__name__)


# ============ 子图状态定义 ============

class CollectInfoState(TypedDict):
    """信息收集子图状态"""
    user_message: str
    collected_info: Optional[Dict[str, Any]]
    usage: Dict[str, int]


class SearchState(TypedDict):
    """搜索子图状态"""
    user_message: str
    collected_info: Dict[str, Any]
    search_results: Optional[Dict[str, Any]]
    usage: Dict[str, int]


class RecommendState(TypedDict):
    """推荐子图状态"""
    user_message: str
    collected_info: Dict[str, Any]
    search_results: Dict[str, Any]
    recommendations: Optional[List[Dict[str, Any]]]
    usage: Dict[str, int]


class BookingState(TypedDict):
    """预订子图状态"""
    user_message: str
    collected_info: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    booking_confirmation: Optional[Dict[str, Any]]
    usage: Dict[str, int]


# ============ 信息收集子图 ============

def collect_info_node(state: CollectInfoState) -> CollectInfoState:
    """
    信息收集节点
    系统提示: "你是信息收集员，只负责收集需求并总结。"
    """
    user_message = state.get("user_message", "")
    
    # 创建 TokenCounter
    token_counter = TokenCounter()
    
    # 创建 LLM（使用便宜层）
    try:
        llm = LLMFactory.create_model("deepseek-chat")
    except Exception as e:
        logger.warning(f"Failed to create deepseek-chat, falling back to default: {e}")
        llm = LLMFactory.create_model()
    
    # 系统提示
    system_prompt = """你是旅游助手的信息收集员，负责从用户消息中提取旅游需求信息。

请从用户消息中提取以下信息（如果有的话）：
- 目的地（destination）
- 出发时间（departure_date）
- 返回时间（return_date）
- 预算范围（budget）
- 人数（travelers_count）
- 偏好（preferences）：如海滨、山区、文化、美食等

以 JSON 格式返回收集到的信息，例如：
{
  "destination": "巴黎",
  "departure_date": "2024-06-01",
  "budget": "10000-15000元",
  "travelers_count": 2,
  "preferences": ["文化", "美食"]
}

如果某些信息未提供，可以省略该字段。"""
    
    # 构建消息
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]
    
    # 调用 LLM（带 callback）
    try:
        response = llm.invoke(messages, config={"callbacks": [token_counter]})
        
        # 解析响应
        import json
        try:
            collected_info = json.loads(response.content)
        except json.JSONDecodeError:
            # 如果不是 JSON，存储原文
            collected_info = {"raw_response": response.content}
        
        # 返回结果和用量
        return {
            "user_message": user_message,
            "collected_info": collected_info,
            "usage": token_counter.dump()
        }
    except Exception as e:
        logger.error(f"Error in collect_info_node: {e}")
        return {
            "user_message": user_message,
            "collected_info": {"error": str(e)},
            "usage": {"prompt": 0, "completion": 0, "total": 0}
        }


def build_collect_info_graph() -> Any:
    """构建信息收集子图"""
    graph = StateGraph(CollectInfoState)
    graph.add_node("collect", collect_info_node)
    graph.set_entry_point("collect")
    graph.add_edge("collect", END)
    return graph.compile()


# ============ 搜索子图 ============

def search_node(state: SearchState) -> SearchState:
    """
    搜索节点
    系统提示: "你是搜索员，收到需求总结后返回目的地等搜索结果。"
    """
    user_message = state.get("user_message", "")
    collected_info = state.get("collected_info", {})
    
    # 创建 TokenCounter
    token_counter = TokenCounter()
    
    # 创建 LLM（使用标准层）
    try:
        llm = LLMFactory.create_model("qwen-turbo")
    except Exception as e:
        logger.warning(f"Failed to create qwen-turbo, falling back to default: {e}")
        llm = LLMFactory.create_model()
    
    # 系统提示
    system_prompt = """你是旅游助手的搜索员，负责根据用户需求搜索相关的旅游信息。

基于收集到的用户需求，搜索并返回以下信息：
- 目的地列表（destinations）
- 酒店推荐（hotels）
- 航班信息（flights）
- 景点推荐（attractions）

以 JSON 格式返回搜索结果，例如：
{
  "destinations": [
    {"id": "dest_001", "name": "巴黎", "country": "法国", "rating": 4.8}
  ],
  "hotels": [
    {"id": "hotel_001", "name": "某酒店", "price": "500-1000元/晚", "rating": 4.5}
  ],
  "attractions": [
    {"id": "attr_001", "name": "埃菲尔铁塔", "rating": 4.9}
  ]
}"""
    
    # 构建消息
    import json
    collected_info_str = json.dumps(collected_info, ensure_ascii=False, indent=2)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"用户需求：{collected_info_str}\n\n原始消息：{user_message}")
    ]
    
    # 调用 LLM（带 callback）
    try:
        response = llm.invoke(messages, config={"callbacks": [token_counter]})
        
        # 解析响应
        try:
            search_results = json.loads(response.content)
        except json.JSONDecodeError:
            search_results = {"raw_response": response.content}
        
        return {
            "user_message": user_message,
            "collected_info": collected_info,
            "search_results": search_results,
            "usage": token_counter.dump()
        }
    except Exception as e:
        logger.error(f"Error in search_node: {e}")
        return {
            "user_message": user_message,
            "collected_info": collected_info,
            "search_results": {"error": str(e)},
            "usage": {"prompt": 0, "completion": 0, "total": 0}
        }


def build_search_graph() -> Any:
    """构建搜索子图"""
    graph = StateGraph(SearchState)
    graph.add_node("search", search_node)
    graph.set_entry_point("search")
    graph.add_edge("search", END)
    return graph.compile()


# ============ 推荐子图 ============

def recommend_node(state: RecommendState) -> RecommendState:
    """
    推荐节点
    系统提示: "你是推荐员，基于需求和搜索结果生成个性化方案。"
    """
    user_message = state.get("user_message", "")
    collected_info = state.get("collected_info", {})
    search_results = state.get("search_results", {})
    
    # 创建 TokenCounter
    token_counter = TokenCounter()
    
    # 创建 LLM（使用标准层）
    try:
        llm = LLMFactory.create_model("qwen-turbo")
    except Exception as e:
        logger.warning(f"Failed to create qwen-turbo, falling back to default: {e}")
        llm = LLMFactory.create_model()
    
    # 系统提示
    system_prompt = """你是旅游助手的推荐员，负责基于用户需求和搜索结果生成个性化旅游方案。

请综合考虑：
- 用户的预算、时间、偏好
- 搜索到的目的地、酒店、景点信息
- 行程的合理性和可行性

生成 2-3 个推荐方案，以 JSON 格式返回：
{
  "recommendations": [
    {
      "id": "rec_001",
      "title": "经典巴黎 5 日游",
      "description": "包含主要景点和美食体验",
      "itinerary": ["Day 1: ...", "Day 2: ..."],
      "estimated_cost": "12000元",
      "confidence": 0.85
    }
  ]
}"""
    
    # 构建消息
    import json
    collected_info_str = json.dumps(collected_info, ensure_ascii=False, indent=2)
    search_results_str = json.dumps(search_results, ensure_ascii=False, indent=2)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"用户需求：\n{collected_info_str}\n\n搜索结果：\n{search_results_str}")
    ]
    
    # 调用 LLM（带 callback）
    try:
        response = llm.invoke(messages, config={"callbacks": [token_counter]})
        
        # 解析响应
        try:
            result = json.loads(response.content)
            recommendations = result.get("recommendations", [])
        except json.JSONDecodeError:
            recommendations = [{"raw_response": response.content}]
        
        return {
            "user_message": user_message,
            "collected_info": collected_info,
            "search_results": search_results,
            "recommendations": recommendations,
            "usage": token_counter.dump()
        }
    except Exception as e:
        logger.error(f"Error in recommend_node: {e}")
        return {
            "user_message": user_message,
            "collected_info": collected_info,
            "search_results": search_results,
            "recommendations": [{"error": str(e)}],
            "usage": {"prompt": 0, "completion": 0, "total": 0}
        }


def build_recommend_graph() -> Any:
    """构建推荐子图"""
    graph = StateGraph(RecommendState)
    graph.add_node("recommend", recommend_node)
    graph.set_entry_point("recommend")
    graph.add_edge("recommend", END)
    return graph.compile()


# ============ 预订子图 ============

def booking_node(state: BookingState) -> BookingState:
    """
    预订节点
    系统提示: "你是预订员，完成用户选定的预订。"
    """
    user_message = state.get("user_message", "")
    collected_info = state.get("collected_info", {})
    recommendations = state.get("recommendations", [])
    
    # 创建 TokenCounter
    token_counter = TokenCounter()
    
    # 创建 LLM（使用便宜层）
    try:
        llm = LLMFactory.create_model("deepseek-chat")
    except Exception as e:
        logger.warning(f"Failed to create deepseek-chat, falling back to default: {e}")
        llm = LLMFactory.create_model()
    
    # 系统提示
    system_prompt = """你是旅游助手的预订员，负责处理用户的预订请求。

根据用户选择的推荐方案，生成预订确认信息：
- 预订 ID（booking_id）
- 预订状态（status）
- 预订详情（details）
- 总价（total_price）

以 JSON 格式返回：
{
  "booking_id": "BK20240601001",
  "status": "confirmed",
  "details": {
    "destination": "巴黎",
    "dates": "2024-06-01 至 2024-06-05",
    "travelers": 2,
    "hotel": "某酒店",
    "flights": "某航班"
  },
  "total_price": "12000元"
}

注意：这是模拟预订，实际预订需要调用真实的预订系统。"""
    
    # 构建消息
    import json
    recommendations_str = json.dumps(recommendations, ensure_ascii=False, indent=2)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"用户消息：{user_message}\n\n推荐方案：\n{recommendations_str}\n\n请生成预订确认。")
    ]
    
    # 调用 LLM（带 callback）
    try:
        response = llm.invoke(messages, config={"callbacks": [token_counter]})
        
        # 解析响应
        try:
            booking_confirmation = json.loads(response.content)
        except json.JSONDecodeError:
            booking_confirmation = {"raw_response": response.content}
        
        return {
            "user_message": user_message,
            "collected_info": collected_info,
            "recommendations": recommendations,
            "booking_confirmation": booking_confirmation,
            "usage": token_counter.dump()
        }
    except Exception as e:
        logger.error(f"Error in booking_node: {e}")
        return {
            "user_message": user_message,
            "collected_info": collected_info,
            "recommendations": recommendations,
            "booking_confirmation": {"error": str(e)},
            "usage": {"prompt": 0, "completion": 0, "total": 0}
        }


def build_booking_graph() -> Any:
    """构建预订子图"""
    graph = StateGraph(BookingState)
    graph.add_node("booking", booking_node)
    graph.set_entry_point("booking")
    graph.add_edge("booking", END)
    return graph.compile()


# ============ 导出所有子图构建函数 ============

__all__ = [
    "build_collect_info_graph",
    "build_search_graph",
    "build_recommend_graph",
    "build_booking_graph",
    # 状态类型
    "CollectInfoState",
    "SearchState",
    "RecommendState",
    "BookingState",
]
