"""Agent 基类定义

MVP 阶段先定义统一接口，后续可替换为更复杂的 DeepAgent / 工具调用框架。
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable, Awaitable


class BaseAgent(ABC):
    name: str = "base_agent"

    @abstractmethod
    async def run(
        self, 
        state: Dict[str, Any], 
        on_progress: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        """处理输入状态并返回更新后的状态
        
        Args:
            state: 输入状态字典
            on_progress: 进度回调函数，接收包含进度信息的字典
        """
        raise NotImplementedError
