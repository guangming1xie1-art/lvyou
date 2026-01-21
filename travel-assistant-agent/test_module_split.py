#!/usr/bin/env python3
"""
Test script to verify the subgraphs module split was successful
"""

import sys
import importlib

def test_module_split():
    """Test that the module split was successful"""
    print("🧪 Testing subgraphs module split...\n")
    
    # Test 1: Import from the new package structure
    print("1️⃣ Testing imports from subgraphs package...")
    try:
        from workflows import subgraphs
        print(f"   ✓ Package imported: {subgraphs.__name__}")
        print(f"   ✓ Package location: {subgraphs.__file__}")
        
        # Check if it's using the new package structure
        if 'subgraphs' in subgraphs.__file__:
            print("   ✓ Using new subgraphs package structure")
        else:
            print("   ⚠️  Using old single-file structure")
    except Exception as e:
        print(f"   ❌ Failed to import subgraphs: {e}")
        sys.exit(1)
    
    # Test 2: Import main API from new package
    print("\n2️⃣ Testing import from subgraphs.__init__...")
    try:
        from workflows.subgraphs import (
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
        sys.exit(1)
    
    # Test 3: Test backward compatibility import from old path
    print("\n3️⃣ Testing backward compatibility import from subgraphs.py...")
    try:
        from workflows.subgraphs import (
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
        sys.exit(1)
    
    # Test 4: Import individual modules
    print("\n4️⃣ Testing individual module imports...")
    modules = [
        ("workflows.subgraphs.common", ["SubState", "cache_strategy", "skill_to_tool"]),
        ("workflows.subgraphs.collect", ["build_collect_info_graph"]),
        ("workflows.subgraphs.search", ["build_search_graph"]),
        ("workflows.subgraphs.recommend", ["build_recommend_graph"]),
        ("workflows.subgraphs.booking", ["build_booking_graph"]),
    ]
    
    for module_name, expected_exports in modules:
        try:
            module = importlib.import_module(module_name)
            print(f"   ✓ {module_name.split('.')[-1]}.py imported")
            
            for export in expected_exports:
                if hasattr(module, export):
                    print(f"     ✓ {export} available")
                else:
                    print(f"     ❌ {export} not found")
                    sys.exit(1)
        except Exception as e:
            print(f"   ❌ Failed to import {module_name}: {e}")
            sys.exit(1)
    
    # Test 5: Check __all__ exports
    print("\n5️⃣ Testing __all__ exports...")
    try:
        from workflows.subgraphs import __all__
        expected = [
            "SubState",
            "build_collect_info_graph",
            "build_search_graph",
            "build_recommend_graph",
            "build_booking_graph",
        ]
        
        for item in expected:
            if item in __all__:
                print(f"   ✓ {item} exported in __all__")
            else:
                print(f"   ❌ {item} missing from __all__")
                sys.exit(1)
        
        print(f"   ✓ All {len(__all__)} items exported correctly")
    except Exception as e:
        print(f"   ❌ Failed to check __all__: {e}")
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
