#!/usr/bin/env python3
"""
测试结构化日志系统

运行此脚本以验证结构化日志功能
"""
import sys
import os
import json

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 直接导入以避免循环依赖
import importlib.util
spec = importlib.util.spec_from_file_location(
    "structured_logger",
    os.path.join(os.path.dirname(__file__), 'src/utils/structured_logger.py')
)
structured_logger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(structured_logger)

StructuredLogger = structured_logger.StructuredLogger
get_app_logger = structured_logger.get_app_logger
get_error_logger = structured_logger.get_error_logger
set_request_context = structured_logger.set_request_context
clear_request_context = structured_logger.clear_request_context
get_request_id = structured_logger.get_request_id

# 日志配置
LOGGING_CONFIG = {
    "log_level": "INFO",
    "log_dir": "test_logs",
    "app_log_file": "test_app.log",
    "access_log_file": "test_access.log",
    "error_log_file": "test_error.log",
    "enable_console": True,
}


def test_basic_logging():
    """测试基本日志功能"""
    print("=" * 60)
    print("测试1: 基本日志功能")
    print("=" * 60)
    
    # 初始化日志系统
    StructuredLogger.setup_logging(
        log_level="INFO",
        log_dir="test_logs",
        app_log_file="test_app.log",
        access_log_file="test_access.log",
        error_log_file="test_error.log",
        enable_console=True
    )
    
    logger = get_app_logger("test_module")
    
    # 测试不同级别的日志
    logger.info("这是一条INFO日志")
    logger.warning("这是一条WARNING日志")
    logger.debug("这是一条DEBUG日志（可能不显示，取决于日志级别）")
    
    print("✓ 基本日志测试完成\n")


def test_request_context():
    """测试请求上下文追踪"""
    print("=" * 60)
    print("测试2: 请求上下文追踪")
    print("=" * 60)
    
    logger = get_app_logger("test_context")
    
    # 设置请求上下文
    set_request_context(
        request_id="test-req-12345",
        user_id="user-001"
    )
    
    print(f"当前请求ID: {get_request_id()}")
    
    logger.info("测试请求上下文日志")
    logger.info(
        "带额外字段的日志",
        extra={
            "extra_action": "test_action",
            "extra_status": "success"
        }
    )
    
    clear_request_context()
    print("✓ 请求上下文测试完成\n")


def test_error_logging():
    """测试错误日志和异常追踪"""
    print("=" * 60)
    print("测试3: 错误日志和异常追踪")
    print("=" * 60)
    
    error_logger = get_error_logger()
    
    # 设置请求上下文
    set_request_context(
        request_id="test-error-req-67890",
        user_id="user-002"
    )
    
    try:
        # 模拟一个错误
        result = 1 / 0
    except Exception as e:
        error_logger.error(
            "发生了一个测试错误",
            exc_info=True,
            extra={
                "extra_operation": "division",
                "extra_input": "1/0"
            }
        )
    
    clear_request_context()
    print("✓ 错误日志测试完成\n")


def test_structured_format():
    """测试日志的结构化格式"""
    print("=" * 60)
    print("测试4: 验证日志格式")
    print("=" * 60)
    
    # 读取日志文件并验证JSON格式
    try:
        with open("test_logs/test_app.log", "r") as f:
            lines = f.readlines()
            
        print(f"读取到 {len(lines)} 条日志记录")
        
        # 验证每行都是有效的JSON
        valid_count = 0
        for i, line in enumerate(lines):
            try:
                log_entry = json.loads(line.strip())
                valid_count += 1
                
                # 打印第一条日志的结构
                if i == 0:
                    print("\n示例日志结构:")
                    print(json.dumps(log_entry, indent=2, ensure_ascii=False))
                    print()
                
                # 验证必需字段
                required_fields = ['timestamp', 'level', 'logger', 'message', 'module', 'function']
                missing_fields = [f for f in required_fields if f not in log_entry]
                
                if missing_fields:
                    print(f"⚠ 日志 {i+1} 缺少字段: {missing_fields}")
                    
            except json.JSONDecodeError as e:
                print(f"✗ 日志 {i+1} JSON格式无效: {line.strip()}")
        
        print(f"✓ {valid_count}/{len(lines)} 条日志格式有效")
        
    except FileNotFoundError:
        print("✗ 未找到日志文件")
    
    print()


def test_log_files():
    """测试日志文件分类"""
    print("=" * 60)
    print("测试5: 日志文件分类")
    print("=" * 60)
    
    # 检查日志文件是否被创建
    log_files = [
        "test_logs/test_app.log",
        "test_logs/test_access.log",
        "test_logs/test_error.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"✓ {log_file} 存在 (大小: {size} bytes)")
        else:
            print(f"✗ {log_file} 不存在")
    
    print()


def cleanup():
    """清理测试日志"""
    print("=" * 60)
    print("清理测试日志文件")
    print("=" * 60)
    
    import shutil
    if os.path.exists("test_logs"):
        shutil.rmtree("test_logs")
        print("✓ 测试日志已清理")
    print()


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("结构化日志系统测试")
    print("=" * 60 + "\n")
    
    try:
        test_basic_logging()
        test_request_context()
        test_error_logging()
        test_structured_format()
        test_log_files()
        
        print("=" * 60)
        print("✓ 所有测试完成！")
        print("=" * 60)
        
        # 询问是否清理
        response = input("\n是否清理测试日志文件？(y/n): ")
        if response.lower() == 'y':
            cleanup()
        else:
            print("测试日志保留在 test_logs/ 目录中")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
