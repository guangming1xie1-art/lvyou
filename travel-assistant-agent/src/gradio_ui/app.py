"""旅行助手Gradio聊天界面

使用新的 deepagents CompiledSubAgent 架构
"""

import gradio as gr
import asyncio
import json
from typing import List, Tuple, Dict, Any, Optional
from loguru import logger

from ..workflows.main_workflow import run_main_workflow_async
from .utils import MediaHandler


class AgentBridge:
    """本地Agent桥接层，直接调用工作流"""

    def __init__(self):
        self.logger = logger

    async def chat(
        self,
        user_input: str,
        history: List[Tuple[str, str]],
        attachments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """调用主工作流处理用户消息
        
        Args:
            user_input: 用户输入的消息
            history: 对话历史（list of (user, assistant) tuples）
            attachments: 附件信息（图片、音频、视频等）
        
        Returns:
            包含完整工作流结果的字典
        """
        try:
            # 构建请求消息（包含历史）
            formatted_history = []
            for user_msg, assistant_msg in history:
                if user_msg:
                    formatted_history.append({"role": "user", "content": user_msg})
                if assistant_msg:
                    formatted_history.append({"role": "assistant", "content": assistant_msg})

            # 构建完整输入消息
            full_message = user_input
            if attachments:
                attachment_info = ", ".join([f"{k}: {v}" for k, v in attachments.items()])
                full_message = f"{user_input}\n\n[附件: {attachment_info}]"

            self.logger.info(f"Calling main workflow with message: {full_message[:100]}...")

            # 调用主工作流
            result = await run_main_workflow_async(full_message)

            self.logger.info("Main workflow completed successfully")
            
            return result

        except Exception as e:
            self.logger.error(f"Workflow failed: {e}")
            raise

    async def close(self):
        """清理资源"""
        pass


# 全局Agent桥接实例
agent_bridge = AgentBridge()


def format_workflow_result(result: Dict[str, Any]) -> str:
    """格式化工作流结果用于显示
    
    Args:
        result: 工作流返回的结果字典
    
    Returns:
        格式化的Markdown字符串
    """
    output_parts = []
    
    # 最终响应
    final_response = result.get("final_response", "")
    if final_response:
        output_parts.append("## 🤖 最终响应\n")
        output_parts.append(final_response)
        output_parts.append("\n")
    
    # 各阶段结果
    collected_info = result.get("collected_info")
    search_results = result.get("search_results")
    recommendations = result.get("recommendations")
    booking_confirmation = result.get("booking_confirmation")
    
    # 收集的信息
    if collected_info and isinstance(collected_info, dict) and not collected_info.get("error"):
        output_parts.append("\n---\n## 📋 收集的信息\n")
        if isinstance(collected_info, dict):
            for key, value in collected_info.items():
                output_parts.append(f"- **{key}**: {value}")
        else:
            output_parts.append(str(collected_info))
        output_parts.append("\n")
    
    # 搜索结果
    if search_results and isinstance(search_results, dict) and not search_results.get("error"):
        output_parts.append("\n---\n## 🔍 搜索结果\n")
        if isinstance(search_results, dict):
            for key, value in search_results.items():
                if isinstance(value, list):
                    output_parts.append(f"\n### {key}")
                    for item in value[:5]:  # 最多显示5项
                        output_parts.append(f"- {item}")
                else:
                    output_parts.append(f"- **{key}**: {value}")
        else:
            output_parts.append(str(search_results))
        output_parts.append("\n")
    
    # 推荐结果
    if recommendations and isinstance(recommendations, dict) and not recommendations.get("error"):
        output_parts.append("\n---\n## 💡 推荐方案\n")
        if isinstance(recommendations, dict):
            for key, value in recommendations.items():
                if isinstance(value, list):
                    output_parts.append(f"\n### {key}")
                    for idx, item in enumerate(value[:5], 1):
                        output_parts.append(f"{idx}. {item}")
                else:
                    output_parts.append(f"- **{key}**: {value}")
        else:
            output_parts.append(str(recommendations))
        output_parts.append("\n")
    
    # 预订确认
    if booking_confirmation and isinstance(booking_confirmation, dict) and not booking_confirmation.get("error"):
        output_parts.append("\n---\n## ✅ 预订确认\n")
        if isinstance(booking_confirmation, dict):
            for key, value in booking_confirmation.items():
                output_parts.append(f"- **{key}**: {value}")
        else:
            output_parts.append(str(booking_confirmation))
        output_parts.append("\n")
    
    # Token使用情况
    usage = result.get("total_usage", {})
    if usage and isinstance(usage, dict):
        output_parts.append("\n---\n## 📊 Token使用统计\n")
        output_parts.append(f"- **Prompt Tokens**: {usage.get('prompt', 0)}")
        output_parts.append(f"- **Completion Tokens**: {usage.get('completion', 0)}")
        output_parts.append(f"- **Total Tokens**: {usage.get('total', 0)}")
        output_parts.append("\n")
    
    return "\n".join(output_parts)


def format_simple_response(result: Dict[str, Any]) -> str:
    """简化版响应格式化（仅显示最终响应）"""
    final_response = result.get("final_response", "")
    if not final_response:
        final_response = "处理完成，但没有返回响应内容。"
    return final_response


async def process_user_message(
    user_input: str,
    image: str,
    audio: str,
    video: str,
    history: List[Tuple[str, str]],
    use_detailed_view: bool = True
):
    """处理用户消息并调用工作流"""
    
    if not user_input and not image and not audio and not video:
        return history, "", None, None, None
    
    logger.info(f"New user message received: {user_input[:100]}...")
    
    try:
        # 1. 准备附件
        attachments = MediaHandler.prepare_attachments(image, audio, video)
        
        if attachments:
            logger.info(f"Attachments prepared: {list(attachments.keys())}")
        
        # 2. 调用工作流
        logger.info("Calling main workflow...")
        result = await agent_bridge.chat(user_input, history, attachments)
        
        # 3. 格式化响应
        if use_detailed_view:
            formatted_response = format_workflow_result(result)
        else:
            formatted_response = format_simple_response(result)
        
        # 4. 更新聊天历史
        history.append((user_input, formatted_response))
        
        logger.info("Message processed successfully")
        
        # 返回更新后的历史，并清空输入框和上传组件
        return history, "", None, None, None
        
    except Exception as e:
        logger.error(f"Failed to process message: {str(e)}", exception=True)
        error_msg = f"抱歉，处理您的请求时出错了：{str(e)}"
        history.append((user_input, error_msg))
        return history, "", None, None, None


def create_chat_interface():
    """创建Gradio聊天界面"""
    
    with gr.Blocks(title="旅行助手 - New Architecture", theme=gr.themes.Soft()) as demo:
        # 标题和说明
        gr.Markdown("# 🌍 智能旅行助手 (新版架构)")
        gr.Markdown("基于 deepagents CompiledSubAgent 架构，支持完整的旅游规划流程。")
        gr.Markdown("**工作流程**: 信息收集 → 搜索 → 推荐 → 预订")
        
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
            detailed_checkbox = gr.Checkbox(
                label="详细显示",
                value=True,
                info="显示每个阶段的详细输出"
            )
            status_display = gr.Textbox(
                value="就绪",
                label="Agent状态",
                interactive=False,
                scale=2
            )
        
        # 事件绑定
        submit_event = submit_btn.click(
            process_user_message,
            inputs=[msg, image_input, audio_input, video_input, chatbot, detailed_checkbox],
            outputs=[chatbot, msg, image_input, audio_input, video_input]
        )
        
        msg.submit(
            process_user_message,
            inputs=[msg, image_input, audio_input, video_input, chatbot, detailed_checkbox],
            outputs=[chatbot, msg, image_input, audio_input, video_input]
        )
        
        def clear_history():
            return [], "", None, None, None
            
        clear_btn.click(
            clear_history,
            outputs=[chatbot, msg, image_input, audio_input, video_input]
        )
        
        def get_status():
            return "✅ 在线 (新架构)"
        
        # 初始化状态
        demo.load(
            get_status,
            outputs=[status_display]
        )
        
    return demo


def create_app():
    """供 run_gradio.py 调用的入口函数"""
    return create_chat_interface()
