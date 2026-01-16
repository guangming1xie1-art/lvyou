"""A lightweight compatibility layer for the demo `deepagents` API.

The original ticket expects imports like:

    from deepagents import create_deep_agent, CompiledSubAgent

The upstream `deepagent/deepagents` package is not available in this repository's
runtime environment, so we provide a minimal implementation that matches the
needed interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class DeepAgent:
    """Top-level agent wrapper.

    This implementation delegates execution to the provided `runnable`.
    """

    def __init__(
        self,
        model: Any,
        subagents: List[Any],
        runnable: Any,
        system_prompt: str = "",
    ):
        self.model = model
        self.subagents = subagents
        self.runnable = runnable
        self.system_prompt = system_prompt

    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.runnable.invoke(input_data)

    async def ainvoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.runnable.ainvoke(input_data)


def create_deep_agent(
    model: Any,
    subagents: List[Any],
    runnable: Any,
    system_prompt: str = "",
) -> DeepAgent:
    return DeepAgent(
        model=model,
        subagents=subagents,
        runnable=runnable,
        system_prompt=system_prompt,
    )


class CompiledSubAgent:
    """Wrap a compiled StateGraph runnable and expose a stable interface.

    Required output format:
        {"output": str, "usage": {...}}
    """

    def __init__(self, name: str, runnable: Any, system_prompt: str = ""):
        self.name = name
        self.runnable = runnable
        self.system_prompt = system_prompt

    def invoke(self, input_state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = self.runnable.invoke(input_state)
            return {
                "output": self._extract_output(result),
                "usage": result.get("usage", {"prompt": 0, "completion": 0, "total": 0}),
                "state": result,
            }
        except Exception as e:
            logger.error("[%s] invoke failed: %s", self.name, e)
            return {
                "output": f"Error: {e}",
                "usage": {"prompt": 0, "completion": 0, "total": 0},
                "state": {"error": str(e)},
            }

    async def ainvoke(self, input_state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = await self.runnable.ainvoke(input_state)
            return {
                "output": self._extract_output(result),
                "usage": result.get("usage", {"prompt": 0, "completion": 0, "total": 0}),
                "state": result,
            }
        except Exception as e:
            logger.error("[%s] ainvoke failed: %s", self.name, e)
            return {
                "output": f"Error: {e}",
                "usage": {"prompt": 0, "completion": 0, "total": 0},
                "state": {"error": str(e)},
            }

    @staticmethod
    def _extract_output(result: Dict[str, Any]) -> str:
        import json

        if "output" in result and isinstance(result["output"], str):
            return result["output"]
        if "collected_info" in result:
            return json.dumps(result["collected_info"], ensure_ascii=False, indent=2)
        if "search_results" in result:
            return json.dumps(result["search_results"], ensure_ascii=False, indent=2)
        if "recommendations" in result:
            return json.dumps(result["recommendations"], ensure_ascii=False, indent=2)
        if "booking_confirmation" in result:
            return json.dumps(result["booking_confirmation"], ensure_ascii=False, indent=2)
        return json.dumps(result, ensure_ascii=False, indent=2)


__all__ = ["DeepAgent", "create_deep_agent", "CompiledSubAgent"]
