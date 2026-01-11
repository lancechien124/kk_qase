"""
Metrics Middleware for Request Tracking
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time

from app.core.metrics import request_metrics
from app.core.logging import logger


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to track request metrics"""
    
    async def dispatch(self, request: Request, call_next):
        # Record start time
        start_time = time.time()
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Record metrics
            is_error = response.status_code >= 400
            request_metrics.record_request(response_time, is_error=is_error)
            
            # Add response time header
            response.headers["X-Response-Time"] = f"{response_time:.3f}"
            
            return response
        except Exception as e:
            # Calculate response time even on error
            response_time = time.time() - start_time
            request_metrics.record_request(response_time, is_error=True)
            logger.error(f"Request error: {e}")
            raise


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured logging"""
    
    async def dispatch(self, request: Request, call_next):
        # Log request
        start_time = time.time()
        
        logger.info(
            "Request started",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client": request.client.host if request.client else None,
            }
        )
        
        try:
            response = await call_next(request)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Log response
            logger.info(
                "Request completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "response_time": round(response_time, 3),
                }
            )
            
            return response
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(
                "Request failed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "response_time": round(response_time, 3),
                },
                exc_info=True,
            )
            raise

