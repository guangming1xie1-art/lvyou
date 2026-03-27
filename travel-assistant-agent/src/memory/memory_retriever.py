"""
记忆检索器

负责从长期记忆中检索相关信息
"""

import logging
from typing import Dict, Any, List

from .memory_gateway import memory_gateway

logger = logging.getLogger(__name__)


class MemoryRetriever:
    """记忆检索器"""
    
    async def retrieve(
        self,
        user_id: str,
        query: str = "用户偏好和习惯",
        k: int = 5
    ) -> Dict[str, Any]:
        """
        检索长期记忆
        
        Args:
            user_id: 用户 ID
            query: 查询文本
            k: 返回数量
            
        Returns:
            记忆字典
        """
        return await memory_gateway.get_long_term_memory(user_id=user_id, k=k)


# 单例实例
memory_retriever = MemoryRetriever()
