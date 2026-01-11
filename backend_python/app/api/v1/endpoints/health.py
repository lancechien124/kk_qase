"""
Health Check and Monitoring Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from datetime import datetime
import time

from app.core.database import get_db
from app.core.redis import redis_client
from app.core.minio import minio_client
from app.core.kafka import kafka_producer
from app.core.config import settings
from app.core.logging import logger

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint
    
    Returns:
        Health status of the application
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0",
        "checks": {},
    }
    
    # Check database
    try:
        from app.core.database import get_db
        async for db in get_db():
            await db.execute("SELECT 1")
            health_status["checks"]["database"] = {
                "status": "healthy",
                "message": "Database connection successful",
            }
            break
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": str(e),
        }
    
    # Check Redis
    try:
        client = await redis_client.get_client()
        await client.ping()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful",
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "message": str(e),
        }
    
    # Check MinIO
    try:
        minio_client.get_client()
        health_status["checks"]["minio"] = {
            "status": "healthy",
            "message": "MinIO connection successful",
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["minio"] = {
            "status": "unhealthy",
            "message": str(e),
        }
    
    # Check Kafka (optional)
    try:
        # Kafka producer is lazy-initialized, just check if it can be created
        if kafka_producer:
            health_status["checks"]["kafka"] = {
                "status": "healthy",
                "message": "Kafka producer available",
            }
        else:
            health_status["checks"]["kafka"] = {
                "status": "unknown",
                "message": "Kafka not configured",
            }
    except Exception as e:
        health_status["checks"]["kafka"] = {
            "status": "unhealthy",
            "message": str(e),
        }
    
    # Determine overall status
    if health_status["status"] == "healthy":
        # Check if any critical service is unhealthy
        critical_services = ["database"]
        for service in critical_services:
            if health_status["checks"].get(service, {}).get("status") != "healthy":
                health_status["status"] = "unhealthy"
                break
    
    return health_status


@router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check endpoint (Kubernetes readiness probe)
    
    Returns:
        Readiness status
    """
    try:
        # Check database
        from sqlalchemy import text
        from app.core.database import engine
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}"
        )


@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check endpoint (Kubernetes liveness probe)
    
    Returns:
        Liveness status
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Get application metrics
    
    Returns:
        Application metrics
    """
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "application": {
            "name": settings.APP_NAME,
            "version": "3.0.0",
            "environment": "production" if not settings.DEBUG else "development",
        },
        "database": {},
        "redis": {},
        "cache": {},
    }
    
    # Database metrics
    try:
        from app.core.database import engine
        pool = engine.pool
        metrics["database"] = {
            "pool_size": pool.size() if hasattr(pool, 'size') else None,
            "checked_in": pool.checkedin() if hasattr(pool, 'checkedin') else None,
            "checked_out": pool.checkedout() if hasattr(pool, 'checkedout') else None,
            "overflow": pool.overflow() if hasattr(pool, 'overflow') else None,
        }
    except Exception as e:
        logger.warning(f"Error getting database metrics: {e}")
    
    # Redis metrics
    try:
        client = await redis_client.get_client()
        info = await client.info()
        metrics["redis"] = {
            "connected_clients": info.get("connected_clients", 0),
            "used_memory": info.get("used_memory", 0),
            "used_memory_human": info.get("used_memory_human", "0B"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
        }
        
        # Calculate cache hit rate
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        hit_rate = (hits / total * 100) if total > 0 else 0
        
        metrics["cache"] = {
            "hit_rate": round(hit_rate, 2),
            "hits": hits,
            "misses": misses,
            "total_requests": total,
        }
    except Exception as e:
        logger.warning(f"Error getting Redis metrics: {e}")
    
    return metrics


@router.get("/metrics/prometheus")
async def get_prometheus_metrics() -> str:
    """
    Get metrics in Prometheus format
    
    Returns:
        Prometheus metrics in text format
    """
    from app.core.metrics import MetricsCollector
    
    collector = MetricsCollector()
    metrics = await collector.collect_all_metrics()
    
    # Format as Prometheus text format
    lines = []
    
    # Application info
    lines.append(f'metersphere_info{{version="3.0.0",environment="{"prod" if not settings.DEBUG else "dev"}"}} 1')
    
    # Database pool metrics
    if metrics.get("database"):
        db = metrics["database"]
        if db.get("pool_size") is not None:
            lines.append(f'metersphere_database_pool_size {db["pool_size"]}')
        if db.get("checked_in") is not None:
            lines.append(f'metersphere_database_pool_checked_in {db["checked_in"]}')
        if db.get("checked_out") is not None:
            lines.append(f'metersphere_database_pool_checked_out {db["checked_out"]}')
    
    # Redis metrics
    if metrics.get("redis"):
        redis = metrics["redis"]
        lines.append(f'metersphere_redis_connected_clients {redis.get("connected_clients", 0)}')
        lines.append(f'metersphere_redis_used_memory_bytes {redis.get("used_memory", 0)}')
        lines.append(f'metersphere_redis_keyspace_hits {redis.get("keyspace_hits", 0)}')
        lines.append(f'metersphere_redis_keyspace_misses {redis.get("keyspace_misses", 0)}')
    
    # Cache metrics
    if metrics.get("cache"):
        cache = metrics["cache"]
        lines.append(f'metersphere_cache_hit_rate {cache.get("hit_rate", 0)}')
        lines.append(f'metersphere_cache_hits {cache.get("hits", 0)}')
        lines.append(f'metersphere_cache_misses {cache.get("misses", 0)}')
    
    return "\n".join(lines) + "\n"

