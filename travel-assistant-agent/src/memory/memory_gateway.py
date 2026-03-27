"""
记忆网关 - 统一接口

负责：
1. 从向量数据库读取长期记忆
2. 从 Redis 读取短期记忆
3. 提取用户画像
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Redis not available, session memory disabled")

try:
    from chromadb import Client as ChromaClient
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("ChromaDB not available, long-term memory disabled")

from conf import settings

logger = logging.getLogger(__name__)


class MemoryGateway:
    """记忆网关（单例模式）"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        
        # 初始化 Redis（短期记忆）
        self.redis = None
        if REDIS_AVAILABLE:
            try:
                self.redis = redis.Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    password=settings.redis_password,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                # 测试连接
                self.redis.ping()
                logger.info("✅ Redis 连接成功")
            except Exception as e:
                logger.warning(f"⚠️ Redis 连接失败：{e}，短期记忆功能不可用")
                self.redis = None
        
        # 初始化 ChromaDB（长期记忆）
        self.chroma_client = None
        self.chroma_collection = None
        if CHROMA_AVAILABLE:
            try:
                self.chroma_client = ChromaClient(Settings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory="./memory_db"
                ))
                self.chroma_collection = self.chroma_client.get_or_create_collection(
                    name="long_term_memory",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info("✅ ChromaDB 连接成功")
            except Exception as e:
                logger.warning(f"⚠️ ChromaDB 连接失败：{e}，长期记忆功能不可用")
                self.chroma_collection = None
    
    async def get_long_term_memory(
        self, 
        user_id: str, 
        k: int = 5
    ) -> Dict[str, Any]:
        """
        获取长期记忆（向量数据库）
        
        Args:
            user_id: 用户 ID
            k: 返回记忆数量
            
        Returns:
            用户偏好和习惯字典
        """
        if not self.chroma_collection:
            return {}
        
        try:
            # 检索用户相关的记忆
            results = self.chroma_collection.query(
                query_texts=["用户偏好和习惯"],
                n_results=k,
                where={"user_id": user_id},
                include=["documents", "metadatas", "distances"]
            )
            
            if not results or not results.get("documents") or not results["documents"][0]:
                return {}
            
            # 解析记忆内容
            memory = {}
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]
            
            for doc, metadata, distance in zip(documents, metadatas, distances):
                # 相似度 = 1 - 距离（余弦距离）
                similarity = 1 - distance
                
                # 只处理高相似度的记忆
                if similarity < 0.7:
                    continue
                
                # 根据事件类型分类
                event_type = metadata.get("event_type")
                if event_type == "user_preference":
                    try:
                        pref = json.loads(doc)
                        memory.update(pref)
                    except:
                        pass
            
            logger.info(f"✅ 长期记忆读取成功：user_id={user_id}, count={len(memory)}")
            return memory
            
        except Exception as e:
            logger.error(f"❌ 长期记忆读取失败：{e}")
            return {}
    
    async def get_session_memory(self, session_id: str) -> Dict[str, Any]:
        """
        获取短期记忆（Redis）
        
        Args:
            session_id: 会话 ID
            
        Returns:
            会话记忆字典
        """
        if not self.redis:
            return {
                "conversation_history": [],
                "recent_searches": [],
                "last_destination": None,
                "last_updated": None
            }
        
        try:
            key = f"session:{session_id}"
            data = self.redis.get(key)
            
            if data:
                memory = json.loads(data)
                logger.info(f"✅ 短期记忆读取成功：session_id={session_id}")
                return memory
            
            return {
                "conversation_history": [],
                "recent_searches": [],
                "last_destination": None,
                "last_updated": None
            }
            
        except Exception as e:
            logger.error(f"❌ 短期记忆读取失败：{e}")
            return {
                "conversation_history": [],
                "recent_searches": [],
                "last_destination": None,
                "last_updated": None
            }
    
    async def update_session_memory(
        self,
        session_id: str,
        user_input: str,
        ai_response: str,
        extracted_info: Optional[Dict] = None,
        ttl: int = 3600
    ):
        """
        更新短期记忆（Redis，TTL 自动过期）
        
        Args:
            session_id: 会话 ID
            user_input: 用户输入
            ai_response: AI 回复
            extracted_info: 提取的信息（用于更新最近搜索）
            ttl: 过期时间（秒）
        """
        if not self.redis:
            return
        
        try:
            key = f"session:{session_id}"
            
            # 获取现有记忆
            memory = await self.get_session_memory(session_id)
            
            # 添加新对话
            memory["conversation_history"].append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().isoformat()
            })
            memory["conversation_history"].append({
                "role": "assistant",
                "content": ai_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # 更新最近搜索
            if extracted_info:
                destination = extracted_info.get("destination")
                if destination:
                    memory["recent_searches"].append(destination)
                    memory["recent_searches"] = memory["recent_searches"][-5:]  # 保留最近 5 个
                    memory["last_destination"] = destination
            
            # 限制对话历史长度（最近 20 轮）
            if len(memory["conversation_history"]) > 40:
                memory["conversation_history"] = memory["conversation_history"][-40:]
            
            # 更新 Redis（自动 TTL 过期）
            memory["last_updated"] = datetime.now().isoformat()
            self.redis.setex(
                key,
                ttl,
                json.dumps(memory, ensure_ascii=False)
            )
            
            logger.info(f"✅ 短期记忆更新成功：session_id={session_id}")
            
        except Exception as e:
            logger.error(f"❌ 短期记忆更新失败：{e}")
    
    async def write_long_term_memory(
        self,
        user_id: str,
        content: str,
        event_type: str,
        metadata: Optional[Dict] = None
    ):
        """
        写入长期记忆（向量数据库，受控写入）
        
        Args:
            user_id: 用户 ID
            content: 记忆内容
            event_type: 事件类型
            metadata: 额外元数据
        """
        if not self.chroma_collection:
            return
        
        try:
            # 生成唯一 ID
            import uuid
            memory_id = str(uuid.uuid4())
            
            # 准备元数据
            doc_metadata = {
                "user_id": user_id,
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            # 添加到向量数据库
            self.chroma_collection.add(
                ids=[memory_id],
                documents=[content],
                metadatas=[doc_metadata]
            )
            
            logger.info(f"✅ 长期记忆写入成功：user_id={user_id}, content={content[:50]}...")
            
        except Exception as e:
            logger.error(f"❌ 长期记忆写入失败：{e}")


# 单例实例
memory_gateway = MemoryGateway()
