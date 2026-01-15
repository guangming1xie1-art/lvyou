"""Conversation Agent

Provides a single-entry conversational interface that orchestrates existing
Search/Recommendation/Booking agents.

Input: {"message": "..."}
Output:
{
  "search_results": [...],
  "recommendations": [...],
  "booking_info": {...},
  "response": "...",
  "status": "success" | "error"
}
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from config.llm_config import LLMFactory, ModelTier
from utils.logger import app_logger

from .booking import BookingAgent
from .recommendation import RecommendationAgent
from .search import SearchAgent


class ConversationAgent:
    """主对话智能体：协调搜索、推荐、预订子智能体"""

    def __init__(self, intent_llm: Optional[Any] = None):
        self.search_agent = SearchAgent()
        self.recommend_agent = RecommendationAgent()
        self.booking_agent = BookingAgent()

        if intent_llm is not None:
            self.intent_llm = intent_llm
            return

        try:
            self.intent_llm = LLMFactory.get_default_llm(ModelTier.POWER)
        except Exception as e:
            app_logger.warning(f"Intent LLM initialization failed, falling back to heuristic intent parsing: {e}")
            self.intent_llm = None

    async def ainvoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        user_message = (state or {}).get("message", "")

        if not user_message:
            return {
                "status": "error",
                "error": "message is required",
                "search_results": [],
                "recommendations": [],
                "booking_info": {},
                "response": "请告诉我您的旅行需求（例如：我想去北京旅游 5 天，预算 3000 元）",
            }

        try:
            intent = await self._extract_intent(user_message)

            # Search
            search_state: Dict[str, Any] = {
                "intent": intent,
                "collected_info": {
                    "destination": intent.get("destination") or "未指定",
                    "dates": intent.get("start_date") or "未指定",
                    "budget": intent.get("budget") or "未指定",
                    "preferences": intent.get("preferences") or [],
                },
            }
            search_state = await self.search_agent.run(search_state)
            search_results = search_state.get("search_results", [])

            # Recommend
            recommend_state: Dict[str, Any] = {
                "intent": intent,
                "collected_info": search_state.get("collected_info", {}),
                "search_results": search_results,
            }
            recommend_state = await self.recommend_agent.run(recommend_state)
            recommendations = recommend_state.get("recommendations", [])

            result: Dict[str, Any] = {
                "status": "success",
                "search_results": search_results,
                "recommendations": recommendations,
                "booking_info": {},
            }

            # Book (optional)
            if bool(intent.get("want_to_book")):
                booking_state: Dict[str, Any] = {
                    "intent": intent,
                    "recommendations": recommendations,
                }
                booking_state = await self.booking_agent.run(booking_state)
                result["booking_info"] = booking_state.get("booking_status", {})

            result["response"] = await self._format_response(result, intent)
            return result

        except Exception as e:
            app_logger.error(f"ConversationAgent failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "search_results": [],
                "recommendations": [],
                "booking_info": {},
                "response": f"处理请求时出错：{str(e)}",
            }

    async def _extract_intent(self, message: str) -> Dict[str, Any]:
        """从自然语言提取意图。

        优先使用强力 LLM；若不可用则降级为启发式解析。
        """

        if self.intent_llm is None:
            return self._extract_intent_fallback(message)

        prompt = f"""
你是一个旅游规划助手。
请从以下用户消息中提取旅游规划意图，并只返回 JSON（不要包含额外文本）。

JSON Schema:
{{
  \"destination\": \"目的地\",
  \"start_date\": \"开始日期（若未知则空字符串）\",
  \"days\": 旅行天数（若未知则 0）, 
  \"budget\": \"预算（原始文本即可，若未知则空字符串）\",
  \"preferences\": [\"偏好1\", \"偏好2\"],
  \"want_to_book\": 是否要预订（true/false）
}}

用户消息：{message}
"""

        try:
            response = await self.intent_llm.ainvoke(prompt)
            raw = getattr(response, "content", None) or str(response)
            intent = self._parse_json_from_text(raw)
            if not isinstance(intent, dict):
                return self._extract_intent_fallback(message)
            return {
                "destination": intent.get("destination") or "",
                "start_date": intent.get("start_date") or "",
                "days": int(intent.get("days") or 0),
                "budget": intent.get("budget") or "",
                "preferences": intent.get("preferences") or [],
                "want_to_book": bool(intent.get("want_to_book")),
            }
        except Exception as e:
            app_logger.warning(f"Intent extraction via LLM failed, falling back to heuristics: {e}")
            return self._extract_intent_fallback(message)

    async def _format_response(self, result: Dict[str, Any], intent: Dict[str, Any]) -> str:
        if self.intent_llm is None:
            return self._format_response_fallback(result, intent)

        prompt = f"""
你是一个旅游规划助手。
请根据以下数据生成友好的自然语言回复，要求：
- 先用 1 句话总结
- 再用 3-6 条要点列出推荐亮点
- 若 booking_info 非空，说明已进入预订流程/预订状态

用户意图：{json.dumps(intent, ensure_ascii=False)}
搜索结果（摘要即可）：{json.dumps(result.get('search_results', [])[:5], ensure_ascii=False)}
推荐方案（摘要即可）：{json.dumps(result.get('recommendations', [])[:3], ensure_ascii=False)}
预订信息：{json.dumps(result.get('booking_info', {}), ensure_ascii=False)}
"""

        try:
            response = await self.intent_llm.ainvoke(prompt)
            return (getattr(response, "content", None) or str(response)).strip()
        except Exception as e:
            app_logger.warning(f"Response formatting via LLM failed, using fallback: {e}")
            return self._format_response_fallback(result, intent)

    def _format_response_fallback(self, result: Dict[str, Any], intent: Dict[str, Any]) -> str:
        destination = intent.get("destination") or "目的地"
        search_count = len(result.get("search_results") or [])
        rec_count = len(result.get("recommendations") or [])
        booked = bool(result.get("booking_info"))

        base = f"已为您生成 {destination} 的初步规划：搜索结果 {search_count} 条，推荐方案 {rec_count} 条。"
        if booked:
            base += " 已进入预订流程，请确认推荐方案与出行人信息。"
        return base

    def _extract_intent_fallback(self, message: str) -> Dict[str, Any]:
        # destination: try patterns like "去北京" "到Tokyo"
        destination = ""
        m = re.search(r"(?:去|到)([\u4e00-\u9fffA-Za-z]{1,16})", message)
        if m:
            destination = m.group(1)

        # days: "5天"
        days = 0
        m = re.search(r"(\d{1,2})\s*天", message)
        if m:
            try:
                days = int(m.group(1))
            except ValueError:
                days = 0

        # budget: "预算3000" or "3000元"
        budget = ""
        m = re.search(r"预算\s*(\d+[\d,]*)\s*(元|块|RMB|人民币)?", message)
        if m:
            budget = (m.group(1) + (m.group(2) or "")).strip()
        else:
            m2 = re.search(r"(\d+[\d,]*)\s*(元|块)", message)
            if m2:
                budget = (m2.group(1) + m2.group(2)).strip()

        preferences = []
        for kw in ["美食", "文化", "自然", "亲子", "购物", "海边", "海滨", "博物馆", "徒步", "温泉"]:
            if kw in message:
                preferences.append(kw)

        want_to_book = any(k in message for k in ["预订", "订票", "订酒店", "下单", "帮我订", "支付"])

        return {
            "destination": destination,
            "start_date": "",
            "days": days,
            "budget": budget,
            "preferences": preferences,
            "want_to_book": want_to_book,
        }

    def _parse_json_from_text(self, text: str) -> Any:
        """Best-effort JSON extraction.

        LLMs may wrap JSON with markdown fences or extra commentary.
        """
        text = text.strip()

        # Strip markdown fences
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\n", "", text)
            text = re.sub(r"\n```$", "", text)
            text = text.strip()

        # Try direct parse
        try:
            return json.loads(text)
        except Exception:
            pass

        # Try extracting the first JSON object
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except Exception:
                return None

        return None
