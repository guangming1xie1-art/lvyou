"""
向量存储管理模块
提供FAISS向量存储的创建、加载和搜索功能
"""
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from typing import List, Optional, Union
import os
import logging
import shutil

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """向量存储管理器"""
    
    def __init__(
        self,
        store_path: Optional[str] = None,
        embedding_model: Optional[str] = None,
        recreate: bool = False
    ):
        """
        初始化向量存储管理器
        
        Args:
            store_path: 向量存储路径，默认从配置读取
            embedding_model: Embedding模型名称
            recreate: 是否强制重新创建（删除现有存储）
        """
        from conf import settings
        
        self.store_path = store_path or settings.vector_store_path
        self.embedding_model = embedding_model or settings.embedding_model
        self.vectorstore: Optional[FAISS] = None
        self._embeddings = None
        
        # 如果强制重建，删除现有存储
        if recreate and os.path.exists(self.store_path):
            shutil.rmtree(self.store_path)
            logger.info(f"Removed existing vectorstore: {self.store_path}")
        
        self._load_or_create()
    
    def _get_embeddings(self):
        """获取Embedding模型"""
        if self._embeddings is None:
            from .embeddings import EmbeddingFactory
            self._embeddings = EmbeddingFactory.get_embeddings()
        return self._embeddings
    
    def _load_or_create(self):
        """加载或创建向量存储"""
        embeddings = self._get_embeddings()
        
        if os.path.exists(self.store_path):
            try:
                self.vectorstore = FAISS.load_local(
                    self.store_path,
                    embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info(f"Loaded vectorstore from {self.store_path}")
            except Exception as e:
                logger.warning(f"Failed to load vectorstore: {e}, creating new one")
                self._create_empty()
        else:
            os.makedirs(self.store_path, exist_ok=True)
            self._create_empty()
    
    def _create_empty(self):
        """创建空的向量存储"""
        embeddings = self._get_embeddings()
        # 创建一个包含占位符文档的FAISS存储
        placeholder_doc = Document(
            page_content="placeholder",
            metadata={"type": "system", "source": "init"}
        )
        self.vectorstore = FAISS.from_documents([placeholder_doc], embeddings)
        self.save()
        logger.info(f"Created new vectorstore at {self.store_path}")
    
    def add_documents(
        self,
        documents: List[Document],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        添加文档到向量存储
        
        Args:
            documents: 文档列表
            ids: 文档ID列表
            
        Returns:
            添加的文档ID列表
        """
        if self.vectorstore is None:
            self._create_empty()
        
        try:
            # 如果提供了ID，使用ID添加
            if ids:
                added_ids = self.vectorstore.add_documents(documents, ids=ids)
            else:
                # 自动生成ID
                added_ids = self.vectorstore.add_documents(documents)
            
            self.save()
            logger.info(f"Added {len(documents)} documents to vectorstore")
            return added_ids
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        添加文本到向量存储
        
        Args:
            texts: 文本列表
            metadatas: 元数据列表
            ids: 文档ID列表
            
        Returns:
            添加的文档ID列表
        """
        if self.vectorstore is None:
            self._create_empty()
        
        try:
            if ids:
                added_ids = self.vectorstore.add_texts(texts, metadatas=metadatas, ids=ids)
            else:
                added_ids = self.vectorstore.add_texts(texts, metadatas=metadatas)
            
            self.save()
            logger.info(f"Added {len(texts)} texts to vectorstore")
            return added_ids
        except Exception as e:
            logger.error(f"Failed to add texts: {e}")
            raise
    
    def search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[dict] = None
    ) -> List[Document]:
        """
        向量相似度搜索
        
        Args:
            query: 查询文本
            k: 返回结果数量
            filter: 元数据过滤条件
            
        Returns:
            匹配的文档列表
        """
        if self.vectorstore is None:
            return []
        
        try:
            if filter:
                results = self.vectorstore.similarity_search(query, k=k, filter=filter)
            else:
                results = self.vectorstore.similarity_search(query, k=k)
            return results
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[dict] = None
    ) -> List[tuple]:
        """
        带分数的向量搜索
        
        Args:
            query: 查询文本
            k: 返回结果数量
            filter: 元数据过滤条件
            
        Returns:
            (文档, 分数) 元组列表
        """
        if self.vectorstore is None:
            return []
        
        try:
            if filter:
                results = self.vectorstore.similarity_search_with_score(
                    query, k=k, filter=filter
                )
            else:
                results = self.vectorstore.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            logger.error(f"Vector search with score failed: {e}")
            return []
    
    def search_by_vector(
        self,
        query_vector: List[float],
        k: int = 5,
        filter: Optional[dict] = None
    ) -> List[Document]:
        """
        基于向量的搜索
        
        Args:
            query_vector: 查询向量
            k: 返回结果数量
            filter: 元数据过滤条件
            
        Returns:
            匹配的文档列表
        """
        if self.vectorstore is None:
            return []
        
        try:
            if filter:
                results = self.vectorstore.similarity_search_by_vector(
                    query_vector, k=k, filter=filter
                )
            else:
                results = self.vectorstore.similarity_search_by_vector(
                    query_vector, k=k
                )
            return results
        except Exception as e:
            logger.error(f"Vector search by vector failed: {e}")
            return []
    
    def max_marginal_relevance_search(
        self,
        query: str,
        k: int = 5,
        fetch_k: int = 20,
        filter: Optional[dict] = None
    ) -> List[Document]:
        """
        最大边际相关性搜索（减少结果冗余）
        
        Args:
            query: 查询文本
            k: 返回结果数量
            fetch_k: 初始候选数量
            filter: 元数据过滤条件
            
        Returns:
            多样化的文档列表
        """
        if self.vectorstore is None:
            return []
        
        try:
            if filter:
                results = self.vectorstore.max_marginal_relevance_search(
                    query, k=k, fetch_k=fetch_k, filter=filter
                )
            else:
                results = self.vectorstore.max_marginal_relevance_search(
                    query, k=k, fetch_k=fetch_k
                )
            return results
        except Exception as e:
            logger.error(f"MMR search failed: {e}")
            return []
    
    def save(self):
        """保存向量存储"""
        if self.vectorstore is not None:
            try:
                self.vectorstore.save_local(self.store_path)
                logger.info(f"Saved vectorstore to {self.store_path}")
            except Exception as e:
                logger.error(f"Failed to save vectorstore: {e}")
                raise
    
    def delete_documents(self, ids: List[str]) -> bool:
        """
        删除文档
        
        Args:
            ids: 要删除的文档ID列表
            
        Returns:
            是否删除成功
        """
        if self.vectorstore is None:
            return False
        
        try:
            self.vectorstore.delete(ids=ids)
            self.save()
            logger.info(f"Deleted {len(ids)} documents from vectorstore")
            return True
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            return False
    
    def clear(self):
        """清空向量存储"""
        if self.vectorstore is not None:
            # 删除所有文档并重新创建
            try:
                # 获取所有ID
                all_ids = self.vectorstore.get_all_documents_ids()
                if all_ids:
                    self.vectorstore.delete(ids=list(all_ids))
                self.save()
                logger.info("Cleared vectorstore")
            except Exception as e:
                logger.error(f"Failed to clear vectorstore: {e}")
    
    def get_document_count(self) -> int:
        """获取文档数量（不包括占位符）"""
        if self.vectorstore is None:
            return 0
        
        try:
            all_ids = self.vectorstore.get_all_documents_ids()
            # 排除占位符
            return len([i for i in all_ids if i != "placeholder"])
        except Exception:
            return 0
    
    def close(self):
        """关闭向量存储"""
        self.vectorstore = None
        logger.info("VectorStoreManager closed")
