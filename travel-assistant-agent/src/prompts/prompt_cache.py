"""提示词缓存模块

实现提示词的内存缓存，使用LRU策略管理缓存大小。
"""

from typing import Dict, Optional, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class PromptCache:
    """提示词缓存
    
    使用LRU策略管理提示词缓存，支持快速访问和缓存大小控制。
    """
    
    def __init__(self, max_size: int = 100):
        """
        初始化提示词缓存
        
        Args:
            max_size: 缓存最大容量
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_order: list = []
        self.max_size = max_size
        self.last_update: Optional[datetime] = None
        
        logger.info(f"PromptCache initialized with max_size={max_size}")
    
    def get(self, category: str, name: str) -> Optional[str]:
        """
        获取提示词
        
        Args:
            category: 提示词分类
            name: 提示词名称
            
        Returns:
            提示词内容，如果不存在返回None
        """
        key = f"{category}:{name}"
        if key in self.cache:
            # 更新访问顺序
            self.access_order.remove(key)
            self.access_order.append(key)
            logger.debug(f"Cache hit: {key}")
            return self.cache[key].get("content")
        logger.debug(f"Cache miss: {key}")
        return None
    
    def set(self, category: str, name: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        设置提示词
        
        Args:
            category: 提示词分类
            name: 提示词名称
            content: 提示词内容
            metadata: 提示词元数据
        """
        key = f"{category}:{name}"
        
        # 更新缓存
        self.cache[key] = {
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now()
        }
        
        # 更新访问顺序
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
        
        # 维护缓存大小
        while len(self.access_order) > self.max_size:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
            logger.debug(f"Cache evicted: {oldest_key}")
        
        self.last_update = datetime.now()
        logger.debug(f"Cache set: {key}")
    
    def delete(self, category: str, name: str) -> bool:
        """
        删除提示词
        
        Args:
            category: 提示词分类
            name: 提示词名称
            
        Returns:
            是否删除成功
        """
        key = f"{category}:{name}"
        if key in self.cache:
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
            logger.debug(f"Cache deleted: {key}")
            return True
        return False
    
    def clear(self):
        """
        清空缓存
        """
        self.cache.clear()
        self.access_order.clear()
        self.last_update = None
        logger.info("Cache cleared")
    
    def size(self) -> int:
        """
        获取缓存大小
        
        Returns:
            缓存中的提示词数量
        """
        return len(self.cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计信息
        """
        return {
            "size": self.size(),
            "max_size": self.max_size,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "keys": list(self.cache.keys())
        }


# 全局缓存实例
prompt_cache = PromptCache()
