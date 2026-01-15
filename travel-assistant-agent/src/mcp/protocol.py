"""
MCP Protocol Handler

This module implements the Model Context Protocol (MCP) for tool and resource
management in the Travel Assistant Agent.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import json
import logging

logger = logging.getLogger(__name__)


class MCPTool(BaseModel):
    """MCP Tool definition"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    inputSchema: Dict[str, Any] = Field(default_factory=dict, description="Input JSON Schema")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump()


class MCPResource(BaseModel):
    """MCP Resource definition"""
    uri: str = Field(..., description="Resource URI")
    name: str = Field(..., description="Resource name")
    description: str = Field(..., description="Resource description")
    mimeType: str = Field(default="text/plain", description="MIME type")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump()


class MCPRequest(BaseModel):
    """MCP Request"""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    id: int = Field(..., description="Request ID")
    method: str = Field(..., description="Method name")
    params: Dict[str, Any] = Field(default_factory=dict, description="Method parameters")


class MCPResponse(BaseModel):
    """MCP Response"""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    id: int = Field(..., description="Request ID")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Result data")
    error: Optional[Dict[str, Any]] = Field(default=None, description="Error information")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump(exclude_none=True)


class MCPProtocolHandler:
    """MCP Protocol Handler
    
    Handles MCP protocol requests including tool listing, tool calling,
    resource listing, and resource reading.
    """
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self._tool_executors: Dict[str, callable] = {}
        self._resource_readers: Dict[str, callable] = {}
    
    def register_tool(
        self,
        tool: MCPTool,
        executor: Optional[callable] = None
    ):
        """Register a tool
        
        Args:
            tool: MCPTool definition
            executor: Optional callable that executes the tool
        """
        self.tools[tool.name] = tool
        if executor:
            self._tool_executors[tool.name] = executor
        logger.info(f"Registered MCP tool: {tool.name}")
    
    def register_resource(
        self,
        resource: MCPResource,
        reader: Optional[callable] = None
    ):
        """Register a resource
        
        Args:
            resource: MCPResource definition
            reader: Optional callable that reads the resource
        """
        self.resources[resource.uri] = resource
        if reader:
            self._resource_readers[resource.uri] = reader
        logger.info(f"Registered MCP resource: {resource.uri}")
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools
        
        Returns:
            List of tool dictionaries
        """
        return [tool.to_dict() for tool in self.tools.values()]
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all registered resources
        
        Returns:
            List of resource dictionaries
        """
        return [resource.to_dict() for resource in self.resources.values()]
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool execution result
            
        Raises:
            ValueError: If tool not found
        """
        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")
        
        logger.info(f"Calling MCP tool: {name} with args: {arguments}")
        
        # Execute using registered executor if available
        if name in self._tool_executors:
            return self._tool_executors[name](arguments)
        
        # Default placeholder result
        return {"result": "tool_result", "name": name, "arguments": arguments}
    
    def read_resource(self, uri: str) -> str:
        """Read a resource
        
        Args:
            uri: Resource URI
            
        Returns:
            Resource content
            
        Raises:
            ValueError: If resource not found
        """
        if uri not in self.resources:
            raise ValueError(f"Unknown resource: {uri}")
        
        logger.info(f"Reading MCP resource: {uri}")
        
        # Read using registered reader if available
        if uri in self._resource_readers:
            return self._resource_readers[uri]()
        
        # Default placeholder content
        return f"Resource content for {uri}"
    
    def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP request
        
        Args:
            request_data: Raw request dictionary
            
        Returns:
            MCP Response dictionary
        """
        try:
            request = MCPRequest(**request_data)
            
            # Handle tools/list
            if request.method == "tools/list":
                return MCPResponse(
                    id=request.id,
                    result={"tools": self.list_tools()}
                ).to_dict()
            
            # Handle tools/call
            elif request.method == "tools/call":
                tool_name = request.params.get("name")
                arguments = request.params.get("arguments", {})
                result = self.call_tool(tool_name, arguments)
                return MCPResponse(
                    id=request.id,
                    result={"content": result}
                ).to_dict()
            
            # Handle resources/list
            elif request.method == "resources/list":
                return MCPResponse(
                    id=request.id,
                    result={"resources": self.list_resources()}
                ).to_dict()
            
            # Handle resources/read
            elif request.method == "resources/read":
                uri = request.params.get("uri")
                content = self.read_resource(uri)
                return MCPResponse(
                    id=request.id,
                    result={"content": content}
                ).to_dict()
            
            # Handle ping
            elif request.method == "ping":
                return MCPResponse(
                    id=request.id,
                    result={"status": "ok"}
                ).to_dict()
            
            # Handle initialize
            elif request.method == "initialize":
                return MCPResponse(
                    id=request.id,
                    result={
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {
                            "name": "travel-assistant-mcp",
                            "version": "1.0.0"
                        },
                        "capabilities": {
                            "tools": {},
                            "resources": {}
                        }
                    }
                ).to_dict()
            
            # Unknown method
            else:
                return MCPResponse(
                    id=request.id,
                    error={
                        "code": -32601,
                        "message": "Method not found",
                        "data": {"method": request.method}
                    }
                ).to_dict()
        
        except Exception as e:
            logger.error(f"Error handling MCP request: {e}")
            return MCPResponse(
                id=request_data.get("id", -1),
                error={
                    "code": -32603,
                    "message": str(e)
                }
            ).to_dict()


__all__ = [
    "MCPTool",
    "MCPResource",
    "MCPRequest",
    "MCPResponse",
    "MCPProtocolHandler",
]
