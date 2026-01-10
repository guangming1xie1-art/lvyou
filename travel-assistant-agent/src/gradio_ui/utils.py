"""Gradio UI 工具函数

提供文件处理、多媒体支持和响应格式化等功能。
"""

import os
import tempfile
from typing import Any, Dict, List, Optional, Tuple, Union
import mimetypes
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def validate_multimedia_file(file_path: str, file_name: str) -> Tuple[bool, str]:
    """
    验证上传的多媒体文件
    
    Args:
        file_path: 文件路径
        file_name: 文件名
        
    Returns:
        (is_valid, error_message)
    """
    if not os.path.exists(file_path):
        return False, "文件不存在"
    
    # 检查文件大小 (最大50MB)
    max_size = 50 * 1024 * 1024  # 50MB
    file_size = os.path.getsize(file_path)
    if file_size > max_size:
        return False, f"文件太大，最大支持50MB，当前文件大小: {file_size / 1024 / 1024:.1f}MB"
    
    # 检查文件类型
    allowed_types = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
        'audio': ['.mp3', '.wav', '.m4a', '.aac', '.ogg'],
        'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']
    }
    
    file_ext = os.path.splitext(file_name.lower())[1]
    is_allowed = any(file_ext in ext_list for ext_list in allowed_types.values())
    
    if not is_allowed:
        return False, f"不支持的文件类型: {file_ext}"
    
    return True, ""


def process_uploaded_file(file_path: str, file_name: str) -> Dict[str, Any]:
    """
    处理上传的文件
    
    Args:
        file_path: 文件路径
        file_name: 文件名
        
    Returns:
        包含文件信息的字典
    """
    try:
        # 验证文件
        is_valid, error_msg = validate_multimedia_file(file_path, file_name)
        if not is_valid:
            return {"error": error_msg}
        
        # 获取文件信息
        file_ext = os.path.splitext(file_name.lower())[1]
        file_size = os.path.getsize(file_path)
        mime_type, _ = mimetypes.guess_type(file_name)
        
        # 确定文件类型
        if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            file_type = 'image'
        elif file_ext in ['.mp3', '.wav', '.m4a', '.aac', '.ogg']:
            file_type = 'audio'
        elif file_ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
            file_type = 'video'
        else:
            file_type = 'unknown'
        
        file_info = {
            "original_name": file_name,
            "file_path": file_path,
            "file_type": file_type,
            "mime_type": mime_type,
            "file_size": file_size,
            "file_size_mb": round(file_size / 1024 / 1024, 2),
            "upload_time": datetime.now().isoformat(),
            "processed": True
        }
        
        logger.info(f"Processed file: {file_name} ({file_type}, {file_size} bytes)")
        return file_info
        
    except Exception as e:
        error_msg = f"处理文件时出错: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}


def format_agent_response(response: Dict[str, Any]) -> str:
    """
    格式化Agent响应为用户友好的文本
    
    Args:
        response: Agent响应字典
        
    Returns:
        格式化的文本
    """
    try:
        message = response.get("message", "暂无响应")
        stage = response.get("stage", "unknown")
        
        # 添加阶段指示器
        stage_indicators = {
            "info_collection": "🔍 信息收集",
            "search": "🔎 搜索中",
            "recommendation": "💡 智能推荐",
            "booking": "📋 预订处理"
        }
        
        indicator = stage_indicators.get(stage, "🤖 AI助手")
        
        # 格式化消息
        formatted = f"**{indicator}**\n\n{message}"
        
        # 添加额外信息
        if "next_actions" in response and response["next_actions"]:
            actions = response["next_actions"]
            formatted += f"\n\n**建议操作：**\n"
            for i, action in enumerate(actions, 1):
                formatted += f"{i}. {action}\n"
        
        return formatted
        
    except Exception as e:
        logger.error(f"格式化响应时出错: {e}")
        return response.get("message", "处理响应时出现错误")


def create_chat_message(
    role: str, 
    content: str, 
    timestamp: Optional[str] = None,
    files: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    创建聊天消息格式
    
    Args:
        role: 消息角色 ('user' 或 'assistant')
        content: 消息内容
        timestamp: 时间戳
        files: 关联的文件列表
        
    Returns:
        聊天消息字典
    """
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    
    message = {
        "role": role,
        "content": content,
        "timestamp": timestamp
    }
    
    if files:
        message["files"] = files
    
    return message


def create_multimedia_display(file_info: Dict[str, Any]) -> Optional[str]:
    """
    创建多媒体文件的显示HTML
    
    Args:
        file_info: 文件信息字典
        
    Returns:
        HTML字符串，如果不支持则返回None
    """
    try:
        file_type = file_info.get("file_type")
        file_path = file_info.get("file_path")
        file_name = file_info.get("original_name")
        
        if file_type == "image":
            return f"""
            <div class="uploaded-image">
                <img src="file={file_path}" alt="{file_name}" style="max-width: 300px; max-height: 200px; border-radius: 8px;">
                <p style="font-size: 12px; color: #666; margin-top: 5px;">📷 {file_name}</p>
            </div>
            """
        elif file_type == "audio":
            return f"""
            <div class="uploaded-audio">
                <audio controls style="width: 100%;">
                    <source src="file={file_path}" type="{file_info.get('mime_type', 'audio/mp3')}">
                    您的浏览器不支持音频播放
                </audio>
                <p style="font-size: 12px; color: #666; margin-top: 5px;">🎵 {file_name}</p>
            </div>
            """
        elif file_type == "video":
            return f"""
            <div class="uploaded-video">
                <video controls style="width: 100%; max-width: 400px; border-radius: 8px;">
                    <source src="file={file_path}" type="{file_info.get('mime_type', 'video/mp4')}">
                    您的浏览器不支持视频播放
                </video>
                <p style="font-size: 12px; color: #666; margin-top: 5px;">🎬 {file_name}</p>
            </div>
            """
        
        return None
        
    except Exception as e:
        logger.error(f"创建多媒体显示时出错: {e}")
        return None


def save_conversation_history(conversation: List[Dict], filepath: str) -> bool:
    """
    保存对话历史到文件
    
    Args:
        conversation: 对话历史列表
        filepath: 保存路径
        
    Returns:
        是否保存成功
    """
    try:
        data = {
            "conversation": conversation,
            "export_time": datetime.now().isoformat(),
            "total_messages": len(conversation)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Conversation history saved to {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"保存对话历史失败: {e}")
        return False


def load_conversation_history(filepath: str) -> Optional[List[Dict]]:
    """
    从文件加载对话历史
    
    Args:
        filepath: 文件路径
        
    Returns:
        对话历史列表，失败则返回None
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Conversation history loaded from {filepath}")
        return data.get("conversation", [])
        
    except Exception as e:
        logger.error(f"加载对话历史失败: {e}")
        return None


def format_file_list(files: List[Dict]) -> str:
    """
    格式化文件列表显示
    
    Args:
        files: 文件信息列表
        
    Returns:
        格式化的文件列表文本
    """
    if not files:
        return ""
    
    message = "📎 **已上传文件：**\n\n"
    
    for i, file_info in enumerate(files, 1):
        file_name = file_info.get("original_name", "未知文件")
        file_type = file_info.get("file_type", "unknown")
        file_size = file_info.get("file_size_mb", 0)
        
        # 文件类型emoji
        type_emojis = {
            "image": "🖼️",
            "audio": "🎵", 
            "video": "🎬",
            "unknown": "📄"
        }
        
        emoji = type_emojis.get(file_type, "📄")
        message += f"{i}. {emoji} {file_name} ({file_size} MB)\n"
    
    return message


def create_progress_indicator(stage: str, progress: float) -> str:
    """
    创建进度指示器
    
    Args:
        stage: 当前阶段
        progress: 进度百分比 (0-100)
        
    Returns:
        进度指示器HTML
    """
    stage_names = {
        "info_collection": "信息收集",
        "search": "搜索信息",
        "recommendation": "生成推荐",
        "booking": "预订处理"
    }
    
    stage_name = stage_names.get(stage, stage)
    progress_bar = "█" * int(progress // 10) + "░" * (10 - int(progress // 10))
    
    return f"""
    <div style="background: #f0f0f0; border-radius: 10px; padding: 10px; margin: 10px 0;">
        <div style="font-weight: bold; margin-bottom: 5px;">进度: {stage_name}</div>
        <div style="font-family: monospace;">{progress_bar} {progress:.0f}%</div>
    </div>
    """


def clean_temp_files(pattern: str = "gradio_*") -> int:
    """
    清理临时文件
    
    Args:
        pattern: 文件名模式
        
    Returns:
        清理的文件数量
    """
    cleaned = 0
    temp_dir = tempfile.gettempdir()
    
    try:
        for filename in os.listdir(temp_dir):
            if filename.startswith("gradio_"):
                filepath = os.path.join(temp_dir, filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    cleaned += 1
                    
    except Exception as e:
        logger.error(f"清理临时文件时出错: {e}")
    
    return cleaned