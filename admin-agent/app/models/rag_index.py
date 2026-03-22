"""
RAG索引数据库模型 - 父子索引结构
"""
from sqlalchemy import Column, String, DateTime, JSON, Integer, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .database import Base


class RagIndex(Base):
    """父级文档索引表"""
    __tablename__ = "rag_index"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False, index=True)  # destination, guide, qa
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    source = Column(String(255), nullable=False)
    doc_type = Column(String(50), nullable=False)
    content_hash = Column(String(64), nullable=False)
    chunk_count = Column(Integer, default=0)
    metadata = Column(JSON, default={})
    status = Column(String(20), default="PENDING")  # PENDING, SYNCED, FAILED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关联子级文档
    chunks = relationship("RagChunk", back_populates="parent", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_rag_index_entity', 'entity_type', 'entity_id'),
        Index('ix_rag_index_status', 'status'),
    )


class RagChunk(Base):
    """子级文档块索引表"""
    __tablename__ = "rag_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("rag_index.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)  # 在父文档中的序号
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False)
    vector_id = Column(String(255), nullable=True, index=True)  # FAISS中的向量ID
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联父级文档
    parent = relationship("RagIndex", back_populates="chunks")

    __table_args__ = (
        Index('ix_rag_chunks_parent', 'parent_id', 'chunk_index'),
    )


class RagSyncLog(Base):
    """RAG同步日志表"""
    __tablename__ = "rag_sync_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String(20), nullable=False)  # CREATE, UPDATE, DELETE
    status = Column(String(20), nullable=False)  # SUCCESS, FAILED
    error_message = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)
    processing_time_ms = Column(Integer, default=0)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_rag_sync_logs_entity', 'entity_type', 'entity_id'),
        Index('ix_rag_sync_logs_created', 'created_at'),
    )
