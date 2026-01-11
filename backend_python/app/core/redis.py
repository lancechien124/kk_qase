"""
Redis Connection and Utilities
"""
try:
    import redis.asyncio as redis
    from redis.asyncio import Redis
except ImportError:
    # Fallback for older redis versions
    import aioredis as redis
    from aioredis import Redis
from typing import Optional, Any, List
import json
import time
from functools import wraps

from app.core.config import settings


class RedisClient:
    """Redis client wrapper for async operations"""
    
    def __init__(self):
        self._client: Optional[Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        if self._client is None:
            self._client = await redis.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                encoding="utf-8",
                decode_responses=True
            )
        return self._client
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self._client:
            await self._client.close()
            self._client = None
    
    async def get_client(self) -> Redis:
        """Get Redis client instance"""
        if self._client is None:
            await self.connect()
        return self._client
    
    # Session Storage
    async def set_session(self, session_id: str, user_id: str, data: dict = None):
        """Store session data"""
        client = await self.get_client()
        session_data = {
            "user_id": user_id,
            "data": data or {},
            "created_at": time.time()
        }
        await client.setex(
            f"session:{session_id}",
            settings.SESSION_TIMEOUT,
            json.dumps(session_data)
        )
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        client = await self.get_client()
        data = await client.get(f"session:{session_id}")
        if data:
            return json.loads(data)
        return None
    
    async def delete_session(self, session_id: str):
        """Delete session"""
        client = await self.get_client()
        await client.delete(f"session:{session_id}")
    
    # Cache Functions
    async def set_cache(self, key: str, value: Any, expire: int = 3600):
        """Set cache value"""
        client = await self.get_client()
        await client.setex(
            key,
            expire,
            json.dumps(value) if not isinstance(value, str) else value
        )
    
    async def get_cache(self, key: str) -> Optional[Any]:
        """Get cache value"""
        client = await self.get_client()
        data = await client.get(key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        return None
    
    async def delete_cache(self, key: str):
        """Delete cache"""
        client = await self.get_client()
        await client.delete(key)
    
    async def clear_cache_pattern(self, pattern: str):
        """Clear cache by pattern"""
        client = await self.get_client()
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)
    
    # Queue Operations (for execution queue)
    async def push_to_queue(self, queue_key: str, value: Any):
        """Push value to queue (right push)"""
        client = await self.get_client()
        value_str = json.dumps(value) if not isinstance(value, str) else value
        await client.rpush(queue_key, value_str)
    
    async def pop_from_queue(self, queue_key: str) -> Optional[Any]:
        """Pop value from queue (left pop)"""
        client = await self.get_client()
        data = await client.lpop(queue_key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        return None
    
    async def get_queue_length(self, queue_key: str) -> int:
        """Get queue length"""
        client = await self.get_client()
        return await client.llen(queue_key)
    
    async def get_queue_items(self, queue_key: str, start: int = 0, end: int = -1) -> List[Any]:
        """Get queue items"""
        client = await self.get_client()
        items = await client.lrange(queue_key, start, end)
        result = []
        for item in items:
            try:
                result.append(json.loads(item))
            except json.JSONDecodeError:
                result.append(item)
        return result
    
    async def set_queue_expire(self, queue_key: str, seconds: int):
        """Set queue expiration"""
        client = await self.get_client()
        await client.expire(queue_key, seconds)
    
    # Set Operations (for execution set)
    async def add_to_set(self, set_key: str, *values: str):
        """Add values to set"""
        client = await self.get_client()
        await client.sadd(set_key, *values)
    
    async def remove_from_set(self, set_key: str, *values: str) -> int:
        """Remove values from set, returns remaining count"""
        client = await self.get_client()
        await client.srem(set_key, *values)
        count = await client.scard(set_key)
        if count == 0:
            await client.delete(set_key)
        return count
    
    async def get_set_size(self, set_key: str) -> int:
        """Get set size"""
        client = await self.get_client()
        return await client.scard(set_key)
    
    async def is_in_set(self, set_key: str, value: str) -> bool:
        """Check if value is in set"""
        client = await self.get_client()
        return await client.sismember(set_key, value)
    
    async def get_set_members(self, set_key: str) -> List[str]:
        """Get all set members"""
        client = await self.get_client()
        return list(await client.smembers(set_key))
    
    async def set_expire(self, key: str, seconds: int):
        """Set key expiration"""
        client = await self.get_client()
        await client.expire(key, seconds)
    
    # Atomic operations
    async def set_if_absent(self, key: str, value: Any, expire: int = None) -> bool:
        """Set value if key doesn't exist (atomic operation)"""
        client = await self.get_client()
        value_str = json.dumps(value) if not isinstance(value, str) else value
        if expire:
            result = await client.set(key, value_str, nx=True, ex=expire)
        else:
            result = await client.set(key, value_str, nx=True)
        return result is True
    
    async def get_and_set(self, key: str, value: Any) -> Optional[Any]:
        """Get old value and set new value (atomic operation)"""
        client = await self.get_client()
        value_str = json.dumps(value) if not isinstance(value, str) else value
        old_value = await client.getset(key, value_str)
        if old_value:
            try:
                return json.loads(old_value)
            except json.JSONDecodeError:
                return old_value
        return None
    
    # Distributed Lock
    async def acquire_lock(self, lock_key: str, timeout: int = 10, expire: int = 30) -> bool:
        """Acquire distributed lock"""
        client = await self.get_client()
        lock_value = f"{time.time()}_{timeout}"
        result = await client.set(
            f"lock:{lock_key}",
            lock_value,
            nx=True,
            ex=expire
        )
        return result is True
    
    async def release_lock(self, lock_key: str):
        """Release distributed lock"""
        client = await self.get_client()
        await client.delete(f"lock:{lock_key}")
    
    async def lock_context(self, lock_key: str, timeout: int = 10, expire: int = 30):
        """Context manager for distributed lock"""
        class LockContext:
            def __init__(self, redis_client, lock_key, timeout, expire):
                self.redis_client = redis_client
                self.lock_key = lock_key
                self.timeout = timeout
                self.expire = expire
                self.acquired = False
            
            async def __aenter__(self):
                self.acquired = await self.redis_client.acquire_lock(
                    self.lock_key,
                    self.timeout,
                    self.expire
                )
                if not self.acquired:
                    raise Exception(f"Failed to acquire lock: {self.lock_key}")
                return self
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                if self.acquired:
                    await self.redis_client.release_lock(self.lock_key)
        
        return LockContext(self, lock_key, timeout, expire)


# Global Redis client instance
redis_client = RedisClient()


# Dependency for FastAPI
async def get_redis() -> RedisClient:
    """Get Redis client dependency"""
    return redis_client


# Decorator for distributed lock
def with_lock(lock_key: str, timeout: int = 10, expire: int = 30):
    """Decorator to use distributed lock"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with await redis_client.lock_context(lock_key, timeout, expire):
                return await func(*args, **kwargs)
        return wrapper
    return decorator

