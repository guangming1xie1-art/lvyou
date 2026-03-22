"""
admin-agent 切割预览API
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import logging

from app.services.document_processor import DocumentProcessor, SplitStrategy

router = APIRouter(prefix="/split", tags=["split"])
logger = logging.getLogger(__name__)

document_processor = DocumentProcessor()


class SplitPreviewRequest(BaseModel):
    documents: List[dict]
    chunk_size: int = 500
    chunk_overlap: int = 50
    strategy: str = "recursive"  # recursive or semantic
    use_embeddings: bool = False
    embedding_model: str = "text-embedding-3-small"


class ChunkItem(BaseModel):
    content: str
    metadata: dict


class SplitPreviewResponse(BaseModel):
    status: str
    chunks: List[ChunkItem]
    chunk_count: int
    original_count: int


@router.post("/preview", response_model=SplitPreviewResponse)
async def preview_split(request: SplitPreviewRequest):
    """
    预览切割效果
    
    用于预览切割结果或自定义切割策略，不实际入库
    
    支持两种策略：
    - recursive: 递归字符切分（传统方式）
    - semantic: 语义切分（智能方式，需要嵌入模型）
    """
    if not request.documents:
        return SplitPreviewResponse(
            status="success",
            chunks=[],
            chunk_count=0,
            original_count=0
        )
    
    try:
        from langchain.schema import Document
        
        docs_to_split = [
            Document(
                page_content=doc.get("content", ""),
                metadata=doc.get("metadata", {})
            )
            for doc in request.documents
            if doc.get("content")
        ]
        
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
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            strategy=strategy,
            embeddings=embeddings
        )
        chunks = processor.process_documents(docs_to_split)
        
        logger.info(f"Preview split ({strategy.value}): {len(docs_to_split)} docs -> {len(chunks)} chunks")
        
        return SplitPreviewResponse(
            status="success",
            chunks=[
                ChunkItem(
                    content=chunk.page_content,
                    metadata=chunk.metadata
                )
                for chunk in chunks
            ],
            chunk_count=len(chunks),
            original_count=len(docs_to_split)
        )
        
    except Exception as e:
        logger.error(f"Failed to preview split: {e}")
        raise HTTPException(status_code=500, detail=str(e))
