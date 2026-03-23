"""提示词渲染模块

实现提示词的变量替换功能，支持模板渲染。
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PromptRenderer:
    """提示词渲染器
    
    实现提示词的变量替换功能，支持{{variable}}格式的变量。
    """
    
    def render(self, content: str, variables: Optional[Dict[str, Any]] = None) -> str:
        """
        渲染提示词，替换变量
        
        Args:
            content: 提示词内容，包含{{variable}}格式的变量
            variables: 变量字典
            
        Returns:
            渲染后的提示词
        """
        if not variables:
            return content
        
        rendered = content
        
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            # 处理不同类型的值
            if isinstance(value, (list, tuple)):
                value_str = ", ".join(str(item) for item in value)
            else:
                value_str = str(value)
            
            rendered = rendered.replace(placeholder, value_str)
            logger.debug(f"Replaced variable {{key}} with {{value_str[:50]}...")
        
        # 检查是否还有未替换的变量
        import re
        remaining_vars = re.findall(r'{{(.*?)}}', rendered)
        if remaining_vars:
            logger.warning(f"Unreplaced variables found: {remaining_vars}")
        
        return rendered
    
    def render_with_defaults(self, content: str, variables: Optional[Dict[str, Any]] = None, 
                           defaults: Optional[Dict[str, Any]] = None) -> str:
        """
        渲染提示词，使用默认值处理缺失的变量
        
        Args:
            content: 提示词内容
            variables: 变量字典
            defaults: 默认值字典
            
        Returns:
            渲染后的提示词
        """
        all_vars = {} if defaults is None else defaults.copy()
        if variables:
            all_vars.update(variables)
        
        return self.render(content, all_vars)
    
    def extract_variables(self, content: str) -> list:
        """
        提取提示词中的变量
        
        Args:
            content: 提示词内容
            
        Returns:
            变量列表
        """
        import re
        variables = re.findall(r'{{(.*?)}}', content)
        logger.debug(f"Extracted variables: {variables}")
        return variables


# 全局渲染器实例
prompt_renderer = PromptRenderer()
