"""
子智能体基类
定义所有子智能体的通用接口和功能
"""
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """子智能体基类"""

    def __init__(self, name: str, description: str, tools: List[Any]):
        """
        初始化子智能体

        Args:
            name: 智能体名称
            description: 智能体描述
            tools: 工具列表
        """
        self.name = name
        self.description = description
        self.tools = tools
        self.token_usage = 0

    @abstractmethod
    async def execute(self, input_data: Dict) -> Dict:
        """
        执行智能体

        Args:
            input_data: 输入数据

        Returns:
            执行结果，包含output和token_usage
        """
        raise NotImplementedError

    @abstractmethod
    async def stream(self, input_data: Dict):
        """
        流式执行

        Args:
            input_data: 输入数据

        Yields:
            执行过程中的状态更新
        """
        raise NotImplementedError

    def _track_tokens(self, count: int):
        """追踪token使用"""
        self.token_usage += count
        logger.debug(f"{self.name}: Token usage updated to {self.token_usage}")

    def get_token_usage(self) -> int:
        """获取当前token使用量"""
        return self.token_usage

    def reset_token_usage(self):
        """重置token使用量"""
        self.token_usage = 0
