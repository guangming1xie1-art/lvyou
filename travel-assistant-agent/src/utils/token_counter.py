"""
通用 Token 计数器 Callback
用于统计 LangChain LLM 调用的 Token 用量
"""
from typing import Dict, Any, Optional
from langchain.callbacks.base import BaseCallbackHandler


class TokenCounter(BaseCallbackHandler):
    """
    把当前 Runnable 的用量累加到内部计数器
    支持 OpenAI, Anthropic, Qwen 等各种 LLM 提供商
    """
    
    def __init__(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.cached_tokens = 0  # ← 新增：缓存节省的 tokens
    
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: list[str], **kwargs: Any
    ) -> None:
        """LLM 开始调用时的回调"""
        pass
    
    def on_llm_end(self, response, **kwargs):
        """
        LLM 调用结束时提取 token 用量
        支持多种提供商的响应格式
        """
        # 尝试从不同提供商格式中提取 token 用量
        usage = None
        
        # OpenAI / DeepSeek / 通义千问格式
        if hasattr(response, 'llm_output') and response.llm_output:
            usage = response.llm_output.get('token_usage', {})
        
        # Anthropic Claude 格式
        elif hasattr(response, 'response_metadata'):
            usage = response.response_metadata.get('usage', {})
        
        # 直接从 generations 中提取（某些提供商）
        if not usage and hasattr(response, 'generations'):
            for gen_list in response.generations:
                for gen in gen_list:
                    if hasattr(gen, 'generation_info') and gen.generation_info:
                        usage = gen.generation_info.get('usage', {})
                        if usage:
                            break
                if usage:
                    break
        
        # 累加 tokens
        if usage:
            # OpenAI 格式
            self.prompt_tokens += usage.get('prompt_tokens', 0)
            self.completion_tokens += usage.get('completion_tokens', 0)
            self.total_tokens += usage.get('total_tokens', 0)
            
            # Anthropic 格式兼容
            if 'input_tokens' in usage:
                self.prompt_tokens += usage.get('input_tokens', 0)
            if 'output_tokens' in usage:
                self.completion_tokens += usage.get('output_tokens', 0)
            
            # 统计缓存 tokens（阿里云 DashScope 格式）
            if 'cached_tokens' in usage:
                self.cached_tokens += usage.get('cached_tokens', 0)
    
    def on_llm_error(
        self, error: Exception, **kwargs: Any
    ) -> None:
        """LLM 错误时的回调"""
        pass
    
    def dump(self) -> Dict[str, int]:
        """
        导出当前的 token 统计
        
        Returns:
            Dict 包含 prompt, completion, total 三个字段
        """
        # 如果 total_tokens 为 0，计算它
        if self.total_tokens == 0:
            self.total_tokens = self.prompt_tokens + self.completion_tokens
            
        return {
            "prompt": self.prompt_tokens,
            "completion": self.completion_tokens,
            "cached": self.cached_tokens,
            "total": self.total_tokens
        }
    
    def reset(self):
        """重置计数器"""
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.cached_tokens = 0
