"""
Permission Decorators and Dependencies
"""
from functools import wraps
from typing import Callable, Optional
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, PermissionType
from app.models.user import User
from app.services.permission_service import PermissionService


def require_permission(
    permission: str,
    permission_type: str = PermissionType.SYSTEM,
    organization_id_param: Optional[str] = None,
    project_id_param: Optional[str] = None,
):
    """
    Decorator to require specific permission
    
    Args:
        permission: Permission ID to check
        permission_type: Type of permission (SYSTEM, ORGANIZATION, PROJECT)
        organization_id_param: Name of parameter containing organization_id
        project_id_param: Name of parameter containing project_id
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependencies
            current_user: User = None
            db: AsyncSession = None
            
            # Find user and db in kwargs (from FastAPI dependencies)
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                elif isinstance(value, AsyncSession):
                    db = value
            
            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            permission_service = PermissionService(db)
            
            # Extract organization_id and project_id from kwargs
            organization_id = None
            project_id = None
            
            if organization_id_param and organization_id_param in kwargs:
                organization_id = kwargs[organization_id_param]
            elif permission_type == PermissionType.ORGANIZATION:
                # Try to get from current_user
                organization_id = current_user.last_organization_id
            
            if project_id_param and project_id_param in kwargs:
                project_id = kwargs[project_id_param]
            elif permission_type == PermissionType.PROJECT:
                # Try to get from current_user
                project_id = current_user.last_project_id
            
            # Check permission
            has_permission = await permission_service.has_permission(
                current_user,
                permission,
                organization_id=organization_id,
                project_id=project_id,
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


async def check_permission_dependency(
    permission: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    organization_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> User:
    """Dependency to check permission"""
    permission_service = PermissionService(db)
    
    # Use organization_id and project_id from user if not provided
    if not organization_id:
        organization_id = current_user.last_organization_id
    if not project_id:
        project_id = current_user.last_project_id
    
    has_permission = await permission_service.has_permission(
        current_user,
        permission,
        organization_id=organization_id,
        project_id=project_id,
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {permission}"
        )
    
    return current_user


def require_project_permission(permission: str):
    """Require project-level permission - returns a dependency"""
    async def permission_check(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        project_id: Optional[str] = None,
    ):
        return await check_permission_dependency(
            permission,
            current_user=current_user,
            db=db,
            project_id=project_id,
        )
    return Depends(permission_check)


def require_organization_permission(permission: str):
    """Require organization-level permission - returns a dependency"""
    async def permission_check(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        organization_id: Optional[str] = None,
    ):
        return await check_permission_dependency(
            permission,
            current_user=current_user,
            db=db,
            organization_id=organization_id,
        )
    return Depends(permission_check)


def require_system_permission(permission: str):
    """Require system-level permission - returns a dependency"""
    async def permission_check(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        return await check_permission_dependency(
            permission,
            current_user=current_user,
            db=db,
        )
    return Depends(permission_check)

