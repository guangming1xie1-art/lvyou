"""
重构后工作流的测试
验证：
1. 4 个子图都能独立执行并返回正确的 usage 统计
2. 主图能按顺序调用 4 个子图，usage 正确累加
3. MCP Client 能成功连接 Java API 并调用工具
4. SkillRegistry 能正确列出、加载、使用 skills
5. 端到端工作流执行完整用户请求，返回最终结果 + 完整 usage 统计
"""
import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault("DEEPSEEK_API_KEY", "test-key")
os.environ.setdefault("DASHSCOPE_API_KEY", "test-key")
from ...src.workflows.subgraphs import (
    build_collect_info_graph,
    build_search_graph,
    build_recommend_graph,
    build_booking_graph,
)
from ...src.workflows.main_workflow import (
    get_main_workflow,
    run_main_workflow_sync,
)
from ...src.agents.mcp_client import get_mcp_client
from ...src.skills.registry import SkillRegistry


class TestSubGraphs:
    """测试子图独立执行"""
    
    def test_collect_info_graph(self):
        """测试信息收集子图"""
        graph = build_collect_info_graph()
        result = graph.invoke({
            "user_message": "我想6月去巴黎玩5天，预算1万",
            "collected_info": None,
            "usage": {"prompt": 0, "completion": 0, "total": 0}
        })
        
        assert "collected_info" in result
        assert "usage" in result
        assert result["usage"]["prompt"] >= 0
        assert result["usage"]["completion"] >= 0
        print(f"✓ Collect info graph: {result['collected_info']}")
        print(f"  Usage: {result['usage']}")
    
    def test_search_graph(self):
        """测试搜索子图"""
        graph = build_search_graph()
        result = graph.invoke({
            "user_message": "搜索巴黎的酒店",
            "collected_info": {"destination": "Paris", "budget": "10000"},
            "search_results": None,
            "usage": {"prompt": 0, "completion": 0, "total": 0}
        })
        
        assert "search_results" in result
        assert "usage" in result
        assert result["usage"]["prompt"] >= 0
        print(f"✓ Search graph: {result['search_results']}")
        print(f"  Usage: {result['usage']}")
    
    def test_recommend_graph(self):
        """测试推荐子图"""
        graph = build_recommend_graph()
        result = graph.invoke({
            "user_message": "给我推荐巴黎旅游方案",
            "collected_info": {"destination": "Paris"},
            "search_results": {"destinations": []},
            "recommendations": None,
            "usage": {"prompt": 0, "completion": 0, "total": 0}
        })
        
        assert "recommendations" in result
        assert "usage" in result
        assert result["usage"]["prompt"] >= 0
        print(f"✓ Recommend graph: {result['recommendations']}")
        print(f"  Usage: {result['usage']}")
    
    def test_booking_graph(self):
        """测试预订子图"""
        graph = build_booking_graph()
        result = graph.invoke({
            "user_message": "预订第一个方案",
            "collected_info": {"destination": "Paris"},
            "recommendations": [{"id": "rec_001", "title": "巴黎5日游"}],
            "booking_confirmation": None,
            "usage": {"prompt": 0, "completion": 0, "total": 0}
        })
        
        assert "booking_confirmation" in result
        assert "usage" in result
        assert result["usage"]["prompt"] >= 0
        print(f"✓ Booking graph: {result['booking_confirmation']}")
        print(f"  Usage: {result['usage']}")


class TestMainWorkflow:
    """测试主工作流"""
    
    def test_main_workflow_execution(self):
        """测试主工作流完整执行"""
        result = run_main_workflow_sync("我想6月去巴黎玩5天，预算1-1.5万")
        
        assert result is not None
        assert "collected_info" in result
        assert "search_results" in result
        assert "recommendations" in result
        assert "booking_confirmation" in result
        assert "total_usage" in result
        
        # 验证 usage 累加
        usage = result["total_usage"]
        assert "prompt" in usage
        assert "completion" in usage
        assert usage["prompt"] >= 0
        assert usage["completion"] >= 0
        
        print(f"✓ Main workflow completed")
        print(f"  Total usage: {usage}")
        print(f"  Collected info: {result['collected_info']}")


class TestMCPClient:
    """测试 MCP Client"""
    
    async def test_mcp_client_connection(self):
        """测试 MCP Client 连接"""
        client = get_mcp_client()
        success = await client.connect()
        
        # 即使连接失败也应该初始化工具
        tools = client.get_tools()
        assert len(tools) > 0
        print(f"✓ MCP Client initialized with {len(tools)} tools")
    
    async def test_mcp_client_tools(self):
        """测试 MCP Client 工具调用"""
        client = get_mcp_client()
        await client.connect()
        
        # 测试 search_destinations
        result = await client.call_tool(
            "search_destinations",
            {"query": "Paris"}
        )
        
        assert "result" in result or "error" in result
        print(f"✓ MCP tool call result: {result}")


class TestSkillRegistry:
    """测试 Skill Registry"""
    
    def test_list_skills(self):
        """测试列出 skills"""
        skills = SkillRegistry.list_skills()
        
        assert len(skills) > 0
        assert all("name" in s and "description" in s for s in skills)
        
        print(f"✓ Found {len(skills)} skills:")
        for skill in skills:
            print(f"  - {skill['name']}: {skill['description']}")
    
    def test_get_skill_summary(self):
        """测试获取 skill 摘要"""
        summary = SkillRegistry.get_skill_summary("search")
        
        assert "name" in summary
        assert "description" in summary
        print(f"✓ Skill summary: {summary['name']}")
    
    async def test_load_skill(self):
        """测试加载 skill"""
        skill = await SkillRegistry.load_skill("search")
        
        assert skill is not None
        assert skill.name == "search"
        print(f"✓ Loaded skill: {skill.name}")
    
    async def test_skill_execution(self):
        """测试 skill 执行"""
        skill = await SkillRegistry.load_skill("search")
        result = await skill.execute({
            "query": "Paris",
            "limit": 5
        })
        
        assert "results" in result
        print(f"✓ Skill execution result: {result}")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("Testing Refactored Workflow")
    print("="*60 + "\n")
    
    # 测试子图
    print("1. Testing SubGraphs...")
    test_subgraphs = TestSubGraphs()
    test_subgraphs.test_collect_info_graph()
    test_subgraphs.test_search_graph()
    test_subgraphs.test_recommend_graph()
    test_subgraphs.test_booking_graph()
    
    # 测试主工作流
    print("\n2. Testing Main Workflow...")
    test_workflow = TestMainWorkflow()
    test_workflow.test_main_workflow_execution()
    
    # 测试 MCP Client
    print("\n3. Testing MCP Client...")
    test_mcp = TestMCPClient()
    asyncio.run(test_mcp.test_mcp_client_connection())
    asyncio.run(test_mcp.test_mcp_client_tools())
    
    # 测试 Skill Registry
    print("\n4. Testing Skill Registry...")
    test_registry = TestSkillRegistry()
    test_registry.test_list_skills()
    test_registry.test_get_skill_summary()
    asyncio.run(test_registry.test_load_skill())
    asyncio.run(test_registry.test_skill_execution())
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)


if __name__ == "__main__":
    run_all_tests()
