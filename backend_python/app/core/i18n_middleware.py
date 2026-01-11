"""
i18n Middleware for FastAPI
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.i18n import Translator, get_locale_from_header, parse_locale
from app.core.config import settings


class I18nMiddleware(BaseHTTPMiddleware):
    """Middleware to handle i18n locale detection and setting"""
    
    async def dispatch(self, request: Request, call_next):
        # Get locale from query parameter, header, or default
        locale = None
        
        # Check query parameter first
        if "locale" in request.query_params:
            locale = parse_locale(request.query_params["locale"])
        
        # Check Accept-Language header
        if not locale:
            accept_language = request.headers.get("Accept-Language")
            locale = get_locale_from_header(accept_language)
        
        # Set locale in Translator
        Translator.set_locale(locale)
        
        # Store locale in request state for access in endpoints
        request.state.locale = locale
        
        # Process request
        response = await call_next(request)
        
        # Add locale to response headers
        response.headers["Content-Language"] = locale
        
        return response

