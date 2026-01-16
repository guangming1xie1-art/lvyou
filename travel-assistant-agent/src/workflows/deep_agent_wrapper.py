"""
DeepAgent 兼容包装器
由于 deepagent 包未安装，我们创建自己的 DeepAgent 实现
"""
from typing import List, Any, Dict, Optional
from langchain_core.messages import HumanMessage, BaseMessage
import logging

logger = logging.getLogger(__name__)


class DeepAgent:
    """
    DeepAgent 包装器
    实现与 deepagent 包兼容的接口
    """
    
    def __init__(
        self,
        model: Any,
        subagents: List[Any],
        runnable: Any,
        system_prompt: str = ""
    ):
        """
        初始化 DeepAgent
        
        Args:
            model: LLM 实例
            subagents: 子代理列表（CompiledSubAgent 实例）
            runnable: 主工作流 runnable (CompiledGraph)
            system_prompt: 系统提示
        """
        self.model = model
        self.subagents = subagents
        self.runnable = runnable
        self.system_prompt = system_prompt
        
        logger.info(f"DeepAgent initialized with {len(subagents)} subagents")
    
    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        同步调用 DeepAgent
        
        Args:
            input_data: {"messages": [HumanMessage(...)], ...}
        
        Returns:
            主工作流的执行结果
        """
        logger.info("DeepAgent invoke() called")
        
        # 调用主工作流
        result = self.runnable.invoke(input_data)
        
        return result
    
    async def ainvoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        异步调用 DeepAgent
        
        Args:
            input_data: {"messages": [HumanMessage(...)], ...}
        
        Returns:
            主工作流的执行结果
        """
        logger.info("DeepAgent ainvoke() called")
        
        # 调用主工作流（异步）
        result = await self.runnable.ainvoke(input_data)
        
        return result


def create_deep_agent(
    model: Any,
    subagents: List[Any],
    runnable: Any,
    system_prompt: str = ""
) -> DeepAgent:
    """
    创建 DeepAgent 实例
    
    Args:
        model: LLM 实例
        subagents: 子代理列表
        runnable: 主工作流 runnable
        system_prompt: 系统提示
    
    Returns:
        DeepAgent 实例
    """
    return DeepAgent(
        model=model,
        subagents=subagents,
        runnable=runnable,
        system_prompt=system_prompt
    )


__all__ = [
    "DeepAgent",
    "create_deep_agent",
]
