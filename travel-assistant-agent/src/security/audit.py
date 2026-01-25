"""
Audit logging for security and compliance
"""
import json
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import Request
from utils.logger import app_logger


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
        Log API call to structured log
        ✅ Changed to log output, no database writes
        
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
            
            # Output structured log
            extra_fields = {
                "extra_user_id": user_id,
                "extra_action": action,
                "extra_endpoint": endpoint,
                "extra_method": method,
                "extra_result": result,
            }
            
            if ip_address:
                extra_fields["extra_ip_address"] = ip_address
            if user_agent:
                extra_fields["extra_user_agent"] = user_agent
            if error_message:
                extra_fields["extra_error_message"] = error_message
            if filtered_params:
                extra_fields["extra_params"] = filtered_params
            
            # Log level based on result
            if result == "success":
                app_logger.info(f"API: {action} by {user_id}", extra=extra_fields)
            else:
                app_logger.warning(f"API: {action} by {user_id} FAILED", extra=extra_fields)
                
        except Exception as e:
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
        Log security event to structured log
        ✅ Changed to log output, no database writes
        
        Args:
            event_type: Type of security event (e.g., "auth_failure", "rate_limit_exceeded")
            severity: Severity level (low, medium, high, critical)
            description: Event description
            user_id: User ID if applicable
            ip_address: Client IP address
            details: Additional event details
        """
        try:
            extra_fields = {
                "extra_event_type": event_type,
                "extra_severity": severity,
            }
            
            if user_id:
                extra_fields["extra_user_id"] = user_id
            if ip_address:
                extra_fields["extra_ip_address"] = ip_address
            if details:
                extra_fields["extra_details"] = details
            
            # Log level based on severity
            log_message = f"SECURITY [{severity}]: {description}"
            if severity in ["high", "critical"]:
                app_logger.error(log_message, extra=extra_fields)
            else:
                app_logger.warning(log_message, extra=extra_fields)
                
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


# Global audit logger instance
audit_logger = AuditLogger()
