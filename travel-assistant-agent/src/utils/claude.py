"""
Claude API 连接管理
使用 LangChain Anthropic 集成
"""
from typing import Optional
from config import settings
from utils.logger import app_logger


class ClaudeClient:
    def __init__(self):
        self.llm = None
        self._configured = False

    def init(self):
        self._configured = bool(settings.anthropic_api_key)
        if not self._configured:
            app_logger.warning("ANTHROPIC_API_KEY not configured")
            return

        try:
            from langchain_anthropic import ChatAnthropic

            self.llm = ChatAnthropic(
                anthropic_api_key=settings.anthropic_api_key,
                model=settings.claude_model,
                max_tokens=settings.claude_max_tokens,
                temperature=settings.claude_temperature
            )
            app_logger.info("Claude client initialized")
        except Exception as e:
            app_logger.error(f"Failed to initialize Claude client: {e}")
            raise

    @property
    def is_configured(self) -> bool:
        return self._configured

    def is_ready(self) -> bool:
        return self.llm is not None

    async def test_connection(self) -> bool:
        if not self.llm:
            return False
        try:
            # Simple test invocation
            await self.llm.ainvoke("Hello")
            return True
        except Exception as e:
            app_logger.warning(f"Claude connection test failed: {e}")
            return False


claude_client = ClaudeClient()
