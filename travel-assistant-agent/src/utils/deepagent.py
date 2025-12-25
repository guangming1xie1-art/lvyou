"""DeepAgent 集成占位

DeepAgent 作为深度推理框架的集成点（MVP 阶段仅提供骨架）。
后续可以在这里实现：
- 多步推理 / Tree-of-Thought
- 反思与自我纠错
- 与 LangGraph 节点结合
"""
from typing import Any, Dict

from utils.logger import app_logger


class DeepAgentManager:
    def __init__(self, enabled: bool = False):
        self.enabled = enabled

    async def reason(self, task: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if not self.enabled:
            app_logger.info("DeepAgent disabled, returning mock reasoning result")
            return {"status": "disabled", "task": task, "context": context or {}}

        # TODO: 接入 DeepAgent 实际能力
        return {"status": "not_implemented", "task": task, "context": context or {}}


deepagent_manager = DeepAgentManager()
