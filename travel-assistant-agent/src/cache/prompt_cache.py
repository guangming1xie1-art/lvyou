"""
Prompt缓存管理模块
提供系统提示、RAG上下文和工具定义的缓存功能
支持Claude Prompt Cache机制
"""
from typing import Optional, Dict, Any, List
from langchain_core.messages import BaseMessage, SystemMessage
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)


class PromptCacheManager:
    """Prompt缓存管理器（用于Claude和其他支持缓存的模型）"""
    
    # Claude Prompt Cache的成本节省比例
    CACHE_SAVINGS_RATIO = 0.75  # 缓存读取成本为常规成本的25%，节省75%
    
    def __init__(
        self,
        enable_cache: bool = True,
        cache_dir: Optional[str] = None
    ):
        """
        初始化Prompt缓存管理器
        
        Args:
            enable_cache: 是否启用缓存
            cache_dir: 缓存目录（用于持久化缓存）
        """
        self.enable_cache = enable_cache
        self.cache_dir = cache_dir or os.getenv("PROMPT_CACHE_DIR", ".prompt_cache")
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self._ensure_cache_dir()
        
        # TTL配置（秒）
        self.ttl_config = {
            "system_prompt": int(os.getenv("SYSTEM_PROMPT_CACHE_TTL", "86400")),  # 24小时
            "tool_definitions": int(os.getenv("TOOL_DEFINITIONS_CACHE_TTL", "86400")),  # 24小时
            "rag_context": int(os.getenv("RAG_CONTEXT_CACHE_TTL", "3600")),  # 1小时
        }
    
    def _ensure_cache_dir(self):
        """确保缓存目录存在"""
        if self.cache_dir and not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.info(f"Created prompt cache directory: {self.cache_dir}")
    
    def _get_cache_path(self, key: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{key}.cache")
    
    def _is_expired(self, cache_item: Dict[str, Any]) -> bool:
        """检查缓存是否过期"""
        if "expires_at" not in cache_item:
            return True
        return datetime.now() > cache_item["expires_at"]
    
    def _cache_item(
        self,
        key: str,
        content: str,
        ttl: int,
        cache_type: str = "general"
    ) -> Dict[str, Any]:
        """
        缓存单个项目
        
        Args:
            key: 缓存键
            content: 缓存内容
            ttl: 过期时间（秒）
            cache_type: 缓存类型
            
        Returns:
            缓存项信息
        """
        if not self.enable_cache:
            return {"cached": False, "reason": "cache_disabled"}
        
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        cache_item = {
            "content": content,
            "cache_type": cache_type,
            "created_at": datetime.now(),
            "expires_at": expires_at,
            "ttl": ttl,
            "size": len(content),
        }
        
        # 内存缓存
        self.memory_cache[key] = cache_item
        
        # 持久化缓存
        try:
            import json
            cache_path = self._get_cache_path(key)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_item, f, ensure_ascii=False, default=str)
            logger.debug(f"Cached item: {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.warning(f"Failed to persist cache: {e}")
        
        return cache_item
    
    def cache_system_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        缓存系统提示词
        
        Args:
            prompt: 系统提示词内容
            
        Returns:
            缓存结果信息
        """
        key = self.generate_system_prompt_key()
        return self._cache_item(
            key, prompt,
            ttl=self.ttl_config["system_prompt"],
            cache_type="system_prompt"
        )
    
    def cache_rag_context(self, context: str, query: str) -> Dict[str, Any]:
        """
        缓存RAG上下文
        
        Args:
            context: RAG上下文内容
            query: 关联的查询
            
        Returns:
            缓存结果信息
        """
        key = self.generate_rag_context_key(query)
        return self._cache_item(
            key, context,
            ttl=self.ttl_config["rag_context"],
            cache_type="rag_context"
        )
    
    def cache_tool_definitions(self, tools: List[Dict]) -> Dict[str, Any]:
        """
        缓存工具定义
        
        Args:
            tools: 工具定义列表
            
        Returns:
            缓存结果信息
        """
        import json
        key = self.generate_tool_definition_key()
        tools_str = json.dumps(tools, ensure_ascii=False)
        return self._cache_item(
            key, tools_str,
            ttl=self.ttl_config["tool_definitions"],
            cache_type="tool_definitions"
        )
    
    def get_cache(self, key: str) -> Optional[str]:
        """
        获取缓存项目
        
        Args:
            key: 缓存键
            
        Returns:
            缓存内容，不存在返回None
        """
        # 首先检查内存缓存
        if key in self.memory_cache:
            cache_item = self.memory_cache[key]
            if not self._is_expired(cache_item):
                logger.debug(f"Memory cache hit: {key}")
                return cache_item["content"]
            else:
                del self.memory_cache[key]
        
        # 尝试从持久化缓存加载
        try:
            import json
            cache_path = self._get_cache_path(key)
            if os.path.exists(cache_path):
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_item = json.load(f)
                
                expires_at = datetime.fromisoformat(cache_item["expires_at"])
                if datetime.now() < expires_at:
                    # 重新加载到内存
                    self.memory_cache[key] = cache_item
                    logger.debug(f"Disk cache hit: {key}")
                    return cache_item["content"]
                else:
                    # 过期，删除缓存文件
                    os.remove(cache_path)
                    logger.debug(f"Cache expired: {key}")
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
        
        return None
    
    def get_system_prompt(self) -> Optional[str]:
        """获取缓存的系统提示"""
        return self.get_cache(self.generate_system_prompt_key())
    
    def get_rag_context(self, query: str) -> Optional[str]:
        """获取缓存的RAG上下文"""
        return self.get_cache(self.generate_rag_context_key(query))
    
    def get_tool_definitions(self) -> Optional[str]:
        """获取缓存的工具定义"""
        return self.get_cache(self.generate_tool_definition_key())
    
    def build_cached_messages(
        self,
        system_prompt: str,
        rag_context: Optional[str] = None,
        user_message: str = "",
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        构建带缓存标记的消息列表（用于Claude API）
        
        Args:
            system_prompt: 系统提示
            rag_context: RAG上下文（可选）
            user_message: 用户消息
            use_cache: 是否启用缓存
            
        Returns:
            格式化的消息列表
        """
        messages = []
        
        if use_cache:
            # 系统提示 - 启用缓存（# 使用磐古的API风格）
            system_content = [
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ]
            messages.append({
                "role": "user",
                "content": system_content
            })
            
            # RAG上下文 - 启用缓存
            if rag_context:
                rag_content = [
                    {
                        "type": "text",
                        "text": f"相关背景信息：\n{rag_context}",
                        "cache_control": {"type": "ephemeral"}
                    }
                ]
                messages.append({
                    "role": "user",
                    "content": rag_content
                })
            
            # 用户消息 - 不缓存
            messages.append({
                "role": "user",
                "content": user_message
            })
        else:
            # 不使用缓存的版本
            messages.append({
                "role": "user",
                "content": f"{system_prompt}\n\n相关背景信息：\n{rag_context or ''}\n\n用户问题：{user_message}"
            })
        
        return messages
    
    def build_anthropic_messages(
        self,
        system_prompt: str,
        messages: List[Dict[str, Any]],
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        构建Anthropic API格式的消息（支持Prompt Cache）
        
        Args:
            system_prompt: 系统提示
            messages: 对话消息列表
            use_cache: 是否启用缓存
            
        Returns:
            格式化的API请求体
        """
        system_content = []
        if use_cache:
            system_content = [
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ]
        else:
            system_content = system_prompt
        
        return {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4096,
            "system": system_content,
            "messages": messages
        }
    
    def calculate_token_savings(
        self,
        cache_hits: int,
        cached_tokens: int,
        input_cost_per_million: float = 3.0,  # Claude $3/1M tokens
        output_cost_per_million: float = 15.0  # Claude $15/1M tokens
    ) -> Dict[str, float]:
        """
        计算缓存带来的token和成本节省
        
        Args:
            cache_hits: 缓存命中次数
            cached_tokens: 每次缓存的token数
            input_cost_per_million: 输入成本（$/1M tokens）
            output_cost_per_million: 输出成本（$/1M tokens）
            
        Returns:
            节省统计信息
        """
        # 缓存读取成本为常规成本的25%
        regular_cost = cache_hits * cached_tokens * (input_cost_per_million / 1_000_000)
        cached_cost = regular_cost * 0.25
        savings = regular_cost - cached_cost
        
        return {
            "cache_hits": cache_hits,
            "cached_tokens_total": cache_hits * cached_tokens,
            "regular_cost_usd": round(regular_cost, 4),
            "cached_cost_usd": round(cached_cost, 4),
            "savings_usd": round(savings, 4),
            "savings_percent": 75.0,
            "savings_ratio": self.CACHE_SAVINGS_RATIO
        }
    
    def clear_cache(self, prefix: Optional[str] = None) -> int:
        """
        清空缓存
        
        Args:
            prefix: 前缀过滤
            
        Returns:
            删除的缓存数量
        """
        count = 0
        
        # 内存缓存
        if prefix is None:
            count = len(self.memory_cache)
            self.memory_cache.clear()
        else:
            keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(prefix)]
            for key in keys_to_delete:
                del self.memory_cache[key]
            count = len(keys_to_delete)
        
        # 持久化缓存
        if self.cache_dir and os.path.exists(self.cache_dir):
            import glob
            pattern = os.path.join(self.cache_dir, "*.cache")
            cache_files = glob.glob(pattern)
            
            if prefix is None:
                for f in cache_files:
                    try:
                        os.remove(f)
                        count += 1
                    except:
                        pass
            else:
                for f in cache_files:
                    if os.path.basename(f).startswith(prefix):
                        try:
                            os.remove(f)
                            count += 1
                        except:
                            pass
        
        logger.info(f"Cleared {count} cache items")
        return count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_size = sum(
            item.get("size", 0)
            for item in self.memory_cache.values()
        )
        
        return {
            "enabled": self.enable_cache,
            "memory_items": len(self.memory_cache),
            "memory_size_bytes": total_size,
            "cache_dir": self.cache_dir,
            "ttl_config": self.ttl_config
        }
    
    # 静态方法便捷函数
    @staticmethod
    def generate_system_prompt_key() -> str:
        """系统提示的缓存键"""
        return "system_prompt_v1"
    
    @staticmethod
    def generate_rag_context_key(query: str) -> str:
        """RAG上下文的缓存键"""
        return CacheKeyGenerator.generate_key("rag_context", query)
    
    @staticmethod
    def generate_tool_definition_key() -> str:
        """工具定义的缓存键"""
        return "tool_definitions_v1"


# 导入CacheKeyGenerator
from .cache_key import CacheKeyGenerator
