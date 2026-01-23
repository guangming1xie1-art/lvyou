"""
FastAPI 主应用入口
提供 Agent 服务的 HTTP API 接口
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from workflows.main_workflow import run_main_workflow_async
from api.routes import router, chat_router, rag_router
from api.auth_routes import router as auth_router

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
    expose_headers=["X-Process-Time", "X-Performance", "Content-Length"],
)

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
