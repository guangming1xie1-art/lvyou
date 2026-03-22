"""
admin-agent 向量索引API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from app.services.vector_store import VectorStore

router = APIRouter(prefix="/vectors", tags=["vectors"])
logger = logging.getLogger(__name__)

vector_store = VectorStore()


class RebuildResponse(BaseModel):
    status: str
    message: str


@router.post("/rebuild", response_model=RebuildResponse)
async def rebuild_index():
    """重建向量索引"""
    try:
        vector_store.rebuild_index()
        logger.info("Vector index rebuilt successfully")
        return RebuildResponse(
            status="success",
            message="Vector index rebuilt successfully"
        )
    except Exception as e:
        logger.error(f"Failed to rebuild index: {e}")
        raise HTTPException(status_code=500, detail=str(e))
