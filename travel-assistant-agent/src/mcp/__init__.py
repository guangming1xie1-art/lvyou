"""
MCP Protocol Module

This module provides complete Model Context Protocol (MCP) implementation
for the Travel Assistant Agent, including protocol handling, tools,
and resources management.
"""

from .protocol import (
    MCPTool,
    MCPResource,
    MCPRequest,
    MCPResponse,
    MCPProtocolHandler,
)

from .server import MCPServerV2
from .tools import MCPToolFactory
from .resources import MCPResourceManager

__version__ = "1.0.0"

__all__ = [
    # Protocol
    "MCPTool",
    "MCPResource",
    "MCPRequest",
    "MCPResponse",
    "MCPProtocolHandler",
    
    # Server
    "MCPServerV2",
    
    # Tools
    "MCPToolFactory",
    
    # Resources
    "MCPResourceManager",
]
