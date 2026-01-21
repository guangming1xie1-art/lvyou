"""
Claude API 连接管理

⚠️ 警告：此模块已标记为遗留代码 (Legacy)
⚠️ 建议使用 config.llm_config.LLMFactory 替代

此模块保留仅用于向后兼容和测试。
新代码应使用 LLMFactory 来创建和管理 LLM 实例。

支持的功能：
- Claude API 初始化
- 连接测试
"""
from typing import Optional
from conf import settings
from utils.logger import app_logger


class ClaudeClient:
    """Claude 客户端（遗留实现）
    
    此类已标记为遗留，建议使用 LLMFactory.create_llm() 替代。
    仅在需要与现有 Claude 特定功能兼容时使用。
    """
    
    def __init__(self):
        self.llm = None
        self._configured = False

    def init(self):
        self._configured = bool(settings.anthropic_api_key)
        if not self._configured:
            app_logger.warning("ANTHROPIC_API_KEY not configured (ClaudeClient is legacy, consider using LLMFactory)")
            return

        try:
            from langchain_anthropic import ChatAnthropic

            self.llm = ChatAnthropic(
                anthropic_api_key=settings.anthropic_api_key,
                model=settings.claude_model,
                max_tokens=settings.claude_max_tokens,
                temperature=settings.claude_temperature
            )
            app_logger.info("Claude client initialized (legacy)")
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


# 全局实例（向后兼容）
claude_client = ClaudeClient()
