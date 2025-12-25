"""
FastAPI 主应用入口
提供 Agent 服务的 HTTP API 接口
"""
from contextlib import asynccontextmanager
from typing import Any, Dict
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from models.schemas import PlanningRequest, PlanningResponse, HealthResponse
from workflows import PlanningWorkflow
from utils.logger import app_logger
from utils.db import db_manager
from utils.claude import claude_client
from utils.api_client import backend_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger.info("Starting Travel Assistant Agent service...")
    
    db_manager.init()
    claude_client.init()
    
    app_logger.info("Service started successfully")
    yield
    
    app_logger.info("Shutting down...")
    db_manager.close()
    await backend_client.close()
    app_logger.info("Service stopped")


app = FastAPI(
    title=settings.app_name,
    description="AI Travel Assistant Agent Service",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.is_development
    )
