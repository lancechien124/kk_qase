"""
Task Running Cache - Two-level cache (memory + Redis)
"""
from typing import Optional
from functools import lru_cache
import time

from app.core.redis import redis_client


class TaskRunningCache:
    """
    Record running tasks
    - Memory cache as first-level cache (reduces network interaction)
    - Redis as second-level distributed cache
    - After execution ends, result-hub clears the second-level cache
    """
    
    RUNNING_TASK_PREFIX = "running:task:"
    
    def __init__(self):
        # Memory cache (first-level)
        self._memory_cache: dict = {}
        self._cache_expiry: dict = {}
        self._cache_ttl = 30  # 30 seconds
    
    def _get_key(self, task_id: str) -> str:
        """Get Redis key for task"""
        return f"{self.RUNNING_TASK_PREFIX}{task_id}"
    
    def _cleanup_memory_cache(self):
        """Cleanup expired entries from memory cache"""
        current_time = time.time()
        expired_keys = [
            key for key, expiry in self._cache_expiry.items()
            if expiry < current_time
        ]
        for key in expired_keys:
            self._memory_cache.pop(key, None)
            self._cache_expiry.pop(key, None)
    
    async def set_if_absent(self, task_id: str) -> bool:
        """
        Set cache if absent (atomic operation)
        Returns True if set successfully (no cache existed)
        Returns False if cache already exists
        """
        # Cleanup expired entries
        self._cleanup_memory_cache()
        
        # Check memory cache first
        if task_id in self._memory_cache:
            return False
        
        # Check Redis cache (second-level)
        key = self._get_key(task_id)
        success = await redis_client.set_if_absent(key, "", expire=86400)  # 1 day
        
        if success:
            # Set memory cache
            self._memory_cache[task_id] = True
            self._cache_expiry[task_id] = time.time() + self._cache_ttl
        
        return success
    
    async def remove(self, task_id: str):
        """Remove task from cache"""
        # Remove from memory cache
        self._memory_cache.pop(task_id, None)
        self._cache_expiry.pop(task_id, None)
        
        # Remove from Redis cache
        key = self._get_key(task_id)
        await redis_client.delete_cache(key)
    
    async def exists(self, task_id: str) -> bool:
        """Check if task is running"""
        # Check memory cache first
        if task_id in self._memory_cache:
            expiry = self._cache_expiry.get(task_id, 0)
            if expiry > time.time():
                return True
            else:
                # Expired, remove it
                self._memory_cache.pop(task_id, None)
                self._cache_expiry.pop(task_id, None)
        
        # Check Redis cache
        key = self._get_key(task_id)
        value = await redis_client.get_cache(key)
        if value is not None:
            # Update memory cache
            self._memory_cache[task_id] = True
            self._cache_expiry[task_id] = time.time() + self._cache_ttl
            return True
        
        return False


# Global task running cache instance
task_running_cache = TaskRunningCache()

