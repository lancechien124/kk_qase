"""
Execution Queue Service - Using Redis List
"""
from typing import List, Optional, Dict, Any
import json

from app.core.redis import redis_client


class ExecutionQueueService:
    """API execution queue service using Redis List"""
    
    QUEUE_PREFIX = "queue:"
    QUEUE_DETAIL_PREFIX = "queue:detail:"
    
    def _get_queue_key(self, queue_id: str) -> str:
        """Get queue key"""
        return f"{self.QUEUE_PREFIX}{queue_id}"
    
    def _get_queue_detail_key(self, queue_id: str) -> str:
        """Get queue detail key"""
        return f"{self.QUEUE_DETAIL_PREFIX}{queue_id}"
    
    async def insert_queue(
        self,
        queue_id: str,
        queue_data: Dict[str, Any],
        queue_details: Optional[List[Dict[str, Any]]] = None
    ):
        """Insert queue and queue details"""
        queue_key = self._get_queue_key(queue_id)
        detail_key = self._get_queue_detail_key(queue_id)
        
        # Save queue information (only if not exists)
        await redis_client.set_if_absent(
            queue_key,
            json.dumps(queue_data),
            expire=86400  # 1 day
        )
        
        # Save queue details
        if queue_details:
            for detail in queue_details:
                await redis_client.push_to_queue(detail_key, json.dumps(detail))
            # Set expiration for queue details
            await redis_client.set_expire(detail_key, 86400)  # 1 day
    
    async def get_queue(self, queue_id: str) -> Optional[Dict[str, Any]]:
        """Get queue information"""
        queue_key = self._get_queue_key(queue_id)
        data = await redis_client.get_cache(queue_key)
        if data:
            if isinstance(data, str):
                return json.loads(data)
            return data
        return None
    
    async def pop_queue_detail(self, queue_id: str) -> Optional[Dict[str, Any]]:
        """Pop queue detail from queue"""
        detail_key = self._get_queue_detail_key(queue_id)
        return await redis_client.pop_from_queue(detail_key)
    
    async def get_queue_detail_count(self, queue_id: str) -> int:
        """Get queue detail count"""
        detail_key = self._get_queue_detail_key(queue_id)
        return await redis_client.get_queue_length(detail_key)
    
    async def get_all_queue_details(self, queue_id: str) -> List[Dict[str, Any]]:
        """Get all queue details"""
        detail_key = self._get_queue_detail_key(queue_id)
        return await redis_client.get_queue_items(detail_key)
    
    async def delete_queue(self, queue_id: str):
        """Delete queue and queue details"""
        queue_key = self._get_queue_key(queue_id)
        detail_key = self._get_queue_detail_key(queue_id)
        await redis_client.delete_cache(queue_key)
        await redis_client.delete_cache(detail_key)


class ExecutionSetService:
    """API execution set service using Redis Set"""
    
    SET_PREFIX = "set:"
    
    def _get_set_key(self, set_id: str) -> str:
        """Get set key"""
        return f"{self.SET_PREFIX}{set_id}"
    
    async def init_set(self, set_id: str, resource_ids: List[str]):
        """Initialize execution set with resource IDs"""
        set_key = self._get_set_key(set_id)
        if resource_ids:
            await redis_client.add_to_set(set_key, *resource_ids)
            # Set expiration
            await redis_client.set_expire(set_key, 86400)  # 1 day
    
    async def remove_item(self, set_id: str, resource_id: str) -> int:
        """Remove item from set, returns remaining count"""
        set_key = self._get_set_key(set_id)
        return await redis_client.remove_from_set(set_key, resource_id)
    
    async def remove_items(self, set_id: str, resource_ids: List[str]) -> int:
        """Remove items from set, returns remaining count"""
        set_key = self._get_set_key(set_id)
        if resource_ids:
            return await redis_client.remove_from_set(set_key, *resource_ids)
        return await redis_client.get_set_size(set_key)
    
    async def get_set_size(self, set_id: str) -> int:
        """Get set size"""
        set_key = self._get_set_key(set_id)
        return await redis_client.get_set_size(set_key)
    
    async def is_in_set(self, set_id: str, resource_id: str) -> bool:
        """Check if resource is in set"""
        set_key = self._get_set_key(set_id)
        return await redis_client.is_in_set(set_key, resource_id)
    
    async def get_set_members(self, set_id: str) -> List[str]:
        """Get all set members"""
        set_key = self._get_set_key(set_id)
        return await redis_client.get_set_members(set_key)


# Global instances
execution_queue_service = ExecutionQueueService()
execution_set_service = ExecutionSetService()

