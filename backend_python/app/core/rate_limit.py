"""
Rate Limiting Middleware
"""
from typing import Callable, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
from app.core.redis import redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis"""
    
    def __init__(
        self,
        app,
        calls: int = 100,
        period: int = 60,  # seconds
        per_user: bool = True,
    ):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.per_user = per_user
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip rate limiting for certain paths
        if request.url.path.startswith("/api/docs") or request.url.path.startswith("/api/redoc"):
            return await call_next(request)
        
        # Get identifier (user ID or IP)
        identifier = await self._get_identifier(request)
        
        if identifier:
            # Check rate limit
            allowed = await self._check_rate_limit(identifier, request.url.path)
            
            if not allowed:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": f"Rate limit exceeded: {self.calls} requests per {self.period} seconds"
                    },
                    headers={
                        "Retry-After": str(self.period),
                        "X-RateLimit-Limit": str(self.calls),
                        "X-RateLimit-Remaining": "0",
                    }
                )
        
        response = await call_next(request)
        
        # Add rate limit headers
        if identifier:
            remaining = await self._get_remaining(identifier, request.url.path)
            response.headers["X-RateLimit-Limit"] = str(self.calls)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
    
    async def _get_identifier(self, request: Request) -> Optional[str]:
        """Get rate limit identifier (user ID or IP)"""
        if self.per_user:
            # Try to get user ID from token
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                try:
                    from jose import jwt
                    from app.core.config import settings
                    token = auth_header.split(" ")[1]
                    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                    user_id = payload.get("user_id")
                    if user_id:
                        return f"user:{user_id}"
                except Exception:
                    pass
        
        # Fallback to IP address
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"
    
    async def _check_rate_limit(self, identifier: str, path: str) -> bool:
        """Check if request is within rate limit"""
        key = f"rate_limit:{identifier}:{path}"
        
        try:
            # Get current count
            count = await redis_client.get_cache(key)
            if count is None:
                count = 0
            
            # Check if limit exceeded
            if count >= self.calls:
                return False
            
            # Increment count
            await redis_client.set_cache(
                key,
                count + 1,
                expire=self.period
            )
            
            return True
        except Exception:
            # If Redis fails, allow request (fail open)
            return True
    
    async def _get_remaining(self, identifier: str, path: str) -> int:
        """Get remaining requests"""
        key = f"rate_limit:{identifier}:{path}"
        
        try:
            count = await redis_client.get_cache(key)
            if count is None:
                return self.calls
            return max(0, self.calls - count)
        except Exception:
            return self.calls


# Simple in-memory rate limiter (fallback if Redis is not available)
class SimpleRateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, calls: int = 100, period: int = 60):
        self.calls = calls
        self.period = period
        self._requests = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        requests = self._requests[identifier]
        
        # Remove old requests
        requests[:] = [req_time for req_time in requests if now - req_time < self.period]
        
        # Check limit
        if len(requests) >= self.calls:
            return False
        
        # Add current request
        requests.append(now)
        return True

