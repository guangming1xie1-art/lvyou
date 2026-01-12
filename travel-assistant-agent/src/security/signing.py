"""
Request signing and verification for API security
"""
import hmac
import hashlib
from typing import Dict, Any
from fastapi import HTTPException, Request, status
from ..utils.logger import app_logger


class RequestSigner:
    """Request signing for additional API security"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def sign_request(
        self,
        method: str,
        path: str,
        body: str = "",
        timestamp: str = ""
    ) -> str:
        """
        Sign a request with HMAC-SHA256
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            body: Request body (for POST/PUT)
            timestamp: Request timestamp (optional)
        
        Returns:
            Hexadecimal signature string
        """
        # Build signature string
        signature_parts = [method.upper(), path]
        if timestamp:
            signature_parts.append(timestamp)
        if body:
            signature_parts.append(body)
        
        signature_string = "\n".join(signature_parts)
        
        # Create HMAC signature
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            signature_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_signature(
        self,
        signature: str,
        method: str,
        path: str,
        body: str = "",
        timestamp: str = ""
    ) -> bool:
        """
        Verify request signature
        
        Args:
            signature: Signature from request
            method: HTTP method
            path: Request path
            body: Request body
            timestamp: Request timestamp
        
        Returns:
            True if signature is valid
        """
        expected_signature = self.sign_request(method, path, body, timestamp)
        
        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected_signature, signature)
    
    def extract_signature_from_request(self, request: Request) -> tuple[str, str]:
        """
        Extract signature and timestamp from request headers
        
        Args:
            request: FastAPI request object
        
        Returns:
            Tuple of (signature, timestamp)
        
        Raises:
            HTTPException: If headers are missing
        """
        signature = request.headers.get("X-Signature")
        timestamp = request.headers.get("X-Timestamp")
        
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing X-Signature header"
            )
        
        if not timestamp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing X-Timestamp header"
            )
        
        return signature, timestamp


# Dependency for verifying signed requests
async def verify_signed_request(
    request: Request,
    signer: RequestSigner
):
    """
    Dependency to verify signed requests
    
    Args:
        request: FastAPI request
        signer: RequestSigner instance
    
    Raises:
        HTTPException: If signature is invalid
    """
    signature, timestamp = signer.extract_signature_from_request(request)
    
    # Verify timestamp is recent (prevent replay attacks)
    # Allow 5 minute window
    import time
    try:
        request_time = float(timestamp)
        current_time = time.time()
        
        if abs(current_time - request_time) > 300:  # 5 minutes
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Request timestamp too old or too new"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid timestamp format"
        )
    
    # Read request body
    body_bytes = await request.body()
    body = body_bytes.decode('utf-8') if body_bytes else ""
    
    # Verify signature
    if not signer.verify_signature(
        signature,
        request.method,
        request.url.path,
        body,
        timestamp
    ):
        app_logger.warning(
            f"Invalid signature for {request.method} {request.url.path}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid request signature"
        )
