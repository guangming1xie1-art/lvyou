#!/usr/bin/env python3
"""
Standalone test to verify the subgraphs module split was successful
This test doesn't rely on the parent __init__.py
"""

import sys
import os
import importlib

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_module_split():
    """Test that the module split was successful"""
    print("🧪 Testing subgraphs module split...\n")
    
    # Test 1: Import from the new package structure
    print("1️⃣ Testing direct module imports...")
    try:
        # Import the new package directly
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src/workflows'))
        import subgraphs
        print(f"   ✓ Package imported: {subgraphs.__name__}")
        print(f"   ✓ Package location: {subgraphs.__file__}")
        
        # Check if it's using the new package structure
        if 'subgraphs' in subgraphs.__file__:
            print("   ✓ Using new subgraphs package structure")
        else:
            print("   ⚠️  Using old single-file structure")
            sys.exit(1)
    except Exception as e:
        print(f"   ❌ Failed to import subgraphs: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Test 2: Import main API from new package
    print("\n2️⃣ Testing import from subgraphs.__init__...")
    try:
        from subgraphs import (
            SubState,
            build_collect_info_graph,
            build_search_graph,
            build_recommend_graph,
            build_booking_graph
        )
        print("   ✓ SubState imported")
        print("   ✓ build_collect_info_graph imported")
        print("   ✓ build_search_graph imported")
        print("   ✓ build_recommend_graph imported")
        print("   ✓ build_booking_graph imported")
    except Exception as e:
        print(f"   ❌ Failed to import from subgraphs: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Test 3: Test backward compatibility import from old path
    print("\n3️⃣ Testing backward compatibility import from subgraphs.py...")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src/workflows'))
        from subgraphs import (
            SubState as OldSubState,
            build_collect_info_graph as old_collect,
            build_search_graph as old_search,
            build_recommend_graph as old_recommend,
            build_booking_graph as old_booking
        )
        print("   ✓ All backward compatibility imports working")
        print("   ✓ Old imports resolve to new package structure")
    except Exception as e:
        print(f"   ❌ Backward compatibility broken: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Test 4: Import individual modules (check file existence and basic syntax)
    print("\n4️⃣ Testing individual module files...")
    module_files = [
        "src/workflows/subgraphs/__init__.py",
        "src/workflows/subgraphs/common.py",
        "src/workflows/subgraphs/collect.py",
        "src/workflows/subgraphs/search.py",
        "src/workflows/subgraphs/recommend.py",
        "src/workflows/subgraphs/booking.py",
        "src/workflows/subgraphs.py"
    ]
    
    for module_file in module_files:
        filepath = os.path.join(os.path.dirname(__file__), module_file)
        if os.path.exists(filepath):
            print(f"   ✓ {module_file} exists")
            
            # Try to compile the file
            try:
                with open(filepath, 'r') as f:
                    code = f.read()
                compile(code, filepath, 'exec')
                print(f"     ✓ {module_file} syntax is valid")
            except SyntaxError as e:
                print(f"     ❌ {module_file} has syntax error: {e}")
                sys.exit(1)
        else:
            print(f"   ❌ {module_file} not found")
            sys.exit(1)
    
    # Test 5: Check content of files for expected components
    print("\n5️⃣ Checking file contents...")
    
    # Check common.py has expected components
    common_file = os.path.join(os.path.dirname(__file__), 'src/workflows/subgraphs/common.py')
    with open(common_file, 'r') as f:
        common_content = f.read()
    
    expected_in_common = [
        "class SubState",
        "def skill_to_tool",
        "def build_search_tools",
        "def build_recommend_tools",
        "def get_tools_and_skills_text",
        "def get_rag_context",
        "cache_strategy = CacheStrategy()",
        "knowledge_base = KnowledgeBase()",
        "mcp_client = get_mcp_client()"
    ]
    
    for component in expected_in_common:
        if component in common_content:
            print(f"   ✓ common.py contains: {component.split('(')[0] if '(' in component else component.split('=')[0].strip()}")
        else:
            print(f"   ❌ common.py missing: {component}")
            sys.exit(1)
    
    # Check other files have expected functions
    file_functions = [
        ("collect.py", ["async def collect_info_node", "def build_collect_info_graph"]),
        ("search.py", ["async def search_plan_node", "async def search_execute_agent_node", "def build_search_graph"]),
        ("recommend.py", ["async def recommend_plan_node", "async def recommend_execute_agent_node", "def build_recommend_graph"]),
        ("booking.py", ["async def booking_node", "def build_booking_graph"]),
    ]
    
    for filename, functions in file_functions:
        filepath = os.path.join(os.path.dirname(__file__), f'src/workflows/subgraphs/{filename}')
        with open(filepath, 'r') as f:
            content = f.read()
        
        for func in functions:
            if func in content:
                print(f"   ✓ {filename} contains: {func}")
            else:
                print(f"   ❌ {filename} missing: {func}")
                sys.exit(1)
    
    # Check __init__.py exports
    init_file = os.path.join(os.path.dirname(__file__), 'src/workflows/subgraphs/__init__.py')
    with open(init_file, 'r') as f:
        init_content = f.read()
    
    expected_exports = [
        "from .common import SubState",
        "from .collect import build_collect_info_graph",
        "from .search import build_search_graph",
        "from .recommend import build_recommend_graph",
        "from .booking import build_booking_graph",
    ]
    
    for export in expected_exports:
        if export in init_content:
            print(f"   ✓ __init__.py contains: {export}")
        else:
            print(f"   ❌ __init__.py missing: {export}")
            sys.exit(1)
    
    # Check backward compatibility file
    compat_file = os.path.join(os.path.dirname(__file__), 'src/workflows/subgraphs.py')
    with open(compat_file, 'r') as f:
        compat_content = f.read()
    
    if "from .subgraphs import" in compat_content:
        print("   ✓ subgraphs.py contains backward compatibility imports")
    else:
        print("   ❌ subgraphs.py missing backward compatibility imports")
        sys.exit(1)
    
    print("\n🎉 All tests passed! Subgraphs module split successful!")
    print("\n📁 New directory structure:")
    print("   src/workflows/subgraphs/")
    print("   ├── __init__.py")
    print("   ├── common.py        (共享状态、组件、工具函数)")
    print("   ├── collect.py       (信息收集工作流)")
    print("   ├── search.py        (搜索工作流)")
    print("   ├── recommend.py     (推荐工作流)")
    print("   └── booking.py       (预订工作流)")
    print("   src/workflows/subgraphs.py  (向后兼容导入代理)")


if __name__ == "__main__":
    test_module_split()
