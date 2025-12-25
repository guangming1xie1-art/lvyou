"""Agent 基类定义

MVP 阶段先定义统一接口，后续可替换为更复杂的 DeepAgent / 工具调用框架。
"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    name: str = "base_agent"

    @abstractmethod
    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入状态并返回更新后的状态"""
        raise NotImplementedError
