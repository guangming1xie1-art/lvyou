#!/usr/bin/env python3
"""
Phase 3 Verification Script

This script verifies that all Phase 3 components (MCP V2, Agent Skills, Concurrency)
are correctly implemented and can be imported.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def print_section(title):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def test_mcp_integration():
    """Test MCP V2 Integration"""
    print_section("Phase 3.1: MCP Integration")
    
    try:
        from mcp import MCPTool, MCPResource, MCPProtocolHandler, MCPServerV2
        from mcp.tools import MCPToolFactory
        from mcp.resources import MCPResourceManager, create_default_resources
        
        print("✅ MCP V2 modules imported successfully")
        
        # Test protocol handler
        handler = MCPProtocolHandler()
        print("✅ MCPProtocolHandler instantiated")
        
        # Test tool factory
        tools = MCPToolFactory.get_all_tools()
        print(f"✅ Created {len(tools)} MCP tools")
        
        # Test resource manager
        resource_manager = create_default_resources()
        print(f"✅ Resource manager created with {len(resource_manager.resources)} resources")
        
        # Test MCP server
        mcp_server = MCPServerV2(handler, resource_manager)
        print("✅ MCPServerV2 instantiated")
        
        # Test router creation
        router = mcp_server.create_router()
        print(f"✅ Created MCP FastAPI router with {len(router.routes)} routes")
        
        # Test tool registration
        handler.register_tool(MCPToolFactory.create_search_flights_tool())
        print("✅ Tool registered successfully")
        
        # Test resource registration
        resource_manager.register_system_prompt_resource(
            uri="test://prompt",
            name="Test Prompt",
            description="Test"
        )
        print("✅ Resource registered successfully")
        
        print("\n📊 MCP Protocol Handler Stats:")
        print(f"   Tools: {len(handler.list_tools())}")
        print(f"   Resources: {len(handler.list_resources())}")
        
        return True
    
    except Exception as e:
        print(f"❌ MCP Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_skills_framework():
    """Test Agent Skills Framework"""
    print_section("Phase 3.2: Agent Skills Framework")
    
    try:
        from skills import Skill, SkillRegistry, SkillLoader, get_skill_registry
        from skills.builtins import (
            SearchDestinationSkill,
            SearchFlightSkill,
            SearchHotelSkill
        )
        
        print("✅ Skills Framework modules imported successfully")
        
        # Test skill creation
        search_skill = SearchDestinationSkill()
        print(f"✅ Created skill: {search_skill.name}")
        print(f"   Description: {search_skill.description}")
        print(f"   Category: {search_skill.category}")
        print(f"   Cost: ${search_skill.cost_estimate:.4f}")
        
        # Test skill execution (dry run - will use mock)
        async def test_skill_execution():
            result = await search_skill.execute({
                "destination": "Tokyo"
            })
            print(f"✅ Skill executed successfully")
            print(f"   Result keys: {list(result.keys())}")
            
            # Check statistics
            metadata = search_skill.get_metadata()
            print(f"   Invocations: {metadata['invocation_count']}")
            print(f"   Success rate: {metadata['success_rate']:.2%}")
        
        asyncio.run(test_skill_execution())
        
        # Test skill registry
        registry = SkillRegistry()
        print("✅ SkillRegistry instantiated")
        
        # Register skills
        registry.register(search_skill)
        registry.register(SearchFlightSkill())
        registry.register(SearchHotelSkill())
        print(f"✅ Registered 3 skills")
        
        # Test skill listing
        all_skills = registry.list_all()
        print(f"✅ Listed {len(all_skills)} skills")
        
        # Test category listing
        search_skills = registry.list_by_category("search")
        print(f"✅ Listed {len(search_skills)} search skills")
        
        # Test skill retrieval
        retrieved = registry.get("search_destination")
        print(f"✅ Retrieved skill: {retrieved.name if retrieved else 'None'}")
        
        # Test skill execution through registry
        async def test_registry_execution():
            result = await registry.execute(
                "search_destination",
                {"destination": "Paris"}
            )
            print("✅ Skill executed through registry")
        
        asyncio.run(test_registry_execution())
        
        # Test statistics
        stats = registry.get_statistics()
        print(f"\n📊 Registry Statistics:")
        print(f"   Total Skills: {stats['total_skills']}")
        print(f"   Total Invocations: {stats['total_invocations']}")
        print(f"   Total Cost: ${stats['total_cost']:.4f}")
        print(f"   Success Rate: {stats['overall_success_rate']:.2%}")
        
        return True
    
    except Exception as e:
        print(f"❌ Skills Framework test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_concurrency():
    """Test Concurrency Optimization"""
    print_section("Phase 3.3: High Concurrency Optimization")
    
    try:
        from concurrency import (
            MemoryPool,
            ObjectPool,
            ConnectionPool,
            APIConnectionPool,
            RateLimiter,
            StreamingManager
        )
        
        print("✅ Concurrency modules imported successfully")
        
        # Test memory pool
        async def test_memory_pool():
            pool = MemoryPool(max_size=10, item_size_limit=1024*1024)
            print("✅ MemoryPool instantiated")
            
            # Test allocation
            success = await pool.allocate("test_key", 1024)
            print(f"✅ Allocated memory: {success}")
            
            # Test retrieval
            item = await pool.get("test_key")
            print(f"✅ Retrieved item: {item is not None}")
            
            # Test deallocation
            freed = await pool.free("test_key")
            print(f"✅ Freed memory: {freed}")
            
            # Test statistics
            stats = pool.get_stats()
            print(f"\n📊 Memory Pool Stats:")
            print(f"   Allocated: {stats['allocated']}")
            print(f"   Freed: {stats['freed']}")
            print(f"   Current: {stats['current']}")
            print(f"   Utilization: {stats['utilization']:.2%}")
        
        asyncio.run(test_memory_pool())
        
        # Test object pool
        async def test_object_pool():
            def create_dict():
                return {"data": "test"}
            
            pool = ObjectPool(create_dict, max_size=10)
            print("\n✅ ObjectPool instantiated")
            
            # Test acquire
            obj1 = await pool.acquire()
            obj2 = await pool.acquire()
            print(f"✅ Acquired {2} objects")
            
            # Test release
            await pool.release(obj1)
            await pool.release(obj2)
            print(f"✅ Released {2} objects")
            
            # Test reuse
            obj3 = await pool.acquire()
            print(f"✅ Reused object from pool")
            
            # Test statistics
            stats = pool.get_stats()
            print(f"\n📊 Object Pool Stats:")
            print(f"   Created: {stats['created']}")
            print(f"   Reused: {stats['reused']}")
            print(f"   Reuse Rate: {stats['reuse_rate']:.2%}")
        
        asyncio.run(test_object_pool())
        
        # Test connection pool
        async def test_connection_pool():
            pool = ConnectionPool(max_connections=10, timeout=5.0)
            print("\n✅ ConnectionPool instantiated")
            
            # Test acquire
            acquired = await pool.acquire()
            print(f"✅ Acquired connection: {acquired}")
            
            # Test release
            await pool.release()
            print(f"✅ Released connection")
            
            # Test context manager
            async with pool:
                pass
            print(f"✅ Context manager works")
            
            # Test statistics
            stats = pool.get_stats()
            print(f"\n📊 Connection Pool Stats:")
            print(f"   Active: {stats['active']}")
            print(f"   Available: {stats['available']}")
            print(f"   Utilization: {stats['utilization']:.2%}")
        
        asyncio.run(test_connection_pool())
        
        # Test API connection pool
        async def test_api_connection_pool():
            pool = APIConnectionPool(
                max_connections=100,
                timeout=10.0,
                max_retries=3
            )
            print("\n✅ APIConnectionPool instantiated")
            
            stats = pool.get_stats()
            print(f"📊 API Pool Stats:")
            print(f"   Max Connections: {stats['max_connections']}")
            print(f"   Request Stats: {stats.get('requests', {})}")
        
        asyncio.run(test_api_connection_pool())
        
        # Test rate limiter
        async def test_rate_limiter():
            limiter = RateLimiter(rate=100, burst=200)
            print("\n✅ RateLimiter instantiated")
            
            # Test acquisition
            acquired = await limiter.acquire(tokens=10)
            print(f"✅ Acquired tokens: {acquired}")
            
            # Test wait
            await limiter.wait_if_needed(tokens=5)
            print(f"✅ Wait completed")
            
            # Test statistics
            stats = limiter.get_stats()
            print(f"\n📊 Rate Limiter Stats:")
            print(f"   Rate: {stats['rate']}/s")
            print(f"   Burst: {stats['burst']}")
            print(f"   Current Tokens: {stats['current_tokens']:.2f}")
            print(f"   Allow Rate: {stats['allow_rate']:.2%}")
        
        asyncio.run(test_rate_limiter())
        
        # Test streaming manager
        async def test_streaming_manager():
            async def item_generator():
                for i in range(5):
                    yield {"id": i, "name": f"Item {i}"}
            
            response = await StreamingManager.stream_json_array(item_generator())
            print("\n✅ StreamingManager created JSON stream response")
            print(f"   Media type: {response.media_type}")
        
        asyncio.run(test_streaming_manager())
        
        return True
    
    except Exception as e:
        print(f"❌ Concurrency test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_integration():
    """Test Configuration Integration"""
    print_section("Configuration Integration")
    
    try:
        from config import settings
        
        print("✅ Settings imported successfully")
        
        # Check MCP V2 settings
        print(f"\n📋 MCP V2 Configuration:")
        print(f"   Enabled: {settings.mcp_v2_enabled}")
        print(f"   Tools Enabled: {settings.mcp_v2_tools_enabled}")
        print(f"   Resources Enabled: {settings.mcp_v2_resources_enabled}")
        print(f"   Max WebSockets: {settings.mcp_v2_max_websockets}")
        
        # Check Skills settings
        print(f"\n📋 Skills Configuration:")
        print(f"   Enabled: {settings.skills_enabled}")
        print(f"   Auto Load: {settings.skills_auto_load}")
        print(f"   Builtin Enabled: {settings.skills_builtin_enabled}")
        print(f"   Max Execution Time: {settings.skills_max_execution_time}s")
        print(f"   Parallel Enabled: {settings.skills_parallel_enabled}")
        
        # Check Concurrency settings
        print(f"\n📋 Concurrency Configuration:")
        print(f"   Max Connections: {settings.connection_pool_max_connections}")
        print(f"   Rate Limiting Enabled: {settings.rate_limiting_enabled}")
        print(f"   Default Rate: {settings.rate_limit_default_rate}/s")
        print(f"   Memory Pool Enabled: {settings.memory_pool_enabled}")
        print(f"   Streaming Enabled: {settings.streaming_enabled}")
        
        return True
    
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification tests"""
    print_section("Phase 3 Verification Script")
    print("Testing MCP Integration, Agent Skills, and Concurrency Optimization")
    
    results = {}
    
    # Run tests
    results["MCP Integration"] = test_mcp_integration()
    results["Skills Framework"] = test_skills_framework()
    results["Concurrency"] = test_concurrency()
    results["Configuration"] = test_config_integration()
    
    # Summary
    print_section("Verification Summary")
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(1 for passed in results.values() if passed)
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if all(results.values()):
        print("\n🎉 All Phase 3 components verified successfully!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
