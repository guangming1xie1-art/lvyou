"""
REST API Schemas
Pydantic models for API request and response validation
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ============== Search API Schemas ==============

class SearchRequest(BaseModel):
    """Request for travel search (flights and hotels)"""
    origin: str = Field(..., description="Departure city or airport code")
    destination: str = Field(..., description="Arrival city or airport code")
    departure_date: str = Field(..., description="Departure date (YYYY-MM-DD)")
    passengers: int = Field(default=1, description="Number of passengers")
    return_date: Optional[str] = Field(None, description="Return date (YYYY-MM-DD) for round trip")
    cabin_class: str = Field(default="economy", description="Cabin class: economy, premium_economy, business, first")
    trip_type: str = Field(default="oneway", description="Trip type: oneway or roundtrip")
    check_in_date: Optional[str] = Field(None, description="Hotel check-in date (YYYY-MM-DD)")
    check_out_date: Optional[str] = Field(None, description="Hotel check-out date (YYYY-MM-DD)")
    rooms: int = Field(default=1, description="Number of hotel rooms")
    min_rating: float = Field(default=0, description="Minimum hotel rating (1-5)")
    include_hotels: bool = Field(default=True, description="Whether to search for hotels")


class FlightInfo(BaseModel):
    """Flight information"""
    flight_id: str
    airline: str
    flight_number: str
    departure_time: str
    arrival_time: str
    duration_minutes: int
    stops: int
    price_per_person: float
    total_price: float
    currency: str = "USD"
    available_seats: int
    cabin_class: str


class HotelInfo(BaseModel):
    """Hotel information"""
    hotel_id: str
    name: str
    rating: float
    review_count: int
    review_score: Optional[float] = None
    address: str
    distance_to_center: Optional[str] = None
    amenities: List[str] = []
    room_type: Optional[str] = None
    price_per_night: float
    total_price: Optional[float] = None
    currency: str = "USD"
    cancellation_policy: Optional[str] = None
    breakfast_included: bool = False


class SearchMetadata(BaseModel):
    """Search metadata"""
    origin: Optional[str] = None
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    passengers: int
    rooms: int = 1
    nights: Optional[int] = None
    results_count: int


class SearchResponse(BaseModel):
    """Response from search API"""
    success: bool
    task_id: str
    outbound_flights: List[FlightInfo] = []
    return_flights: List[FlightInfo] = []
    hotels: List[HotelInfo] = []
    search_metadata: Optional[SearchMetadata] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# ============== Recommendation API Schemas ==============

class RecommendRequest(BaseModel):
    """Request for travel recommendations"""
    destination: str = Field(..., description="Travel destination")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    preferences: List[str] = Field(default_factory=list, description="Travel preferences (e.g., nature, culture, food)")
    include_attractions: bool = Field(default=True, description="Whether to include attractions")
    include_weather: bool = Field(default=True, description="Whether to include weather forecast")
    include_reviews: bool = Field(default=True, description="Whether to include destination reviews")
    max_attractions: int = Field(default=10, description="Maximum number of attractions")
    attraction_category: Optional[str] = Field(None, description="Filter attractions by category")


class DestinationInfo(BaseModel):
    """Destination information"""
    destination: str
    country: str
    region: Optional[str] = None
    description: str
    best_time_to_visit: Optional[str] = None
    average_duration: Optional[str] = None
    currency: Optional[str] = None
    language: Optional[str] = None
    visa_info: Optional[str] = None
    local_tips: List[str] = []
    timezone: Optional[str] = None
    emergency_number: Optional[str] = None


class AttractionInfo(BaseModel):
    """Attraction information"""
    name: str
    category: str
    description: Optional[str] = None
    rating: Optional[float] = None
    must_see: bool = False
    estimated_duration: Optional[str] = None
    entrance_fee: Optional[str] = None
    best_time_to_visit: Optional[str] = None
    location: Optional[str] = None


class WeatherDay(BaseModel):
    """Weather forecast for a day"""
    date: str
    day_of_week: str
    temperature_high: int
    temperature_low: int
    condition: str
    humidity: Optional[int] = None
    wind_speed: Optional[str] = None
    precipitation_chance: Optional[int] = None


class ReviewSummary(BaseModel):
    """Review summary"""
    overall_rating: float
    total_reviews: int
    recommended_by: Optional[float] = None
    sentiment_breakdown: Optional[Dict[str, int]] = None
    recent_reviews: Optional[List[Dict[str, Any]]] = None
    pros: List[str] = []
    cons: List[str] = []


class RecommendResponse(BaseModel):
    """Response from recommendation API"""
    success: bool
    task_id: str
    destination_info: Optional[DestinationInfo] = None
    attractions: List[AttractionInfo] = []
    weather_forecast: List[WeatherDay] = []
    reviews: Optional[ReviewSummary] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# ============== Booking API Schemas ==============

class PassengerInfo(BaseModel):
    """Passenger information"""
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    passport_number: Optional[str] = None
    nationality: Optional[str] = None


class BookRequest(BaseModel):
    """Request for booking"""
    customer_info: Dict[str, Any] = Field(..., description="Customer information (name, email, phone)")
    trip_details: Dict[str, Any] = Field(..., description="Trip details (destination, departure_date, return_date, travelers)")
    selected_flight: Optional[Dict[str, Any]] = Field(None, description="Selected flight details")
    selected_hotel: Optional[Dict[str, Any]] = Field(None, description="Selected hotel details")
    passengers: List[PassengerInfo] = Field(default_factory=list, description="List of passenger details")
    additional_services: List[Dict[str, Any]] = Field(default_factory=list, description="Additional services")


class PriceBreakdown(BaseModel):
    """Price breakdown"""
    flights_total: float = 0
    hotels_total: float = 0
    services_total: float = 0
    subtotal: float = 0
    taxes_and_fees: float = 0
    total: float = 0
    currency: str = "USD"


class TripSummary(BaseModel):
    """Trip summary"""
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    travelers: int
    flight_included: bool = False
    hotel_included: bool = False
    additional_services_count: int = 0


class BookResponse(BaseModel):
    """Response from booking API"""
    success: bool
    task_id: str
    booking_id: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    expires_at: Optional[str] = None
    customer_info: Optional[Dict[str, Any]] = None
    trip_summary: Optional[TripSummary] = None
    price_breakdown: Optional[PriceBreakdown] = None
    payment_required: bool = True
    next_steps: List[str] = []
    error: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# ============== Status API Schemas ==============

class StatusResponse(BaseModel):
    """Response from status API"""
    task_id: str
    status: str  # pending, processing, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str
    progress: Optional[float] = None


# ============== Common Error Schema ==============

class ErrorDetail(BaseModel):
    """Error detail"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    status_code: Optional[int] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: ErrorDetail
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
