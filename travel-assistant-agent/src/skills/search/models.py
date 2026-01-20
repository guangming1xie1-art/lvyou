from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from typing_extensions import Literal


class BudgetFilter(BaseModel):
    """预算过滤条件"""
    min: Optional[float] = Field(None, ge=0, description="最低预算")
    max: Optional[float] = Field(None, ge=0, description="最高预算")
    currency: str = Field("CNY", description="货币代码")


class DatesFilter(BaseModel):
    """日期过滤条件"""
    check_in: Optional[str] = Field(None, description="入住日期 (YYYY-MM-DD)")
    check_out: Optional[str] = Field(None, description="退房日期 (YYYY-MM-DD)")
    departure: Optional[str] = Field(None, description="出发日期 (YYYY-MM-DD)")
    return_date: Optional[str] = Field(None, description="返回日期 (YYYY-MM-DD)", alias="return")


class SearchFilters(BaseModel):
    """搜索过滤器"""
    budget: Optional[BudgetFilter] = None
    dates: Optional[DatesFilter] = None
    preferences: Optional[List[str]] = Field(None, description="用户偏好标签")
    travelers_count: int = Field(1, ge=1, description="旅行人数")
    search_type: Optional[Literal["destination", "hotel", "flight", "all"]] = Field(None, description="搜索类型")


class SearchInput(BaseModel):
    """搜索技能输入"""
    query: str = Field(..., min_length=1, max_length=200, description="搜索关键词")
    filters: Optional[SearchFilters] = None
    limit: int = Field(10, ge=1, le=100, description="返回结果数")
    offset: int = Field(0, ge=0, description="分页偏移")


class PriceRange(BaseModel):
    """价格范围"""
    min: Optional[float] = None
    max: Optional[float] = None
    currency: Optional[str] = None


class SearchResultItem(BaseModel):
    """搜索结果项"""
    id: str = Field(..., description="结果ID")
    type: Literal["destination", "hotel", "flight"] = Field(..., description="结果类型")
    name: str = Field(..., description="名称")
    country: Optional[str] = Field(None, description="国家（仅目的地）")
    description: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5, description="评分（0-5）")
    reviews_count: Optional[int] = None
    price_range: Optional[PriceRange] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    amenities: Optional[List[str]] = None
    popular_attractions: Optional[List[str]] = None
    best_season: Optional[List[str]] = None


class SearchMetadata(BaseModel):
    """搜索元数据"""
    execution_time_ms: Optional[int] = None
    data_sources: Optional[List[str]] = None
    mock: Optional[bool] = None


class SearchOutput(BaseModel):
    """搜索技能输出"""
    results: List[SearchResultItem] = Field(..., description="搜索结果")
    total: int = Field(..., description="总结果数")
    search_quality: float = Field(..., ge=0, le=1, description="搜索质量评分（0-1）")
    filters_applied: Optional[Dict] = Field(None, description="应用的过滤条件")
    metadata: Optional[SearchMetadata] = Field(None, description="元数据")


__all__ = [
    "BudgetFilter",
    "DatesFilter", 
    "SearchFilters",
    "SearchInput",
    "PriceRange",
    "SearchResultItem",
    "SearchMetadata",
    "SearchOutput"
]
