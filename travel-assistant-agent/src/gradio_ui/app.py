"""Gradio Travel Assistant Chat Interface

基于Gradio的旅行助手聊天界面，支持多媒体交互和Agent工作流。
"""

import asyncio
import os
import tempfile
from typing import List, Dict, Any, Optional, Tuple
import gradio as gr
from datetime import datetime
import logging

from .agent_bridge import AgentBridge
from .utils import (
    process_uploaded_file,
    format_agent_response,
    create_chat_message,
    create_multimedia_display,
    format_file_list,
    create_progress_indicator,
    clean_temp_files
)

logger = logging.getLogger(__name__)


class TravelAssistantApp:
    """旅行助手Gradio应用"""
    
    def __init__(self):
        self.agent_bridge = AgentBridge()
        self.current_files = []
        
    def create_interface(self) -> gr.Blocks:
        """创建Gradio界面"""
        
        with gr.Blocks(
            title="🌍 旅行助手Agent",
            fill_height=True
        ) as demo:
            
            # 页面标题
            gr.HTML("""
            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 20px;">
                <h1 style="color: white; margin: 0; font-size: 2.5em;">🌍 智能旅行助手</h1>
                <p style="color: white; margin: 10px 0 0 0; font-size: 1.2em;">让我帮您规划完美的旅程 ✈️</p>
            </div>
            """)
            
            # 状态管理
            chatbot_state = gr.State([])
            stage_state = gr.State("info_collection")
            collected_info_state = gr.State({})
            
            with gr.Row():
                # 左侧聊天区域
                with gr.Column(scale=2):
                    # 聊天界面
                    chatbot = gr.Chatbot(
                        label="💬 对话历史",
                        height=600,
                        avatar_images=(None, None),
                        elem_id="chatbot"
                    )
                    
                    # 输入区域
                    with gr.Row():
                        user_input = gr.Textbox(
                            label="💭 输入您的旅行需求",
                            placeholder="例如：我想计划一个东京之旅，3月份，预算5000美元...",
                            scale=4,
                            lines=3,
                            max_lines=5
                        )
                        
                        with gr.Column(scale=1):
                            send_btn = gr.Button("🚀 发送", variant="primary")
                            clear_btn = gr.Button("🗑️ 清除", variant="secondary")
                    
                    # 文件上传区域
                    gr.HTML("""
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 10px;">
                        <h4 style="margin: 0 0 10px 0; color: #333;">📎 上传多媒体文件</h4>
                    </div>
                    """)
                    
                    with gr.Row():
                        image_upload = gr.Image(
                            label="🖼️ 图片",
                            type="filepath",
                            height=100
                        )
                        audio_upload = gr.Audio(
                            label="🎵 语音",
                            type="filepath"
                        )
                        video_upload = gr.Video(
                            label="🎬 视频", 
                            height=100
                        )
                    
                    # 文件显示区域
                    files_display = gr.HTML(label="上传的文件")
                
                # 右侧信息面板
                with gr.Column(scale=1):
                    gr.HTML("""
                    <div style="background: #e3f2fd; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                        <h3 style="margin: 0 0 15px 0; color: #1976d2;">📊 当前状态</h3>
                    </div>
                    """)
                    
                    # 当前阶段显示
                    current_stage_display = gr.HTML()
                    
                    # 收集的信息显示
                    collected_info_display = gr.HTML()
                    
                    # 进度条
                    progress_display = gr.HTML()
                    
                    # 操作建议
                    gr.HTML("""
                    <div style="background: #f3e5f5; padding: 15px; border-radius: 10px; margin-top: 20px;">
                        <h4 style="margin: 0 0 10px 0; color: #7b1fa2;">💡 快速提示</h4>
                        <ul style="margin: 0; padding-left: 20px; color: #666;">
                            <li>告诉我您的目的地和出行时间</li>
                            <li>上传相关图片获取更精准推荐</li>
                            <li>通过语音输入快速描述需求</li>
                            <li>我会逐步引导您完成旅行规划</li>
                        </ul>
                    </div>
                    """)
            
            # 事件绑定
            send_btn.click(
                self.handle_user_input,
                inputs=[user_input, chatbot_state],
                outputs=[chatbot, chatbot_state, current_stage_display, collected_info_display, progress_display, files_display]
            )
            
            user_input.submit(
                self.handle_user_input,
                inputs=[user_input, chatbot_state],
                outputs=[chatbot, chatbot_state, current_stage_display, collected_info_display, progress_display, files_display]
            )
            
            clear_btn.click(
                self.clear_conversation,
                outputs=[chatbot, chatbot_state, current_stage_display, collected_info_display, progress_display, files_display]
            )
            
            # 文件上传事件
            image_upload.upload(
                self.handle_file_upload,
                inputs=[image_upload, chatbot_state],
                outputs=[chatbot, chatbot_state, files_display]
            )
            
            audio_upload.upload(
                self.handle_file_upload,
                inputs=[audio_upload, chatbot_state],
                outputs=[chatbot, chatbot_state, files_display]
            )
            
            video_upload.upload(
                self.handle_file_upload,
                inputs=[video_upload, chatbot_state],
                outputs=[chatbot, chatbot_state, files_display]
            )
            
            # 初始化界面
            demo.load(
                self.initialize_interface,
                outputs=[chatbot, current_stage_display, collected_info_display, progress_display]
            )
        
        return demo
    
    async def handle_user_input(self, user_message: str, chat_history: List) -> Tuple[List, List, str, str, str, str]:
        """处理用户输入"""
        if not user_message.strip():
            return chat_history, chat_history, "", "", "", ""
        
        try:
            # 添加用户消息到聊天历史
            user_msg = create_chat_message("user", user_message)
            chat_history.append(user_msg)
            
            # 处理用户消息
            response = await self.agent_bridge.process_message(user_message, self.current_files)
            
            # 格式化响应
            formatted_response = format_agent_response(response)
            
            # 添加Agent响应到聊天历史
            agent_msg = create_chat_message("assistant", formatted_response)
            chat_history.append(agent_msg)
            
            # 更新状态显示
            stage_info = self.agent_bridge.get_stage_info()
            
            current_stage_html = self._create_stage_display(stage_info["current_stage"])
            collected_info_html = self._create_info_display(stage_info["collected_info"])
            progress_html = self._create_progress_display(stage_info["current_stage"], stage_info["is_complete"])
            
            # 清除当前文件列表
            self.current_files = []
            
            return chat_history, chat_history, current_stage_html, collected_info_html, progress_html, ""
            
        except Exception as e:
            logger.error(f"处理用户输入时出错: {e}")
            error_msg = f"❌ 处理消息时发生错误: {str(e)}"
            chat_history.append(create_chat_message("assistant", error_msg))
            return chat_history, chat_history, "", "", "", ""
    
    async def handle_file_upload(self, file_path: str, chat_history: List) -> Tuple[List, List, str]:
        """处理文件上传"""
        if not file_path:
            return chat_history, chat_history, ""
        
        try:
            # 获取文件名
            file_name = os.path.basename(file_path)
            
            # 处理文件
            file_info = process_uploaded_file(file_path, file_name)
            
            if "error" in file_info:
                error_msg = f"❌ 文件处理失败: {file_info['error']}"
                chat_history.append(create_chat_message("assistant", error_msg))
                return chat_history, chat_history, ""
            
            # 添加到当前文件列表
            self.current_files.append(file_info)
            
            # 在聊天中显示上传的文件
            multimedia_display = create_multimedia_display(file_info)
            if multimedia_display:
                upload_msg = create_chat_message("user", f"📎 上传了文件: {file_name}")
                chat_history.append(upload_msg)
                
                # 添加文件显示
                display_msg = create_chat_message("assistant", f"已收到文件: {file_name}")
                chat_history.append(display_msg)
            else:
                upload_msg = create_chat_message("user", f"📎 上传了文件: {file_name}")
                chat_history.append(upload_msg)
            
            # 更新文件显示
            files_display = format_file_list(self.current_files)
            
            return chat_history, chat_history, files_display
            
        except Exception as e:
            logger.error(f"处理文件上传时出错: {e}")
            error_msg = f"❌ 文件上传失败: {str(e)}"
            chat_history.append(create_chat_message("assistant", error_msg))
            return chat_history, chat_history, ""
    
    def clear_conversation(self) -> Tuple[List, List, str, str, str, str]:
        """清除对话"""
        try:
            # 清理临时文件
            clean_temp_files()
            
            # 清除Agent状态
            self.agent_bridge.clear_conversation()
            self.current_files = []
            
            # 重置聊天历史
            welcome_msg = create_chat_message(
                "assistant",
                "🌟 欢迎使用智能旅行助手！\n\n我可以帮您：\n• 🗺️ 规划旅行路线\n• 🏨 推荐酒店住宿\n• ✈️ 搜索航班信息\n• 💰 估算旅行预算\n• 📋 制定详细行程\n\n请告诉我您想去哪里旅行，或上传相关图片获取更精准的推荐！"
            )
            
            chat_history = [welcome_msg]
            
            # 重置状态显示
            stage_info = self.agent_bridge.get_stage_info()
            current_stage_html = self._create_stage_display(stage_info["current_stage"])
            collected_info_html = self._create_info_display(stage_info["collected_info"])
            progress_html = self._create_progress_display(stage_info["current_stage"], stage_info["is_complete"])
            
            return chat_history, chat_history, current_stage_html, collected_info_html, progress_html, ""
            
        except Exception as e:
            logger.error(f"清除对话时出错: {e}")
            return chat_history, chat_history, "", "", "", ""
    
    def initialize_interface(self) -> Tuple[List, str, str, str]:
        """初始化界面"""
        welcome_msg = create_chat_message(
            "assistant",
            "🌟 欢迎使用智能旅行助手！\n\n我可以帮您：\n• 🗺️ 规划旅行路线\n• 🏨 推荐酒店住宿\n• ✈️ 搜索航班信息\n• 💰 估算旅行预算\n• 📋 制定详细行程\n\n请告诉我您想去哪里旅行，或上传相关图片获取更精准的推荐！"
        )
        
        chat_history = [welcome_msg]
        
        stage_info = self.agent_bridge.get_stage_info()
        current_stage_html = self._create_stage_display(stage_info["current_stage"])
        collected_info_html = self._create_info_display(stage_info["collected_info"])
        progress_html = self._create_progress_display(stage_info["current_stage"], stage_info["is_complete"])
        
        return chat_history, current_stage_html, collected_info_html, progress_html
    
    def _create_stage_display(self, stage: str) -> str:
        """创建阶段显示"""
        stage_info = {
            "info_collection": {
                "name": "🔍 信息收集",
                "description": "正在收集您的旅行需求",
                "color": "#2196F3"
            },
            "search": {
                "name": "🔎 搜索信息", 
                "description": "正在搜索相关旅行信息",
                "color": "#FF9800"
            },
            "recommendation": {
                "name": "💡 智能推荐",
                "description": "正在生成个性化推荐",
                "color": "#4CAF50"
            },
            "booking": {
                "name": "📋 预订处理",
                "description": "正在处理预订相关事务",
                "color": "#9C27B0"
            }
        }
        
        info = stage_info.get(stage, stage_info["info_collection"])
        
        return f"""
        <div style="background: {info['color']}; color: white; padding: 15px; border-radius: 10px; text-align: center;">
            <h3 style="margin: 0; font-size: 1.2em;">{info['name']}</h3>
            <p style="margin: 5px 0 0 0; font-size: 0.9em;">{info['description']}</p>
        </div>
        """
    
    def _create_info_display(self, collected_info: Dict) -> str:
        """创建收集信息显示"""
        if not collected_info:
            return """
            <div style="background: #f5f5f5; padding: 15px; border-radius: 10px; text-align: center; color: #666;">
                暂无收集信息
            </div>
            """
        
        html = '<div style="background: #f8f9fa; padding: 15px; border-radius: 10px;">'
        html += '<h4 style="margin: 0 0 10px 0; color: #333;">📝 已收集信息</h4>'
        
        for key, value in collected_info.items():
            if value and value != "未指定":
                key_map = {
                    "destination": "📍 目的地",
                    "dates": "📅 旅行时间", 
                    "budget": "💰 预算",
                    "preferences": "🎯 偏好"
                }
                display_key = key_map.get(key, key)
                
                if isinstance(value, list):
                    value = ", ".join(map(str, value))
                
                html += f'<p style="margin: 5px 0;"><strong>{display_key}:</strong> {value}</p>'
        
        html += '</div>'
        return html
    
    def _create_progress_display(self, stage: str, is_complete: bool) -> str:
        """创建进度显示"""
        stage_progress = {
            "info_collection": 25,
            "search": 50, 
            "recommendation": 75,
            "booking": 100
        }
        
        progress = stage_progress.get(stage, 0)
        if is_complete and stage == "info_collection":
            progress = 25
        
        return create_progress_indicator(stage, progress)
    
    def _get_custom_css(self) -> str:
        """获取自定义CSS样式"""
        return """
        .gradio-container {
            max-width: 1400px !important;
            margin: auto !important;
        }
        
        #chatbot {
            border-radius: 15px !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        }
        
        .uploaded-image img {
            border-radius: 8px !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        }
        
        .uploaded-video video {
            border-radius: 8px !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        }
        
        .uploaded-audio audio {
            border-radius: 8px !important;
        }
        
        /* 滚动条样式 */
        .gradio-chatbot {
            scrollbar-width: thin;
            scrollbar-color: #cbd5e0 #f7fafc;
        }
        
        .gradio-chatbot::-webkit-scrollbar {
            width: 8px;
        }
        
        .gradio-chatbot::-webkit-scrollbar-track {
            background: #f7fafc;
            border-radius: 4px;
        }
        
        .gradio-chatbot::-webkit-scrollbar-thumb {
            background: #cbd5e0;
            border-radius: 4px;
        }
        
        .gradio-chatbot::-webkit-scrollbar-thumb:hover {
            background: #a0aec0;
        }
        """


def create_app() -> gr.Blocks:
    """创建并返回Gradio应用"""
    app = TravelAssistantApp()
    return app.create_interface()


# 如果直接运行此文件，启动应用
if __name__ == "__main__":
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        inbrowser=True
    )