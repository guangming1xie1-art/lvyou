"""MCP 工具骨架

Model Context Protocol (MCP) 后续用于统一对外部工具的调用方式。
当前仅提供接口占位。
"""
from typing import Any, Dict
from utils.logger import app_logger


class MCPToolManager:
    def __init__(self, enabled: bool = False):
        self.enabled = enabled

    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled:
            app_logger.warning(f"MCP disabled, tool {tool_name} call skipped")
            return {"status": "disabled", "tool": tool_name}

        # TODO: 实现 MCP 客户端调用
        app_logger.info(f"Calling MCP tool: {tool_name} with params: {params}")
        return {"status": "not_implemented", "tool": tool_name, "params": params}


mcp_manager = MCPToolManager()
