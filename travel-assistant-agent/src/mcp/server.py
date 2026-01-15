"""
MCP Server Implementation

This module provides a FastAPI-based MCP server implementation
for the Travel Assistant Agent.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, Any, List, Optional
import json
import logging
import asyncio

from .protocol import MCPProtocolHandler
from .tools import MCPToolFactory
from .resources import MCPResourceManager, create_default_resources

logger = logging.getLogger(__name__)


class MCPServerV2:
    """MCP Server V2
    
    Provides HTTP and WebSocket endpoints for MCP protocol communication.
    """
    
    def __init__(
        self,
        protocol_handler: Optional[MCPProtocolHandler] = None,
        resource_manager: Optional[MCPResourceManager] = None
    ):
        """Initialize MCP Server
        
        Args:
            protocol_handler: Optional custom protocol handler
            resource_manager: Optional custom resource manager
        """
        self.protocol_handler = protocol_handler or MCPProtocolHandler()
        self.resource_manager = resource_manager or create_default_resources()
        self._register_tools()
        self._register_resources()
        self.active_websockets: List[WebSocket] = []
    
    def _register_tools(self):
        """Register all MCP tools"""
        for tool in MCPToolFactory.get_all_tools():
            self.protocol_handler.register_tool(tool)
        logger.info(f"Registered {len(MCPToolFactory.get_all_tools())} MCP tools")
    
    def _register_resources(self):
        """Register all MCP resources"""
        for resource_dict in self.resource_manager.list_resources():
            uri = resource_dict["uri"]
            resource = self.resource_manager.get_resource(uri)
            if resource:
                reader = lambda u=uri: self.resource_manager.read_resource(u)
                self.protocol_handler.register_resource(resource, reader)
        logger.info(f"Registered {len(self.resource_manager.resources)} MCP resources")
    
    def create_router(self) -> APIRouter:
        """Create FastAPI router for MCP endpoints
        
        Returns:
            APIRouter with MCP endpoints
        """
        router = APIRouter(prefix="/mcp", tags=["mcp"])
        
        @router.post("/request")
        async def handle_mcp_request(request: Dict[str, Any]) -> Dict[str, Any]:
            """Handle MCP request
            
            Args:
                request: MCP request dictionary
                
            Returns:
                MCP response dictionary
            """
            logger.debug(f"Received MCP request: {request.get('method')}")
            response = self.protocol_handler.handle_request(request)
            return response
        
        @router.get("/tools")
        async def list_tools() -> Dict[str, Any]:
            """List all available tools
            
            Returns:
                Dictionary with tools list
            """
            tools = self.protocol_handler.list_tools()
            return {
                "tools": tools,
                "count": len(tools)
            }
        
        @router.get("/tools/{tool_name}")
        async def get_tool(tool_name: str) -> Dict[str, Any]:
            """Get a specific tool by name
            
            Args:
                tool_name: Tool name
                
            Returns:
                Tool dictionary or 404 if not found
            """
            tool = MCPToolFactory.get_tool_by_name(tool_name)
            if not tool:
                raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
            return tool.to_dict()
        
        @router.get("/resources")
        async def list_resources() -> Dict[str, Any]:
            """List all available resources
            
            Returns:
                Dictionary with resources list
            """
            resources = self.protocol_handler.list_resources()
            return {
                "resources": resources,
                "count": len(resources)
            }
        
        @router.get("/resources/{resource_uri:path}")
        async def read_resource_endpoint(resource_uri: str) -> Dict[str, Any]:
            """Read a resource by URI
            
            Args:
                resource_uri: Resource URI (path parameter)
                
            Returns:
                Dictionary with resource content or 404 if not found
            """
            try:
                # Decode URI
                decoded_uri = resource_uri
                content = self.protocol_handler.read_resource(decoded_uri)
                return {
                    "uri": decoded_uri,
                    "content": content
                }
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
        
        @router.post("/tools/call")
        async def call_tool_endpoint(request: Dict[str, Any]) -> Dict[str, Any]:
            """Call a tool
            
            Args:
                request: Dictionary with 'name' and 'arguments'
                
            Returns:
                Tool execution result
            """
            tool_name = request.get("name")
            arguments = request.get("arguments", {})
            
            if not tool_name:
                raise HTTPException(status_code=400, detail="Tool name is required")
            
            try:
                result = self.protocol_handler.call_tool(tool_name, arguments)
                return {
                    "success": True,
                    "tool_name": tool_name,
                    "result": result
                }
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                logger.error(f"Error calling tool {tool_name}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @router.get("/status")
        async def get_status() -> Dict[str, Any]:
            """Get MCP server status
            
            Returns:
                Status dictionary with server info
            """
            return {
                "status": "running",
                "version": "1.0.0",
                "tools_count": len(self.protocol_handler.tools),
                "resources_count": len(self.protocol_handler.resources),
                "active_websockets": len(self.active_websockets)
            }
        
        return router
    
    async def handle_websocket(self, websocket: WebSocket):
        """Handle WebSocket connection for MCP
        
        Args:
            websocket: WebSocket connection
        """
        await websocket.accept()
        self.active_websockets.append(websocket)
        client_id = f"ws_{id(websocket)}"
        logger.info(f"WebSocket client connected: {client_id}")
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                logger.debug(f"Received from {client_id}: {data}")
                
                try:
                    # Parse request
                    request = json.loads(data)
                    
                    # Handle request
                    response = self.protocol_handler.handle_request(request)
                    
                    # Send response
                    await websocket.send_json(response)
                    logger.debug(f"Sent to {client_id}: {response.get('method', 'response')}")
                
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error from {client_id}: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id", -1) if 'request' in locals() else -1,
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    await websocket.send_json(error_response)
                
                except Exception as e:
                    logger.error(f"Error processing request from {client_id}: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id", -1) if 'request' in locals() else -1,
                        "error": {
                            "code": -32603,
                            "message": str(e)
                        }
                    }
                    await websocket.send_json(error_response)
        
        except WebSocketDisconnect:
            logger.info(f"WebSocket client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"WebSocket error for {client_id}: {e}")
        finally:
            if websocket in self.active_websockets:
                self.active_websockets.remove(websocket)
            logger.info(f"WebSocket connection closed for {client_id}")
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast a message to all connected WebSocket clients
        
        Args:
            message: Message to broadcast
        """
        disconnected = []
        for websocket in self.active_websockets:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(websocket)
        
        # Remove disconnected clients
        for ws in disconnected:
            if ws in self.active_websockets:
                self.active_websockets.remove(ws)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get server statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            "tools_count": len(self.protocol_handler.tools),
            "resources_count": len(self.protocol_handler.resources),
            "active_websockets": len(self.active_websockets),
            "tool_names": list(self.protocol_handler.tools.keys()),
            "resource_uris": list(self.protocol_handler.resources.keys())
        }


__all__ = [
    "MCPServerV2",
]
