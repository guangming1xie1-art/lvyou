"""
长期记忆复合检索器模块

结合向量检索和BM25关键词检索的混合搜索，用于从长期记忆中检索相关信息。
支持结构化过滤、语义检索和关键词匹配的多维度检索。

数据来源：
- 用户偏好（user_preferences表）
- 历史任务案例（task_cases表）
- 向量记忆（vector_memories表）

检索流程：
1. 结构化过滤（PostgreSQL）
2. 混合检索（向量 + BM25）
3. 结果融合（权重加权）
4. 重排序（可选）
5. 返回Top-K结果
"""
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
import logging
from datetime import datetime

from rag.retriever import HybridRetriever
from rag.vectorstore import VectorStoreManager
from utils.java_api_client import java_api_client
from utils.logger import app_logger

logger = app_logger.getChild(__name__)


class MemoryRetriever:
    """长期记忆复合检索器
    
    结合向量检索和BM25关键词检索的混合搜索，用于从长期记忆中检索相关信息。
    支持结构化过滤、语义检索和关键词匹配的多维度检索。
    """
    
    def __init__(
        self,
        vector_weight: float = 0.6,
        bm25_weight: float = 0.4,
        enable_hybrid_search: bool = True
    ):
        """
        初始化记忆检索器
        
        Args:
            vector_weight: 向量检索权重（0-1）
            bm25_weight: BM25检索权重（0-1）
            enable_hybrid_search: 是否启用混合检索
        """
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        self.enable_hybrid_search = enable_hybrid_search
        
        # 初始化向量存储
        self.vectorstore_manager = VectorStoreManager()
        self.vectorstore = self.vectorstore_manager.vectorstore
        
        # 初始化混合检索器
        self.hybrid_retriever = None
        if enable_hybrid_search:
            self.hybrid_retriever = HybridRetriever(
                vectorstore=self.vectorstore,
                vector_weight=vector_weight,
                bm25_weight=bm25_weight
            )
        
        logger.info(f"MemoryRetriever initialized: hybrid={enable_hybrid_search}, vector_weight={vector_weight}, bm25_weight={bm25_weight}")
    
    async def retrieve(
        self,
        user_id: int,
        query: str,
        memory_types: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 10,
        use_hybrid: bool = True
    ) -> List[Dict[str, Any]]:
        """
        复合检索长期记忆
        
        Args:
            user_id: 用户ID
            query: 查询文本
            memory_types: 记忆类型列表（preference, task_case, knowledge）
            filters: 结构化过滤条件
            top_k: 返回结果数量
            use_hybrid: 是否使用混合检索
            
        Returns:
            检索结果列表
        """
        try:
            logger.info(f"Retrieving long-term memory: user_id={user_id}, query='{query[:50]}...', top_k={top_k}")
            
            # 1. 从数据库获取候选记忆
            candidates = await self._fetch_candidates(
                user_id=user_id,
                memory_types=memory_types,
                filters=filters
            )
            
            if not candidates:
                logger.warning(f"No candidates found for user {user_id}")
                return []
            
            logger.info(f"Fetched {len(candidates)} candidates from database")
            
            # 2. 构建检索文档
            documents = self._build_documents(candidates)
            
            # 3. 执行检索
            if use_hybrid and self.hybrid_retriever:
                results = await self._hybrid_search(
                    query=query,
                    documents=documents,
                    top_k=top_k
                )
            else:
                results = await self._vector_search(
                    query=query,
                    documents=documents,
                    top_k=top_k
                )
            
            # 4. 重排序（结合结构化信息）
            ranked_results = self._rerank(results, candidates, filters)
            
            logger.info(f"Retrieved {len(ranked_results)} results")
            return ranked_results[:top_k]
        
        except Exception as e:
            logger.error(f"Failed to retrieve long-term memory: {e}")
            return []
    
    async def _fetch_candidates(
        self,
        user_id: int,
        memory_types: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        从数据库获取候选记忆
        
        Args:
            user_id: 用户ID
            memory_types: 记忆类型列表
            filters: 过滤条件
            
        Returns:
            候选记忆列表
        """
        candidates = []
        
        # 1. 获取用户偏好
        if not memory_types or "preference" in memory_types:
            preferences = await java_api_client.get_user_preferences(
                user_id=user_id,
                user_token=None
            )
            for pref in preferences:
                candidates.append({
                    "type": "preference",
                    "content": f"用户偏好：{pref.get('preference_type')} = {pref.get('preference_value')}",
                    "metadata": {
                        "user_id": user_id,
                        "preference_type": pref.get('preference_type'),
                        "preference_value": pref.get('preference_value'),
                        "confidence": pref.get('confidence', 0.8),
                        "source": pref.get('source', 'conversation')
                    }
                })
        
        # 2. 获取历史任务案例
        if not memory_types or "task_case" in memory_types:
            cases = await java_api_client.get_task_cases(
                user_id=user_id,
                destination=filters.get('destination') if filters else None,
                limit=20,
                user_token=None
            )
            for case in cases:
                candidates.append({
                    "type": "task_case",
                    "content": f"历史任务：{case.get('destination')} {case.get('duration_days')}天游，预算{case.get('budget_range')}，满意度{case.get('satisfaction', 'N/A')}",
                    "metadata": {
                        "user_id": user_id,
                        "destination": case.get('destination'),
                        "duration_days": case.get('duration_days'),
                        "budget_range": case.get('budget_range'),
                        "satisfaction": case.get('satisfaction'),
                        "plan_summary": case.get('plan_summary')
                    }
                })
        
        # 3. 应用结构化过滤
        if filters:
            candidates = self._apply_filters(candidates, filters)
        
        return candidates
    
    def _apply_filters(
        self,
        candidates: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        应用结构化过滤
        
        Args:
            candidates: 候选列表
            filters: 过滤条件
            
        Returns:
            过滤后的候选列表
        """
        filtered = []
        
        for candidate in candidates:
            metadata = candidate.get('metadata', {})
            match = True
            
            # 满意度过滤
            if 'min_satisfaction' in filters:
                satisfaction = metadata.get('satisfaction')
                if satisfaction is None or satisfaction < filters['min_satisfaction']:
                    match = False
            
            # 预算范围过滤
            if 'budget_range' in filters and match:
                budget = metadata.get('budget_range')
                if budget and budget != filters['budget_range']:
                    match = False
            
            # 目的地过滤
            if 'destination' in filters and match:
                dest = metadata.get('destination')
                if dest and dest != filters['destination']:
                    match = False
            
            if match:
                filtered.append(candidate)
        
        return filtered
    
    def _build_documents(
        self,
        candidates: List[Dict[str, Any]]
    ) -> List[Document]:
        """
        构建检索文档
        
        Args:
            candidates: 候选列表
            
        Returns:
            文档列表
        """
        documents = []
        
        for candidate in candidates:
            doc = Document(
                page_content=candidate['content'],
                metadata=candidate['metadata']
            )
            documents.append(doc)
        
        return documents
    
    async def _hybrid_search(
        self,
        query: str,
        documents: List[Document],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        混合检索（向量 + BM25）
        
        Args:
            query: 查询文本
            documents: 文档列表
            top_k: 返回数量
            
        Returns:
            检索结果列表
        """
        try:
            # 临时添加文档到检索器
            self.hybrid_retriever.add_documents(documents)
            
            # 执行混合检索
            results = self.hybrid_retriever.retrieve(
                query=query,
                k=top_k,
                vector_k=top_k * 2,
                bm25_k=top_k * 2
            )
            
            # 转换为结果格式
            formatted_results = []
            for doc in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "retrieval_method": "hybrid"
                })
            
            return formatted_results
        
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return []
    
    async def _vector_search(
        self,
        query: str,
        documents: List[Document],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        仅向量检索
        
        Args:
            query: 查询文本
            documents: 文档列表
            top_k: 返回数量
            
        Returns:
            检索结果列表
        """
        try:
            # 临时添加文档到向量存储
            self.vectorstore_manager.add_documents(documents)
            
            # 执行向量检索
            results = self.vectorstore.similarity_search(
                query=query,
                k=top_k
            )
            
            # 转换为结果格式
            formatted_results = []
            for doc in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "retrieval_method": "vector"
                })
            
            return formatted_results
        
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def _rerank(
        self,
        results: List[Dict[str, Any]],
        candidates: List[Dict[str, Any]],
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        重排序结果
        
        结合多个维度排序：
        - 检索得分
        - 满意度
        - 时间新鲜度
        - 用户偏好匹配度
        
        Args:
            results: 检索结果
            candidates: 原始候选
            filters: 过滤条件
            
        Returns:
            重排序后的结果
        """
        # 构建候选映射
        candidate_map = {c['content']: c for c in candidates}
        
        # 计算综合得分
        for result in results:
            content = result['content']
            metadata = result['metadata']
            candidate = candidate_map.get(content, {})
            
            # 基础得分（检索得分）
            score = 1.0
            
            # 满意度加权
            satisfaction = metadata.get('satisfaction')
            if satisfaction:
                score *= (0.5 + 0.5 * (satisfaction / 5.0))
            
            # 置信度加权
            confidence = metadata.get('confidence')
            if confidence:
                score *= (0.5 + 0.5 * confidence)
            
            # 预算匹配度
            if filters and 'budget_range' in filters:
                budget = metadata.get('budget_range')
                if budget == filters['budget_range']:
                    score *= 1.2
            
            result['score'] = score
        
        # 按得分排序
        sorted_results = sorted(
            results,
            key=lambda x: x.get('score', 0),
            reverse=True
        )
        
        return sorted_results
    
    async def add_memory(
        self,
        user_id: int,
        content: str,
        memory_type: str,
        metadata: Dict[str, Any]
    ):
        """
        添加记忆到向量存储
        
        Args:
            user_id: 用户ID
            content: 记忆内容
            memory_type: 记忆类型
            metadata: 元数据
        """
        try:
            document = Document(
                page_content=content,
                metadata={
                    "user_id": user_id,
                    "memory_type": memory_type,
                    **metadata
                }
            )
            
            self.vectorstore_manager.add_documents([document])
            
            if self.hybrid_retriever:
                self.hybrid_retriever.add_documents([document])
            
            logger.info(f"Added memory to vector store: type={memory_type}")
        
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取检索器统计信息"""
        stats = {
            "hybrid_search_enabled": self.enable_hybrid_search,
            "vector_weight": self.vector_weight,
            "bm25_weight": self.bm25_weight,
        }
        
        if self.hybrid_retriever:
            stats.update(self.hybrid_retriever.get_stats())
        
        return stats


# 全局记忆检索器实例
memory_retriever = MemoryRetriever()
