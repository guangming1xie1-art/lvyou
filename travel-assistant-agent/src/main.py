"""
FastAPI 主应用入口
提供 Agent 服务的 HTTP API 接口
"""
import uuid
import time
import asyncio
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from workflows.main_workflow import run_main_workflow_async
from api.routes import router, chat_router, rag_router, memory_router, prompt_router
from api.auth_routes import router as auth_router
from api.websocket import router as ws_router
from auth.dependencies import get_current_active_user, get_user_token
from auth.models import User
from security import rate_limiter
from utils.structured_logger import (
    StructuredLogger,
    set_request_context,
    clear_request_context,
    get_app_logger,
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # Startup
    logger.info("Starting up Travel Assistant Agent API...")
    
    # 初始化提示词加载器
    try:
        from prompts.prompt_loader import prompt_loader
        await prompt_loader.initialize()
        logger.info("Prompt loader initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize prompt loader: {e}")
    
    # 初始化消息队列消费者
    mq_task = None
    try:
        from prompts.mq_consumer import prompt_mq_consumer
        from prompts.prompt_loader import prompt_loader
        
        async def handle_prompt_update(message: dict):
            """处理提示词更新消息"""
            from prompts.prompt_cache import prompt_cache
            
            update_type = message.get("type")
            category = message.get("category")
            name = message.get("name")
            
            logger.info(f"Processing prompt update: {update_type}, category={category}, name={name}")
            
            if update_type == "reload_all":
                await prompt_loader.reload()
                prompt_cache.clear()
                logger.info("All prompts reloaded from MQ message")
            elif update_type in ["create", "update", "delete"]:
                if category and name:
                    prompt_cache.delete(f"{category}:{name}")
                    if update_type != "delete":
                        await prompt_loader.reload()
                    logger.info(f"Prompt {category}:{name} cache cleared")
                    
        prompt_mq_consumer.set_message_callback(handle_prompt_update)
        mq_task = asyncio.create_task(prompt_mq_consumer.run_forever())
        logger.info("Prompt MQ consumer started")
        
    except Exception as e:
        logger.error(f"Failed to initialize MQ consumer: {e}")
    
    yield  # 应用运行中
    
    # Shutdown
    logger.info("Shutting down Travel Assistant Agent API...")
    
    # 停止消息队列消费者
    try:
        from prompts.mq_consumer import prompt_mq_consumer
        prompt_mq_consumer.stop_consuming()
        if mq_task:
            mq_task.cancel()
        await prompt_mq_consumer.disconnect()
        logger.info("MQ consumer disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting MQ consumer: {e}")


app = FastAPI(title="Travel Assistant Agent API", version="2.0.0", lifespan=lifespan)


# 配置 CORS

def get_allowed_origins() -> list[str]:
    from conf import settings

    return [origin.strip() for origin in settings.cors_origins.split(",")]


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
app.include_router(memory_router)  # 新增：记忆系统路由
app.include_router(ws_router)    # 新增：WebSocket路由
app.include_router(prompt_router)  # 新增：提示词管理路由

class ChatRequest(BaseModel):
    message: str
    session_id: str = None  # 可选：会话ID，用于记忆系统


def _extract_response_from_workflow_result(result: dict) -> str:
    final_response = result.get("final_response")
    if final_response:
        return final_response

    messages = result.get("messages") or []
    if messages:
        last_msg = messages[-1]
        content = getattr(last_msg, "content", None)
        return content if content is not None else str(last_msg)

    return ""


@app.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    http_request: Request,
    current_user: User = Depends(get_current_active_user),
    user_token: str = Depends(get_user_token),
):
    """唯一入口：接收用户消息，调用主代理（支持记忆系统）"""

    if not await rate_limiter.check_limit(http_request, user_id=current_user.id):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {rate_limiter.requests_per_minute} requests per minute.",
        )

    # 如果没有提供session_id，生成一个新的
    session_id = request.session_id or str(uuid.uuid4())

    result = await run_main_workflow_async(
        user_message=request.message,
        user_id=current_user.id,
        session_id=session_id
    )

    collected_info = result.get("collected_info") or {}
    is_complete = bool(collected_info.get("complete", False))

    total_usage = result.get("total_usage", {})

    if not is_complete:
        clarification_message = (
            collected_info.get("message")
            or collected_info.get("raw")
            or "请补充更多信息以便我们为您规划。"
        )
        return {
            "status": "incomplete",
            "response": clarification_message,
            "stage": "collect",
            "total_usage": total_usage,
            "collected_info": collected_info,
            "session_id": session_id,  # 返回会话ID
        }

    return {
        "status": "success",
        "response": _extract_response_from_workflow_result(result),
        "stage": "completed",
        "total_usage": total_usage,
        "details": {
            "collected_info": collected_info,
            "search_results": result.get("search_results") or {},
            "recommendations": result.get("recommendations") or {},
            "booking": result.get("booking_confirmation") or {},
        },
        "session_id": session_id,  # 返回会话ID
        "memory_info": {  # 新增：记忆系统信息
            "long_term_memory_count": result.get("long_term_memory", {}).get("count", 0),
            "rewritten_query": result.get("rewritten_query"),
        },
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
