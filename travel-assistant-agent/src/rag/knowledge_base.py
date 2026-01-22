"""
知识库管理模块
提供旅游领域的知识库管理和检索功能
"""
from typing import List, Dict, Optional, Any
from langchain_core.documents import Document
from .retriever import HybridRetriever
from .vectorstore import VectorStoreManager
import logging

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """旅游知识库管理"""
    
    # 默认知识库配置
    DEFAULT_TOP_K = 5
    DEFAULT_VECTOR_K = 10
    DEFAULT_BM25_K = 10
    
    def __init__(
        self,
        retriever: Optional[HybridRetriever] = None,
        store_path: Optional[str] = None
    ):
        """
        初始化知识库
        
        Args:
            retriever: 自定义混合检索器
            store_path: 向量存储路径
        """
        if retriever is not None:
            self.retriever = retriever
        else:
            self.retriever = HybridRetriever()
        
        self.store_path = store_path
    
    def add_knowledge(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        添加知识到知识库
        
        Args:
            texts: 知识文本列表
            metadatas: 元数据列表
            ids: 文档ID列表
            
        Returns:
            添加的文档ID列表
        """
        if ids:
            return self.retriever.add_texts(texts, metadatas=metadatas, ids=ids)
        else:
            return self.retriever.add_texts(texts, metadatas=metadatas)
    
    def add_documents(
        self,
        documents: List[Document],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        添加文档到知识库
        
        Args:
            documents: 文档列表
            ids: 文档ID列表
            
        Returns:
            添加的文档ID列表
        """
        if ids:
            self.retriever.add_documents(documents)
            return ids
        else:
            self.retriever.add_documents(documents)
            return [f"doc_{i}" for i in range(len(documents))]
    
    def search(
        self,
        query: str,
        k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        use_mmr: bool = False
    ) -> List[Document]:
        """
        搜索知识库
        
        Args:
            query: 查询文本
            k: 返回结果数量
            filters: 元数据过滤条件
            use_mmr: 是否使用MMR增加结果多样性
            
        Returns:
            匹配的文档列表
        """
        # 转换 filters 格式（从 {key: value} 转为 FAISS filter 格式）
        faiss_filter = None
        if filters:
            faiss_filter = self._convert_filters(filters)
        
        results = self.retriever.retrieve(
            query=query,
            k=k,
            filter=faiss_filter,
            use_mmr=use_mmr
        )
        
        # 如果有额外的过滤器，再应用一次
        if filters:
            results = self._apply_filters(results, filters)
        
        return results
    
    def search_by_category(
        self,
        query: str,
        category: str,
        k: int = 3
    ) -> List[Document]:
        """
        按类别搜索知识库
        
        Args:
            query: 查询文本
            category: 类别名称
            k: 返回结果数量
            
        Returns:
            匹配的文档列表
        """
        return self.search(query, k=k, filters={"category": category})
    
    def search_by_destination(
        self,
        query: str,
        destination: str,
        k: int = 3
    ) -> List[Document]:
        """
        按目的地搜索知识库
        
        Args:
            query: 查询文本
            destination: 目的地名称
            k: 返回结果数量
            
        Returns:
            匹配的文档列表
        """
        return self.search(query, k=k, filters={"destination": destination})
    
    def get_relevant_context(
        self,
        query: str,
        k: int = 3,
        include_metadata: bool = False
    ) -> str:
        """
        获取相关上下文（用于Prompt）
        
        Args:
            query: 查询文本
            k: 返回结果数量
            include_metadata: 是否包含元数据
            
        Returns:
            格式化的上下文字符串
        """
        docs = self.search(query, k=k)
        
        if not docs:
            return ""
        
        context_parts = []
        for i, doc in enumerate(docs):
            if include_metadata:
                meta_info = f"[来源: {doc.metadata.get('source', '未知')}]"
                context_parts.append(f"{i+1}. {doc.page_content} {meta_info}")
            else:
                context_parts.append(f"- {doc.page_content}")
        
        return "\n".join(context_parts)
    
    def get_rag_context_for_prompt(
        self,
        query: str,
        k: int = 5
    ) -> str:
        """
        获取适合放入Prompt的RAG上下文
        
        Args:
            query: 查询文本
            k: 返回结果数量
            
        Returns:
            格式化的RAG上下文
        """
        docs = self.search(query, k=k)
        
        if not docs:
            return ""
        
        contexts = []
        for doc in docs:
            source = doc.metadata.get("source", "")
            category = doc.metadata.get("category", "")
            
            header = f"【{source} - {category}】" if source or category else ""
            contexts.append(f"{header}\n{doc.page_content}")
        
        return "\n\n".join(contexts)
    
    def _convert_filters(self, filters: Dict[str, Any]) -> Optional[Dict]:
        """转换过滤器格式"""
        # FAISS 支持的过滤器格式
        converted = {}
        for key, value in filters.items():
            converted[key] = value
        return converted if converted else None
    
    def _apply_filters(
        self,
        documents: List[Document],
        filters: Dict[str, Any]
    ) -> List[Document]:
        """应用过滤器"""
        if not filters:
            return documents
        
        filtered = []
        for doc in documents:
            match = True
            for key, value in filters.items():
                if doc.metadata.get(key) != value:
                    match = False
                    break
            if match:
                filtered.append(doc)
        
        return filtered
    
    def get_document_count(self) -> int:
        """获取知识库文档数量"""
        if hasattr(self.retriever, 'vectorstore_manager'):
            return self.retriever.vectorstore_manager.get_document_count()
        return 0
    
    def clear(self):
        """清空知识库"""
        if hasattr(self.retriever, 'vectorstore_manager'):
            self.retriever.vectorstore_manager.clear()
        logger.info("KnowledgeBase cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        stats = self.retriever.get_stats()
        stats["document_count"] = self.get_document_count()
        return stats


class TravelKnowledgeBase(KnowledgeBase):
    """旅游领域专用知识库"""
    
    # 旅游知识类别
    CATEGORY_FLIGHTS = "flights"
    CATEGORY_HOTELS = "hotels"
    CATEGORY_ATTRACTIONS = "attractions"
    CATEGORY_TIPS = "tips"
    CATEGORY_POLICY = "policy"
    
    def __init__(self, store_path: Optional[str] = None):
        """
        初始化旅游知识库
        
        Args:
            store_path: 向量存储路径
        """
        super().__init__(store_path=store_path)
    
    def add_flight_knowledge(
        self,
        texts: List[str],
        destinations: Optional[List[str]] = None
    ):
        """添加航班知识"""
        metadatas = []
        for i, text in enumerate(texts):
            meta = {"category": self.CATEGORY_FLIGHTS}
            if destinations and i < len(destinations):
                meta["destination"] = destinations[i]
            metadatas.append(meta)
        
        self.add_knowledge(texts, metadatas=metadatas)
    
    def add_hotel_knowledge(
        self,
        texts: List[str],
        destinations: Optional[List[str]] = None
    ):
        """添加酒店知识"""
        metadatas = []
        for i, text in enumerate(texts):
            meta = {"category": self.CATEGORY_HOTELS}
            if destinations and i < len(destinations):
                meta["destination"] = destinations[i]
            metadatas.append(meta)
        
        self.add_knowledge(texts, metadatas=metadatas)
    
    def add_attraction_knowledge(
        self,
        texts: List[str],
        destinations: Optional[List[str]] = None
    ):
        """添加景点知识"""
        metadatas = []
        for i, text in enumerate(texts):
            meta = {"category": self.CATEGORY_ATTRACTIONS}
            if destinations and i < len(destinations):
                meta["destination"] = destinations[i]
            metadatas.append(meta)
        
        self.add_knowledge(texts, metadatas=metadatas)
    
    def search_flights(self, query: str, k: int = 3) -> List[Document]:
        """搜索航班知识"""
        return self.search(query, k=k, filters={"category": self.CATEGORY_FLIGHTS})
    
    def search_hotels(self, query: str, k: int = 3) -> List[Document]:
        """搜索酒店知识"""
        return self.search(query, k=k, filters={"category": self.CATEGORY_HOTELS})
    
    def search_attractions(self, query: str, k: int = 3) -> List[Document]:
        """搜索景点知识"""
        return self.search(query, k=k, filters={"category": self.CATEGORY_ATTRACTIONS})
    
    def search_tips(self, query: str, k: int = 3) -> List[Document]:
        """搜索旅行贴士"""
        return self.search(query, k=k, filters={"category": self.CATEGORY_TIPS})
    
    def search_policy(self, query: str, k: int = 3) -> List[Document]:
        """搜索政策知识"""
        return self.search(query, k=k, filters={"category": self.CATEGORY_POLICY})
    
    def get_travel_tips_for_destination(self, destination: str) -> str:
        """获取目的地的旅行贴士"""
        docs = self.search_tips(f"{destination} 旅行贴士", k=5)
        return "\n".join([f"- {doc.page_content}" for doc in docs])
    
    def get_destination_info(self, destination: str) -> str:
        """获取目的地综合信息"""
        docs = self.search(f"{destination} 旅游信息", k=5)
        return "\n\n".join([doc.page_content for doc in docs])
