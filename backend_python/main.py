"""
MeterSphere Python Backend - Main Application Entry Point
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import setup_logging
# Import all models to ensure they are registered with SQLAlchemy
from app.models import *  # noqa: F401, F403
from app.core.redis import redis_client
from app.core.kafka import kafka_producer
from app.core.minio import minio_client
from app.core.rate_limit import RateLimitMiddleware
from app.core.request_validation import RequestValidationMiddleware
from app.core.i18n_middleware import I18nMiddleware
from app.core.metrics_middleware import MetricsMiddleware, StructuredLoggingMiddleware
from app.api.v1 import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    setup_logging()
    await init_db()
    
    # Initialize Redis
    try:
        await redis_client.connect()
        print("✓ Redis connected")
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
    
    # Initialize MinIO
    try:
        minio_client.get_client()
        print("✓ MinIO connected")
    except Exception as e:
        print(f"✗ MinIO connection failed: {e}")
    
    # Kafka producer is lazy-initialized, no need to connect here
    
    yield
    
    # Shutdown
    await redis_client.disconnect()
    kafka_producer.close()
    print("✓ Cleaned up connections")


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="MeterSphere API",
        description="新一代的开源持续测试工具 - Python 版本",
        version="3.0.0",
        lifespan=lifespan,
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        openapi_tags=[
            {"name": "认证", "description": "用户认证相关接口"},
            {"name": "用户管理", "description": "用户管理相关接口"},
            {"name": "API测试", "description": "API测试相关接口"},
            {"name": "缺陷管理", "description": "缺陷管理相关接口"},
            {"name": "用例管理", "description": "功能用例管理相关接口"},
            {"name": "仪表板", "description": "仪表板数据相关接口"},
            {"name": "项目管理", "description": "项目管理相关接口"},
            {"name": "系统设置", "description": "系统设置相关接口"},
            {"name": "测试计划", "description": "测试计划相关接口"},
            {"name": "文件管理", "description": "文件上传下载相关接口"},
            {"name": "导入导出", "description": "数据导入导出相关接口"},
            {"name": "JMeter整合", "description": "JMeter脚本执行相关接口"},
            {"name": "AI功能", "description": "AI辅助测试相关接口"},
            {"name": "国际化", "description": "国际化相关接口"},
        ],
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # GZip Middleware
    app.add_middleware(GZipMiddleware, minimum_size=2048)

    # i18n Middleware (should be early in the stack)
    app.add_middleware(I18nMiddleware)

    # Structured Logging Middleware (should be early to log all requests)
    app.add_middleware(StructuredLoggingMiddleware)

    # Metrics Middleware (track request metrics)
    app.add_middleware(MetricsMiddleware)

    # Request Validation Middleware
    app.add_middleware(RequestValidationMiddleware)

    # Rate Limiting Middleware
    app.add_middleware(
        RateLimitMiddleware,
        calls=100,  # 100 requests
        period=60,   # per 60 seconds
        per_user=True,
    )

    # Include routers
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )

