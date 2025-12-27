"""
MCP Server configuration module
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class MCPServerConfig(BaseModel):
    """MCP Server Configuration"""
    host: str = "localhost"
    port: int = 8765
    transport: str = "stdio"  # stdio or sse
    enabled: bool = True
    skills: List[str] = Field(default_factory=list)


class MCPClientConfig(BaseModel):
    """MCP Client Configuration for Agent"""
    server_url: Optional[str] = None
    transport: str = "stdio"
    timeout: int = 30
    retry_attempts: int = 3


class SkillDefinition(BaseModel):
    """Skill definition schema"""
    name: str
    description: str
    input_schema: dict
    output_schema: dict
    category: str
    version: str = "1.0.0"
