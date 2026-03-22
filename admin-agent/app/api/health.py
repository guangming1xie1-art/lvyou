"""
admin-agent 健康检查API
"""
from fastapi import APIRouter
from pydantic import BaseModel
import logging

router = APIRouter(prefix="", tags=["health"])
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        service="admin-agent",
        version="1.0.0"
    )
