"""
Security and Permission Usage Examples
"""

# Example 1: Using permission decorator
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.core.permissions import require_permission, require_project_permission
from app.models.user import User

router = APIRouter()

@router.get("/example1")
async def example_with_decorator(
    current_user: User = Depends(get_current_user),
):
    """Example using permission check in function"""
    from app.services.permission_service import PermissionService
    from app.core.database import get_db
    from sqlalchemy.ext.asyncio import AsyncSession
    
    db: AsyncSession = Depends(get_db)
    permission_service = PermissionService(db)
    
    # Check permission
    has_permission = await permission_service.has_permission(
        current_user,
        "PROJECT:READ",
        project_id="project_123"
    )
    
    if not has_permission:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return {"message": "Access granted"}


# Example 2: Using permission dependency
@router.get("/example2")
async def example_with_dependency(
    current_user: User = require_project_permission("PROJECT:READ"),
):
    """Example using permission dependency"""
    return {"message": "Access granted"}


# Example 3: Check admin
@router.get("/example3")
async def example_check_admin(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Example checking if user is admin"""
    from app.services.permission_service import PermissionService
    
    permission_service = PermissionService(db)
    is_admin = await permission_service.check_admin(current_user)
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return {"message": "Admin access granted"}


# Example 4: Module permission check
@router.get("/example4")
async def example_module_permission(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Example checking module permission"""
    from app.services.permission_service import PermissionService
    from app.core.security import Module
    
    permission_service = PermissionService(db)
    has_permission = await permission_service.check_module_permission(
        current_user,
        project_id,
        Module.API_TEST,
        "API_TEST:READ"
    )
    
    if not has_permission:
        raise HTTPException(status_code=403, detail="Module permission denied")
    
    return {"message": "Module access granted"}

