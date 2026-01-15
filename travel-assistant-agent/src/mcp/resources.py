"""
MCP Resources Management

This module provides resource management for the MCP protocol,
including system prompts, knowledge base content, and configuration.
"""

from typing import Dict, Any, Optional, Callable
from .protocol import MCPResource
import logging
import os

logger = logging.getLogger(__name__)


class MCPResourceManager:
    """MCP Resource Manager
    
    Manages MCP resources including system prompts, knowledge base,
    and configuration files.
    """
    
    def __init__(self):
        self.resources: Dict[str, MCPResource] = {}
        self._readers: Dict[str, Callable] = {}
    
    def register_resource(
        self,
        resource: MCPResource,
        reader: Optional[Callable] = None
    ):
        """Register a resource
        
        Args:
            resource: MCPResource definition
            reader: Optional callable that reads the resource content
        """
        self.resources[resource.uri] = resource
        if reader:
            self._readers[resource.uri] = reader
        logger.info(f"Registered MCP resource: {resource.uri}")
    
    def get_resource(self, uri: str) -> Optional[MCPResource]:
        """Get a resource by URI
        
        Args:
            uri: Resource URI
            
        Returns:
            MCPResource if found, None otherwise
        """
        return self.resources.get(uri)
    
    def list_resources(self) -> list:
        """List all registered resources
        
        Returns:
            List of resource dictionaries
        """
        return [res.to_dict() for res in self.resources.values()]
    
    def read_resource(self, uri: str) -> Optional[str]:
        """Read a resource content
        
        Args:
            uri: Resource URI
            
        Returns:
            Resource content as string, or None if not found
        """
        if uri not in self.resources:
            logger.warning(f"Resource not found: {uri}")
            return None
        
        if uri in self._readers:
            try:
                return self._readers[uri]()
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                return None
        
        logger.warning(f"No reader registered for resource: {uri}")
        return None
    
    def register_system_prompt_resource(
        self,
        uri: str = "system://prompt",
        name: str = "System Prompt",
        description: str = "System prompt for the travel assistant",
        prompt_content: str = None
    ):
        """Register system prompt resource
        
        Args:
            uri: Resource URI
            name: Resource name
            description: Resource description
            prompt_content: Optional prompt content (if None, reads from default)
        """
        if prompt_content is None:
            prompt_content = """You are a helpful travel assistant agent. Your role is to help users plan their trips, search for flights and hotels, get recommendations, and make bookings.

Capabilities:
- Search for flights and hotels
- Get personalized recommendations
- Provide destination information
- Get weather forecasts
- Read reviews
- Make bookings

Always be helpful, friendly, and provide accurate information."""
        
        resource = MCPResource(
            uri=uri,
            name=name,
            description=description,
            mimeType="text/plain"
        )
        
        self.register_resource(resource, lambda: prompt_content)
    
    def register_knowledge_base_resource(
        self,
        uri: str = "kb://travel-guide",
        name: str = "Travel Guide",
        description: str = "Travel guide knowledge base",
        kb_path: str = None
    ):
        """Register knowledge base resource
        
        Args:
            uri: Resource URI
            name: Resource name
            description: Resource description
            kb_path: Path to knowledge base file
        """
        def read_kb():
            if kb_path and os.path.exists(kb_path):
                with open(kb_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return "Knowledge base not available"
        
        resource = MCPResource(
            uri=uri,
            name=name,
            description=description,
            mimeType="text/plain"
        )
        
        self.register_resource(resource, read_kb)
    
    def register_config_resource(
        self,
        uri: str = "config://agent",
        name: str = "Agent Configuration",
        description: str = "Agent configuration",
        config_dict: Dict[str, Any] = None
    ):
        """Register configuration resource
        
        Args:
            uri: Resource URI
            name: Resource name
            description: Resource description
            config_dict: Configuration dictionary
        """
        if config_dict is None:
            config_dict = {
                "version": "1.0.0",
                "features": {
                    "search": True,
                    "recommendation": True,
                    "booking": True
                }
            }
        
        def read_config():
            import json
            return json.dumps(config_dict, indent=2)
        
        resource = MCPResource(
            uri=uri,
            name=name,
            description=description,
            mimeType="application/json"
        )
        
        self.register_resource(resource, read_config)


def create_default_resources() -> MCPResourceManager:
    """Create default MCP resources
    
    Returns:
        MCPResourceManager with default resources registered
    """
    manager = MCPResourceManager()
    
    # Register system prompt
    manager.register_system_prompt_resource()
    
    # Register knowledge base
    manager.register_knowledge_base_resource()
    
    # Register configuration
    manager.register_config_resource()
    
    logger.info("Created default MCP resources")
    return manager


__all__ = [
    "MCPResourceManager",
    "create_default_resources",
]
