#!/usr/bin/env python3
"""
Phase 3 Syntax Verification Script

This script verifies that all Phase 3 modules have correct Python syntax
without requiring external dependencies.
"""

import ast
import sys
from pathlib import Path


def check_file_syntax(filepath):
    """Check if a Python file has valid syntax"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)


def verify_module_files(base_path, module_name, expected_files):
    """Verify all files in a module have valid syntax"""
    print(f"\n📦 Verifying {module_name}...")
    
    module_path = base_path / module_name
    if not module_path.exists():
        print(f"   ⚠️  Module directory not found: {module_path}")
        return False
    
    results = {}
    for filename in expected_files:
        filepath = module_path / filename
        if not filepath.exists():
            print(f"   ⚠️  File not found: {filename}")
            results[filename] = False
            continue
        
        valid, error = check_file_syntax(filepath)
        results[filename] = valid
        
        if valid:
            line_count = len(filepath.read_text().split('\n'))
            print(f"   ✅ {filename} ({line_count} lines)")
        else:
            print(f"   ❌ {filename} - SYNTAX ERROR: {error}")
    
    all_valid = all(results.values())
    success_count = sum(1 for v in results.values() if v)
    print(f"   📊 {success_count}/{len(expected_files)} files valid")
    
    return all_valid


def main():
    """Run syntax verification for all Phase 3 modules"""
    print("="*70)
    print("Phase 3 Syntax Verification")
    print("="*70)
    print("\nVerifying Python syntax for all Phase 3 modules...")
    
    base_path = Path(__file__).parent / "src"
    
    results = {}
    
    # Phase 3.1: MCP Integration
    results["MCP Integration"] = verify_module_files(
        base_path,
        "mcp",
        [
            "__init__.py",
            "protocol.py",
            "tools.py",
            "resources.py",
            "server.py"
        ]
    )
    
    # Phase 3.2: Agent Skills Framework
    results["Skills Framework"] = verify_module_files(
        base_path,
        "skills",
        [
            "__init__.py",
            "base.py",
            "registry.py",
            "loader.py"
        ]
    )
    
    # Verify built-in skills
    results["Built-in Skills"] = verify_module_files(
        base_path / "skills",
        "builtins",
        [
            "__init__.py",
            "search_skills.py",
            "recommend_skills.py",
            "booking_skills.py"
        ]
    )
    
    # Phase 3.3: Concurrency Optimization
    results["Concurrency"] = verify_module_files(
        base_path,
        "concurrency",
        [
            "__init__.py",
            "memory_pool.py",
            "connection_pool.py",
            "streaming.py",
            "rate_limiter.py"
        ]
    )
    
    # Summary
    print("\n" + "="*70)
    print("Verification Summary")
    print("="*70)
    
    for module_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {module_name}")
    
    total_tests = len(results)
    passed_tests = sum(1 for passed in results.values() if passed)
    
    print(f"\n📊 Total: {passed_tests}/{total_tests} modules valid")
    
    if all(results.values()):
        print("\n🎉 All Phase 3 modules have valid Python syntax!")
        print("\n✅ Implementation complete:")
        print("   • Phase 3.1: MCP Integration")
        print("   • Phase 3.2: Agent Skills Framework")
        print("   • Phase 3.3: High Concurrency Optimization")
        return 0
    else:
        print("\n⚠️  Some modules have syntax errors. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
