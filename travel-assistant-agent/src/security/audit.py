"""
Audit logging for security and compliance
"""
import json
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import Request
from utils.logger import app_logger
from utils.db import db_manager


class AuditLogger:
    """Audit logger for API calls and security events"""
    
    async def log_api_call(
        self,
        user_id: str,
        action: str,
        endpoint: str,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        result: str = "success",
        error_message: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        Log API call to audit log
        
        Args:
            user_id: User ID who made the request
            action: Action performed (e.g., "search", "book", "login")
            endpoint: API endpoint called
            method: HTTP method
            params: Request parameters (will be filtered)
            result: Result status ("success" or "failure")
            error_message: Error message if failed
            ip_address: Client IP address
            user_agent: Client user agent
        """
        try:
            # Filter sensitive parameters
            filtered_params = self._filter_sensitive_params(params or {})
            
            audit_data = {
                "user_id": user_id,
                "action": action,
                "endpoint": endpoint,
                "method": method,
                "params": filtered_params,
                "result": result,
                "error_message": error_message,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Log to file (for quick access)
            app_logger.info(f"AUDIT: {action} by {user_id} - {result}")
            
            # Log to database
            await db_manager.create_audit_log(audit_data)
            
        except Exception as e:
            # Don't fail the request if audit logging fails
            app_logger.error(f"Audit logging failed: {e}")
    
    async def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log security event
        
        Args:
            event_type: Type of security event (e.g., "auth_failure", "rate_limit_exceeded")
            severity: Severity level (low, medium, high, critical)
            description: Event description
            user_id: User ID if applicable
            ip_address: Client IP address
            details: Additional event details
        """
        try:
            audit_data = {
                "user_id": user_id,
                "action": f"security_{event_type}",
                "endpoint": "N/A",
                "method": "SECURITY",
                "params": details or {},
                "result": "security_event",
                "error_message": f"{severity}: {description}",
                "ip_address": ip_address,
                "user_agent": None,
                "created_at": datetime.utcnow().isoformat(),
                "metadata": {
                    "event_type": event_type,
                    "severity": severity
                }
            }
            
            # Log to file with severity
            if severity in ["high", "critical"]:
                app_logger.warning(f"SECURITY [{severity}]: {description}")
            else:
                app_logger.info(f"SECURITY [{severity}]: {description}")
            
            # Log to database
            await db_manager.create_audit_log(audit_data)
            
        except Exception as e:
            app_logger.error(f"Security event logging failed: {e}")
    
    def _filter_sensitive_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter sensitive parameters from logs
        
        Args:
            params: Original parameters
        
        Returns:
            Filtered parameters with sensitive data masked
        """
        sensitive_fields = [
            "password", "token", "credit_card", "cvv", "ssn",
            "api_key", "secret", "authorization", "refresh_token"
        ]
        
        filtered = {}
        for key, value in params.items():
            key_lower = key.lower()
            if any(field in key_lower for field in sensitive_fields):
                filtered[key] = "***REDACTED***"
            elif isinstance(value, dict):
                filtered[key] = self._filter_sensitive_params(value)
            elif isinstance(value, list):
                filtered[key] = [
                    self._filter_sensitive_params(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                filtered[key] = value
        
        return filtered
    
    async def get_user_audit_logs(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> list:
        """
        Get audit logs for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of logs to return
            offset: Offset for pagination
        
        Returns:
            List of audit logs
        """
        return await db_manager.get_user_audit_logs(user_id, limit, offset)
    
    async def get_security_events(
        self,
        severity: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list:
        """
        Get security events
        
        Args:
            severity: Filter by severity
            limit: Maximum number of events to return
            offset: Offset for pagination
        
        Returns:
            List of security events
        """
        return await db_manager.get_security_events(severity, limit, offset)


# Global audit logger instance
audit_logger = AuditLogger()
