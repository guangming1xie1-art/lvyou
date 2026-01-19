from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from typing_extensions import Literal


class ConversationMessage(BaseModel):
    """对话消息"""
    role: Literal["user", "assistant"] = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")
    timestamp: Optional[str] = None


class DateInfo(BaseModel):
    """日期信息"""
    departure: Optional[str] = Field(None, description="出发日期 (YYYY-MM-DD)")
    return_date: Optional[str] = Field(None, description="返回日期 (YYYY-MM-DD)", alias="return")
    check_in: Optional[str] = Field(None, description="入住日期 (YYYY-MM-DD)")
    check_out: Optional[str] = Field(None, description="退房日期 (YYYY-MM-DD)")


class BudgetInfo(BaseModel):
    """预算信息"""
    min: Optional[float] = Field(None, ge=0, description="最低预算")
    max: Optional[float] = Field(None, ge=0, description="最高预算")
    currency: str = Field("CNY", description="货币代码")


class TravelerDetail(BaseModel):
    """旅客详情"""
    name: str
    age: int = Field(..., ge=0, description="年龄")
    document_type: Optional[str] = None
    document_number: Optional[str] = None


class CollectedInfo(BaseModel):
    """收集到的信息"""
    destination: Optional[str] = None
    dates: Optional[DateInfo] = None
    budget: Optional[BudgetInfo] = None
    travelers_count: int = Field(1, ge=1, description="旅行人数")
    travelers_details: Optional[List[TravelerDetail]] = None
    preferences: Optional[List[str]] = None
    accommodation_type: Optional[Literal["hotel", "hostel", "apartment", "resort", "villa"]] = None
    special_requirements: Optional[List[str]] = None
    contact_info: Optional[Dict] = None


class MissingField(BaseModel):
    """缺失的字段"""
    field: str = Field(..., description="字段名")
    description: str = Field(..., description="字段描述")
    required_for: Optional[str] = Field(None, description="用于什么场景")
    priority: Optional[Literal["high", "medium", "low"]] = None


class ExtractionMetadata(BaseModel):
    """提取元数据"""
    extraction_method: str = Field("llm", description="提取方法")
    execution_time_ms: Optional[int] = None
    model_used: Optional[str] = None
    retry_count: int = Field(0, description="重试次数")


class InfoCollectionInput(BaseModel):
    """信息收集输入"""
    user_message: str = Field(..., min_length=1, description="用户消息（自然语言）")
    context: Optional[Dict] = Field(None, description="上下文信息")


class InfoCollectionOutput(BaseModel):
    """信息收集输出"""
    collected_info: CollectedInfo = Field(..., description="收集到的信息")
    missing_fields: List[MissingField] = Field(default_factory=list, description="缺失的字段列表")
    confidence: float = Field(..., ge=0, le=1, description="信息提取置信度（0-1）")
    suggestions: Optional[List[str]] = None
    needs_clarification: bool = Field(False, description="是否需要用户澄清")
    clarification_questions: List[str] = Field(default_factory=list, description="澄清问题列表")
    metadata: Optional[ExtractionMetadata] = None


__all__ = [
    "ConversationMessage",
    "DateInfo", 
    "BudgetInfo",
    "TravelerDetail",
    "CollectedInfo",
    "MissingField",
    "ExtractionMetadata",
    "InfoCollectionInput",
    "InfoCollectionOutput"
]