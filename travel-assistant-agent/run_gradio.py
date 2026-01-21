#!/usr/bin/env python3
"""启动Gradio聊天界面

使用新的 deepagents CompiledSubAgent 架构
"""

import asyncio
import sys
from pathlib import Path
from loguru import logger

# 添加项目路径
current_dir = Path(__file__).parent
src_path = current_dir / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))


def setup_logging():
    """配置日志"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO"
    )
    logger.add(
        "logs/gradio_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="7 days",
        level="DEBUG"
    )


async def start_app():
    """启动Gradio应用"""
    try:
        setup_logging()
        logger.info("🚀 启动旅行助手Gradio界面 (新版架构)...")
        logger.info("=" * 50)
        logger.info("使用 deepagents CompiledSubAgent 架构")
        logger.info("工作流程: 信息收集 → 搜索 → 推荐 → 预订")
        logger.info("=" * 50)
        
        # 导入应用创建函数
        from gradio_ui.app import create_app
        
        # 创建Gradio应用
        app = create_app()
        
        # 启动服务
        logger.info("📦 Gradio服务启动中...")
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True,
            debug=True
        )
        
        logger.info("✅ Gradio界面已启动，访问 http://0.0.0.0:7860")
        
    except KeyboardInterrupt:
        logger.info("收到中断信号，关闭应用...")
    except ImportError as e:
        logger.error(f"导入失败: {e}")
        logger.error("请确保已安装依赖: pip install -r requirements-gradio.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(start_app())
