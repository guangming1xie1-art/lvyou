"""数据模型定义 (Pydantic)

这里包含 MVP 阶段需要的输入输出 schema 和混合工作流的扩展模型。
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


class ChatRequest(BaseModel):
    """统一对话入口请求"""

    message: str


class ChatResponse(BaseModel):
    """统一对话入口响应"""

    search_results: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    booking_info: Dict[str, Any] = Field(default_factory=dict)
    response: str = ""
    status: str = "error"


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


# ============== 混合工作流模型 ==============

class TokenUsageStats(BaseModel):
    """Token 使用统计"""
    node_name: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    execution_time_ms: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


class PerformanceReport(BaseModel):
    """性能报告"""
    request_id: str
    total_tokens: int
    total_execution_time_ms: float
    node_count: int
    average_tokens_per_node: float
    average_time_per_node_ms: float
    nodes: Dict[str, TokenUsageStats]
    performance_summary: Dict[str, Any]
    generated_at: str


class WorkflowNodeStats(BaseModel):
    """工作流节点统计"""
    node_name: str
    execution_count: int
    success_rate: float
    average_tokens: float
    average_time_ms: float
    most_common_error: Optional[str] = None


class AgentStatsResponse(BaseModel):
    """Agent 统计信息响应"""
    timestamp: str
    workflow_stats: Dict[str, WorkflowNodeStats]
    total_requests: int
    success_rate: float
    average_tokens_per_request: float
    average_execution_time_ms: float
    system_health: Dict[str, str]


class HybridWorkflowRequest(BaseModel):
    """混合工作流请求"""
    user_message: str = Field(..., description="用户的旅行需求描述")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="附加上下文信息"
    )
    use_deep_agent: bool = Field(
        default=True,
        description="是否使用 DeepAgent 进行深度推理"
    )


class HybridWorkflowResponse(BaseModel):
    """混合工作流响应"""
    request_id: str
    status: str
    stage: str
    workflow_path: List[str]
    collected_info: Dict[str, Any] = Field(default_factory=dict)
    search_results: Dict[str, Any] = Field(default_factory=dict)
    search_quality: float = 0.0
    validate_results: Dict[str, Any] = Field(default_factory=dict)
    recommendations: Dict[str, Any] = Field(default_factory=dict)
    booking_confirmation: Dict[str, Any] = Field(default_factory=dict)
    final_plan: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    token_report: Optional[PerformanceReport] = None
    efficiency_score: float = 0.0


class DeepAgentConfig(BaseModel):
    """DeepAgent 配置"""
    enabled: bool = True
    search_model: str = "claude-3-5-sonnet-20241022"
    recommend_model: str = "claude-3-5-sonnet-20241022"
    temperature: float = 0.3
    max_tokens: int = 4096


class WorkflowConfig(BaseModel):
    """工作流配置"""
    max_retries: int = 2
    retry_delay: float = 1.0
    quality_threshold: float = 0.6
    enable_deep_agent: bool = True
    deep_agent_config: DeepAgentConfig = Field(default_factory=DeepAgentConfig)


class WorkflowDebugInfo(BaseModel):
    """工作流调试信息"""
    execution_path: List[str]
    decision_points: Dict[str, str]
    node_outputs: Dict[str, Any]
    token_usage_by_node: Dict[str, int]
    error_trace: Optional[str] = None
