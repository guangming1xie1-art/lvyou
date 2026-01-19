"""
deepagents 兼容层

提供 deepagent v0.2.7 接口的本地实现，替代 PyPI 不可用的情况。
"""
from typing import Any, Dict, Optional
from langgraph.pregel import Pregel


class CompiledSubAgent:
    """子代理编译包装器，模拟 deepagent.CompiledSubAgent 接口"""
    
    def __init__(
        self,
        name: str,
        runnable: Pregel,
        system_prompt: str,
        description: Optional[str] = None,
    ):
        self.name = name
        self.runnable = runnable
        self.system_prompt = system_prompt
        self.description = description or f"SubAgent: {name}"
    
    def invoke(self, input: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """同步调用子代理"""
        return self.runnable.invoke(input, **kwargs)
    
    async def ainvoke(self, input: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """异步调用子代理"""
        return await self.runnable.ainvoke(input, **kwargs)
    
    def stream(self, input: Dict[str, Any], **kwargs):
        """流式调用"""
        return self.runnable.stream(input, **kwargs)
    
    async def astream(self, input: Dict[str, Any], **kwargs):
        """异步流式调用"""
        return self.runnable.astream(input, **kwargs)


class DeepAgent:
    """深度代理，模拟 create_deep_agent 接口"""
    
    def __init__(
        self,
        name: str,
        agent: Any,
        system_prompt: Optional[str] = None,
        max_iterations: int = 10,
        **kwargs
    ):
        self.name = name
        self.agent = agent
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        self.kwargs = kwargs
    
    async def ainvoke(self, input: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """异步调用"""
        if hasattr(self.agent, 'ainvoke'):
            return await self.agent.ainvoke(input, **kwargs)
        return self.agent.invoke(input, **kwargs)
    
    def invoke(self, input: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """同步调用"""
        return self.agent.invoke(input, **kwargs)


def create_deep_agent(
    name: str,
    agent: Any,
    system_prompt: Optional[str] = None,
    max_iterations: int = 10,
    **kwargs
) -> DeepAgent:
    """
    创建 DeepAgent 实例
    
    Args:
        name: 代理名称
        agent: 底层 agent (LangGraph CompiledGraph)
        system_prompt: 系统提示词
        max_iterations: 最大迭代次数
        **kwargs: 其他参数
    
    Returns:
        DeepAgent 实例
    """
    return DeepAgent(
        name=name,
        agent=agent,
        system_prompt=system_prompt,
        max_iterations=max_iterations,
        **kwargs
    )


__all__ = [
    "CompiledSubAgent",
    "DeepAgent", 
    "create_deep_agent",
]
