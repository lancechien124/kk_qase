"""
Request Validation Middleware
"""
from typing import Callable
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import json
from app.core.logging import logger


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Request validation middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Validate request size
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                max_size = 1024 * 1024 * 1024  # 1GB
                if size > max_size:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={"detail": "Request entity too large"}
                    )
            except ValueError:
                pass
        
        # Validate content type for POST/PUT/PATCH
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if content_type and not any(
                content_type.startswith(ct) for ct in [
                    "application/json",
                    "application/x-www-form-urlencoded",
                    "multipart/form-data",
                    "text/plain",
                ]
            ):
                # Allow if it's a file upload endpoint
                if "/upload" not in str(request.url.path):
                    logger.warning(f"Invalid content type: {content_type} for {request.url.path}")
        
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Request validation error: {e}")
            raise

