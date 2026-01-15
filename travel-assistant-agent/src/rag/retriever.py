"""
混合检索器模块
结合向量检索和BM25关键词检索的混合搜索
"""
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
import logging
import re
from collections import defaultdict

logger = logging.getLogger(__name__)

try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    logger.warning("rank_bm25 not installed, BM25 features will be disabled")
    BM25_AVAILABLE = False


class HybridRetriever:
    """混合检索器：向量检索 + BM25关键词检索"""
    
    def __init__(
        self,
        vectorstore: Optional[FAISS] = None,
        embedding_model: Optional[str] = None,
        vector_weight: float = 0.6,
        bm25_weight: float = 0.4
    ):
        """
        初始化混合检索器
        
        Args:
            vectorstore: 已存在的FAISS向量存储
            embedding_model: Embedding模型名称
            vector_weight: 向量检索权重 (0-1)
            bm25_weight: BM25检索权重 (0-1)
        """
        from .vectorstore import VectorStoreManager
        
        if vectorstore is not None:
            self.vectorstore_manager = None
            self.vectorstore = vectorstore
        else:
            self.vectorstore_manager = VectorStoreManager()
            self.vectorstore = self.vectorstore_manager.vectorstore
        
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        
        # BM25相关
        self.bm25_index: Optional[BM25Okapi] = None
        self.bm25_corpus: List[str] = []
        self.bm25_doc_map: Dict[int, Document] = {}  # 索引到文档的映射
        self._doc_counter = 0
        
        # 确保权重之和为1
        total_weight = vector_weight + bm25_weight
        if total_weight != 1.0:
            self.vector_weight = vector_weight / total_weight
            self.bm25_weight = bm25_weight / total_weight
    
    def _tokenize(self, text: str) -> List[str]:
        """
        文本分词（简单实现）
        
        Args:
            text: 输入文本
            
        Returns:
            分词后的词列表
        """
        # 简单中英文分词
        text = text.lower()
        # 保留字母、数字、中文，替换为空格
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
        tokens = text.split()
        # 过滤过短的词
        return [t for t in tokens if len(t) > 1]
    
    def _rebuild_bm25_index(self):
        """重建BM25索引"""
        if not BM25_AVAILABLE or len(self.bm25_corpus) == 0:
            return
        
        try:
            tokenized_corpus = [self._tokenize(doc) for doc in self.bm25_corpus]
            self.bm25_index = BM25Okapi(tokenized_corpus)
            logger.info(f"Rebuilt BM25 index with {len(self.bm25_corpus)} documents")
        except Exception as e:
            logger.error(f"Failed to rebuild BM25 index: {e}")
    
    def add_documents(self, documents: List[Document]):
        """
        添加文档到混合索引
        
        Args:
            documents: 文档列表
        """
        # 添加到向量存储
        if self.vectorstore_manager is not None:
            self.vectorstore_manager.add_documents(documents)
            # 重新加载向量存储
            self.vectorstore = self.vectorstore_manager.vectorstore
        else:
            # 直接添加到向量存储
            ids = []
            for doc in documents:
                doc_id = f"doc_{self._doc_counter}"
                self._doc_counter += 1
                ids.append(doc_id)
            self.vectorstore.add_documents(documents, ids=ids)
        
        # 添加到BM25索引
        for doc in documents:
            content = doc.page_content
            self.bm25_corpus.append(content)
            self.bm25_doc_map[len(self.bm25_corpus) - 1] = doc
        
        # 重建BM25索引
        self._rebuild_bm25_index()
        
        logger.info(f"Added {len(documents)} documents to hybrid retriever")
    
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict]] = None
    ):
        """
        添加文本到混合索引
        
        Args:
            texts: 文本列表
            metadatas: 元数据列表
        """
        documents = []
        for i, text in enumerate(texts):
            metadata = metadatas[i] if metadatas else {}
            doc = Document(page_content=text, metadata=metadata)
            documents.append(doc)
        
        self.add_documents(documents)
    
    def retrieve(
        self,
        query: str,
        k: int = 5,
        vector_k: Optional[int] = None,
        bm25_k: Optional[int] = None,
        filter: Optional[Dict] = None,
        use_mmr: bool = False
    ) -> List[Document]:
        """
        混合检索
        
        Args:
            query: 查询文本
            k: 最终返回结果数量
            vector_k: 向量检索候选数量
            bm25_k: BM25检索候选数量
            filter: 元数据过滤条件
            use_mmr: 是否使用MMR（最大边际相关性）来增加结果多样性
            
        Returns:
            排序后的文档列表
        """
        vector_k = vector_k or k * 2
        bm25_k = bm25_k or k * 2
        
        # 1. 向量检索
        if use_mmr:
            vector_results = self.vectorstore.max_marginal_relevance_search(
                query, k=vector_k, fetch_k=vector_k * 2, filter=filter
            )
        else:
            vector_results = self.vectorstore.similarity_search(
                query, k=vector_k, filter=filter
            )
        
        # 计算向量相似度分数
        vector_scores = self._calculate_vector_scores(query, vector_results, vector_k)
        
        # 2. BM25检索
        bm25_results = self._bm25_search(query, bm25_k, filter)
        
        # 3. 合并结果
        combined_scores = self._combine_scores(
            vector_results, vector_scores,
            bm25_results
        )
        
        # 4. 去重并排序
        result = self._dedupe_and_rank(combined_scores, k)
        
        logger.info(f"Hybrid retrieve: query='{query[:50]}...' returned {len(result)} docs")
        return result
    
    def _calculate_vector_scores(
        self,
        query: str,
        documents: List[Document],
        max_results: int
    ) -> Dict[str, float]:
        """计算向量检索分数"""
        scores = {}
        for i, doc in enumerate(documents):
            # 倒序排名计分（越靠前分数越高）
            score = (max_results - i) / max_results
            scores[doc.page_content] = score * self.vector_weight
        return scores
    
    def _bm25_search(
        self,
        query: str,
        k: int,
        filter: Optional[Dict] = None
    ) -> List[tuple]:
        """
        BM25检索
        
        Returns:
            (文档, 分数) 元组列表
        """
        if not BM25_AVAILABLE or self.bm25_index is None:
            return []
        
        try:
            query_tokens = self._tokenize(query)
            bm25_scores = self.bm25_index.get_scores(query_tokens)
            
            # 获取Top-k的BM25结果
            top_indices = sorted(
                range(len(bm25_scores)),
                key=lambda i: bm25_scores[i],
                reverse=True
            )[:k]
            
            results = []
            for idx in top_indices:
                if idx in self.bm25_doc_map:
                    doc = self.bm25_doc_map[idx]
                    # 归一化分数
                    max_score = max(bm25_scores) if max(bm25_scores) > 0 else 1
                    normalized_score = bm25_scores[idx] / max_score
                    results.append((doc, normalized_score * self.bm25_weight))
            
            return results
        except Exception as e:
            logger.error(f"BM25 search failed: {e}")
            return []
    
    def _combine_scores(
        self,
        vector_results: List[Document],
        vector_scores: Dict[str, float],
        bm25_results: List[tuple]
    ) -> Dict[Document, float]:
        """合并向量和BM25分数"""
        combined = defaultdict(float)
        
        # 添加向量分数
        for doc in vector_results:
            combined[doc] += vector_scores.get(doc.page_content, 0)
        
        # 添加BM25分数
        for doc, score in bm25_results:
            combined[doc] += score
        
        return combined
    
    def _dedupe_and_rank(
        self,
        combined_scores: Dict[Document, float],
        k: int
    ) -> List[Document]:
        """去重并排序"""
        seen = set()
        result = []
        
        # 按分数排序
        sorted_docs = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for doc, score in sorted_docs:
            content_hash = doc.page_content[:100]  # 使用前100字符作为唯一标识
            if content_hash not in seen and len(result) < k:
                result.append(doc)
                seen.add(content_hash)
        
        return result
    
    def vector_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[Document]:
        """仅向量检索"""
        return self.vectorstore.similarity_search(query, k=k, filter=filter)
    
    def bm25_search(
        self,
        query: str,
        k: int = 5
    ) -> List[tuple]:
        """仅BM25检索"""
        return self._bm25_search(query, k)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取检索器统计信息"""
        return {
            "vectorstore_available": self.vectorstore is not None,
            "bm25_available": BM25_AVAILABLE and self.bm25_index is not None,
            "bm25_corpus_size": len(self.bm25_corpus),
            "vector_weight": self.vector_weight,
            "bm25_weight": self.bm25_weight,
        }
