"""
Security and Permission Utilities
"""
from typing import Optional, List, Set
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.user_role import UserRole
from app.models.user_role_relation import UserRoleRelation
from app.services.auth_service import AuthService

# HTTP Bearer token security
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    auth_service = AuthService(db)
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await auth_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.enable:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is disabled"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user"""
    if not current_user.enable:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is disabled"
        )
    return current_user


# Internal user role constants
class InternalUserRole:
    """Internal user role IDs"""
    ADMIN = "admin"


# Permission types
class PermissionType:
    """Permission type constants"""
    SYSTEM = "SYSTEM"
    ORGANIZATION = "ORGANIZATION"
    PROJECT = "PROJECT"


# Module names
class Module:
    """Module constants"""
    API_TEST = "apiTest"
    TEST_PLAN = "testPlan"
    FUNCTIONAL_CASE = "caseManagement"
    BUG = "bugManagement"

