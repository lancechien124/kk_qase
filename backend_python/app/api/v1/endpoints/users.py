"""
User Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.services.user_service import UserService
from app.utils.pagination import PaginationParams, PaginatedResponse, get_pagination_params

router = APIRouter()


@router.get("/users", response_model=List[UserSchema])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    organization_id: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get users with pagination (optimized with caching)"""
    service = UserService(db)
    users = await service.get_users(skip, limit, organization_id, keyword, use_cache=True)
    return users


@router.get("/users/paginated", response_model=PaginatedResponse[UserSchema])
async def get_users_paginated(
    pagination: PaginationParams = Depends(get_pagination_params),
    organization_id: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get users with pagination (optimized)"""
    service = UserService(db)
    result = await service.get_users_paginated(
        page=pagination.page,
        page_size=pagination.page_size,
        organization_id=organization_id,
        keyword=keyword,
    )
    return PaginatedResponse(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        pages=result["pages"],
    )


@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get user by ID"""
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users", response_model=UserSchema)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create new user"""
    service = UserService(db)
    try:
        user = await service.create_user(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password,
            create_user=user_data.create_user,
            language=user_data.language,
            phone=user_data.phone,
            source=user_data.source or "LOCAL",
        )
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update user"""
    service = UserService(db)
    update_dict = user_data.dict(exclude_unset=True)
    user = await service.update_user(user_id, **update_dict)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete user (soft delete)"""
    service = UserService(db)
    success = await service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

