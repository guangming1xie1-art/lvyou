"""旅行助手Gradio聊天界面"""

import gradio as gr
import asyncio
import uuid
from typing import List, Tuple, Dict, Any
from .agent_bridge import agent_bridge
from .utils import MediaHandler, format_agent_response

try:
    from utils.logger import app_logger
except ModuleNotFoundError:
    from src.utils.logger import app_logger

async def process_user_message(user_input: str, image: str, audio: str, video: str, history: List[Tuple[str, str]]):
    """处理用户消息并调用Agent"""
    
    if not user_input and not image and not audio and not video:
        return history, ""
    
    request_id = str(uuid.uuid4())
    
    with app_logger.with_request_id(request_id):
        app_logger.info(f"New user message received", user_input=user_input[:100] if user_input else "")
        
        try:
            # 1. 准备附件
            attachments = MediaHandler.prepare_attachments(image, audio, video)
            
            # 2. 发送给Agent
            app_logger.info(f"Calling agent bridge", attachments=list(attachments.keys()))
            
            agent_response = await agent_bridge.chat(user_input, history, attachments)
            
            # 3. 格式化响应
            formatted_response = format_agent_response(agent_response)
            
            # 4. 更新聊天历史
            history.append((user_input, formatted_response))
            
            app_logger.info("Message processed successfully")
            
            # 返回更新后的历史，并清空输入框和上传组件
            return history, "", None, None, None
            
        except Exception as e:
            app_logger.error(f"Failed to process message: {str(e)}", exception=e)
            error_msg = f"抱歉，处理您的请求时出错了：{str(e)}"
            history.append((user_input, error_msg))
            return history, "", None, None, None

def create_chat_interface():
    """创建Gradio聊天界面"""
    
    with gr.Blocks(title="旅行助手", theme=gr.themes.Soft()) as demo:
        # 标题和说明
        gr.Markdown("# 🌍 智能旅行助手")
        gr.Markdown("与AI助手聊天规划你的旅行。支持文字、图片、语音和视频交互。")
        
        # 聊天历史区域
        chatbot = gr.Chatbot(
            label="对话历史",
            height=500,
            show_label=True,
            avatar_images=(None, "🤖"),
            bubble_full_width=False
        )
        
        # 用户输入区域
        with gr.Row():
            msg = gr.Textbox(
                label="你的消息",
                placeholder="例如：我想去东京3月份的旅行，预算5000美元",
                lines=2,
                scale=4
            )
            submit_btn = gr.Button("发送", scale=1, variant="primary")
        
        # 文件上传区域
        with gr.Row():
            image_input = gr.Image(
                label="上传图片",
                type="filepath",
                interactive=True,
                height=150
            )
            audio_input = gr.Audio(
                label="录音/上传音频",
                type="filepath",
                interactive=True
            )
            video_input = gr.Video(
                label="上传视频",
                interactive=True,
                height=150
            )
        
        with gr.Row():
            clear_btn = gr.Button("清除对话历史", variant="secondary")
            status_display = gr.Textbox(
                value="就绪",
                label="Agent状态",
                interactive=False,
                scale=2
            )
        
        # 事件绑定
        submit_event = submit_btn.click(
            process_user_message,
            inputs=[msg, image_input, audio_input, video_input, chatbot],
            outputs=[chatbot, msg, image_input, audio_input, video_input]
        )
        
        msg.submit(
            process_user_message,
            inputs=[msg, image_input, audio_input, video_input, chatbot],
            outputs=[chatbot, msg, image_input, audio_input, video_input]
        )
        
        def clear_history():
            return [], "", None, None, None
            
        clear_btn.click(
            clear_history,
            outputs=[chatbot, msg, image_input, audio_input, video_input]
        )
        
        async def update_status():
            status = await agent_bridge.get_agent_status()
            return status.get("status", "unknown")
        
        # 自动更新状态
        demo.load(
            update_status,
            outputs=[status_display]
        )
        
    return demo

def create_app():
    """供 run_gradio.py 调用的入口函数"""
    return create_chat_interface()
