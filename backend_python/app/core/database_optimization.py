"""
Database optimization utilities
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Index, text
from typing import List, Optional, Dict, Any
from sqlalchemy.sql import Select

from app.core.logging import logger


class QueryOptimizer:
    """Query optimization utilities"""
    
    @staticmethod
    def optimize_select_query(
        query: Select,
        use_index: bool = True,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Select:
        """
        Optimize SELECT query
        
        Args:
            query: SQLAlchemy select query
            use_index: Whether to use indexes
            limit: Limit number of results
            offset: Offset for pagination
        
        Returns:
            Optimized query
        """
        # Add limit if specified
        if limit is not None:
            query = query.limit(limit)
        
        # Add offset if specified
        if offset is not None:
            query = query.offset(offset)
        
        return query
    
    @staticmethod
    async def get_count_optimized(
        db: AsyncSession,
        query: Select,
        use_approximate: bool = False,
    ) -> int:
        """
        Get count with optimization
        
        Args:
            db: Database session
            query: SQLAlchemy select query
            use_approximate: Use approximate count (faster but less accurate)
        
        Returns:
            Count of records
        """
        if use_approximate:
            # For MySQL, use approximate count from information_schema
            # This is faster but less accurate
            table_name = query.column_descriptions[0]['entity'].__tablename__
            count_query = text(
                f"SELECT table_rows FROM information_schema.tables "
                f"WHERE table_schema = DATABASE() AND table_name = :table_name"
            )
            result = await db.execute(count_query, {"table_name": table_name})
            row = result.fetchone()
            return row[0] if row else 0
        else:
            # Use exact count
            count_query = select(func.count()).select_from(query.subquery())
            result = await db.execute(count_query)
            return result.scalar() or 0


class PaginationHelper:
    """Pagination helper for optimized queries"""
    
    @staticmethod
    async def paginate(
        db: AsyncSession,
        query: Select,
        page: int = 1,
        page_size: int = 10,
        max_page_size: int = 100,
    ) -> Dict[str, Any]:
        """
        Paginate query results
        
        Args:
            db: Database session
            query: SQLAlchemy select query
            page: Page number (1-based)
            page_size: Number of items per page
            max_page_size: Maximum page size
        
        Returns:
            Dictionary with items, total, page, page_size, pages
        """
        # Validate and adjust page size
        page_size = min(page_size, max_page_size)
        page = max(1, page)
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get total count (optimized)
        total = await QueryOptimizer.get_count_optimized(db, query)
        
        # Get items
        optimized_query = QueryOptimizer.optimize_select_query(
            query,
            limit=page_size,
            offset=offset,
        )
        result = await db.execute(optimized_query)
        items = result.scalars().all()
        
        # Calculate total pages
        pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        }


class IndexManager:
    """Database index management"""
    
    @staticmethod
    async def create_index_if_not_exists(
        db: AsyncSession,
        table_name: str,
        index_name: str,
        columns: List[str],
        unique: bool = False,
    ):
        """
        Create index if it doesn't exist
        
        Args:
            db: Database session
            table_name: Table name
            index_name: Index name
            columns: List of column names
            unique: Whether index is unique
        """
        try:
            # Check if index exists
            check_query = text(
                """
                SELECT COUNT(*) FROM information_schema.statistics
                WHERE table_schema = DATABASE()
                AND table_name = :table_name
                AND index_name = :index_name
                """
            )
            result = await db.execute(
                check_query,
                {"table_name": table_name, "index_name": index_name}
            )
            exists = result.scalar() > 0
            
            if not exists:
                # Create index
                columns_str = ", ".join(columns)
                unique_str = "UNIQUE" if unique else ""
                create_query = text(
                    f"CREATE {unique_str} INDEX {index_name} ON {table_name} ({columns_str})"
                )
                await db.execute(create_query)
                await db.commit()
                logger.info(f"Created index {index_name} on {table_name}")
            else:
                logger.debug(f"Index {index_name} already exists on {table_name}")
        except Exception as e:
            logger.error(f"Error creating index {index_name}: {e}")
            await db.rollback()
            raise


class ConnectionPoolOptimizer:
    """Connection pool optimization"""
    
    @staticmethod
    def get_optimized_pool_settings(
        min_size: int = 10,
        max_size: int = 100,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 1800,
    ) -> Dict[str, Any]:
        """
        Get optimized connection pool settings
        
        Args:
            min_size: Minimum pool size
            max_size: Maximum pool size
            max_overflow: Maximum overflow connections
            pool_timeout: Pool timeout in seconds
            pool_recycle: Connection recycle time in seconds
        
        Returns:
            Dictionary of pool settings
        """
        return {
            "pool_size": min_size,
            "max_overflow": max_overflow,
            "pool_timeout": pool_timeout,
            "pool_recycle": pool_recycle,
            "pool_pre_ping": True,  # Verify connections before using
        }

