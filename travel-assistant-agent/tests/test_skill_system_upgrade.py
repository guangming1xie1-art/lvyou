"""
Comprehensive Test for Skill System Upgrade

Tests all new components: YAML schemas, Pydantic models, enhanced skills,
dependency resolver, skill executor, and prompt generator.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ...src.skills.search.models import SearchInput, SearchOutput, SearchResultItem
from ...src.skills.registry import SkillRegistry
from ...src.skills.prompt_generator import SkillPromptGenerator
from ...src.skills.dependency_resolver import DependencyResolver
from ...src.skills.executor import SkillExecutor


class TestSkillSystemUpgrade:
    """测试套件 - 验证技能系统升级的所有组件"""
    
    def __init__(self):
        self.skills_dir = Path(__file__).parent.parent / "src" / "skills"
        self.test_results = []
    
    def run_all_tests(self):
        """运行所有测试"""
        logger.info("🚀 Starting Skill System Upgrade Tests")
        
        # Run async tests
        asyncio.run(self._run_async_tests())
        
        # Run sync tests
        self._run_sync_tests()
        
        # Print summary
        self._print_test_summary()
        
        return all(result["passed"] for result in self.test_results)
    
    async def _run_async_tests(self):
        """运行异步测试"""
        await self.test_yaml_schema_loading()
        await self.test_pydantic_models()
        await self.test_dependency_resolver()
        await self.test_skill_executor()
    
    def _run_sync_tests(self):
        """运行同步测试"""
        self.test_prompt_generator()
    
    def record_result(self, name: str, passed: bool, details: str = ""):
        """记录测试结果"""
        self.test_results.append({
            "name": name,
            "passed": passed,
            "details": details
        })
        
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status}: {name}")
        if details and not passed:
            logger.info(f"  → {details}")
    
    async def test_yaml_schema_loading(self):
        """测试 YAML Schema 加载"""
        try:
            # Test loading all skill schemas
            skills = ["search", "recommend", "booking", "info_collection"]
            
            for skill_name in skills:
                schema = SkillRegistry.load_yaml_schema(skill_name)
                assert schema is not None, f"Failed to load schema for {skill_name}"
                assert "name" in schema, f"Schema for {skill_name} missing name"
                assert "input_schema" in schema, f"Schema for {skill_name} missing input_schema"
                assert "output_schema" in schema, f"Schema for {skill_name} missing output_schema"
                assert "examples" in schema, f"Schema for {skill_name} missing examples"
            
            self.record_result("YAML Schema Loading", True)
            
        except Exception as e:
            self.record_result("YAML Schema Loading", False, str(e))
    
    async def test_pydantic_models(self):
        """测试 Pydantic 模型"""
        try:
            # Test SearchInput model
            search_input = SearchInput(query="巴黎", limit=10)
            assert search_input.query == "巴黎"
            assert search_input.limit == 10
            
            # Test validation
            try:
                SearchInput()  # Should fail without query
                self.record_result("Pydantic Models", False, "SearchInput should require query")
                return
            except Exception:
                pass  # Expected
            
            # Test SearchOutput
            result_item = SearchResultItem(
                id="test_001",
                type="destination",
                name="测试目的地",
                description="测试描述"
            )
            
            self.record_result("Pydantic Models", True)
            
        except Exception as e:
            self.record_result("Pydantic Models", False, str(e))
    
    async def test_dependency_resolver(self):
        """测试依赖解析器"""
        try:
            # Test schema loading function
            def load_schema(name):
                return SkillRegistry.load_yaml_schema(name)
            
            # Test cycle detection (should pass for all skills)
            skills = ["search", "recommend", "booking", "info_collection"]
            
            for skill_name in skills:
                has_cycle = DependencyResolver.validate_dependencies(skill_name, load_schema)
                assert has_cycle, f"Dependency validation failed for {skill_name}"
            
            # Test dependency graph generation
            for skill_name in skills:
                graph = DependencyResolver.get_dependency_graph(skill_name, load_schema)
                assert isinstance(graph, dict), f"Invalid graph for {skill_name}"
            
            # Test execution order generation
            for skill_name in skills:
                order = DependencyResolver.get_execution_order(skill_name, load_schema)
                assert isinstance(order, list), f"Invalid execution order for {skill_name}"
            
            self.record_result("Dependency Resolver", True)
            
        except Exception as e:
            self.record_result("Dependency Resolver", False, str(e))
    
    async def test_skill_executor(self):
        """测试技能执行器"""
        try:
            # Mock async skill loader
            async def mock_skill_loader(name):
                class MockSkill:
                    def __init__(self):
                        self.name = name
                        self.enabled = True
                        self.cost_estimate = 0.05
                    
                    async def execute_raw(self, input_data):
                        return {"results": ["test"], "success": True}
                    
                    async def validate_input(self, input_data):
                        return input_data
                    
                    async def validate_output(self, output_data):
                        return type('', (), {'model_dump': lambda: output_data})()
                    
                    def calculate_cost(self, input_data, output_data):
                        return 0.05
                    
                    def get_metadata(self):
                        return {"name": name}
                
                return MockSkill()
            
            def mock_schema_loader(name):
                return SkillRegistry.load_yaml_schema(name)
            
            # Test basic execution
            result = await SkillExecutor.execute(
                "search",
                {"query": "test", "limit": 5},
                mock_skill_loader,
                mock_schema_loader,
                track_cost=True
            )
            
            assert result["success"], f"Skill execution failed: {result.get('error')}"
            assert "cost" in result, "Cost not tracked in execution"
            assert "execution_time_ms" in result, "Execution time not tracked"
            
            self.record_result("Skill Executor", True)
            
        except Exception as e:
            self.record_result("Skill Executor", False, str(e))
    
    def test_prompt_generator(self):
        """测试 Prompt Generator"""
        try:
            # Test system prompt generation
            system_prompt = SkillPromptGenerator.generate_system_prompt(self.skills_dir)
            assert len(system_prompt) > 1000, "System prompt too short"
            assert "## Available Skills" in system_prompt, "Missing skills section"
            assert "search" in system_prompt.lower(), "Missing search skill"
            assert "recommend" in system_prompt.lower(), "Missing recommend skill"
            assert "## Cost Awareness" in system_prompt, "Missing cost section"
            
            # Test individual skill prompt
            search_prompt = SkillPromptGenerator.generate_skill_prompt(self.skills_dir, "search")
            assert search_prompt is not None, "Failed to get search skill prompt"
            assert "INPUT SCHEMA" in search_prompt, "Missing input schema in prompt"
            assert "OUTPUT SCHEMA" in search_prompt, "Missing output schema in prompt"
            
            # Test summary table
            summary_table = SkillPromptGenerator.generate_summary_table(self.skills_dir)
            assert "| Skill |" in summary_table, "Missing table header"
            assert "search" in summary_table, "Missing search in table"
            
            self.record_result("Prompt Generator", True)
            
        except Exception as e:
            self.record_result("Prompt Generator", False, str(e))
    
    async def test_registry_enhancements(self):
        """测试 Registry 增强功能"""
        try:
            # Test YAML skill listing
            yaml_skills = SkillRegistry.list_skills_yaml()
            assert len(yaml_skills) >= 4, f"Expected at least 4 skills, got {len(yaml_skills)}"
            
            # Test schema retrieval
            for skill_name in ["search", "recommend", "booking", "info_collection"]:
                schema = SkillRegistry.get_skill_schema(skill_name)
                assert "cost" in schema, f"Missing cost in {skill_name} schema"
                assert "dependencies" in schema, f"Missing dependencies in {skill_name} schema"
                assert "performance" in schema, f"Missing performance in {skill_name} schema"
            
            # Test LLM prompt generation
            llm_prompt = SkillRegistry.get_all_summaries_for_llm()
            assert len(llm_prompt) > 500, "LLM prompt too short"
            
            self.record_result("Registry Enhancements", True)
            
        except Exception as e:
            self.record_result("Registry Enhancements", False, str(e))
    
    def _print_test_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 60)
        print("📊 SKILL SYSTEM UPGRADE - TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r["passed"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['name']}")
        
        print("-" * 60)
        print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("\n🎉 All tests passed! Skill system upgrade is ready!")
        else:
            print(f"\n⚠️  {total - passed} tests failed. Please review the implementation.")
        
        print("=" * 60)


def main():
    """主测试函数"""
    test_suite = TestSkillSystemUpgrade()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
