"""
Batch operation utilities for performance optimization
"""
from typing import List, TypeVar, Callable, Awaitable, Dict, Any
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger

T = TypeVar('T')


class BatchProcessor:
    """Batch processor for bulk operations"""
    
    def __init__(self, batch_size: int = 100):
        """
        Initialize batch processor
        
        Args:
            batch_size: Size of each batch
        """
        self.batch_size = batch_size
    
    async def batch_get(
        self,
        get_func: Callable[[str], Awaitable[Optional[T]]],
        ids: List[str],
    ) -> Dict[str, T]:
        """
        Batch get items
        
        Args:
            get_func: Async function to get single item by ID
            ids: List of IDs
        
        Returns:
            Dictionary mapping ID to item
        """
        results = {}
        
        # Process in batches
        for i in range(0, len(ids), self.batch_size):
            batch_ids = ids[i:i + self.batch_size]
            
            # Execute batch in parallel
            batch_results = await asyncio.gather(
                *[get_func(id) for id in batch_ids],
                return_exceptions=True
            )
            
            # Collect results
            for id, result in zip(batch_ids, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Error getting item {id}: {result}")
                elif result is not None:
                    results[id] = result
        
        return results
    
    async def batch_create(
        self,
        create_func: Callable[[Any], Awaitable[T]],
        items: List[Any],
    ) -> List[T]:
        """
        Batch create items
        
        Args:
            create_func: Async function to create single item
            items: List of items to create
        
        Returns:
            List of created items
        """
        results = []
        
        # Process in batches
        for i in range(0, len(items), self.batch_size):
            batch_items = items[i:i + self.batch_size]
            
            # Execute batch in parallel
            batch_results = await asyncio.gather(
                *[create_func(item) for item in batch_items],
                return_exceptions=True
            )
            
            # Collect results
            for item, result in zip(batch_items, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Error creating item: {result}")
                else:
                    results.append(result)
        
        return results
    
    async def batch_update(
        self,
        update_func: Callable[[str, Any], Awaitable[T]],
        updates: Dict[str, Any],
    ) -> List[T]:
        """
        Batch update items
        
        Args:
            update_func: Async function to update single item
            updates: Dictionary mapping ID to update data
        
        Returns:
            List of updated items
        """
        results = []
        items = list(updates.items())
        
        # Process in batches
        for i in range(0, len(items), self.batch_size):
            batch_items = items[i:i + self.batch_size]
            
            # Execute batch in parallel
            batch_results = await asyncio.gather(
                *[update_func(id, data) for id, data in batch_items],
                return_exceptions=True
            )
            
            # Collect results
            for (id, _), result in zip(batch_items, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Error updating item {id}: {result}")
                else:
                    results.append(result)
        
        return results
    
    async def batch_delete(
        self,
        delete_func: Callable[[str], Awaitable[bool]],
        ids: List[str],
    ) -> int:
        """
        Batch delete items
        
        Args:
            delete_func: Async function to delete single item
            ids: List of IDs to delete
        
        Returns:
            Number of successfully deleted items
        """
        deleted_count = 0
        
        # Process in batches
        for i in range(0, len(ids), self.batch_size):
            batch_ids = ids[i:i + self.batch_size]
            
            # Execute batch in parallel
            batch_results = await asyncio.gather(
                *[delete_func(id) for id in batch_ids],
                return_exceptions=True
            )
            
            # Count successes
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Error deleting item: {result}")
                elif result:
                    deleted_count += 1
        
        return deleted_count


class BulkInsert:
    """Bulk insert utilities"""
    
    @staticmethod
    async def bulk_insert(
        db: AsyncSession,
        model_class: type,
        items: List[Dict[str, Any]],
        batch_size: int = 1000,
    ) -> int:
        """
        Bulk insert items
        
        Args:
            db: Database session
            model_class: SQLAlchemy model class
            items: List of item dictionaries
            batch_size: Size of each batch
        
        Returns:
            Number of inserted items
        """
        inserted_count = 0
        
        # Process in batches
        for i in range(0, len(items), batch_size):
            batch_items = items[i:i + batch_size]
            
            # Create model instances
            instances = [model_class(**item) for item in batch_items]
            
            # Bulk insert
            db.add_all(instances)
            await db.flush()
            
            inserted_count += len(instances)
        
        await db.commit()
        return inserted_count
    
    @staticmethod
    async def bulk_update(
        db: AsyncSession,
        model_class: type,
        updates: List[Dict[str, Any]],
        update_key: str = "id",
        batch_size: int = 1000,
    ) -> int:
        """
        Bulk update items
        
        Args:
            db: Database session
            model_class: SQLAlchemy model class
            updates: List of update dictionaries (must include update_key)
            update_key: Key to identify items to update
            batch_size: Size of each batch
        
        Returns:
            Number of updated items
        """
        updated_count = 0
        
        # Process in batches
        for i in range(0, len(updates), batch_size):
            batch_updates = updates[i:i + batch_size]
            
            for update_data in batch_updates:
                key_value = update_data.pop(update_key)
                await db.execute(
                    db.query(model_class)
                    .filter(getattr(model_class, update_key) == key_value)
                    .update(update_data)
                )
            
            await db.flush()
            updated_count += len(batch_updates)
        
        await db.commit()
        return updated_count

