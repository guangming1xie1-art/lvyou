"""
会话管理器

负责会话级别的记忆管理
"""

import logging
from typing import Dict, Any, Optional

from .memory_gateway import memory_gateway

logger = logging.getLogger(__name__)


class SessionManager:
    """会话管理器"""
    
    async def update_memory(
        self,
        session_id: str,
        user_input: str,
        ai_response: str,
        extracted_info: Optional[Dict] = None
    ):
        """
        更新会话记忆
        
        Args:
            session_id: 会话 ID
            user_input: 用户输入
            ai_response: AI 回复
            extracted_info: 提取的信息
        """
        await memory_gateway.update_session_memory(
            session_id=session_id,
            user_input=user_input,
            ai_response=ai_response,
            extracted_info=extracted_info,
            ttl=3600  # 1 小时过期
        )
    
    async def get_memory(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话记忆
        
        Args:
            session_id: 会话 ID
            
        Returns:
            会话记忆字典
        """
        return await memory_gateway.get_session_memory(session_id)


# 单例实例
session_manager = SessionManager()
