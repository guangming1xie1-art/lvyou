from typing import Dict, Optional, Any, List
import logging
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

class PromptCacheManager:
    """管理 Prompt Cache 的生命周期"""
    
    def __init__(self):
        self.caches: Dict[str, str] = {}  # { "search_plan": CACHE_ID, ... }
    
    async def get_or_create_cache(self,
        cache_key: str,
        llm: Any,
        system_prompt: str,
        few_shots: str,
        tools_text: str
    ) -> Optional[str]:
        """
        获取或创建缓存 ID
        
        首次调用：create_cache=True，阿里云返回 cache_id
        后续调用：直接返回保存的 cache_id（无需重复创建）
        
        Args:
            cache_key: 缓存键，如 "search_plan", "search_execute", "recommend_plan", "recommend_execute"
            llm: LangChain LLM 对象
            system_prompt: 系统提示词（固定内容）
            few_shots: Few-shot 示例（固定内容）
            tools_text: 工具列表文本
        
        Returns:
            缓存 ID（用于后续请求）
        """
        # 如果已有缓存，直接返回（避免重复创建）
        if cache_key in self.caches:
            logger.info(f"✅ Prompt cache REUSE: {cache_key}")
            return self.caches[cache_key]
        
        # 第一次创建缓存
        logger.info(f"📝 Creating prompt cache for: {cache_key}")
        
        # 组合系统 prompt、few-shots、工具列表
        cache_content = f"{system_prompt}\n\n{few_shots}\n\n工具列表：\n{tools_text}"
        cache_msg = [{"role": "system", "content": cache_content}]
        
        try:
            # 调用 LLM，开启缓存创建
            # 注意：这里需要 LLM 支持 extra_body 或者类似机制
            # 在阿里云 DashScope 中通常是通过 extra_body 传递 create_cache
            if hasattr(llm, 'invoke'):
                # resp = llm.invoke(cache_msg, extra_body={"create_cache": True})
                resp = llm.invoke(cache_msg)
                
                # 尝试从 response_metadata 中获取 cache_id
                cache_id = resp.response_metadata.get("cache_id")
                
                if cache_id:
                    self.caches[cache_key] = cache_id
                    logger.info(f"✅ Prompt cache created: {cache_key} -> {cache_id}")
                    return cache_id
                else:
                    logger.warning(f"⚠️ Failed to create cache for {cache_key} - no cache_id in metadata")
                    return None
            else:
                logger.warning(f"⚠️ LLM object does not have invoke method")
                return None
        except Exception as e:
            logger.error(f"❌ Error creating prompt cache: {e}")
            return None
    
    async def invoke_with_cache(self,
        llm: Any,
        cache_id: str,
        user_query: str,
        counter: Any = None
    ) -> tuple:
        """
        使用缓存调用 LLM
        
        Args:
            llm: LLM 对象
            cache_id: 之前创建的缓存 ID
            user_query: 用户查询（变动部分）
            counter: TokenCounter 实例（可选）
        
        Returns:
            (response_content, cached_tokens)
        """
        msg = [{"role": "user", "content": user_query}]
        
        try:
            # 使用缓存 ID 调用 LLM
            resp = llm.invoke(msg, extra_body={"cache_id": cache_id})
            
            usage = resp.response_metadata.get("usage", {})
            cached_tokens = usage.get("cached_tokens", 0)
            
            if cached_tokens > 0:
                prompt_tokens = usage.get("prompt_tokens", 1)
                saved_percentage = (cached_tokens / (cached_tokens + prompt_tokens)) * 100
                logger.info(f"✅ Cache HIT! Saved {cached_tokens} tokens ({saved_percentage:.1f}% of system prompt)")
                
                if counter and hasattr(counter, 'cached_tokens'):
                    counter.cached_tokens += cached_tokens
            
            return resp.content, cached_tokens
        
        except Exception as e:
            logger.error(f"❌ Error invoking with cache: {e}")
            return None, 0

# 全局单例
_prompt_cache_manager: Optional[PromptCacheManager] = None

def get_prompt_cache_manager() -> PromptCacheManager:
    """获取全局 PromptCacheManager 实例"""
    global _prompt_cache_manager
    if _prompt_cache_manager is None:
        _prompt_cache_manager = PromptCacheManager()
    return _prompt_cache_manager
