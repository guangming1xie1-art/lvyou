#!/usr/bin/env python3
"""启动Gradio聊天界面

这个脚本用于启动旅行助手的Gradio聊天界面。
用户可以通过纯对话方式与Agent交互完成旅行规划。
"""

import sys
import os
import logging
from pathlib import Path

# 添加src目录到Python路径
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    from src.gradio_ui.app import create_app
    logger = logging.getLogger(__name__)
    
    def main():
        """主函数"""
        logger.info("🚀 启动旅行助手Gradio界面...")
        
        try:
            # 创建应用
            app = create_app()
            logger.info("✅ Gradio应用创建成功")
            
            # 启动应用
            logger.info("🌐 正在启动服务器...")
            app.launch(
                server_name="0.0.0.0",
                server_port=7860,
                share=False,
                show_error=True,
                inbrowser=False,  # 在容器环境中不自动打开浏览器
                debug=True,
                # 添加自定义CSS
                css="""
                .gradio-container {
                    max-width: 1400px !important;
                    margin: auto !important;
                }
                """
            )
            
        except KeyboardInterrupt:
            logger.info("🛑 用户中断，关闭应用...")
        except Exception as e:
            logger.error(f"❌ 启动失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装所有依赖：")
    print("1. 安装依赖：pip install -r requirements-gradio.txt")
    print("2. 或者：pip install gradio fastapi loguru")
    sys.exit(1)
except Exception as e:
    print(f"❌ 启动失败: {e}")
    sys.exit(1)