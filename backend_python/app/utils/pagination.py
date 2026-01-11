"""
Pagination utilities
"""
from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = 1
    page_size: int = 10
    max_page_size: int = 100
    
    def __init__(self, **data):
        super().__init__(**data)
        # Validate and adjust
        self.page = max(1, self.page)
        self.page_size = min(self.page_size, self.max_page_size)
        self.page_size = max(1, self.page_size)
    
    @property
    def offset(self) -> int:
        """Calculate offset"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit"""
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response"""
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int
    
    @property
    def has_next(self) -> bool:
        """Check if there is next page"""
        return self.page < self.pages
    
    @property
    def has_previous(self) -> bool:
        """Check if there is previous page"""
        return self.page > 1


def get_pagination_params(
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    max_page_size: int = 100,
) -> PaginationParams:
    """
    Get pagination parameters from query params
    
    Args:
        page: Page number
        page_size: Page size
        max_page_size: Maximum page size
    
    Returns:
        PaginationParams instance
    """
    return PaginationParams(
        page=page or 1,
        page_size=page_size or 10,
        max_page_size=max_page_size,
    )

