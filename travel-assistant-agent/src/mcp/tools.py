"""
MCP Tools Definition

This module provides factory methods for creating MCP tools
that wrap Travel Assistant skills and capabilities.
"""

from typing import Dict, Any, List, Optional
from .protocol import MCPTool
import logging

logger = logging.getLogger(__name__)


class MCPToolFactory:
    """MCP Tool Factory
    
    Creates MCP tool definitions for various travel assistant capabilities.
    """
    
    @staticmethod
    def create_search_flights_tool() -> MCPTool:
        """Create flight search tool"""
        return MCPTool(
            name="search_flights",
            description="搜索航班 - Search for flights based on destination and dates",
            inputSchema={
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "目的地 (Destination city or airport code)"
                    },
                    "departure_date": {
                        "type": "string",
                        "description": "出发日期 (YYYY-MM-DD format)"
                    },
                    "return_date": {
                        "type": "string",
                        "description": "返回日期 (YYYY-MM-DD format, optional for one-way)"
                    },
                    "passengers": {
                        "type": "integer",
                        "description": "乘客数量 (Number of passengers, default: 1)",
                        "default": 1
                    },
                    "class": {
                        "type": "string",
                        "enum": ["economy", "business", "first"],
                        "description": "舱位等级 (Travel class, default: economy)",
                        "default": "economy"
                    }
                },
                "required": ["destination", "departure_date"]
            }
        )
    
    @staticmethod
    def create_search_hotels_tool() -> MCPTool:
        """Create hotel search tool"""
        return MCPTool(
            name="search_hotels",
            description="搜索酒店 - Search for hotels based on destination and dates",
            inputSchema={
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "目的地 (Destination city)"
                    },
                    "check_in": {
                        "type": "string",
                        "description": "入住日期 (YYYY-MM-DD format)"
                    },
                    "check_out": {
                        "type": "string",
                        "description": "退房日期 (YYYY-MM-DD format)"
                    },
                    "guests": {
                        "type": "integer",
                        "description": "客人数量 (Number of guests, default: 2)",
                        "default": 2
                    },
                    "min_rating": {
                        "type": "integer",
                        "description": "最低评分 (Minimum rating 1-5, default: 3)",
                        "default": 3
                    }
                },
                "required": ["destination", "check_in", "check_out"]
            }
        )
    
    @staticmethod
    def create_get_recommendations_tool() -> MCPTool:
        """Create recommendations tool"""
        return MCPTool(
            name="get_recommendations",
            description="获取旅游推荐 - Get personalized travel recommendations",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "用户ID (User identifier)"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["flight", "hotel", "attraction", "destination"],
                        "description": "推荐类别 (Recommendation category)"
                    },
                    "destination": {
                        "type": "string",
                        "description": "目的地 (Optional destination filter)"
                    },
                    "budget": {
                        "type": "number",
                        "description": "预算 (Optional budget limit)"
                    }
                },
                "required": ["user_id"]
            }
        )
    
    @staticmethod
    def create_get_destination_info_tool() -> MCPTool:
        """Create destination info tool"""
        return MCPTool(
            name="get_destination_info",
            description="获取目的地信息 - Get detailed information about a destination",
            inputSchema={
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "目的地 (Destination name)"
                    },
                    "info_type": {
                        "type": "string",
                        "enum": ["general", "attractions", "weather", "reviews"],
                        "description": "信息类型 (Type of information, default: general)",
                        "default": "general"
                    }
                },
                "required": ["destination"]
            }
        )
    
    @staticmethod
    def create_book_flight_tool() -> MCPTool:
        """Create flight booking tool"""
        return MCPTool(
            name="book_flight",
            description="预订航班 - Book a flight",
            inputSchema={
                "type": "object",
                "properties": {
                    "flight_id": {
                        "type": "string",
                        "description": "航班ID (Flight identifier)"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "用户ID (User identifier)"
                    },
                    "passengers": {
                        "type": "array",
                        "description": "乘客信息 (Array of passenger details)",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "email": {"type": "string"},
                                "phone": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["flight_id", "user_id", "passengers"]
            }
        )
    
    @staticmethod
    def create_book_hotel_tool() -> MCPTool:
        """Create hotel booking tool"""
        return MCPTool(
            name="book_hotel",
            description="预订酒店 - Book a hotel room",
            inputSchema={
                "type": "object",
                "properties": {
                    "hotel_id": {
                        "type": "string",
                        "description": "酒店ID (Hotel identifier)"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "用户ID (User identifier)"
                    },
                    "check_in": {
                        "type": "string",
                        "description": "入住日期 (YYYY-MM-DD format)"
                    },
                    "check_out": {
                        "type": "string",
                        "description": "退房日期 (YYYY-MM-DD format)"
                    },
                    "rooms": {
                        "type": "integer",
                        "description": "房间数量 (Number of rooms, default: 1)",
                        "default": 1
                    },
                    "guest_info": {
                        "type": "object",
                        "description": "客人信息 (Guest details)",
                        "properties": {
                            "name": {"type": "string"},
                            "email": {"type": "string"},
                            "phone": {"type": "string"}
                        }
                    }
                },
                "required": ["hotel_id", "user_id", "check_in", "check_out"]
            }
        )
    
    @staticmethod
    def create_get_weather_tool() -> MCPTool:
        """Create weather tool"""
        return MCPTool(
            name="get_weather",
            description="获取天气预报 - Get weather forecast for a destination",
            inputSchema={
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "目的地 (Destination name)"
                    },
                    "days": {
                        "type": "integer",
                        "description": "预报天数 (Number of days, 1-7, default: 3)",
                        "default": 3,
                        "minimum": 1,
                        "maximum": 7
                    }
                },
                "required": ["destination"]
            }
        )
    
    @staticmethod
    def create_get_reviews_tool() -> MCPTool:
        """Create reviews tool"""
        return MCPTool(
            name="get_reviews",
            description="获取评价 - Get reviews for destinations, hotels, or attractions",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "目标 (Target name - destination, hotel, or attraction)"
                    },
                    "target_type": {
                        "type": "string",
                        "enum": ["destination", "hotel", "attraction"],
                        "description": "目标类型 (Target type)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回数量限制 (Number of reviews to return, default: 10)",
                        "default": 10
                    },
                    "min_rating": {
                        "type": "integer",
                        "description": "最低评分 (Minimum rating filter 1-5, default: 1)",
                        "default": 1
                    }
                },
                "required": ["target", "target_type"]
            }
        )
    
    @staticmethod
    def get_all_tools() -> List[MCPTool]:
        """Get all available MCP tools
        
        Returns:
            List of all MCP tool definitions
        """
        return [
            MCPToolFactory.create_search_flights_tool(),
            MCPToolFactory.create_search_hotels_tool(),
            MCPToolFactory.create_get_recommendations_tool(),
            MCPToolFactory.create_get_destination_info_tool(),
            MCPToolFactory.create_book_flight_tool(),
            MCPToolFactory.create_book_hotel_tool(),
            MCPToolFactory.create_get_weather_tool(),
            MCPToolFactory.create_get_reviews_tool(),
        ]
    
    @staticmethod
    def get_tool_by_name(name: str) -> Optional[MCPTool]:
        """Get a specific tool by name
        
        Args:
            name: Tool name
            
        Returns:
            MCPTool if found, None otherwise
        """
        tools = MCPToolFactory.get_all_tools()
        for tool in tools:
            if tool.name == name:
                return tool
        return None


__all__ = [
    "MCPToolFactory",
]
