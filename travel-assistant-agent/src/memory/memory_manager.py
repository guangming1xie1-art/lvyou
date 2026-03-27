"""
长期记忆更新机制

扩展 MemoryGateway，提供记忆的增删改查功能
"""
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from conf import settings
from utils.logger import app_logger

logger = logging.getLogger(__name__)


class MemoryEventType(Enum):
    """记忆事件类型"""
    USER_PREFERENCE = "user_preference"
    TRAVEL_HISTORY = "travel_history"
    BOOKING_PATTERN = "booking_pattern"
    SEARCH_HISTORY = "search_history"
    FEEDBACK = "feedback"


@dataclass
class MemoryRecord:
    """记忆记录"""
    id: Optional[str]
    user_id: str
    content: Dict[str, Any]
    event_type: MemoryEventType
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LongTermMemoryManager:
    """
    长期记忆管理器
    
    功能：
    1. 添加新记忆
    2. 查询记忆
    3. 更新现有记忆
    4. 删除记忆
    5. 批量操作
    """
    
    def __init__(self, memory_gateway=None):
        self._gateway = memory_gateway
        self._collection_name = "long_term_memory"
    
    @property
    def chroma_collection(self):
        """获取 ChromaDB collection"""
        if self._gateway and self._gateway.chroma_collection:
            return self._gateway.chroma_collection
        return None
    
    async def add_memory(
        self,
        user_id: str,
        key: str,
        value: Any,
        event_type: MemoryEventType = MemoryEventType.USER_PREFERENCE,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        添加新记忆
        
        Args:
            user_id: 用户 ID
            key: 记忆键（如 "preferred_destinations"）
            value: 记忆值
            event_type: 事件类型
            metadata: 扩展元数据
            
        Returns:
            生成的记忆 ID
        """
        if not self.chroma_collection:
            logger.warning("ChromaDB not available, cannot add memory")
            return None
        
        try:
            content = json.dumps({key: value}, ensure_ascii=False)
            doc_id = f"{user_id}_{key}_{datetime.now().timestamp()}"
            
            record_metadata = {
                "user_id": user_id,
                "key": key,
                "event_type": event_type.value,
                "created_at": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            self.chroma_collection.add(
                ids=[doc_id],
                documents=[content],
                metadatas=[record_metadata]
            )
            
            logger.info(f"Added memory: user={user_id}, key={key}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            return None
    
    async def update_memory(
        self,
        user_id: str,
        key: str,
        value: Any,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        更新现有记忆
        
        如果记忆存在则更新，不存在则新增
        
        Args:
            user_id: 用户 ID
            key: 记忆键
            value: 记忆值
            metadata: 扩展元数据
            
        Returns:
            是否成功
        """
        existing = await self.find_memory(user_id, key)
        
        if existing:
            return await self._update_existing(existing["id"], key, value, metadata)
        else:
            result = await self.add_memory(user_id, key, value, metadata=metadata)
            return result is not None
    
    async def _update_existing(
        self,
        doc_id: str,
        key: str,
        value: Any,
        metadata: Optional[Dict] = None
    ) -> bool:
        """更新已存在的记忆"""
        if not self.chroma_collection:
            return False
        
        try:
            content = json.dumps({key: value}, ensure_ascii=False)
            
            update_metadata = {
                "updated_at": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            self.chroma_collection.update(
                ids=[doc_id],
                documents=[content],
                metadatas=[update_metadata]
            )
            
            logger.info(f"Updated memory: id={doc_id}, key={key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update memory: {e}")
            return False
    
    async def delete_memory(
        self,
        user_id: str,
        key: Optional[str] = None,
        doc_id: Optional[str] = None
    ) -> bool:
        """
        删除记忆
        
        Args:
            user_id: 用户 ID
            key: 记忆键（可选，删除该用户所有匹配 key 的记忆）
            doc_id: 文档 ID（可选，直接删除指定文档）
            
        Returns:
            是否成功
        """
        if not self.chroma_collection:
            return False
        
        try:
            where_filter = {"user_id": user_id}
            if key:
                where_filter["key"] = key
            if doc_id:
                where_filter["id"] = doc_id
            
            self.chroma_collection.delete(where=where_filter)
            
            logger.info(f"Deleted memory: user={user_id}, key={key}, doc_id={doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
            return False
    
    async def find_memory(
        self,
        user_id: str,
        key: str
    ) -> Optional[Dict[str, Any]]:
        """
        查找指定记忆
        
        Args:
            user_id: 用户 ID
            key: 记忆键
            
        Returns:
            记忆记录（包含 id, content, metadata）
        """
        if not self.chroma_collection:
            return None
        
        try:
            results = self.chroma_collection.get(
                where={"user_id": user_id, "key": key},
                include=["documents", "metadatas"]
            )
            
            if not results or not results.get("ids") or not results["ids"][0]:
                return None
            
            doc_id = results["ids"][0]
            document = results["documents"][0]
            metadata = results["metadatas"][0]
            
            return {
                "id": doc_id,
                "content": json.loads(document),
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to find memory: {e}")
            return None
    
    async def get_user_memories(
        self,
        user_id: str,
        event_type: Optional[MemoryEventType] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取用户的所有记忆
        
        Args:
            user_id: 用户 ID
            event_type: 事件类型过滤（可选）
            limit: 返回数量限制
            
        Returns:
            记忆记录列表
        """
        if not self.chroma_collection:
            return []
        
        try:
            where_filter = {"user_id": user_id}
            if event_type:
                where_filter["event_type"] = event_type.value
            
            results = self.chroma_collection.get(
                where=where_filter,
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            if not results or not results.get("ids"):
                return []
            
            memories = []
            for doc_id, document, metadata in zip(
                results["ids"],
                results["documents"],
                results["metadatas"]
            ):
                memories.append({
                    "id": doc_id,
                    "content": json.loads(document),
                    "metadata": metadata
                })
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to get user memories: {e}")
            return []
    
    async def upsert_memory(
        self,
        user_id: str,
        key: str,
        value: Any,
        event_type: MemoryEventType = MemoryEventType.USER_PREFERENCE,
        merge: bool = True
    ) -> bool:
        """
        插入或更新记忆（原子操作）
        
        Args:
            user_id: 用户 ID
            key: 记忆键
            value: 记忆值
            event_type: 事件类型
            merge: 是否合并现有值
            
        Returns:
            是否成功
        """
        existing = await self.find_memory(user_id, key)
        
        if existing and merge:
            existing_value = existing["content"].get(key, {})
            if isinstance(existing_value, dict) and isinstance(value, dict):
                merged_value = {**existing_value, **value}
                return await self.update_memory(user_id, key, merged_value)
        
        return await self.update_memory(user_id, key, value)
    
    async def batch_add_memories(
        self,
        memories: List[Dict[str, Any]]
    ) -> int:
        """
        批量添加记忆
        
        Args:
            memories: 记忆列表，每项包含 user_id, key, value, event_type
            
        Returns:
            成功添加的数量
        """
        if not self.chroma_collection:
            return 0
        
        try:
            ids = []
            documents = []
            metadatas = []
            
            for mem in memories:
                content = json.dumps({mem["key"]: mem["value"]}, ensure_ascii=False)
                doc_id = f"{mem['user_id']}_{mem['key']}_{datetime.now().timestamp()}_{len(ids)}"
                
                ids.append(doc_id)
                documents.append(content)
                metadatas.append({
                    "user_id": mem["user_id"],
                    "key": mem["key"],
                    "event_type": mem.get("event_type", MemoryEventType.USER_PREFERENCE).value,
                    "created_at": datetime.now().isoformat()
                })
            
            self.chroma_collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"Batch added {len(ids)} memories")
            return len(ids)
            
        except Exception as e:
            logger.error(f"Failed to batch add memories: {e}")
            return 0


long_term_memory_manager = LongTermMemoryManager()
