"""数据模型定义 (Pydantic)

这里只放 MVP 阶段需要的输入输出 schema。
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PlanningRequest(BaseModel):
    user_message: str = Field(..., description="用户的旅行需求描述")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="附加上下文信息，如用户偏好、预算等"
    )


class PlanningResponse(BaseModel):
    request_id: str
    status: str
    result: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    app_env: str
    components: Dict[str, Any]


class AgentState(BaseModel):
    """LangGraph 工作流状态"""

    user_message: str
    collected_info: Dict[str, Any] = Field(default_factory=dict)
    search_results: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    booking_status: Dict[str, Any] = Field(default_factory=dict)
    final_plan: Dict[str, Any] = Field(default_factory=dict)

    error: Optional[str] = None
