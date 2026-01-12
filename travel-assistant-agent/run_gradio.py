#!/usr/bin/env python3
"""启动Gradio聊天界面"""

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

try:
    from src.gradio_ui.app import create_app
    from src.gradio_ui.agent_bridge import agent_bridge
except ImportError as e:
    logger.error(f"导入失败: {e}")
    # 尝试另一种导入方式
    try:
        from gradio_ui.app import create_app
        from gradio_ui.agent_bridge import agent_bridge
    except ImportError:
        logger.error("无法找到 gradio_ui 模块，请检查路径设置")
        sys.exit(1)

async def start_app():
    try:
        logger.info("🚀 启动旅行助手Gradio界面...")
        
        # 创建Gradio应用
        app = create_app()
        
        # 启动服务
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True,
            debug=True
        )
        
    except KeyboardInterrupt:
        logger.info("收到中断信号，关闭应用...")
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await agent_bridge.close()

if __name__ == "__main__":
    asyncio.run(start_app())
