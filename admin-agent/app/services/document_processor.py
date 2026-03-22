"""
文档处理模块
提供文档切割、清洗和预处理功能
"""
from typing import List, Optional, Dict, Any
from enum import Enum
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter, SemanticChunker
import logging
import re

logger = logging.getLogger(__name__)


class SplitStrategy(Enum):
    """切分策略枚举"""
    RECURSIVE = "recursive"  # 递归字符切分
    SEMANTIC = "semantic"    # 语义切分


class DocumentProcessor:
    """文档处理器"""
    
    DEFAULT_SEPARATORS = [
        "\n\n",
        "\n",
        "。",
        "！",
        "？",
        "；",
        "，",
        " ",
        ""
    ]
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: Optional[List[str]] = None,
        strategy: SplitStrategy = SplitStrategy.RECURSIVE,
        embeddings: Optional[Any] = None,
        breakpoint_threshold: float = 95,
        breakpoint_threshold_type: str = "percentile"
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or self.DEFAULT_SEPARATORS
        self.strategy = strategy
        self.embeddings = embeddings
        self.breakpoint_threshold = breakpoint_threshold
        self.breakpoint_threshold_type = breakpoint_threshold_type
        
        if strategy == SplitStrategy.RECURSIVE:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=self.separators,
                length_function=len,
                is_separator_regex=False
            )
        elif strategy == SplitStrategy.SEMANTIC:
            if not embeddings:
                raise ValueError("Semantic strategy requires embeddings")
            self.text_splitter = SemanticChunker(
                embeddings=embeddings,
                breakpoint_threshold=breakpoint_threshold,
                breakpoint_threshold_type=breakpoint_threshold_type,
                sentence_split_regex=r'(?<=[。！？.!?])\s*'
            )
        
        logger.info(
            f"DocumentProcessor initialized: "
            f"strategy={strategy.value}, "
            f"chunk_size={chunk_size}, chunk_overlap={chunk_overlap}"
        )
    
    def split_documents(
        self,
        documents: List[Document],
        add_metadata: bool = True
    ) -> List[Document]:
        """切割文档"""
        all_chunks = []
        
        for doc_idx, doc in enumerate(documents):
            if self.strategy == SplitStrategy.SEMANTIC:
                chunks = [Document(page_content=chunk) for chunk in self.text_splitter.split_text(doc.page_content)]
            else:
                chunks = self.text_splitter.split_documents([doc])
            
            if add_metadata:
                for chunk_idx, chunk in enumerate(chunks):
                    chunk.metadata.update({
                        "chunk_index": chunk_idx,
                        "chunk_total": len(chunks),
                        "doc_index": doc_idx,
                        "original_length": len(doc.page_content),
                        "chunk_length": len(chunk.page_content),
                        "split_strategy": self.strategy.value
                    })
            
            all_chunks.extend(chunks)
            logger.info(
                f"Split document {doc_idx} ({self.strategy.value}): "
                f"{len(doc.page_content)} chars -> {len(chunks)} chunks"
            )
        
        logger.info(f"Total: {len(documents)} docs -> {len(all_chunks)} chunks")
        return all_chunks
    
    def split_text(
        self,
        text: str,
        metadata: Optional[dict] = None
    ) -> List[Document]:
        """切割文本"""
        doc = Document(page_content=text, metadata=metadata or {})
        return self.split_documents([doc])
    
    def clean_text(self, text: str) -> str:
        """清洗文本"""
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        text = text.replace('\t', ' ')
        text = text.strip()
        return text
    
    def process_documents(
        self,
        documents: List[Document],
        clean: bool = True,
        split: bool = True
    ) -> List[Document]:
        """处理文档（清洗 + 切割）"""
        processed_docs = []
        
        for doc in documents:
            if clean:
                content = self.clean_text(doc.page_content)
                doc = Document(page_content=content, metadata=doc.metadata)
            
            processed_docs.append(doc)
        
        if split:
            processed_docs = self.split_documents(processed_docs)
        
        return processed_docs
    
    def process_with_strategy(
        self,
        documents: List[Document],
        strategy: SplitStrategy,
        embeddings: Optional[Any] = None,
        clean: bool = True
    ) -> List[Document]:
        """使用指定策略处理文档"""
        processor = DocumentProcessor(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            strategy=strategy,
            embeddings=embeddings if strategy == SplitStrategy.SEMANTIC else None
        )
        return processor.process_documents(documents, clean=clean)
    
    def compare_strategies(
        self,
        documents: List[Document],
        embeddings: Any
    ) -> Dict[str, Any]:
        """对比两种切分策略"""
        results = {}
        
        # 递归字符切分
        recursive_docs = self.process_with_strategy(
            documents, SplitStrategy.RECURSIVE, clean=True
        )
        results["recursive"] = {
            "chunks": recursive_docs,
            "count": len(recursive_docs),
            "avg_chunk_length": sum(len(d.page_content) for d in recursive_docs) / len(recursive_docs) if recursive_docs else 0
        }
        
        # 语义切分
        semantic_docs = self.process_with_strategy(
            documents, SplitStrategy.SEMANTIC, embeddings=embeddings, clean=True
        )
        results["semantic"] = {
            "chunks": semantic_docs,
            "count": len(semantic_docs),
            "avg_chunk_length": sum(len(d.page_content) for d in semantic_docs) / len(semantic_docs) if semantic_docs else 0
        }
        
        logger.info(
            f"Strategy comparison: "
            f"recursive={results['recursive']['count']} chunks, "
            f"semantic={results['semantic']['count']} chunks"
        )
        
        return results
