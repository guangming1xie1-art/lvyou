"""Gradio UI的工具函数"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger

class MediaHandler:
    """处理多媒体文件的工具类"""
    
    # 允许的文件类型和大小限制
    ALLOWED_EXTENSIONS = {
        'image': {'jpg', 'jpeg', 'png', 'gif', 'webp'},
        'audio': {'mp3', 'wav', 'ogg', 'm4a'},
        'video': {'mp4', 'avi', 'mov', 'mkv'}
    }
    
    MAX_FILE_SIZES = {
        'image': 10 * 1024 * 1024,  # 10MB
        'audio': 50 * 1024 * 1024,  # 50MB
        'video': 100 * 1024 * 1024  # 100MB
    }
    
    @staticmethod
    def validate_file(file_path: Optional[str], file_type: str) -> bool:
        """验证上传的文件
        
        Args:
            file_path: 文件路径
            file_type: 文件类型 ('image', 'audio', 'video')
        
        Returns:
            是否有效
        """
        if not file_path:
            return True  # 可选文件，None是允许的
        
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在: {file_path}")
            return False
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size > MediaHandler.MAX_FILE_SIZES.get(file_type, 50 * 1024 * 1024):
            logger.warning(f"文件过大: {file_path} ({file_size} bytes)")
            return False
        
        # 检查文件扩展名
        ext = Path(file_path).suffix.lstrip('.').lower()
        if ext not in MediaHandler.ALLOWED_EXTENSIONS.get(file_type, set()):
            logger.warning(f"不支持的文件类型: {ext}")
            return False
        
        return True
    
    @staticmethod
    def prepare_attachments(
        image_path: Optional[str],
        audio_path: Optional[str],
        video_path: Optional[str]
    ) -> Dict[str, Any]:
        """准备附件信息供Agent使用
        
        Args:
            image_path: 图片路径
            audio_path: 音频路径
            video_path: 视频路径
        
        Returns:
            附件字典
        """
        attachments = {}
        
        if image_path and MediaHandler.validate_file(image_path, 'image'):
            attachments['image'] = image_path
            logger.info(f"准备图片附件: {image_path}")
        
        if audio_path and MediaHandler.validate_file(audio_path, 'audio'):
            attachments['audio'] = audio_path
            logger.info(f"准备音频附件: {audio_path}")
        
        if video_path and MediaHandler.validate_file(video_path, 'video'):
            attachments['video'] = video_path
            logger.info(f"准备视频附件: {video_path}")
        
        return attachments

def format_agent_response(response: str) -> str:
    """格式化Agent的响应文本
    
    Args:
        response: Agent的原始响应
    
    Returns:
        格式化后的响应
    """
    # 如果响应包含markdown，Gradio会自动渲染
    return response


def validate_multimedia_file(file_path: Optional[str], file_type: str) -> bool:
    """验证多媒体文件
    
    Args:
        file_path: 文件路径
        file_type: 文件类型 ('image', 'audio', 'video')
    
    Returns:
        是否有效
    """
    return MediaHandler.validate_file(file_path, file_type)


# 为了向后兼容，保留一些可能被其他地方调用的函数名（如果必要）
def create_chat_message(role, content):
    return {"role": role, "content": content}

def clean_temp_files():
    import tempfile
    import shutil
    # 简单实现
    pass
