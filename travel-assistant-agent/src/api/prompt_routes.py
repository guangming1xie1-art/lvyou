"""提示词相关的API路由

提供提示词的热更新、健康检查等接口。
支持通过消息队列通知所有Agent节点更新提示词。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from prompts.prompt_loader import prompt_loader
from prompts.prompt_cache import prompt_cache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


class PromptUpdateRequest(BaseModel):
    """提示词更新请求"""
    category: str
    name: str
    version: Optional[str] = None
    updated_by: Optional[str] = None
    update_type: str = "update"


class ReloadAllRequest(BaseModel):
    """全量重新加载请求"""
    reason: Optional[str] = "manual_trigger"
    notify_mq: Optional[bool] = True


@router.post("/reload")
async def reload_prompts() -> Dict[str, Any]:
    """
    热更新提示词
    
    从Java Admin API重新加载提示词并更新缓存。
    当Java Admin更新提示词时，会调用此接口。
    """
    try:
        success = await prompt_loader.reload()
        if success:
            logger.info("Prompts reloaded successfully")
            return {
                "status": "success",
                "message": "Prompts reloaded successfully",
                "stats": prompt_loader.get_stats()
            }
        else:
            logger.warning("Prompts reloaded with fallback")
            return {
                "status": "warning",
                "message": "Prompts reloaded using fallback",
                "stats": prompt_loader.get_stats()
            }
    except Exception as e:
        logger.error(f"Failed to reload prompts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reload prompts: {str(e)}")


@router.post("/reload-all")
async def reload_all_prompts(request: ReloadAllRequest) -> Dict[str, Any]:
    """
    全量重新加载提示词并通知所有节点
    
    重新加载提示词，并通过消息队列通知所有Agent节点更新。
    """
    try:
        success = await prompt_loader.reload()
        prompt_cache.clear()
        
        mq_notified = False
        if request.notify_mq:
            try:
                from prompts.mq_publisher import prompt_mq_publisher
                mq_notified = await prompt_mq_publisher.publish_reload_all(request.reason)
            except Exception as e:
                logger.error(f"Failed to notify MQ: {e}")
        
        return {
            "status": "success" if success else "warning",
            "message": "All prompts reloaded",
            "mq_notified": mq_notified,
            "stats": prompt_loader.get_stats()
        }
    except Exception as e:
        logger.error(f"Failed to reload all prompts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reload all prompts: {str(e)}")


@router.post("/notify-update")
async def notify_prompt_update(request: PromptUpdateRequest) -> Dict[str, Any]:
    """
    通知提示词更新
    
    通过消息队列通知所有Agent节点某个提示词已更新。
    """
    try:
        from prompts.mq_publisher import prompt_mq_publisher
        
        if request.update_type == "create":
            success = await prompt_mq_publisher.publish_prompt_created(
                category=request.category,
                name=request.name,
                version=request.version or "1.0.0",
                updated_by=request.updated_by
            )
        elif request.update_type == "update":
            success = await prompt_mq_publisher.publish_prompt_updated(
                category=request.category,
                name=request.name,
                version=request.version or "1.0.0",
                updated_by=request.updated_by
            )
        elif request.update_type == "delete":
            success = await prompt_mq_publisher.publish_prompt_deleted(
                category=request.category,
                name=request.name,
                updated_by=request.updated_by
            )
        else:
            raise HTTPException(status_code=400, detail=f"Invalid update_type: {request.update_type}")
        
        return {
            "status": "success" if success else "failed",
            "message": f"Prompt {request.update_type} notification sent",
            "category": request.category,
            "name": request.name
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to notify prompt update: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to notify prompt update: {str(e)}")


@router.get("/health")
async def check_prompt_health() -> Dict[str, Any]:
    """
    检查提示词状态
    
    返回提示词加载器和缓存的状态信息。
    """
    try:
        mq_status = {}
        try:
            from prompts.mq_consumer import prompt_mq_consumer
            from prompts.mq_publisher import prompt_mq_publisher
            mq_status = {
                "consumer": prompt_mq_consumer.get_status(),
                "publisher": prompt_mq_publisher.get_status()
            }
        except Exception:
            pass
        
        return {
            "status": "healthy",
            "loader_stats": prompt_loader.get_stats(),
            "cache_stats": prompt_cache.get_stats(),
            "mq_stats": mq_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/list")
async def list_prompts() -> Dict[str, Any]:
    """
    获取所有提示词
    
    返回当前缓存中的所有提示词信息。
    """
    try:
        prompts = prompt_loader.get_all()
        return {
            "status": "success",
            "count": len(prompts),
            "prompts": prompts
        }
    except Exception as e:
        logger.error(f"Failed to list prompts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list prompts: {str(e)}")


@router.post("/test")
async def test_prompt_rendering(content: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    测试提示词渲染
    
    测试提示词的变量替换功能。
    """
    from prompts.prompt_renderer import prompt_renderer
    
    try:
        rendered = prompt_renderer.render(content, variables)
        return {
            "status": "success",
            "rendered": rendered,
            "variables": variables
        }
    except Exception as e:
        logger.error(f"Failed to test prompt rendering: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test prompt rendering: {str(e)}")
