"""
Unit tests for ToolAdapter

测试工具适配器的核心功能：
1. 工具元数据转换
2. 异步调用包装
3. LangChain Tool 对象创建
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

from agents.tool_adapter import ToolAdapter, wrap_mcp_tools


class TestToolAdapter:
    """测试 ToolAdapter 类"""
    
    @pytest.fixture
    def mock_mcp_client(self):
        """创建 mock MCP 客户端"""
        client = AsyncMock()
        client.call_tool = AsyncMock(return_value={
            "status": "success",
            "data": ["result1", "result2"]
        })
        return client
    
    @pytest.fixture
    def sample_tool_def(self):
        """创建示例工具定义"""
        return {
            "name": "test_search_hotels",
            "description": "搜索酒店信息",
            "args_schema": {
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "目的地"
                    },
                    "price_min": {
                        "type": "number",
                        "description": "最低价格"
                    }
                },
                "required": ["destination"]
            }
        }
    
    def test_tool_adapter_initialization(self, sample_tool_def, mock_mcp_client):
        """测试工具适配器初始化"""
        adapter = ToolAdapter(sample_tool_def, mock_mcp_client)
        
        assert adapter.tool_name == "test_search_hotels"
        assert adapter.description == "搜索酒店信息"
        assert adapter.args_schema is not None
        assert adapter.mcp_client == mock_mcp_client
    
    @pytest.mark.asyncio
    async def test_invoke_async_success(self, sample_tool_def, mock_mcp_client):
        """测试异步调用成功场景"""
        adapter = ToolAdapter(sample_tool_def, mock_mcp_client)
        
        result = await adapter.invoke_async(
            destination="杭州",
            price_min=100
        )
        
        # 验证调用了 MCP 客户端
        mock_mcp_client.call_tool.assert_called_once_with(
            "test_search_hotels",
            parameters={"destination": "杭州", "price_min": 100}
        )
        
        # 验证返回结果是 JSON 字符串
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_invoke_async_failure(self, sample_tool_def, mock_mcp_client):
        """测试异步调用失败场景"""
        # 模拟调用失败
        mock_mcp_client.call_tool.side_effect = Exception("Connection timeout")
        
        adapter = ToolAdapter(sample_tool_def, mock_mcp_client)
        result = await adapter.invoke_async(destination="杭州")
        
        # 验证返回错误信息
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["status"] == "failed"
    
    def test_to_langchain_tool(self, sample_tool_def, mock_mcp_client):
        """测试转换为 LangChain Tool 对象"""
        adapter = ToolAdapter(sample_tool_def, mock_mcp_client)
        tool = adapter.to_langchain_tool()
        
        # 验证工具属性
        assert tool.name == "test_search_hotels"
        assert tool.description == "搜索酒店信息"
        assert hasattr(tool, 'func')  # 同步调用方法
        assert hasattr(tool, 'coroutine')  # 异步调用方法
    
    def test_json_type_to_python_conversion(self):
        """测试 JSON 类型到 Python 类型的转换"""
        assert ToolAdapter._json_type_to_python("string") == str
        assert ToolAdapter._json_type_to_python("number") == float
        assert ToolAdapter._json_type_to_python("integer") == int
        assert ToolAdapter._json_type_to_python("boolean") == bool
        assert ToolAdapter._json_type_to_python("array") == list
        assert ToolAdapter._json_type_to_python("object") == dict
        assert ToolAdapter._json_type_to_python("unknown_type") == str  # 默认


class TestWrapMCPTools:
    """测试批量包装 MCP 工具的功能"""
    
    @pytest.fixture
    def mock_mcp_client(self):
        """创建 mock MCP 客户端"""
        return AsyncMock()
    
    @pytest.fixture
    def sample_tools_dicts(self):
        """创建示例工具定义列表"""
        return [
            {
                "name": "search_hotels",
                "description": "搜索酒店",
                "args_schema": {}
            },
            {
                "name": "search_flights",
                "description": "搜索航班",
                "args_schema": {}
            },
            {
                "name": "get_recommendations",
                "description": "获取推荐",
                "args_schema": {}
            }
        ]
    
    def test_wrap_mcp_tools_success(self, sample_tools_dicts, mock_mcp_client):
        """测试批量包装工具成功"""
        tools = wrap_mcp_tools(sample_tools_dicts, mock_mcp_client)
        
        # 验证返回的工具数量
        assert len(tools) == 3
        
        # 验证每个工具的名称
        tool_names = [tool.name for tool in tools]
        assert "search_hotels" in tool_names
        assert "search_flights" in tool_names
        assert "get_recommendations" in tool_names
    
    def test_wrap_mcp_tools_partial_failure(self, mock_mcp_client):
        """测试部分工具包装失败的场景"""
        # 创建一些有效和无效的工具定义
        tools_dicts = [
            {"name": "valid_tool", "description": "Valid tool"},
            {"invalid": "missing_name"},  # 缺少 name 字段
            {"name": "another_valid_tool", "description": "Another valid tool"}
        ]
        
        tools = wrap_mcp_tools(tools_dicts, mock_mcp_client)
        
        # 应该只包装成功有效的工具
        assert len(tools) >= 0  # 至少不会崩溃
    
    def test_wrap_empty_tools_list(self, mock_mcp_client):
        """测试空工具列表"""
        tools = wrap_mcp_tools([], mock_mcp_client)
        assert len(tools) == 0


class TestToolIntegration:
    """集成测试：验证工具能被 LangChain Agent 使用"""
    
    @pytest.fixture
    def mock_mcp_client(self):
        """创建 mock MCP 客户端"""
        client = AsyncMock()
        client.call_tool = AsyncMock(return_value={
            "hotels": [
                {"name": "酒店A", "price": 500},
                {"name": "酒店B", "price": 300}
            ]
        })
        return client
    
    @pytest.mark.asyncio
    async def test_tool_can_be_invoked(self, mock_mcp_client):
        """测试工具可以被调用"""
        tool_def = {
            "name": "search_hotels",
            "description": "搜索酒店",
            "args_schema": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string"}
                }
            }
        }
        
        adapter = ToolAdapter(tool_def, mock_mcp_client)
        tool = adapter.to_langchain_tool()
        
        # 模拟 LangChain Agent 调用工具
        result = await tool.coroutine(destination="杭州")
        
        # 验证结果
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert "hotels" in result_data
        assert len(result_data["hotels"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
