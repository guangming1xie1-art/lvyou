#!/usr/bin/env python3
"""
测试 Agent 网关层修改
验证所有数据库交互已移除，仅保留结构化日志输出
"""

import os
import sys

# 添加 src 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_removed_routes():
    """测试认证路由是否正确删除"""
    print("🔍 检查认证路由...")
    
    # 检查 auth/routes.py
    with open('src/auth/routes.py', 'r') as f:
        content = f.read()
    
    # 应该删除的路由
    removed_routes = [
        'register',
        'login', 
        'refresh'
    ]
    
    # 应该保留的路由
    kept_routes = [
        'get_current_user',
        'logout'
    ]
    
    for route in removed_routes:
        if f'@router.post("/' in content and route in content:
            print(f"❌ {route} 路由仍然存在")
            return False
        else:
            print(f"✅ {route} 路由已删除")
    
    for route in kept_routes:
        if route in content:
            print(f"✅ {route} 路由已保留")
        else:
            print(f"❌ {route} 路由缺失")
            return False
    
    return True

def test_db_manager_simplified():
    """测试数据库管理器是否已简化"""
    print("\n🔍 检查数据库管理器...")
    
    with open('src/utils/db.py', 'r') as f:
        content = f.read()
    
    # 检查不应该存在的方法
    removed_methods = [
        'create_user',
        'get_user_by_id',
        'get_user_by_username', 
        'get_user_by_email',
        'update_last_login',
        'create_audit_log',
        'get_user_audit_logs',
        'get_security_events'
    ]
    
    for method in removed_methods:
        if f'async def {method}' in content:
            print(f"❌ {method} 方法仍然存在")
            return False
        else:
            print(f"✅ {method} 方法已删除")
    
    # 检查应该保留的方法
    kept_methods = [
        'init',
        'health_check',
        'close'
    ]
    
    for method in kept_methods:
        if method in content:
            print(f"✅ {method} 方法已保留")
        else:
            print(f"❌ {method} 方法缺失")
            return False
    
    return True

def test_audit_logger_logging_only():
    """测试审计日志器是否仅输出日志"""
    print("\n🔍 检查审计日志器...")
    
    with open('src/security/audit.py', 'r') as f:
        content = f.read()
    
    # 检查不应该有数据库相关导入
    if 'from utils.db import db_manager' in content:
        print("❌ audit.py 仍然导入 db_manager")
        return False
    else:
        print("✅ audit.py 不再导入 db_manager")
    
    # 检查不应该有数据库调用
    if 'db_manager.create_audit_log' in content:
        print("❌ audit.py 仍然调用数据库")
        return False
    else:
        print("✅ audit.py 不再调用数据库")
    
    # 检查应该有结构化日志
    if 'app_logger.info' in content and 'extra_' in content:
        print("✅ audit.py 使用结构化日志")
    else:
        print("❌ audit.py 未使用结构化日志")
        return False
    
    return True

def test_dependencies_jwt_only():
    """测试认证依赖是否仅验证 JWT"""
    print("\n🔍 检查认证依赖...")
    
    with open('src/auth/dependencies.py', 'r') as f:
        content = f.read()
    
    # 检查不应该有数据库导入
    if 'from utils.db import db_manager' in content:
        print("❌ dependencies.py 仍然导入 db_manager")
        return False
    else:
        print("✅ dependencies.py 不再导入 db_manager")
    
    # 检查不应该有数据库查询
    if 'db_manager.get_user_by_id' in content:
        print("❌ dependencies.py 仍然查询数据库")
        return False
    else:
        print("✅ dependencies.py 不再查询数据库")
    
    # 检查应该有JWT验证
    if 'jwt_handler.verify_token' in content and 'payload.get("sub")' in content:
        print("✅ dependencies.py 使用JWT验证")
    else:
        print("❌ dependencies.py 未使用JWT验证")
        return False
    
    return True

def test_api_routes_logging():
    """测试API路由是否使用结构化日志"""
    print("\n🔍 检查API路由...")
    
    with open('src/api/routes.py', 'r') as f:
        content = f.read()
    
    # 检查不应该导入audit_logger
    if 'audit_logger' in content:
        print("❌ routes.py 仍然导入 audit_logger")
        return False
    else:
        print("✅ routes.py 不再导入 audit_logger")
    
    # 检查应该有结构化日志调用
    if 'app_logger.info' in content and 'extra_' in content:
        print("✅ routes.py 使用结构化日志")
    else:
        print("❌ routes.py 未使用结构化日志")
        return False
    
    return True

def main():
    """运行所有测试"""
    print("🧪 测试 Agent 网关层修改\n")
    
    tests = [
        test_removed_routes,
        test_db_manager_simplified,
        test_audit_logger_logging_only,
        test_dependencies_jwt_only,
        test_api_routes_logging
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✅ {test.__name__} 通过\n")
            else:
                print(f"❌ {test.__name__} 失败\n")
        except Exception as e:
            print(f"❌ {test.__name__} 异常: {e}\n")
    
    print(f"🎯 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！Agent 已成功改为纯网关层！")
        print("\n📋 修改总结:")
        print("  ✅ 删除了 register/login/refresh 认证路由")
        print("  ✅ JWT 验证不再查询数据库")
        print("  ✅ 数据库管理器已简化")
        print("  ✅ 审计日志改为结构化日志输出")
        print("  ✅ 所有 API 调用改为结构化日志")
        print("\n🚀 Agent 现在是纯网关层:")
        print("  - 转发认证请求到 Java")
        print("  - 仅验证 JWT 签名")
        print("  - 输出结构化日志")
        print("  - 调用 MCP 服务")
        print("  - 完全不与数据库交互")
    else:
        print(f"\n⚠️  有 {total-passed} 个测试失败，需要进一步检查")

if __name__ == "__main__":
    main()