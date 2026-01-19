from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from typing_extensions import Literal


class TravelerInfo(BaseModel):
    """旅客信息"""
    name: str
    age: int = Field(..., ge=0, description="年龄")
    document_type: Optional[str] = Field(None, description="证件类型")
    document_number: Optional[str] = Field(None, description="证件号码")


class ContactInfo(BaseModel):
    """联系信息"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class PaymentInfo(BaseModel):
    """支付信息"""
    method: str = Field(..., description="支付方式")
    amount: float = Field(..., ge=0, description="金额")
    currency: str = Field("CNY", description="货币代码")
    transaction_id: Optional[str] = None


class BookingDates(BaseModel):
    """预订日期"""
    check_in: Optional[str] = Field(None, description="入住日期 (YYYY-MM-DD)")
    check_out: Optional[str] = Field(None, description="退房日期 (YYYY-MM-DD)")
    departure: Optional[str] = Field(None, description="出发日期 (YYYY-MM-DD)")
    return_date: Optional[str] = Field(None, description="返回日期 (YYYY-MM-DD)", alias="return")


class HotelDetails(BaseModel):
    """酒店详情"""
    name: str
    address: str
    check_in: str
    check_out: str
    room_type: str
    nights: int
    guests: Optional[int] = None


class FlightDetails(BaseModel):
    """航班详情"""
    airline: str
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    class_type: str
    baggage: Optional[str] = None


class BookingDetails(BaseModel):
    """预订详情"""
    type: Literal["hotel", "flight", "package", "activity"] = Field(..., description="预订类型")
    destination: str = Field(..., description="目的地")
    product_id: Optional[str] = Field(None, description="产品ID")
    dates: BookingDates = Field(..., description="日期信息")
    travelers: Optional[List[TravelerInfo]] = Field(None, description="旅客信息")
    contact: ContactInfo = Field(..., description="联系信息")
    payment: Optional[PaymentInfo] = None
    special_requests: Optional[str] = None


class BookingCreateInput(BaseModel):
    """预订创建输入"""
    action: Literal["create", "query", "cancel"] = Field("create", description="预订操作类型")
    booking_details: BookingDetails = Field(..., description="预订详情")


class BookingQueryInput(BaseModel):
    """预订查询输入"""
    action: Literal["query"] = Field("query", description="预订操作类型")
    booking_id: str = Field(..., description="预订ID")


class BookingInput(BaseModel):
    """预订技能通用输入"""
    action: Literal["create", "query", "cancel"] = Field(..., description="预订操作类型")
    booking_id: Optional[str] = None
    booking_details: Optional[BookingDetails] = None


class BookingOutput(BaseModel):
    """预订技能输出"""
    booking_id: str = Field(..., description="预订ID")
    status: Literal["confirmed", "pending", "cancelled", "failed"] = Field(..., description="预订状态")
    message: Optional[str] = Field(None, description="状态消息")
    total_cost: Optional[float] = None
    confirmation_code: Optional[str] = None
    payment_status: Optional[Literal["paid", "pending", "failed"]] = None
    cancellation_policy: Optional[str] = None
    details: Optional[dict] = Field(None, description="预订详情")
    metadata: Optional[dict] = Field(None, description="元数据")


__all__ = [
    "TravelerInfo",
    "ContactInfo", 
    "PaymentInfo",
    "BookingDates",
    "HotelDetails",
    "FlightDetails",
    "BookingDetails",
    "BookingCreateInput",
    "BookingQueryInput",
    "BookingInput",
    "BookingOutput"
]
