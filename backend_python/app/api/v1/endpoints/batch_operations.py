"""
Batch Operations API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.utils.batch_operations import BatchProcessor, BulkInsert
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()


class BatchGetRequest(BaseModel):
    """Batch get request"""
    ids: List[str]


class BatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[Dict[str, Any]]


class BatchUpdateRequest(BaseModel):
    """Batch update request"""
    updates: Dict[str, str]  # ID -> update data JSON string


class BatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[str]


@router.post("/users/batch-get", response_model=Dict[str, UserResponse])
async def batch_get_users(
    request: BatchGetRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Batch get users by IDs (optimized)"""
    from app.services.user_service import UserService
    
    user_service = UserService(db)
    processor = BatchProcessor(batch_size=100)
    
    async def get_user(id: str):
        return await user_service.get_user_by_id(id)
    
    users = await processor.batch_get(get_user, request.ids)
    return {id: user for id, user in users.items() if user}


@router.post("/users/batch-create", response_model=List[UserResponse])
async def batch_create_users(
    request: BatchCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Batch create users (optimized)"""
    from app.services.user_service import UserService
    
    user_service = UserService(db)
    processor = BatchProcessor(batch_size=50)
    
    async def create_user(item: Dict[str, Any]):
        user_data = UserCreate(**item)
        return await user_service.create_user(user_data)
    
    users = await processor.batch_create(create_user, request.items)
    return users


@router.post("/users/batch-delete")
async def batch_delete_users(
    request: BatchDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Batch delete users (optimized)"""
    from app.services.user_service import UserService
    
    user_service = UserService(db)
    processor = BatchProcessor(batch_size=100)
    
    async def delete_user(id: str):
        await user_service.delete_user(id)
        return True
    
    deleted_count = await processor.batch_delete(delete_user, request.ids)
    return {"deleted_count": deleted_count, "total": len(request.ids)}

