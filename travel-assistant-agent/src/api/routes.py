"""
REST API Routes for Travel Assistant Agent
Provides HTTP endpoints for search, recommendation, and booking operations
"""
import uuid
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Request, Query, Depends
from .schemas import (
    SearchRequest, SearchResponse,
    RecommendRequest, RecommendResponse,
    BookRequest, BookResponse,
    StatusResponse, ErrorDetail
)
from ..agents import get_mcp_client
from ..agents.conversation_agent import ConversationAgent
from ..models.schemas import ChatRequest, ChatResponse
from ..utils.logger import app_logger
from ..utils.pagination import paginate_results, sort_flights, sort_hotels
from ..auth.dependencies import get_current_active_user, get_current_user
from ..security import rate_limiter, audit_logger
from ..auth.models import User
from ..cache import RedisCache, CacheManager
from ..config import settings
from ..workflows.subgraphs.common import knowledge_base


# Create API routers
# - router: legacy REST endpoints (search/recommend/book)
# - chat_router: unified conversation entry
router = APIRouter(prefix="/api/agent", tags=["agent"])
chat_router = APIRouter(tags=["chat"])
rag_router = APIRouter(prefix="/api/rag", tags=["rag"])

_conversation_agent: Optional[ConversationAgent] = None


def get_conversation_agent() -> ConversationAgent:
    global _conversation_agent
    if _conversation_agent is None:
        _conversation_agent = ConversationAgent()
    return _conversation_agent


# ============== RAG Synchronization ==============

@rag_router.post("/sync")
async def sync_rag_documents(request: Dict[str, Any]):
    """
    Synchronize documents from Java MCP to Python Agent RAG
    """
    documents = request.get("documents", [])
    if not documents:
        return {"status": "success", "count": 0, "message": "No documents provided"}
    
    try:
        from langchain.schema import Document
        docs_to_add = []
        for doc in documents:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            if content:
                docs_to_add.append(Document(page_content=content, metadata=metadata))
        
        if docs_to_add:
            knowledge_base.add_documents(docs_to_add)
            app_logger.info(f"Synchronized {len(docs_to_add)} documents to RAG")
            
        return {"status": "success", "count": len(docs_to_add)}
    except Exception as e:
        app_logger.error(f"RAG sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Initialize cache
redis_cache = None
cache_manager = None

if settings.redis_enabled:
    try:
        redis_cache = RedisCache(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password if settings.redis_password else None,
            max_connections=settings.redis_max_connections
        )
        cache_manager = CacheManager(redis_cache)
        app_logger.info("Redis cache initialized successfully")
    except Exception as e:
        app_logger.warning(f"Redis cache initialization failed: {e}. Running without cache.")
        redis_cache = None
        cache_manager = None
else:
    app_logger.info("Redis cache disabled")


# ============== Task Status Management ==============
# In-memory task store for async task tracking
# In production, this should be replaced with Redis or database
_task_store: Dict[str, Dict[str, Any]] = {}


async def _create_task(
    task_type: str,
    task_data: Dict[str, Any]
) -> str:
    """Create a new task and return its ID"""
    task_id = str(uuid.uuid4())
    _task_store[task_id] = {
        "task_id": task_id,
        "task_type": task_type,
        "status": "pending",
        "result": None,
        "error": None,
        "created_at": asyncio.get_event_loop().time(),
        "updated_at": asyncio.get_event_loop().time(),
        "progress": 0.0
    }
    return task_id


async def _update_task(
    task_id: str,
    status: Optional[str] = None,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[Dict[str, Any]] = None,
    progress: Optional[float] = None
) -> None:
    """Update task status"""
    if task_id in _task_store:
        if status is not None:
            _task_store[task_id]["status"] = status
        if result is not None:
            _task_store[task_id]["result"] = result
        if error is not None:
            _task_store[task_id]["error"] = error
        if progress is not None:
            _task_store[task_id]["progress"] = progress
        _task_store[task_id]["updated_at"] = asyncio.get_event_loop().time()


def _format_task_status(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format task data for response"""
    return {
        "task_id": task_data["task_id"],
        "status": task_data["status"],
        "result": task_data["result"],
        "error": task_data["error"],
        "created_at": task_data["created_at"],
        "updated_at": task_data["updated_at"],
        "progress": task_data.get("progress")
    }


# ============== Search Endpoint ==============

@router.post("/search", response_model=SearchResponse)
async def search_travel(
    request: SearchRequest,
    http_request: Request,
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    sort_by: str = Query("price", description="排序字段 (price, duration, rating)"),
    use_cache: bool = Query(True, description="是否使用缓存")
):
    """
    Search for flights and hotels
    
    This endpoint searches for travel options based on the provided criteria.
    It can search for flights, hotels, or both depending on the request parameters.
    
    - **origin**: Departure city or airport code
    - **destination**: Arrival city or airport code
    - **departure_date**: Departure date (YYYY-MM-DD)
    - **return_date**: Optional return date for round trip
    - **passengers**: Number of passengers
    - **cabin_class**: Cabin class (economy, premium_economy, business, first)
    - **include_hotels**: Whether to search for hotels
    - **page**: 页码（从 1 开始）
    - **page_size**: 每页数量（1-100）
    - **sort_by**: 排序字段 (price, duration, rating)
    - **use_cache**: 是否使用缓存
    """
    # Check cache first
    if use_cache and cache_manager:
        cached_result = cache_manager.get_search_cache(
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date,
            return_date=request.return_date,
            passengers=request.passengers,
            cabin_class=request.cabin_class,
            include_hotels=request.include_hotels,
            check_in_date=request.check_in_date,
            check_out_date=request.check_out_date,
            rooms=request.rooms
        )
        
        if cached_result:
            app_logger.info(f"Cache hit for search: {request.origin} -> {request.destination}")
            
            # Apply sorting and pagination to cached results
            outbound_flights = sort_flights(cached_result.get("outbound_flights", []), sort_by)
            return_flights = sort_flights(cached_result.get("return_flights", []), sort_by)
            hotels = sort_hotels(cached_result.get("hotels", []), sort_by)
            
            # Paginate results
            paginated_outbound = paginate_results(outbound_flights, page, page_size)
            paginated_return = paginate_results(return_flights, page, page_size)
            paginated_hotels = paginate_results(hotels, page, page_size)
            
            return {
                "success": True,
                "task_id": cached_result.get("task_id", "cached"),
                "outbound_flights": paginated_outbound["items"],
                "return_flights": paginated_return["items"],
                "hotels": paginated_hotels["items"],
                "search_metadata": cached_result.get("search_metadata"),
                "pagination": paginated_outbound["pagination"],
                "cache_hit": True
            }
    
    # Check rate limit
    await rate_limiter.check_limit(http_request)
    
    task_id = await _create_task("search", request.dict())
    app_logger.info(f"[{task_id}] Search request received", request=request.dict())
    
    # Log API call
    await audit_logger.log_api_call(
        user_id=current_user.id,
        action="search",
        endpoint="/api/agent/search",
        method="POST",
        params=request.dict(),
        ip_address=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent")
    )
    
    try:
        await _update_task(task_id, status="processing", progress=0.1)
        
        mcp_client = get_mcp_client()
        
        # Prepare search results
        outbound_flights = []
        return_flights = []
        hotels = []
        search_metadata = None
        error = None
        
        # Search for flights
        try:
            await _update_task(task_id, progress=0.2)
            app_logger.info(f"[{task_id}] Searching flights from {request.origin} to {request.destination}")
            
            flight_result = await mcp_client.call_skill(
                "search_flights",
                {
                    "origin": request.origin,
                    "destination": request.destination,
                    "departure_date": request.departure_date,
                    "return_date": request.return_date,
                    "passengers": request.passengers,
                    "cabin_class": request.cabin_class
                }
            )
            
            if flight_result.success:
                outbound_flights = flight_result.result.get("outbound_flights", [])
                return_flights = flight_result.result.get("return_flights", [])
                search_metadata = flight_result.result.get("search_metadata")
                app_logger.info(f"[{task_id}] Found {len(outbound_flights)} outbound flights")
            else:
                error = flight_result.error
                app_logger.warning(f"[{task_id}] Flight search failed: {error}")
            
            await _update_task(task_id, progress=0.5)
            
        except Exception as e:
            app_logger.error(f"[{task_id}] Flight search error: {e}")
            if not error:
                error = {"code": "FLIGHT_SEARCH_ERROR", "message": str(e)}
        
        # Search for hotels (if requested)
        if request.include_hotels and request.check_in_date and request.check_out_date:
            try:
                app_logger.info(f"[{task_id}] Searching hotels in {request.destination}")
                
                hotel_result = await mcp_client.call_skill(
                    "search_hotels",
                    {
                        "destination": request.destination,
                        "check_in_date": request.check_in_date,
                        "check_out_date": request.check_out_date,
                        "guests": request.passengers,
                        "rooms": request.rooms,
                        "min_rating": request.min_rating
                    }
                )
                
                if hotel_result.success:
                    hotels = hotel_result.result.get("hotels", [])
                    app_logger.info(f"[{task_id}] Found {len(hotels)} hotels")
                    
                    # Update search metadata with hotel info
                    if search_metadata is None:
                        search_metadata = hotel_result.result.get("search_metadata")
                    elif hotel_result.result.get("search_metadata"):
                        search_metadata.update(hotel_result.result["search_metadata"])
                else:
                    if not error:
                        error = hotel_result.error
                    app_logger.warning(f"[{task_id}] Hotel search failed: {error}")
                
                await _update_task(task_id, progress=0.8)
                
            except Exception as e:
                app_logger.error(f"[{task_id}] Hotel search error: {e}")
                if not error:
                    error = {"code": "HOTEL_SEARCH_ERROR", "message": str(e)}
        
        # Build search metadata if not set
        if not search_metadata:
            search_metadata = {
                "origin": request.origin,
                "destination": request.destination,
                "departure_date": request.departure_date,
                "return_date": request.return_date,
                "passengers": request.passengers,
                "rooms": request.rooms,
                "results_count": len(outbound_flights) + len(hotels)
            }
        
        # Cache the results (before pagination)
        if cache_manager and not error:
            cache_manager.set_search_cache(
                data={
                    "task_id": task_id,
                    "outbound_flights": outbound_flights,
                    "return_flights": return_flights,
                    "hotels": hotels,
                    "search_metadata": search_metadata
                },
                origin=request.origin,
                destination=request.destination,
                departure_date=request.departure_date,
                return_date=request.return_date,
                passengers=request.passengers,
                cabin_class=request.cabin_class,
                include_hotels=request.include_hotels,
                check_in_date=request.check_in_date,
                check_out_date=request.check_out_date,
                rooms=request.rooms
            )
        
        # Apply sorting
        sorted_outbound = sort_flights(outbound_flights, sort_by)
        sorted_return = sort_flights(return_flights, sort_by)
        sorted_hotels = sort_hotels(hotels, sort_by)
        
        # Apply pagination
        paginated_outbound = paginate_results(sorted_outbound, page, page_size)
        paginated_return = paginate_results(sorted_return, page, page_size)
        paginated_hotels = paginate_results(sorted_hotels, page, page_size)
        
        # Mark task as completed
        await _update_task(
            task_id,
            status="completed",
            result={
                "outbound_flights": sorted_outbound,
                "return_flights": sorted_return,
                "hotels": sorted_hotels,
                "search_metadata": search_metadata
            },
            progress=1.0
        )
        
        app_logger.info(f"[{task_id}] Search completed successfully")
        
        return {
            "success": True,
            "task_id": task_id,
            "outbound_flights": paginated_outbound["items"],
            "return_flights": paginated_return["items"],
            "hotels": paginated_hotels["items"],
            "search_metadata": search_metadata,
            "pagination": paginated_outbound["pagination"],
            "cache_hit": False,
            "error": error
        }
        
    except Exception as e:
        app_logger.error(f"[{task_id}] Search failed with error: {e}")
        
        error_detail = {
            "code": "INTERNAL_ERROR",
            "message": str(e)
        }
        
        await _update_task(
            task_id,
            status="failed",
            error=error_detail
        )
        
        return {
            "success": False,
            "task_id": task_id,
            "outbound_flights": [],
            "return_flights": [],
            "hotels": [],
            "error": error_detail
        }


# ============== Recommendation Endpoint ==============

@router.post("/recommend", response_model=RecommendResponse)
async def recommend_travel(
    request: RecommendRequest,
    http_request: Request,
    current_user: User = Depends(get_current_active_user),
    use_cache: bool = Query(True, description="是否使用缓存")
):
    """
    Get travel recommendations
    
    This endpoint provides comprehensive travel recommendations including:
    - Destination information
    - Top attractions
    - Weather forecast
    - Destination reviews
    
    - **destination**: Travel destination
    - **start_date**: Start date (YYYY-MM-DD)
    - **end_date**: End date (YYYY-MM-DD)
    - **preferences**: Travel preferences (nature, culture, food, etc.)
    - **use_cache**: 是否使用缓存
    """
    # Check cache first
    if use_cache and cache_manager:
        cached_result = cache_manager.get_recommend_cache(
            destination=request.destination,
            interests=request.preferences,
            budget=request.budget
        )
        
        if cached_result:
            app_logger.info(f"Cache hit for recommendations: {request.destination}")
            return {
                **cached_result,
                "cache_hit": True
            }
    
    # Check rate limit
    await rate_limiter.check_limit(http_request)
    
    task_id = await _create_task("recommend", request.dict())
    app_logger.info(f"[{task_id}] Recommend request received for {request.destination}")
    
    # Log API call
    await audit_logger.log_api_call(
        user_id=current_user.id,
        action="recommend",
        endpoint="/api/agent/recommend",
        method="POST",
        params=request.dict(),
        ip_address=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent")
    )
    
    try:
        await _update_task(task_id, status="processing", progress=0.1)
        
        mcp_client = get_mcp_client()
        
        # Prepare recommendation results
        destination_info = None
        attractions = []
        weather_forecast = []
        reviews = None
        error = None
        
        # Get destination information
        try:
            await _update_task(task_id, progress=0.2)
            app_logger.info(f"[{task_id}] Getting destination info for {request.destination}")
            
            dest_result = await mcp_client.call_skill(
                "get_destination_info",
                {
                    "destination": request.destination,
                    "language": "en"
                }
            )
            
            if dest_result.success:
                destination_info = dest_result.result
                app_logger.info(f"[{task_id}] Got destination info")
            else:
                error = dest_result.error
                app_logger.warning(f"[{task_id}] Destination info failed: {error}")
            
            await _update_task(task_id, progress=0.4)
            
        except Exception as e:
            app_logger.error(f"[{task_id}] Destination info error: {e}")
            if not error:
                error = {"code": "DESTINATION_INFO_ERROR", "message": str(e)}
        
        # Get attractions (if requested)
        if request.include_attractions:
            try:
                app_logger.info(f"[{task_id}] Getting attractions for {request.destination}")
                
                attractions_result = await mcp_client.call_skill(
                    "get_attractions",
                    {
                        "destination": request.destination,
                        "category": request.attraction_category,
                        "max_results": request.max_attractions
                    }
                )
                
                if attractions_result.success:
                    attractions = attractions_result.result.get("attractions", [])
                    app_logger.info(f"[{task_id}] Found {len(attractions)} attractions")
                else:
                    if not error:
                        error = attractions_result.error
                    app_logger.warning(f"[{task_id}] Attractions failed: {error}")
                
                await _update_task(task_id, progress=0.6)
                
            except Exception as e:
                app_logger.error(f"[{task_id}] Attractions error: {e}")
                if not error:
                    error = {"code": "ATTRACTIONS_ERROR", "message": str(e)}
        
        # Get weather forecast (if requested)
        if request.include_weather:
            try:
                app_logger.info(f"[{task_id}] Getting weather forecast for {request.destination}")
                
                weather_result = await mcp_client.call_skill(
                    "get_weather_forecast",
                    {
                        "destination": request.destination,
                        "start_date": request.start_date,
                        "end_date": request.end_date
                    }
                )
                
                if weather_result.success:
                    weather_forecast = weather_result.result.get("forecast", [])
                    app_logger.info(f"[{task_id}] Got {len(weather_forecast)} days of weather forecast")
                else:
                    if not error:
                        error = weather_result.error
                    app_logger.warning(f"[{task_id}] Weather forecast failed: {error}")
                
                await _update_task(task_id, progress=0.8)
                
            except Exception as e:
                app_logger.error(f"[{task_id}] Weather forecast error: {e}")
                if not error:
                    error = {"code": "WEATHER_ERROR", "message": str(e)}
        
        # Get destination reviews (if requested)
        if request.include_reviews:
            try:
                app_logger.info(f"[{task_id}] Getting reviews for {request.destination}")
                
                reviews_result = await mcp_client.call_skill(
                    "get_destination_reviews",
                    {
                        "destination": request.destination,
                        "limit": 5,
                        "sort_by": "rating_high"
                    }
                )
                
                if reviews_result.success:
                    reviews = reviews_result.result
                    app_logger.info(f"[{task_id}] Got destination reviews")
                else:
                    if not error:
                        error = reviews_result.error
                    app_logger.warning(f"[{task_id}] Reviews failed: {error}")
                
                await _update_task(task_id, progress=0.9)
                
            except Exception as e:
                app_logger.error(f"[{task_id}] Reviews error: {e}")
                if not error:
                    error = {"code": "REVIEWS_ERROR", "message": str(e)}
        
        # Cache the results
        result_data = {
            "success": True,
            "task_id": task_id,
            "destination_info": destination_info,
            "attractions": attractions,
            "weather_forecast": weather_forecast,
            "reviews": reviews,
            "error": error
        }
        
        if cache_manager and not error:
            cache_manager.set_recommend_cache(
                data=result_data,
                destination=request.destination,
                interests=request.preferences,
                budget=request.budget
            )
        
        # Mark task as completed
        await _update_task(
            task_id,
            status="completed",
            result={
                "destination_info": destination_info,
                "attractions": attractions,
                "weather_forecast": weather_forecast,
                "reviews": reviews
            },
            progress=1.0
        )
        
        app_logger.info(f"[{task_id}] Recommendation completed successfully")
        
        return {
            **result_data,
            "cache_hit": False
        }
        
    except Exception as e:
        app_logger.error(f"[{task_id}] Recommendation failed with error: {e}")
        
        error_detail = {
            "code": "INTERNAL_ERROR",
            "message": str(e)
        }
        
        await _update_task(
            task_id,
            status="failed",
            error=error_detail
        )
        
        return {
            "success": False,
            "task_id": task_id,
            "destination_info": None,
            "attractions": [],
            "weather_forecast": [],
            "reviews": None,
            "error": error_detail
        }


# ============== Booking Endpoint ==============

@router.post("/book", response_model=BookResponse)
async def create_booking(
    request: BookRequest,
    http_request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a travel booking
    
    This endpoint creates a booking for flights, hotels, and other services.
    Returns a booking ID that can be used to track the booking status.
    
    - **customer_info**: Customer details (name, email, phone)
    - **trip_details**: Trip details (destination, dates, travelers)
    - **selected_flight**: Optional selected flight
    - **selected_hotel**: Optional selected hotel
    - **passengers**: List of passenger details
    - **additional_services**: Additional services to include
    """
    # Check rate limit
    await rate_limiter.check_limit(http_request)
    
    task_id = await _create_task("booking", request.dict())
    app_logger.info(f"[{task_id}] Booking request received for {request.trip_details.get('destination')}")
    
    # Log API call
    await audit_logger.log_api_call(
        user_id=current_user.id,
        action="book",
        endpoint="/api/agent/book",
        method="POST",
        params=request.dict(),
        ip_address=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent")
    )
    
    try:
        await _update_task(task_id, status="processing", progress=0.2)
        
        mcp_client = get_mcp_client()
        
        # Prepare booking data for MCP skill
        booking_data = {
            "customer_info": request.customer_info,
            "trip_details": request.trip_details,
            "selected_flight": request.selected_flight,
            "selected_hotel": request.selected_hotel,
            "additional_services": request.additional_services
        }
        
        app_logger.info(f"[{task_id}] Creating booking...")
        
        # Call create_booking skill
        booking_result = await mcp_client.call_skill(
            "create_booking",
            booking_data
        )
        
        await _update_task(task_id, progress=0.8)
        
        if booking_result.success:
            app_logger.info(f"[{task_id}] Booking created successfully: {booking_result.result.get('booking_id')}")
            
            # Mark task as completed
            await _update_task(
                task_id,
                status="completed",
                result=booking_result.result,
                progress=1.0
            )
            
            return {
                "success": True,
                "task_id": task_id,
                "booking_id": booking_result.result.get("booking_id"),
                "status": booking_result.result.get("status"),
                "created_at": booking_result.result.get("created_at"),
                "expires_at": booking_result.result.get("expires_at"),
                "customer_info": booking_result.result.get("customer_info"),
                "trip_summary": booking_result.result.get("trip_summary"),
                "price_breakdown": booking_result.result.get("price_breakdown"),
                "payment_required": booking_result.result.get("payment_required", True),
                "next_steps": booking_result.result.get("next_steps", []),
                "error": None
            }
        else:
            app_logger.warning(f"[{task_id}] Booking failed: {booking_result.error}")
            
            error_detail = booking_result.error or {
                "code": "BOOKING_FAILED",
                "message": "Booking could not be created"
            }
            
            await _update_task(
                task_id,
                status="failed",
                error=error_detail
            )
            
            return {
                "success": False,
                "task_id": task_id,
                "booking_id": None,
                "status": None,
                "error": error_detail,
                "next_steps": ["Please try again or contact support"]
            }
        
    except Exception as e:
        app_logger.error(f"[{task_id}] Booking failed with error: {e}")
        
        error_detail = {
            "code": "INTERNAL_ERROR",
            "message": str(e)
        }
        
        await _update_task(
            task_id,
            status="failed",
            error=error_detail
        )
        
        return {
            "success": False,
            "task_id": task_id,
            "booking_id": None,
            "status": None,
            "error": error_detail,
            "next_steps": ["Please try again later"]
        }


# ============== Status Endpoint ==============

@router.get("/status/{task_id}", response_model=StatusResponse)
async def get_task_status(
    task_id: str,
    http_request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get task status
    
    Query the status of a previously submitted task.
    
    - **task_id**: The ID returned when the task was created
    
    Returns the current status and result (if completed) of the task.
    """
    if task_id not in _task_store:
        app_logger.warning(f"Status request for unknown task: {task_id}")
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    task_data = _task_store[task_id]
    app_logger.info(f"Status request for task {task_id}: {task_data['status']}")
    
    # Log API call
    await audit_logger.log_api_call(
        user_id=current_user.id,
        action="get_status",
        endpoint=f"/api/agent/status/{task_id}",
        method="GET",
        params={"task_id": task_id},
        ip_address=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent")
    )
    
    return _format_task_status(task_data)


@router.get("/tasks")
async def list_tasks(
    status: Optional[str] = None,
    limit: int = 20
):
    """
    List all tasks
    
    Returns a list of all tasks, optionally filtered by status.
    Useful for debugging and monitoring.
    """
    tasks = list(_task_store.values())
    
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    
    # Sort by updated_at (newest first)
    tasks.sort(key=lambda x: x["updated_at"], reverse=True)
    
    # Apply limit
    tasks = tasks[:limit]
    
    return {
        "total": len(_task_store),
        "filtered": len(tasks),
        "tasks": [_format_task_status(t) for t in tasks]
    }


# ============== Unified Chat Endpoint ==============

@chat_router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    http_request: Request,
    current_user: User = Depends(get_current_active_user),
):
    """唯一的对话入口。

    请求：{"message": "我想去北京旅游 5 天..."}
    响应：{"search_results": [...], "recommendations": [...], "booking_info": {...}, "response": "...", "status": "success"}
    """
    await rate_limiter.check_limit(http_request)

    agent = get_conversation_agent()

    result = await agent.ainvoke({"message": request.message})

    return ChatResponse(
        search_results=result.get("search_results", []),
        recommendations=result.get("recommendations", []),
        booking_info=result.get("booking_info", {}),
        response=result.get("response", ""),
        status=result.get("status", "error"),
    )
