"""
父子索引模块（admin-agent）
实现文档的父子关系管理和检索
"""
from typing import List, Dict, Any, Optional, Tuple
from langchain_core.documents import Document
from datetime import datetime
import uuid
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class ParentChildIndex:
    """父子索引管理器"""
    
    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or settings.async_database_url
        self.pool = None
    
    async def init_pool(self):
        """初始化数据库连接池"""
        if self.db_url and not self.pool:
            import asyncpg
            self.pool = await asyncpg.create_pool(self.db_url, min_size=2, max_size=10)
            logger.info("ParentChildIndex database pool initialized")
    
    async def close_pool(self):
        """关闭数据库连接池"""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    async def index_documents(
        self,
        child_docs: List[Document],
        parent_docs: List[Document]
    ) -> Dict[str, Any]:
        """
        索引父子文档
        
        Args:
            child_docs: 子文档列表（已切割）
            parent_docs: 父文档列表（原始文档）
            
        Returns:
            索引结果
        """
        if not self.pool:
            await self.init_pool()
        
        indexed_count = 0
        parent_child_map: Dict[str, List[str]] = {}
        
        async with self.pool.acquire() as conn:
            for parent_doc in parent_docs:
                parent_id = str(uuid.uuid4())
                metadata = parent_doc.metadata or {}
                
                await conn.execute("""
                    INSERT INTO parent_documents 
                    (id, content, metadata, doc_type, source, entity_type, entity_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                    parent_id,
                    parent_doc.page_content,
                    metadata,
                    metadata.get("doc_type"),
                    metadata.get("source"),
                    metadata.get("entity_type"),
                    metadata.get("entity_id")
                )
                
                parent_child_map[parent_id] = []
                
                for child_doc in child_docs:
                    if self._is_child_of(child_doc, parent_doc):
                        child_id = str(uuid.uuid4())
                        child_metadata = child_doc.metadata or {}
                        
                        await conn.execute("""
                            INSERT INTO child_documents 
                            (id, parent_id, content, chunk_index, metadata)
                            VALUES ($1, $2, $3, $4, $5)
                        """,
                            child_id,
                            parent_id,
                            child_doc.page_content,
                            child_metadata.get("chunk_index", 0),
                            child_metadata
                        )
                        
                        parent_child_map[parent_id].append(child_id)
                        indexed_count += 1
        
        logger.info(f"Indexed {len(parent_docs)} parent docs with {indexed_count} child docs")
        
        return {
            "parent_count": len(parent_docs),
            "child_count": indexed_count,
            "parent_child_map": parent_child_map
        }
    
    def _is_child_of(self, child_doc: Document, parent_doc: Document) -> bool:
        """判断子文档是否属于父文档"""
        child_content = child_doc.page_content
        parent_content = parent_doc.page_content
        
        if child_content in parent_content:
            return True
        
        child_metadata = child_doc.metadata or {}
        parent_metadata = parent_doc.metadata or {}
        
        if child_metadata.get("doc_index") == parent_metadata.get("doc_index"):
            return True
        
        return False
    
    async def get_parent_document(self, child_id: str) -> Optional[Document]:
        """根据子文档ID获取父文档"""
        if not self.pool:
            await self.init_pool()
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT pd.id, pd.content, pd.metadata
                FROM parent_documents pd
                JOIN child_documents cd ON cd.parent_id = pd.id
                WHERE cd.id = $1
            """, child_id)
            
            if row:
                return Document(
                    page_content=row['content'],
                    metadata=row['metadata'] or {}
                )
        
        return None
    
    async def retrieve_with_parent(
        self,
        child_docs: List[Document],
        include_parent: bool = True
    ) -> List[Document]:
        """检索并返回父文档上下文"""
        if not include_parent:
            return child_docs
        
        enhanced_docs = []
        
        for child_doc in child_docs:
            child_id = child_doc.metadata.get("child_id")
            
            if child_id:
                parent_doc = await self.get_parent_document(child_id)
                
                if parent_doc:
                    enhanced_doc = Document(
                        page_content=parent_doc.page_content,
                        metadata={
                            **child_doc.metadata,
                            "parent_content": parent_doc.page_content,
                            "retrieval_type": "parent_child"
                        }
                    )
                    enhanced_docs.append(enhanced_doc)
                    continue
            
            enhanced_docs.append(child_doc)
        
        return enhanced_docs
    
    async def delete_by_parent_id(self, parent_id: str) -> int:
        """删除父文档及其所有子文档"""
        if not self.pool:
            await self.init_pool()
        
        async with self.pool.acquire() as conn:
            child_count = await conn.fetchval("""
                SELECT COUNT(*) FROM child_documents WHERE parent_id = $1
            """, parent_id)
            
            await conn.execute("""
                DELETE FROM child_documents WHERE parent_id = $1
            """, parent_id)
            
            await conn.execute("""
                DELETE FROM parent_documents WHERE id = $1
            """, parent_id)
            
            logger.info(f"Deleted parent {parent_id} and {child_count} children")
            
            return child_count + 1
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        if not self.pool:
            await self.init_pool()
        
        async with self.pool.acquire() as conn:
            parent_count = await conn.fetchval("SELECT COUNT(*) FROM parent_documents")
            child_count = await conn.fetchval("SELECT COUNT(*) FROM child_documents")
            
            return {
                "parent_document_count": parent_count,
                "child_document_count": child_count,
                "avg_children_per_parent": child_count / parent_count if parent_count > 0 else 0
            }
