"""
FastAPI 主应用入口
提供 Agent 服务的 HTTP API 接口
"""
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional
import uuid
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from config import settings
from models.schemas import PlanningRequest, PlanningResponse, HealthResponse
from workflows import PlanningWorkflow
from utils.logger import app_logger
from utils.db import db_manager
from utils.claude import claude_client
from utils.api_client import backend_client
from agents import (
    get_mcp_client,
    init_mcp_client,
    SkillBasedAgent,
    MCPSkillsPlanner
)
from src.api import routes as api_routes
from src.api import websocket as websocket_routes
from src.auth import routes as auth_routes
from src.security import rate_limiter
from src.middleware import PerformanceMiddleware


# ============== MCP-related Models ==============

class MCPSkillInfo(BaseModel):
    """MCP Skill information"""
    name: str
    description: str
    category: str
    version: str = "1.0.0"
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)


class MCPSkillsListResponse(BaseModel):
    """Response for skills list endpoint"""
    skills: List[MCPSkillInfo]
    total_count: int


class SkillCallRequest(BaseModel):
    """Request to call a single skill"""
    skill_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class SkillCallResponse(BaseModel):
    """Response from skill execution"""
    success: bool
    skill_name: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


class BatchSkillCallRequest(BaseModel):
    """Request to call multiple skills"""
    calls: List[SkillCallRequest]


class BatchSkillCallResponse(BaseModel):
    """Response from batch skill execution"""
    results: List[SkillCallResponse]
    total_calls: int
    successful_calls: int
    failed_calls: int


class DemoPlanningRequest(BaseModel):
    """Request for demo planning with skills"""
    destination: str = Field(..., description="Travel destination")
    duration_days: int = Field(default=5, description="Number of days")
    budget: float = Field(default=2000.0, description="Budget in USD")
    start_date: Optional[str] = Field(default=None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, description="End date (YYYY-MM-DD)")
    interests: List[str] = Field(default_factory=list, description="Traveler interests")
    accommodation_type: str = Field(default="mid-range", description="Accommodation preference")
    pace: str = Field(default="moderate", description="Travel pace: relaxed, moderate, packed")
    use_template: str = Field(default="comprehensive", description="Skill template: basic, comprehensive, quick")


class DemoPlanningResponse(BaseModel):
    """Response for demo planning endpoint"""
    request_id: str
    destination: str
    skills_used: List[str]
    skill_results: Dict[str, Any]
    travel_plan: Dict[str, Any]


class ChatRequest(BaseModel):
    """Request for agent chat endpoint"""
    message: str
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    attachments: Dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    """Response for agent chat endpoint"""
    response: str
    status: str = "success"
    metadata: Dict[str, Any] = Field(default_factory=dict)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger.info("Starting Travel Assistant Agent service...")
    
    db_manager.init()
    claude_client.init()
    
    # Initialize MCP Client
    try:
        await init_mcp_client()
        app_logger.info("MCP Client initialized")
    except Exception as e:
        app_logger.warning(f"MCP Client initialization failed: {e}")
    
    app_logger.info("Service started successfully")
    yield
    
    app_logger.info("Shutting down...")
    db_manager.close()
    await backend_client.close()
    
    # Disconnect MCP client
    mcp_client = get_mcp_client()
    if mcp_client.is_connected():
        await mcp_client.disconnect()
    
    app_logger.info("Service stopped")


app = FastAPI(
    title=settings.app_name,
    description="AI Travel Assistant Agent Service",
    version="0.1.0",
    lifespan=lifespan
)

# Add Performance Monitoring Middleware
app.add_middleware(
    PerformanceMiddleware,
    slow_request_threshold=settings.slow_request_threshold,
    log_all_requests=True
)

# Add Gzip Compression Middleware
if settings.enable_gzip:
    app.add_middleware(
        GZipMiddleware,
        minimum_size=settings.gzip_min_size
    )
    app_logger.info(f"Gzip compression enabled (min size: {settings.gzip_min_size} bytes)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-Total-Count",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
        "X-Process-Time",
        "X-Performance"
    ]
)


@app.middleware("http")
async def https_redirect(request: Request, call_next):
    """HTTPS redirect middleware for production"""
    if settings.require_https and request.url.scheme != "https":
        # In production, redirect HTTP to HTTPS
        return RedirectResponse(url=request.url.replace("http://", "https://"))
    return await call_next(request)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

# Register REST API routes
app.include_router(api_routes.router)
app_logger.info("REST API routes registered")

# Register WebSocket routes
app.include_router(websocket_routes.router)
app_logger.info("WebSocket routes registered")

# Register Authentication routes
app.include_router(auth_routes.router)
app_logger.info("Authentication routes registered")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    db_ok = db_manager.health_check()
    claude_ready = claude_client.is_ready()

    claude_component = (
        "ok" if claude_ready else ("not_configured" if not claude_client.is_configured else "error")
    )

    overall_status = "healthy" if db_ok and claude_component in {"ok", "not_configured"} else "degraded"

    return {
        "status": overall_status,
        "app_env": settings.app_env,
        "components": {
            "database": "ok" if db_ok else "error",
            "claude": claude_component,
        },
    }


@app.get("/")
async def root():
    return {
        "service": settings.app_name,
        "version": "0.1.0",
        "status": "running"
    }


@app.post("/agent/start-planning", response_model=PlanningResponse)
async def start_planning(request: PlanningRequest):
    if not request.user_message:
        raise HTTPException(status_code=400, detail="user_message is required")
    
    request_id = str(uuid.uuid4())
    app_logger.info(f"[{request_id}] Received planning request: {request.user_message}")
    
    try:
        workflow = PlanningWorkflow()
        result = await workflow.run(request.user_message, request.metadata)
        
        return PlanningResponse(
            request_id=request_id,
            status="completed",
            result=result
        )
    except Exception as e:
        app_logger.error(f"[{request_id}] Planning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agent/status/{request_id}")
async def get_status(request_id: str):
    # TODO: 实现异步任务状态查询
    return {
        "request_id": request_id,
        "status": "not_implemented",
        "message": "Async task tracking not yet implemented"
    }


# ============== MCP Endpoints ==============

@app.get("/mcp/skills", response_model=MCPSkillsListResponse)
async def list_mcp_skills(agent_type: Optional[str] = None):
    """
    List all available MCP skills, optionally filtered by agent type.
    
    Args:
        agent_type: Filter skills by agent type (info_collection, search, recommendation, booking)
    
    Returns a list of skills registered with the MCP server,
    including their names, descriptions, agent types, and schemas.
    """
    mcp_client = get_mcp_client()
    skills = mcp_client.list_skills()
    
    # Filter by agent_type if provided
    if agent_type:
        skills = [s for s in skills if s.agent_type == agent_type]
    
    skill_infos = [
        MCPSkillInfo(
            name=s.name,
            description=s.description,
            category=s.agent_type,  # Use agent_type as category for API compatibility
            version=s.version,
            input_schema=s.input_schema,
            output_schema=s.output_schema
        )
        for s in skills
    ]
    
    return {
        "skills": skill_infos,
        "total_count": len(skill_infos)
    }


@app.post("/mcp/call-skill", response_model=SkillCallResponse)
async def call_mcp_skill(request: SkillCallRequest):
    """
    Call a single MCP skill.
    
    Executes the specified skill with the given parameters and returns
    the result. Useful for testing individual skills or building custom
    workflows.
    """
    import time
    start_time = time.time()
    
    mcp_client = get_mcp_client()
    result = await mcp_client.call_skill(request.skill_name, request.parameters)
    
    execution_time_ms = (time.time() - start_time) * 1000
    
    return SkillCallResponse(
        success=result.success,
        skill_name=result.skill_name,
        result=result.result,
        error=result.error,
        execution_time_ms=execution_time_ms
    )


@app.post("/mcp/batch-call", response_model=BatchSkillCallResponse)
async def call_mcp_skills_batch(request: BatchSkillCallRequest):
    """
    Call multiple MCP skills in parallel.
    
    Executes all specified skill calls in parallel and returns the results
    for each. This is more efficient than calling skills sequentially when
    skills don't depend on each other's outputs.
    """
    mcp_client = get_mcp_client()
    
    calls = [
        {"skill": call.skill_name, "parameters": call.parameters}
        for call in request.calls
    ]
    
    results = await mcp_client.call_skills_parallel(calls)
    
    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful
    
    return BatchSkillCallResponse(
        results=[
            SkillCallResponse(
                success=r.success,
                skill_name=r.skill_name,
                result=r.result,
                error=r.error
            )
            for r in results
        ],
        total_calls=len(results),
        successful_calls=successful,
        failed_calls=failed
    )


@app.get("/mcp/status")
async def get_mcp_status():
    """
    Get MCP client status and statistics.
    
    Returns information about the MCP connection, including:
    - Connection status
    - Number of available skills
    - List of skill names
    """
    mcp_client = get_mcp_client()
    stats = mcp_client.get_statistics()
    
    return {
        "mcp_enabled": True,
        "connected": stats["connected"],
        "skills_count": stats["skills_count"],
        "skills": stats["skills"]
    }


@app.post("/agent/chat")
async def chat(request: ChatRequest):
    """
    与Agent进行对话
    
    Args:
        request: 包含用户消息、历史记录和附件的请求对象
    
    Returns:
        Agent的响应
    """
    app_logger.info(f"Received chat request: {request.message}")
    
    try:
        # 使用现有的 PlanningWorkflow
        workflow = PlanningWorkflow()
        
        # 将历史记录和附件等信息传递给 workflow
        metadata = {
            "conversation_history": request.conversation_history,
            "attachments": request.attachments
        }
        
        result = await workflow.run(request.message, metadata)
        
        # 从结果中构造响应文本
        if result.get("error"):
            response_text = f"抱歉，在处理您的请求时遇到了错误：{result['error']}"
        elif result.get("booking_status"):
            response_text = "我已经为您完成了旅行规划和预订处理。以下是您的行程单..."
        elif result.get("recommendations"):
            response_text = "根据您的需求，我为您推荐了以下方案..."
        elif result.get("collected_info"):
            response_text = "我已经收集到了您的基本信息，正在为您搜索相关方案..."
        else:
            response_text = "收到您的消息，正在为您处理..."

        if result.get("final_plan"):
             response_text = str(result.get("final_plan"))
             
        data = {
            "response": response_text,
            "status": "success",
            "metadata": {"stage": result.get("metadata", {}).get("stage", "planning")}
        }
        
        return {
            "code": 200,
            "message": "success",
            "data": data
        }
        
    except Exception as e:
        app_logger.error(f"Chat failed: {e}")
        return {
            "code": 500,
            "message": str(e),
            "data": {
                "response": f"与Agent通信时发生错误: {str(e)}",
                "status": "error"
            }
        }


@app.get("/agent/status")
async def get_agent_status():
    """获取Agent状态"""
    return {
        "code": 200,
        "message": "success",
        "data": {"status": "online", "version": "1.0.0"}
    }


@app.post("/agent/demo-planning-with-skills", response_model=DemoPlanningResponse)
async def demo_planning_with_skills(request: DemoPlanningRequest):
    """
    Demo endpoint for planning with MCP Skills.
    
    This endpoint demonstrates how the Agent uses MCP skills to gather
    information and create comprehensive travel plans. It:
    1. Searches for destination information
    2. Queries pricing for hotels and flights
    3. Gets user reviews and ratings
    4. Checks weather forecast
    5. Creates a complete travel plan
    
    This is a proof-of-concept demonstrating the MCP skill integration
    pattern for future full implementation.
    """
    import time
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    app_logger.info(f"[{request_id}] Starting demo planning for {request.destination}")
    
    try:
        mcp_client = get_mcp_client()
        
        # Prepare parameters
        params = {
            "destination": request.destination,
            "duration_days": request.duration_days,
            "budget": request.budget,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "interests": request.interests,
            "accommodation_type": request.accommodation_type,
            "pace": request.pace
        }
        
        # Get the skill template
        template_name = request.use_template
        template = getattr(MCPSkillsPlanner.TEMPLATES, template_name, MCPSkillsPlanner.TEMPLATES["comprehensive"])
        
        # Fill template with parameters
        calls = MCPSkillsPlanner.fill_parameters(template, params)
        
        # Execute skills
        app_logger.info(f"[{request_id}] Executing {len(calls)} skills")
        skill_results = {}
        
        for call in calls:
            skill_name = call["skill"]
            parameters = call["parameters"]
            
            app_logger.info(f"[{request_id}] Calling skill: {skill_name}")
            
            result = await mcp_client.call_skill(skill_name, parameters)
            
            skill_results[skill_name] = {
                "success": result.success,
                "error": result.error,
                "data": result.result
            }
        
        # Create the final plan
        app_logger.info(f"[{request_id}] Creating final travel plan")
        plan_result = await mcp_client.call_skill(
            "create_travel_plan",
            {
                "destination": request.destination,
                "duration_days": request.duration_days,
                "budget": request.budget,
                "travel_dates": {"start": request.start_date, "end": request.end_date},
                "interests": request.interests,
                "accommodation_type": request.accommodation_type,
                "pace": request.pace
            }
        )
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        return DemoPlanningResponse(
            request_id=request_id,
            destination=request.destination,
            skills_used=[c["skill"] for c in calls],
            skill_results=skill_results,
            travel_plan=plan_result.result if plan_result.success else {"error": plan_result.error}
        )
        
    except Exception as e:
        app_logger.error(f"[{request_id}] Demo planning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.is_development
    )
