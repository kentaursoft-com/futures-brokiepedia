"""Middleware for API server - rate limiting, auth, logging."""
import logging
import time
from typing import Callable
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware."""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host
        now = time.time()
        
        # Clean old entries
        self.requests = {
            ip: times for ip, times in self.requests.items()
            if any(t > now - 60 for t in times)
        }
        
        # Check rate limit
        client_requests = self.requests.get(client_ip, [])
        client_requests = [t for t in client_requests if t > now - 60]
        
        if len(client_requests) >= self.requests_per_minute:
            return Response(
                content='{"error": "Rate limit exceeded"}',
                status_code=429,
                media_type="application/json"
            )
        
        client_requests.append(now)
        self.requests[client_ip] = client_requests
        
        return await call_next(request)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/response logging middleware."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start
        logger.info(
            f"{request.method} {request.url.path} - "
            f"{response.status_code} - {duration:.3f}s"
        )
        
        return response
