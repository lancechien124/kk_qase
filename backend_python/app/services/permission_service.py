"""
Permission Service for RBAC
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Set, Optional, List
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.user_role import UserRole
from app.models.user_role_relation import UserRoleRelation
from app.core.security import InternalUserRole, PermissionType


class PermissionService:
    """Permission checking service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def check_admin(self, user: User) -> bool:
        """Check if user is admin"""
        # Get user roles
        result = await self.db.execute(
            select(UserRoleRelation)
            .where(UserRoleRelation.user_id == user.id)
            .options(selectinload(UserRoleRelation.role))
        )
        relations = result.scalars().all()
        
        # Check if user has admin role
        for relation in relations:
            if relation.role and relation.role.id == InternalUserRole.ADMIN:
                return True
        return False
    
    async def get_user_permissions(
        self,
        user: User,
        organization_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> Set[str]:
        """Get all permissions for user at system/organization/project level"""
        permissions = set()
        
        # Check if admin
        if await self.check_admin(user):
            # Admin has all permissions
            return permissions  # Return empty set, admin check is done separately
        
        # Get user role relations
        result = await self.db.execute(
            select(UserRoleRelation)
            .where(UserRoleRelation.user_id == user.id)
            .options(selectinload(UserRoleRelation.role))
        )
        relations = result.scalars().all()
        
        # Get permissions from roles
        for relation in relations:
            role = relation.role
            if not role:
                continue
            
            # Check if role matches the scope
            if role.type == PermissionType.SYSTEM:
                # System level permissions
                role_permissions = await self._get_role_permissions(role.id)
                permissions.update(role_permissions)
            elif role.type == PermissionType.ORGANIZATION:
                # Organization level permissions
                if organization_id and relation.source_id == organization_id:
                    role_permissions = await self._get_role_permissions(role.id)
                    permissions.update(role_permissions)
            elif role.type == PermissionType.PROJECT:
                # Project level permissions
                if project_id and relation.source_id == project_id:
                    role_permissions = await self._get_role_permissions(role.id)
                    permissions.update(role_permissions)
        
        return permissions
    
    async def has_permission(
        self,
        user: User,
        permission: str,
        organization_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> bool:
        """Check if user has permission"""
        # Admin has all permissions
        if await self.check_admin(user):
            return True
        
        # Get user permissions
        permissions = await self.get_user_permissions(user, organization_id, project_id)
        return permission in permissions
    
    async def check_module_permission(
        self,
        user: User,
        project_id: str,
        module: str,
        permission: str,
    ) -> bool:
        """Check if user has module permission in project"""
        # First check if user has project permission
        has_permission = await self.has_permission(
            user,
            permission,
            project_id=project_id
        )
        
        if not has_permission:
            return False
        
        # TODO: Check if module is enabled in project
        # This would require checking project.module_setting
        # For now, just return True if permission check passes
        return True
    
    async def _get_role_permissions(self, role_id: str) -> Set[str]:
        """Get permissions for a role"""
        # TODO: Implement permission lookup from user_role_permission table
        # For now, return empty set
        # This should query the permission table based on role_id
        return set()
    
    async def get_user_roles(
        self,
        user: User,
        source_id: Optional[str] = None,
        permission_type: Optional[str] = None,
    ) -> List[UserRole]:
        """Get user roles filtered by source and type"""
        result = await self.db.execute(
            select(UserRoleRelation)
            .where(UserRoleRelation.user_id == user.id)
            .options(selectinload(UserRoleRelation.role))
        )
        relations = result.scalars().all()
        
        roles = []
        for relation in relations:
            role = relation.role
            if not role:
                continue
            
            # Filter by source_id if provided
            if source_id and relation.source_id != source_id:
                continue
            
            # Filter by permission_type if provided
            if permission_type and role.type != permission_type:
                continue
            
            roles.append(role)
        
        return roles

