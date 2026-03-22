"""
admin-agent 文档处理API
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import logging

from app.services.document_processor import DocumentProcessor, SplitStrategy
from app.services.parent_child_index import ParentChildIndex
from app.services.vector_store import VectorStore

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)

document_processor = DocumentProcessor()
parent_child_index = ParentChildIndex()
vector_store = VectorStore()


class DocumentItem(BaseModel):
    content: str
    metadata: Optional[dict] = {}


class DocumentProcessRequest(BaseModel):
    documents: List[DocumentItem]
    auto_split: bool = True
    chunk_size: int = 500
    chunk_overlap: int = 50
    doc_type: str = "default"
    strategy: str = "recursive"  # recursive or semantic
    use_embeddings: bool = False
    embedding_model: str = "text-embedding-3-small"


class StrategyInfo(BaseModel):
    auto_split: bool
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None


class DocumentProcessResponse(BaseModel):
    status: str
    original_count: int
    chunk_count: int
    strategy: StrategyInfo


@router.post("/process", response_model=DocumentProcessResponse)
async def process_documents(request: DocumentProcessRequest):
    """
    处理文档（切割 + 向量化）
    
    支持两种模式：
    1. 自动切割模式（默认）：传入原始文档，自动切割
    2. 手动切割模式：传入已切割的文档，直接入库
    
    支持两种策略：
    - recursive: 递归字符切分（传统方式）
    - semantic: 语义切分（智能方式，需要嵌入模型）
    """
    if not request.documents:
        return DocumentProcessResponse(
            status="success",
            original_count=0,
            chunk_count=0,
            strategy=StrategyInfo(auto_split=request.auto_split)
        )
    
    try:
        from langchain.schema import Document
        
        docs_to_process = [
            Document(
                page_content=doc.content,
                metadata=doc.metadata
            )
            for doc in request.documents
            if doc.content
        ]
        
        chunk_size = request.chunk_size
        chunk_overlap = request.chunk_overlap
        
        if request.auto_split:
            chunk_size, chunk_overlap = _get_chunk_strategy(
                request.doc_type, 
                request.chunk_size, 
                request.chunk_overlap
            )
            
            # 处理策略
            strategy = SplitStrategy.RECURSIVE
            embeddings = None
            
            if request.strategy == "semantic" and request.use_embeddings:
                strategy = SplitStrategy.SEMANTIC
                try:
                    from langchain_openai import OpenAIEmbeddings
                    embeddings = OpenAIEmbeddings(model=request.embedding_model)
                    logger.info(f"Using OpenAI embeddings: {request.embedding_model}")
                except Exception as e:
                    logger.warning(f"Failed to initialize embeddings, falling back to recursive: {e}")
                    strategy = SplitStrategy.RECURSIVE
            
            processor = DocumentProcessor(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                strategy=strategy,
                embeddings=embeddings
            )
            processed_docs = processor.process_documents(docs_to_process)
            
            await parent_child_index.index_documents(processed_docs, docs_to_process)
        else:
            processed_docs = docs_to_process
        
        vector_store.add_documents(processed_docs)
        
        logger.info(f"Processed {len(docs_to_process)} docs -> {len(processed_docs)} chunks")
        
        return DocumentProcessResponse(
            status="success",
            original_count=len(docs_to_process),
            chunk_count=len(processed_docs),
            strategy=StrategyInfo(
                auto_split=request.auto_split,
                chunk_size=chunk_size if request.auto_split else None,
                chunk_overlap=chunk_overlap if request.auto_split else None
            )
        )
        
    except Exception as e:
        logger.error(f"Failed to process documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def batch_process_documents(request: DocumentProcessRequest):
    """批量处理文档"""
    return await process_documents(request)


def _get_chunk_strategy(doc_type: str, default_size: int, default_overlap: int) -> tuple:
    """根据文档类型获取切割策略"""
    strategies = {
        "travel_guide": (800, 100),
        "qa": (200, 20),
        "review": (300, 30),
        "policy": (600, 80),
        "default": (default_size, default_overlap)
    }
    return strategies.get(doc_type, strategies["default"])
