"""提示词加载器模块

从Java Admin API或本地fallback文件加载提示词，支持热更新和版本管理。
"""

from typing import Dict, List, Optional, Any
import logging
import json
import os
from datetime import datetime
import httpx

from .prompt_cache import prompt_cache

logger = logging.getLogger(__name__)


class PromptLoader:
    """提示词加载器
    
    从Java Admin API或本地fallback文件加载提示词，支持热更新和版本管理。
    """
    
    def __init__(self):
        """
        初始化提示词加载器
        """
        self.api_base_url = "http://localhost:8080/admin"
        self.fallback_path = os.path.join(os.path.dirname(__file__), "fallback_prompts.json")
        self.cache_version = None
        self.last_updated = None
        self.fallback_used = False
        
        logger.info(f"PromptLoader initialized with API: {self.api_base_url}")
        logger.info(f"Fallback path: {self.fallback_path}")
    
    async def initialize(self):
        """
        初始化提示词加载器
        """
        try:
            await self.reload()
            logger.info("PromptLoader initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PromptLoader: {e}")
            # 尝试从fallback加载
            await self._load_from_fallback()
    
    async def reload(self) -> bool:
        """
        重新加载提示词
        
        Returns:
            是否加载成功
        """
        try:
            prompts = await self._load_from_api()
            self._update_cache(prompts)
            self.fallback_used = False
            self.last_updated = datetime.now()
            logger.info("Prompts reloaded from API")
            return True
        except Exception as e:
            logger.error(f"Failed to reload from API: {e}")
            # 尝试从fallback加载
            await self._load_from_fallback()
            return False
    
    async def _load_from_api(self) -> Dict[str, Any]:
        """
        从Java Admin API加载提示词
        
        Returns:
            提示词数据
        """
        url = f"{self.api_base_url}/prompts"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            data = response.json()
            if "data" in data:
                prompts = data["data"]
            else:
                prompts = data
            
            logger.info(f"Loaded {len(prompts)} prompts from API")
            return {
                "prompts": prompts,
                "version": datetime.now().isoformat(),
                "source": "api"
            }
    
    async def _load_from_fallback(self) -> Dict[str, Any]:
        """
        从本地fallback文件加载提示词
        
        Returns:
            提示词数据
        """
        try:
            with open(self.fallback_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            prompts = data.get("prompts", [])
            logger.info(f"Loaded {len(prompts)} prompts from fallback")
            
            self._update_cache(data)
            self.fallback_used = True
            self.last_updated = datetime.now()
            
            return data
        except Exception as e:
            logger.error(f"Failed to load from fallback: {e}")
            return {"prompts": [], "version": "fallback", "source": "fallback"}
    
    def _update_cache(self, data: Dict[str, Any]):
        """
        更新缓存
        
        Args:
            data: 提示词数据
        """
        prompts = data.get("prompts", [])
        
        # 清空现有缓存
        prompt_cache.clear()
        
        # 更新缓存
        for prompt in prompts:
            category = prompt.get("category", "other")
            name = prompt.get("name")
            content = prompt.get("content")
            
            if name and content:
                metadata = {
                    "id": prompt.get("id"),
                    "description": prompt.get("description"),
                    "version": prompt.get("version"),
                    "isActive": prompt.get("isActive", True),
                    "variables": prompt.get("variables", []),
                    "createdAt": prompt.get("createdAt"),
                    "updatedAt": prompt.get("updatedAt")
                }
                prompt_cache.set(category, name, content, metadata)
                logger.debug(f"Cached prompt: {category}:{name}")
        
        # 更新版本
        self.cache_version = data.get("version", datetime.now().isoformat())
        logger.info(f"Cache updated with version: {self.cache_version}")
    
    def get(self, category: str, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        获取提示词
        
        Args:
            category: 提示词分类
            name: 提示词名称
            default: 默认值
            
        Returns:
            提示词内容
        """
        content = prompt_cache.get(category, name)
        if content is None and default:
            logger.warning(f"Prompt not found: {category}:{name}, using default")
            return default
        return content
    
    def get_all(self) -> List[Dict[str, Any]]:
        """
        获取所有提示词
        
        Returns:
            提示词列表
        """
        prompts = []
        for key in prompt_cache.cache:
            category, name = key.split(":", 1)
            prompt_data = prompt_cache.cache[key]
            prompts.append({
                "category": category,
                "name": name,
                "content": prompt_data["content"],
                "metadata": prompt_data["metadata"]
            })
        return prompts
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取加载器状态
        
        Returns:
            状态信息
        """
        return {
            "cache_version": self.cache_version,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "fallback_used": self.fallback_used,
            "cache_stats": prompt_cache.get_stats(),
            "api_base_url": self.api_base_url,
            "fallback_path": self.fallback_path
        }
    
    def set_api_base_url(self, url: str):
        """
        设置API基础URL
        
        Args:
            url: API基础URL
        """
        self.api_base_url = url
        logger.info(f"API base URL updated: {url}")
    
    def set_fallback_path(self, path: str):
        """
        设置fallback文件路径
        
        Args:
            path: fallback文件路径
        """
        self.fallback_path = path
        logger.info(f"Fallback path updated: {path}")


# 全局加载器实例
prompt_loader = PromptLoader()
