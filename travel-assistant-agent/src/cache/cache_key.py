"""
缓存键生成模块
提供统一的缓存键生成策略
"""
import hashlib
from typing import Dict, List, Any, Optional
import json


class CacheKeyGenerator:
    """缓存键生成器"""
    
    @staticmethod
    def generate_key(
        prefix: str,
        *args,
        **kwargs
    ) -> str:
        """
        生成缓存键
        
        Args:
            prefix: 键前缀
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            缓存键（MD5哈希）
        """
        key_parts = [prefix]
        
        # 添加位置参数
        for arg in args:
            if isinstance(arg, str):
                key_parts.append(arg)
            elif isinstance(arg, (dict, list)):
                key_parts.append(json.dumps(arg, sort_keys=True, ensure_ascii=False))
            else:
                key_parts.append(str(arg))
        
        # 添加关键字参数（按键排序以确保一致性）
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (dict, list)):
                key_parts.append(f"{k}:{json.dumps(v, sort_keys=True, ensure_ascii=False)}")
            else:
                key_parts.append(f"{k}:{v}")
        
        # 拼接并哈希
        key_str = "|".join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    @staticmethod
    def generate_conversation_key(conversation_id: str) -> str:
        """对话缓存键"""
        return CacheKeyGenerator.generate_key("conversation", conversation_id)
    
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
    
    @staticmethod
    def generate_search_key(
        query: str,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        date: Optional[str] = None
    ) -> str:
        """搜索结果缓存键"""
        return CacheKeyGenerator.generate_key(
            "search",
            query=query,
            origin=origin,
            destination=destination,
            date=date
        )
    
    @staticmethod
    def generate_recommend_key(
        destination: str,
        interests: Optional[List[str]] = None,
        budget: Optional[str] = None
    ) -> str:
        """推荐结果缓存键"""
        return CacheKeyGenerator.generate_key(
            "recommend",
            destination=destination,
            interests=interests,
            budget=budget
        )
    
    @staticmethod
    def generate_user_preferences_key(user_id: str) -> str:
        """用户偏好缓存键"""
        return CacheKeyGenerator.generate_key("user_prefs", user_id)
    
    @staticmethod
    def generate_destination_key(destination: str) -> str:
        """目的地信息缓存键"""
        return CacheKeyGenerator.generate_key("destination", destination)
    
    @staticmethod
    def generate_workflow_state_key(workflow_id: str) -> str:
        """工作流状态缓存键"""
        return CacheKeyGenerator.generate_key("workflow_state", workflow_id)
    
    @staticmethod
    def generate_llm_response_key(
        prompt_hash: str,
        model: str,
        temperature: float
    ) -> str:
        """LLM响应缓存键"""
        return CacheKeyGenerator.generate_key(
            "llm_response",
            prompt_hash=prompt_hash,
            model=model,
            temperature=temperature
        )
