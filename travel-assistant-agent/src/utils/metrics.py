"""性能指标收集和监控"""

from typing import Dict, Any
import time
from collections import defaultdict
from utils.logger import app_logger

class MetricsCollector:
    """收集系统性能指标"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
    
    def record_api_call(
        self,
        api_name: str,
        duration_ms: float,
        success: bool,
        status_code: int = None
    ):
        """记录API调用"""
        
        self.metrics[f"api.{api_name}.duration"].append(duration_ms)
        
        if success:
            self.counters[f"api.{api_name}.success"] += 1
        else:
            self.counters[f"api.{api_name}.failure"] += 1
        
        if status_code:
            self.counters[f"api.{api_name}.status.{status_code}"] += 1
    
    def record_skill_execution(
        self,
        skill_name: str,
        duration_ms: float,
        success: bool
    ):
        """记录skill执行"""
        
        self.metrics[f"skill.{skill_name}.duration"].append(duration_ms)
        
        if success:
            self.counters[f"skill.{skill_name}.success"] += 1
        else:
            self.counters[f"skill.{skill_name}.failure"] += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        
        summary = {
            "counters": dict(self.counters),
            "metrics": {}
        }
        
        # 计算平均值和其他统计
        for metric_name, values in self.metrics.items():
            if values:
                summary["metrics"][metric_name] = {
                    "count": len(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values)
                }
        
        return summary

# 全局指标收集器
metrics = MetricsCollector()
