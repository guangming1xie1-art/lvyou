"""
向量存储模块
管理FAISS向量索引
"""
from typing import List, Optional
from langchain_core.documents import Document
import logging
import os

from app.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """向量存储管理器"""
    
    def __init__(self, index_path: Optional[str] = None):
        self.index_path = index_path or settings.faiss_index_path
        self.vectorstore = None
        self._ensure_index_dir()
    
    def _ensure_index_dir(self):
        """确保索引目录存在"""
        os.makedirs(self.index_path, exist_ok=True)
        logger.info(f"Vector store index path: {self.index_path}")
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """添加文档到向量库"""
        if not documents:
            return []
        
        try:
            from langchain_community.vectorstores import FAISS
            from langchain_community.embeddings import FakeEmbeddings
            
            if self.vectorstore is None:
                self.vectorstore = FAISS.from_documents(
                    documents,
                    FakeEmbeddings()
                )
            else:
                self.vectorstore.add_documents(documents)
            
            self._save_index()
            
            logger.info(f"Added {len(documents)} documents to vector store")
            return [str(i) for i in range(len(documents))]
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def _save_index(self):
        """保存索引到磁盘"""
        if self.vectorstore:
            self.vectorstore.save_local(self.index_path)
            logger.info(f"Saved vector index to {self.index_path}")
    
    def _load_index(self):
        """从磁盘加载索引"""
        try:
            from langchain_community.vectorstores import FAISS
            from langchain_community.embeddings import FakeEmbeddings
            
            index_file = os.path.join(self.index_path, "index.faiss")
            if os.path.exists(index_file):
                self.vectorstore = FAISS.load_local(
                    self.index_path,
                    FakeEmbeddings(),
                    allow_dangerous_deserialization=True
                )
                logger.info(f"Loaded vector index from {self.index_path}")
                return True
        except Exception as e:
            logger.warning(f"Failed to load index: {e}")
        return False
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """相似度搜索"""
        if self.vectorstore is None:
            self._load_index()
        
        if self.vectorstore is None:
            return []
        
        return self.vectorstore.similarity_search(query, k=k)
    
    def rebuild_index(self):
        """重建向量索引"""
        self.vectorstore = None
        
        import shutil
        if os.path.exists(self.index_path):
            shutil.rmtree(self.index_path)
        
        self._ensure_index_dir()
        logger.info("Vector index rebuilt")
