"""日志查看和分析工具"""

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta

class LogViewer:
    """查看和分析日志文件"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
    
    def get_logs_by_request_id(self, request_id: str) -> List[Dict[str, Any]]:
        """获取特定请求ID的所有日志"""
        
        logs = []
        
        # 遍历所有日志文件
        for log_file in self.log_dir.glob("*.log"):
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line)
                        if log_entry.get("request_id") == request_id:
                            logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue
        
        # 按时间戳排序
        logs.sort(key=lambda x: x.get("timestamp", ""))
        return logs
    
    def get_errors_since(self, hours: int = 1) -> List[Dict[str, Any]]:
        """获取最近N小时的所有错误"""
        
        errors = []
        since = datetime.now() - timedelta(hours=hours)
        
        for log_file in self.log_dir.glob("*.log"):
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line)
                        if log_entry.get("level") == "ERROR":
                            timestamp_str = log_entry.get("timestamp", "")
                            if timestamp_str:
                                # 处理 ISO 格式的时间戳
                                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                if timestamp.replace(tzinfo=None) > since:
                                    errors.append(log_entry)
                    except (json.JSONDecodeError, ValueError):
                        continue
        
        return errors
