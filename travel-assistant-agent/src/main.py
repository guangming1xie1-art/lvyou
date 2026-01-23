"""
FastAPI 主应用入口
提供 Agent 服务的 HTTP API 接口
"""
import os
import uuid
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from workflows.main_workflow import run_main_workflow_async
from api.routes import router, chat_router, rag_router
from api.auth_routes import router as auth_router
from utils.structured_logger import (
    StructuredLogger, 
    set_request_context, 
    clear_request_context,
    get_request_id,
    get_app_logger
)
from config.logging_config import LOGGING_CONFIG

# 初始化日志系统
StructuredLogger.setup_logging(
    log_level=LOGGING_CONFIG["log_level"],
    log_dir=LOGGING_CONFIG["log_dir"],
    app_log_file=LOGGING_CONFIG["app_log_file"],
    access_log_file=LOGGING_CONFIG["access_log_file"],
    error_log_file=LOGGING_CONFIG["error_log_file"],
    enable_console=LOGGING_CONFIG["enable_console"]
)

logger = get_app_logger(__name__)

app = FastAPI(title="Travel Assistant Agent API", version="2.0.0")

# 配置 CORS
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

def get_allowed_origins() -> list[str]:
    from conf import settings
    # 分割 cors_origins 字符串为列表
    origins = [origin.strip() for origin in settings.cors_origins.split(",")]
    return origins

allowed_origins = get_allowed_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-Performance", "Content-Length", "X-Request-ID"],
)

# 中间件：请求追踪和日志
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """
    请求追踪中间件
    - 为每个请求生成唯一ID
    - 记录请求信息
    - 记录响应时间
    """
    # 从请求header中获取或生成request_id
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    
    # 从header中获取user_id（如果有）
    user_id = request.headers.get("X-User-ID") or "anonymous"
    
    # 设置请求上下文
    set_request_context(
        request_id=request_id,
        user_id=user_id
    )
    
    # 记录请求信息
    start_time = time.time()
    logger.info(
        f"Incoming request: {request.method} {request.url.path}",
        extra={
            "extra_method": request.method,
            "extra_path": request.url.path,
            "extra_query_params": dict(request.query_params)
        }
    )
    
    try:
        response = await call_next(request)
        
        # 记录响应信息
        duration = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "extra_method": request.method,
                "extra_path": request.url.path,
                "extra_status_code": response.status_code,
                "extra_duration_ms": round(duration * 1000, 2)
            }
        )
        
        # 在响应头中添加request_id
        response.headers["X-Request-ID"] = request_id
        
        return response
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path}",
            exc_info=True,
            extra={
                "extra_method": request.method,
                "extra_path": request.url.path,
                "extra_error": str(e),
                "extra_duration_ms": round(duration * 1000, 2)
            }
        )
        raise
    finally:
        # 清除请求上下文
        clear_request_context()

# Register routers
app.include_router(auth_router)  # 新增：认证路由
app.include_router(router)       # 现有：agent业务路由
app.include_router(chat_router)  # 现有：chat路由
app.include_router(rag_router)   # 现有：rag路由

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """唯一入口：接收用户消息，调用主代理"""
    result = await run_main_workflow_async(request.message)
    
    return {
        "status": "success",
        "response": result.get("final_response", ""),
        "total_usage": result.get("total_usage", {}),
        "details": {
            "collected_info": result.get("collected_info", {}),
            "search_results": result.get("search_results", {}),
            "recommendations": result.get("recommendations", {}),
            "booking": result.get("booking_confirmation", {})
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
