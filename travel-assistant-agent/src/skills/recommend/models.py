from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from typing_extensions import Literal


class BudgetInfo(BaseModel):
    """预算信息"""
    min: Optional[float] = Field(None, ge=0, description="最低预算")
    max: Optional[float] = Field(None, ge=0, description="最高预算")
    currency: str = Field("CNY", description="货币代码")


class DateInfo(BaseModel):
    """日期信息"""
    departure: Optional[str] = Field(None, description="出发日期 (YYYY-MM-DD)")
    return_date: Optional[str] = Field(None, description="返回日期 (YYYY-MM-DD)", alias="return")


class TravelerInfo(BaseModel):
    """旅客信息"""
    name: str
    age: int = Field(..., ge=0, description="年龄")
    document_type: Optional[str] = None
    document_number: Optional[str] = None


class UserPreferences(BaseModel):
    """用户偏好"""
    budget: BudgetInfo = Field(..., description="预算范围")
    dates: DateInfo = Field(..., description="旅行日期")
    travelers_count: int = Field(1, ge=1, description="旅行人数")
    preferences: Optional[List[str]] = Field(None, description="偏好标签")
    accommodation_type: Optional[Literal["hotel", "hostel", "apartment", "resort"]] = None
    pace: Optional[Literal["relaxed", "moderate", "packed"]] = Field(None, description="行程节奏")


class ActivityInfo(BaseModel):
    """活动信息"""
    time: str
    activity: str
    location: str
    duration: Optional[str] = None


class ItineraryDay(BaseModel):
    """行程天数"""
    day: int = Field(..., ge=1, description="天数")
    title: str
    activities: List[ActivityInfo]


class CostBreakdown(BaseModel):
    """费用明细"""
    flights: Optional[float] = None
    accommodation: Optional[float] = None
    activities: Optional[float] = None
    meals: Optional[float] = None


class TotalCost(BaseModel):
    """总费用"""
    amount: float
    currency: str = Field("CNY", description="货币代码")
    breakdown: Optional[CostBreakdown] = None


class RecommendationItem(BaseModel):
    """推荐方案项"""
    id: str
    title: str
    description: str
    confidence: float = Field(..., ge=0, le=1, description="置信度（0-1）")
    total_cost: TotalCost
    itinerary: List[ItineraryDay]
    highlights: Optional[List[str]] = None
    estimated_duration_days: int = Field(..., ge=1)


class RecommendInput(BaseModel):
    """推荐技能输入"""
    user_prefs: UserPreferences = Field(..., description="用户偏好信息")
    search_results: Optional[List[Dict]] = Field(None, description="搜索结果列表")
    num_recommendations: int = Field(3, ge=1, le=10, description="生成推荐数量")


class RecommendOutput(BaseModel):
    """推荐技能输出"""
    recommendations: List[RecommendationItem] = Field(..., description="推荐方案列表")
    selected_recommendation_id: Optional[str] = None


__all__ = [
    "BudgetInfo",
    "DateInfo", 
    "TravelerInfo",
    "UserPreferences",
    "ActivityInfo",
    "ItineraryDay",
    "CostBreakdown",
    "TotalCost",
    "RecommendationItem",
    "RecommendInput",
    "RecommendOutput"
]
