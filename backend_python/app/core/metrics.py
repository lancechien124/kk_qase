"""
Metrics Collection
"""
from typing import Dict, Any
from datetime import datetime
import time
import psutil
import os

from app.core.redis import redis_client
from app.core.database import engine
from app.core.config import settings
from app.core.logging import logger


class MetricsCollector:
    """Collect application metrics"""
    
    async def collect_all_metrics(self) -> Dict[str, Any]:
        """
        Collect all application metrics
        
        Returns:
            Dictionary of metrics
        """
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "application": await self._collect_application_metrics(),
            "database": await self._collect_database_metrics(),
            "redis": await self._collect_redis_metrics(),
            "system": await self._collect_system_metrics(),
            "cache": await self._collect_cache_metrics(),
        }
        
        return metrics
    
    async def _collect_application_metrics(self) -> Dict[str, Any]:
        """Collect application-level metrics"""
        return {
            "name": settings.APP_NAME,
            "version": "3.0.0",
            "environment": "production" if not settings.DEBUG else "development",
            "uptime": self._get_uptime(),
        }
    
    async def _collect_database_metrics(self) -> Dict[str, Any]:
        """Collect database metrics"""
        try:
            pool = engine.pool
            return {
                "pool_size": pool.size() if hasattr(pool, 'size') else None,
                "checked_in": pool.checkedin() if hasattr(pool, 'checkedin') else None,
                "checked_out": pool.checkedout() if hasattr(pool, 'checkedout') else None,
                "overflow": pool.overflow() if hasattr(pool, 'overflow') else None,
            }
        except Exception as e:
            logger.warning(f"Error collecting database metrics: {e}")
            return {}
    
    async def _collect_redis_metrics(self) -> Dict[str, Any]:
        """Collect Redis metrics"""
        try:
            client = await redis_client.get_client()
            info = await client.info()
            
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "used_memory_peak": info.get("used_memory_peak", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "instantaneous_ops_per_sec": info.get("instantaneous_ops_per_sec", 0),
            }
        except Exception as e:
            logger.warning(f"Error collecting Redis metrics: {e}")
            return {}
    
    async def _collect_cache_metrics(self) -> Dict[str, Any]:
        """Collect cache metrics"""
        try:
            client = await redis_client.get_client()
            info = await client.info()
            
            hits = info.get("keyspace_hits", 0)
            misses = info.get("keyspace_misses", 0)
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0
            
            return {
                "hit_rate": round(hit_rate, 2),
                "hits": hits,
                "misses": misses,
                "total_requests": total,
            }
        except Exception as e:
            logger.warning(f"Error collecting cache metrics: {e}")
            return {}
    
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system metrics"""
        try:
            process = psutil.Process(os.getpid())
            
            return {
                "cpu_percent": process.cpu_percent(interval=0.1),
                "memory_used_mb": round(process.memory_info().rss / 1024 / 1024, 2),
                "memory_percent": process.memory_percent(),
                "num_threads": process.num_threads(),
                "open_files": len(process.open_files()),
            }
        except Exception as e:
            logger.warning(f"Error collecting system metrics: {e}")
            return {}
    
    def _get_uptime(self) -> float:
        """Get application uptime in seconds"""
        try:
            process = psutil.Process(os.getpid())
            return time.time() - process.create_time()
        except Exception:
            return 0.0


class RequestMetrics:
    """Request metrics tracking"""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
        self.min_response_time = float('inf')
        self.max_response_time = 0.0
    
    def record_request(self, response_time: float, is_error: bool = False):
        """Record a request"""
        self.request_count += 1
        self.total_response_time += response_time
        
        if is_error:
            self.error_count += 1
        
        self.min_response_time = min(self.min_response_time, response_time)
        self.max_response_time = max(self.max_response_time, response_time)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get request statistics"""
        avg_response_time = (
            self.total_response_time / self.request_count
            if self.request_count > 0
            else 0.0
        )
        
        error_rate = (
            self.error_count / self.request_count * 100
            if self.request_count > 0
            else 0.0
        )
        
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": round(error_rate, 2),
            "avg_response_time": round(avg_response_time, 3),
            "min_response_time": self.min_response_time if self.min_response_time != float('inf') else 0.0,
            "max_response_time": self.max_response_time,
        }
    
    def reset(self):
        """Reset metrics"""
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
        self.min_response_time = float('inf')
        self.max_response_time = 0.0


# Global request metrics instance
request_metrics = RequestMetrics()

