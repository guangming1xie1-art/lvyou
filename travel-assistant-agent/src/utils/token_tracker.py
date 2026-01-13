"""
Token 使用追踪器
用于统计工作流中每个节点的 token 消耗，生成性能报告
"""
import time
import json
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from loguru import logger


@dataclass
class NodeTokenUsage:
    """节点 token 使用统计"""
    node_name: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    execution_time_ms: float = 0.0
    start_time: float = 0.0
    end_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


class TokenTracker:
    """Token 使用追踪器"""
    
    def __init__(self):
        self.node_usages: Dict[str, NodeTokenUsage] = {}
        self.total_tokens = 0
        self.total_execution_time = 0.0
        self.request_id: Optional[str] = None
        self.start_time: Optional[float] = None
        
    def start_request(self, request_id: str):
        """开始追踪一个请求"""
        self.request_id = request_id
        self.start_time = time.time()
        self.node_usages.clear()
        self.total_tokens = 0
        self.total_execution_time = 0.0
        logger.info(f"[{request_id}] Started token tracking")
        
    def start_node(self, node_name: str) -> float:
        """开始追踪一个节点"""
        start_time = time.time()
        if node_name not in self.node_usages:
            self.node_usages[node_name] = NodeTokenUsage(node_name=node_name)
        
        usage = self.node_usages[node_name]
        usage.start_time = start_time
        logger.debug(f"[{self.request_id}] Started node '{node_name}'")
        return start_time
        
    def end_node(self, node_name: str, 
                 input_tokens: int = 0, 
                 output_tokens: int = 0,
                 success: bool = True,
                 error_message: Optional[str] = None):
        """结束节点追踪"""
        if node_name not in self.node_usages:
            logger.warning(f"[{self.request_id}] Node '{node_name}' not started")
            return
            
        usage = self.node_usages[node_name]
        usage.end_time = time.time()
        usage.input_tokens = input_tokens
        usage.output_tokens = output_tokens
        usage.total_tokens = input_tokens + output_tokens
        usage.execution_time_ms = (usage.end_time - usage.start_time) * 1000
        usage.success = success
        usage.error_message = error_message
        
        self.total_tokens += usage.total_tokens
        self.total_execution_time += usage.execution_time_ms
        
        logger.info(f"[{self.request_id}] Completed node '{node_name}': "
                   f"{usage.total_tokens} tokens, {usage.execution_time_ms:.1f}ms")
        
    def add_tokens(self, node_name: str, input_tokens: int = 0, output_tokens: int = 0):
        """添加 token 使用"""
        if node_name not in self.node_usages:
            self.node_usages[node_name] = NodeTokenUsage(node_name=node_name)
            
        usage = self.node_usages[node_name]
        usage.input_tokens += input_tokens
        usage.output_tokens += output_tokens
        usage.total_tokens += input_tokens + output_tokens
        
    def get_node_usage(self, node_name: str) -> Optional[NodeTokenUsage]:
        """获取节点使用统计"""
        return self.node_usages.get(node_name)
        
    def get_total_tokens(self) -> int:
        """获取总 token 使用量"""
        return self.total_tokens
        
    def get_node_breakdown(self) -> Dict[str, NodeTokenUsage]:
        """获取节点分解统计"""
        return dict(self.node_usages)
        
    def generate_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        if not self.start_time:
            return {"error": "No tracking data available"}
            
        total_time = time.time() - self.start_time
        
        # 节点统计
        nodes_data = {}
        for name, usage in self.node_usages.items():
            nodes_data[name] = asdict(usage)
            
        # 计算性能指标
        avg_tokens_per_node = self.total_tokens / len(self.node_usages) if self.node_usages else 0
        avg_time_per_node = self.total_execution_time / len(self.node_usages) if self.node_usages else 0
        
        # 最消耗资源的节点
        most_tokens_node = max(self.node_usages.items(), 
                             key=lambda x: x[1].total_tokens)[0] if self.node_usages else None
        slowest_node = max(self.node_usages.items(), 
                         key=lambda x: x[1].execution_time_ms)[0] if self.node_usages else None
        
        report = {
            "request_id": self.request_id,
            "total_tokens": self.total_tokens,
            "total_execution_time_ms": total_time * 1000,
            "node_count": len(self.node_usages),
            "average_tokens_per_node": round(avg_tokens_per_node, 2),
            "average_time_per_node_ms": round(avg_time_per_node, 2),
            "nodes": nodes_data,
            "performance_summary": {
                "most_tokens_node": most_tokens_node,
                "slowest_node": slowest_node,
                "success_rate": sum(1 for u in self.node_usages.values() if u.success) / len(self.node_usages) if self.node_usages else 0
            },
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info(f"[{self.request_id}] Generated token report: {self.total_tokens} tokens total")
        return report
        
    def reset(self):
        """重置追踪器"""
        self.node_usages.clear()
        self.total_tokens = 0
        self.total_execution_time = 0.0
        self.request_id = None
        self.start_time = None
        
    def export_json(self) -> str:
        """导出 JSON 格式的报告"""
        return json.dumps(self.generate_report(), indent=2, ensure_ascii=False)
        
    def get_efficiency_score(self) -> float:
        """计算效率分数（0-100）"""
        if not self.node_usages:
            return 0.0
            
        # 基于 token 效率和时间效率计算分数
        avg_tokens = self.total_tokens / len(self.node_usages)
        avg_time = self.total_execution_time / len(self.node_usages)
        
        # 标准化分数（示例值）
        token_score = max(0, 100 - (avg_tokens - 1000) / 10)  # 1000 tokens 为基准
        time_score = max(0, 100 - (avg_time - 500) / 5)       # 500ms 为基准
        
        return round((token_score + time_score) / 2, 2)