"""
工具调用追踪器 - 记录所有工具调用的详细信息

用途：
1. 监控工具调用频率和性能
2. 调试工具绑定问题
3. 审计工具使用情况
"""

import logging
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ToolInvocationLogger:
    """
    工具调用追踪器
    
    记录每次工具调用的：
    - 工具名称
    - 输入参数
    - 返回结果（摘要）
    - 执行耗时
    - 缓存命中情况
    - 错误信息
    """
    
    def __init__(self):
        self.invocations = []
        self.stats = {
            "total_calls": 0,
            "success_calls": 0,
            "failed_calls": 0,
            "total_duration": 0.0,
            "cache_hits": 0
        }
    
    def log_invocation(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        result: Optional[Any] = None,
        error: Optional[str] = None,
        duration: float = 0.0,
        cache_hit: bool = False
    ):
        """
        记录一次工具调用
        
        Args:
            tool_name: 工具名称
            parameters: 输入参数
            result: 返回结果
            error: 错误信息（如果失败）
            duration: 执行耗时（秒）
            cache_hit: 是否缓存命中
        """
        # 创建调用记录
        invocation = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "parameters": parameters,
            "result_summary": self._summarize_result(result),
            "error": error,
            "duration": duration,
            "cache_hit": cache_hit,
            "status": "success" if error is None else "failed"
        }
        
        self.invocations.append(invocation)
        
        # 更新统计
        self.stats["total_calls"] += 1
        if error is None:
            self.stats["success_calls"] += 1
        else:
            self.stats["failed_calls"] += 1
        self.stats["total_duration"] += duration
        if cache_hit:
            self.stats["cache_hits"] += 1
        
        # 输出结构化日志
        self._log_structured(invocation)
    
    def _summarize_result(self, result: Any, max_length: int = 200) -> str:
        """
        生成结果摘要
        
        Args:
            result: 原始结果
            max_length: 最大长度
            
        Returns:
            结果摘要字符串
        """
        if result is None:
            return "None"
        
        result_str = str(result)
        if len(result_str) > max_length:
            return result_str[:max_length] + "..."
        return result_str
    
    def _log_structured(self, invocation: Dict[str, Any]):
        """
        输出结构化日志
        
        Args:
            invocation: 调用记录
        """
        status_emoji = "✅" if invocation["status"] == "success" else "❌"
        cache_emoji = "💾" if invocation["cache_hit"] else "🌐"
        
        log_msg = (
            f"{status_emoji} {cache_emoji} Tool: {invocation['tool_name']} | "
            f"Duration: {invocation['duration']:.2f}s | "
            f"Status: {invocation['status']}"
        )
        
        extra_fields = {
            "extra_tool_name": invocation["tool_name"],
            "extra_duration": invocation["duration"],
            "extra_status": invocation["status"],
            "extra_cache_hit": invocation["cache_hit"],
            "extra_parameters": json.dumps(invocation["parameters"], ensure_ascii=False),
            "extra_result_summary": invocation["result_summary"]
        }
        
        if invocation["error"]:
            extra_fields["extra_error"] = invocation["error"]
            logger.error(log_msg, extra=extra_fields)
        else:
            logger.info(log_msg, extra=extra_fields)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计字典
        """
        avg_duration = (
            self.stats["total_duration"] / self.stats["total_calls"]
            if self.stats["total_calls"] > 0
            else 0.0
        )
        
        cache_hit_rate = (
            self.stats["cache_hits"] / self.stats["total_calls"]
            if self.stats["total_calls"] > 0
            else 0.0
        )
        
        success_rate = (
            self.stats["success_calls"] / self.stats["total_calls"]
            if self.stats["total_calls"] > 0
            else 0.0
        )
        
        return {
            **self.stats,
            "avg_duration": avg_duration,
            "cache_hit_rate": cache_hit_rate,
            "success_rate": success_rate
        }
    
    def get_invocations(self, limit: Optional[int] = None) -> list:
        """
        获取调用记录
        
        Args:
            limit: 限制返回数量（最近的 N 条）
            
        Returns:
            调用记录列表
        """
        if limit:
            return self.invocations[-limit:]
        return self.invocations
    
    def clear(self):
        """清空记录"""
        self.invocations.clear()
        self.stats = {
            "total_calls": 0,
            "success_calls": 0,
            "failed_calls": 0,
            "total_duration": 0.0,
            "cache_hits": 0
        }
        logger.info("Tool invocation logs cleared")
    
    def report(self) -> str:
        """
        生成调用报告
        
        Returns:
            格式化的报告字符串
        """
        stats = self.get_stats()
        
        report = f"""
========== Tool Invocation Report ==========
Total Calls:    {stats['total_calls']}
Success:        {stats['success_calls']} ({stats['success_rate']*100:.1f}%)
Failed:         {stats['failed_calls']}
Cache Hits:     {stats['cache_hits']} ({stats['cache_hit_rate']*100:.1f}%)
Total Duration: {stats['total_duration']:.2f}s
Avg Duration:   {stats['avg_duration']:.2f}s
===========================================
"""
        return report


# 全局单例
_tool_invocation_logger: Optional[ToolInvocationLogger] = None


def get_tool_invocation_logger() -> ToolInvocationLogger:
    """
    获取全局工具调用追踪器
    
    Returns:
        ToolInvocationLogger 实例
    """
    global _tool_invocation_logger
    if _tool_invocation_logger is None:
        _tool_invocation_logger = ToolInvocationLogger()
    return _tool_invocation_logger


__all__ = [
    "ToolInvocationLogger",
    "get_tool_invocation_logger",
]
