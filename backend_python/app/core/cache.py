"""
Cache utilities for performance optimization
"""
from typing import Optional, Any, Callable, TypeVar, Coroutine
from functools import wraps
import json
import hashlib
import time

from app.core.redis import redis_client
from app.core.logging import logger

T = TypeVar('T')


class CacheDecorator:
    """Cache decorator for function results"""
    
    def __init__(
        self,
        ttl: int = 3600,
        key_prefix: str = "cache",
        use_cache: bool = True,
    ):
        """
        Initialize cache decorator
        
        Args:
            ttl: Time to live in seconds
            key_prefix: Prefix for cache keys
            use_cache: Whether to use cache
        """
        self.ttl = ttl
        self.key_prefix = key_prefix
        self.use_cache = use_cache
    
    def __call__(self, func: Callable) -> Callable:
        """Decorate function with caching"""
        if not self.use_cache:
            return func
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = self._generate_key(func.__name__, args, kwargs)
            
            # Try to get from cache
            try:
                cached_value = await redis_client.get_cache(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value
            except Exception as e:
                logger.warning(f"Cache get error: {e}")
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            try:
                await redis_client.set_cache(cache_key, result, ttl=self.ttl)
                logger.debug(f"Cache set: {cache_key}")
            except Exception as e:
                logger.warning(f"Cache set error: {e}")
            
            return result
        
        return wrapper
    
    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key from function name and arguments"""
        # Create a hash of arguments
        key_data = {
            "func": func_name,
            "args": str(args),
            "kwargs": str(sorted(kwargs.items())),
        }
        key_str = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{self.key_prefix}:{func_name}:{key_hash}"


def cache_result(
    ttl: int = 3600,
    key_prefix: str = "cache",
    use_cache: bool = True,
):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache keys
        use_cache: Whether to use cache
    
    Example:
        @cache_result(ttl=3600, key_prefix="user")
        async def get_user(user_id: str):
            # Function implementation
            pass
    """
    return CacheDecorator(ttl=ttl, key_prefix=key_prefix, use_cache=use_cache)


class QueryCache:
    """Query result cache manager"""
    
    @staticmethod
    async def get_cached_query(
        cache_key: str,
        query_func: Callable,
        ttl: int = 3600,
        *args,
        **kwargs,
    ) -> Any:
        """
        Get cached query result or execute query
        
        Args:
            cache_key: Cache key
            query_func: Function to execute if cache miss
            ttl: Time to live in seconds
            *args: Arguments for query function
            **kwargs: Keyword arguments for query function
        
        Returns:
            Query result
        """
        # Try to get from cache
        try:
            cached_result = await redis_client.get_cache(cache_key)
            if cached_result is not None:
                logger.debug(f"Query cache hit: {cache_key}")
                return cached_result
        except Exception as e:
            logger.warning(f"Query cache get error: {e}")
        
        # Execute query
        result = await query_func(*args, **kwargs)
        
        # Store in cache
        try:
            await redis_client.set_cache(cache_key, result, ttl=ttl)
            logger.debug(f"Query cache set: {cache_key}")
        except Exception as e:
            logger.warning(f"Query cache set error: {e}")
        
        return result
    
    @staticmethod
    async def invalidate_cache(cache_key: str):
        """Invalidate cache by key"""
        try:
            await redis_client.delete_cache(cache_key)
            logger.debug(f"Cache invalidated: {cache_key}")
        except Exception as e:
            logger.warning(f"Cache invalidation error: {e}")
    
    @staticmethod
    async def invalidate_pattern(pattern: str):
        """Invalidate cache by pattern"""
        try:
            client = await redis_client.get_client()
            keys = await client.keys(pattern)
            if keys:
                await client.delete(*keys)
                logger.debug(f"Cache invalidated pattern: {pattern}, keys: {len(keys)}")
        except Exception as e:
            logger.warning(f"Cache pattern invalidation error: {e}")


class BatchOperation:
    """Batch operation utilities for performance optimization"""
    
    @staticmethod
    async def batch_get(
        get_func: Callable,
        ids: list,
        batch_size: int = 100,
    ) -> dict:
        """
        Batch get items in chunks
        
        Args:
            get_func: Function to get single item (async)
            ids: List of IDs
            batch_size: Size of each batch
        
        Returns:
            Dictionary mapping ID to item
        """
        results = {}
        
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_results = await asyncio.gather(*[
                get_func(id) for id in batch_ids
            ])
            
            for id, result in zip(batch_ids, batch_results):
                if result:
                    results[id] = result
        
        return results
    
    @staticmethod
    async def batch_create(
        create_func: Callable,
        items: list,
        batch_size: int = 100,
    ) -> list:
        """
        Batch create items in chunks
        
        Args:
            create_func: Function to create single item (async)
            items: List of items to create
            batch_size: Size of each batch
        
        Returns:
            List of created items
        """
        results = []
        
        for i in range(0, len(items), batch_size):
            batch_items = items[i:i + batch_size]
            batch_results = await asyncio.gather(*[
                create_func(item) for item in batch_items
            ])
            results.extend(batch_results)
        
        return results


import asyncio
from typing import Optional

