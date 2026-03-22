"""
admin-agent 统计信息API
"""
from fastapi import APIRouter
from pydantic import BaseModel
import logging

from app.services.parent_child_index import ParentChildIndex

router = APIRouter(prefix="", tags=["stats"])
logger = logging.getLogger(__name__)

parent_child_index = ParentChildIndex()


class StatsResponse(BaseModel):
    parent_document_count: int
    child_document_count: int
    avg_children_per_parent: float


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """获取RAG统计信息"""
    try:
        stats = await parent_child_index.get_stats()
        return StatsResponse(**stats)
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return StatsResponse(
            parent_document_count=0,
            child_document_count=0,
            avg_children_per_parent=0.0
        )
