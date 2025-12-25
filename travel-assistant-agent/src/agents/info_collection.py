"""信息收集 Agent

负责从用户输入中提取旅行需求关键信息：
- 目的地
- 出发时间和旅行天数
- 预算
- 偏好类型（美食、自然、文化等）
"""
from typing import Any, Dict
from utils.logger import app_logger
from utils.claude import claude_client
from .base import BaseAgent


class InfoCollectionAgent(BaseAgent):
    name = "info_collection_agent"

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        app_logger.info(f"[{self.name}] Starting information collection")

        user_message = state.get("user_message", "")
        if not user_message:
            app_logger.warning("No user message provided")
            return state

        try:
            collected_info = await self._extract_info(user_message)
            state["collected_info"] = {
                **(state.get("collected_info") or {}),
                **collected_info,
            }
            app_logger.info(f"[{self.name}] Collected info: {state['collected_info']}")
        except Exception as e:
            app_logger.error(f"[{self.name}] Error: {e}")
            state["error"] = str(e)

        return state

    async def _extract_info(self, user_message: str) -> Dict[str, Any]:
        if not claude_client.is_ready():
            app_logger.warning("Claude client not ready, using mock data")
            return {
                "destination": "未指定",
                "dates": "未指定",
                "budget": "未指定",
                "preferences": []
            }

        prompt = f"""
从以下用户消息中提取旅行规划所需的关键信息：

用户消息: {user_message}

请以 JSON 格式返回以下信息：
- destination: 目的地
- dates: 出发日期和旅行天数
- budget: 预算范围
- preferences: 偏好列表（美食、自然、文化、购物等）

如果某些信息未提及，请标记为"未指定"。
"""

        try:
            response = await claude_client.llm.ainvoke(prompt)
            # TODO: 解析 LLM 响应为结构化数据
            return {
                "destination": "北京",
                "dates": "2024年5月1日 - 5月3日",
                "budget": "3000-5000元",
                "preferences": ["文化", "美食"]
            }
        except Exception as e:
            app_logger.error(f"Failed to extract info: {e}")
            raise
