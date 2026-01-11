"""
Project Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import uuid
import time

from app.core.redis import redis_client
from app.models.project import Project


class ProjectService:
    """Project service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_project_by_id(self, project_id: str, use_cache: bool = True) -> Optional[Project]:
        """Get project by ID with optional cache"""
        cache_key = f"project:{project_id}"
        
        # Try to get from cache
        if use_cache:
            cached_project = await redis_client.get_cache(cache_key)
            if cached_project:
                # Reconstruct Project object from cache
                project = Project(
                    id=cached_project.get("id"),
                    name=cached_project.get("name"),
                    organization_id=cached_project.get("organization_id"),
                    description=cached_project.get("description"),
                    enable=cached_project.get("enable", True),
                )
                return project
        
        # Get from database
        result = await self.db.execute(
            select(Project).where(Project.id == project_id, Project.deleted == False)
        )
        project = result.scalar_one_or_none()
        
        # Cache project data
        if project and use_cache:
            await redis_client.set_cache(
                cache_key,
                {
                    "id": project.id,
                    "name": project.name,
                    "organization_id": project.organization_id,
                    "description": project.description,
                    "enable": project.enable,
                },
                expire=3600  # 1 hour
            )
        
        return project
    
    async def get_projects(
        self,
        organization_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        keyword: Optional[str] = None
    ) -> List[Project]:
        """Get projects with pagination"""
        query = select(Project).where(Project.deleted == False)
        
        if organization_id:
            query = query.where(Project.organization_id == organization_id)
        
        if keyword:
            query = query.where(Project.name.like(f"%{keyword}%"))
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_projects(
        self,
        organization_id: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> int:
        """Count projects"""
        query = select(func.count(Project.id)).where(Project.deleted == False)
        
        if organization_id:
            query = query.where(Project.organization_id == organization_id)
        
        if keyword:
            query = query.where(Project.name.like(f"%{keyword}%"))
        
        result = await self.db.execute(query)
        return result.scalar_one()
    
    async def create_project(
        self,
        organization_id: str,
        name: str,
        create_user: Optional[str] = None,
        **kwargs
    ) -> Project:
        """Create new project"""
        # Generate project ID
        project_id = str(uuid.uuid4())
        
        # Get next num (project number)
        result = await self.db.execute(
            select(func.max(Project.num)).where(Project.organization_id == organization_id)
        )
        max_num = result.scalar_one_or_none() or 0
        next_num = max_num + 1
        
        # Create project
        project = Project(
            id=project_id,
            num=next_num,
            organization_id=organization_id,
            name=name,
            create_user=create_user,
            deleted=False,
            enable=kwargs.get("enable", True),
            all_resource_pool=kwargs.get("all_resource_pool", False),
            **{k: v for k, v in kwargs.items() if k not in ["enable", "all_resource_pool"]}
        )
        
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project
    
    async def update_project(
        self,
        project_id: str,
        update_user: Optional[str] = None,
        **kwargs
    ) -> Optional[Project]:
        """Update project"""
        project = await self.get_project_by_id(project_id, use_cache=False)
        if not project:
            return None
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(project, key) and value is not None:
                setattr(project, key, value)
        
        project.update_user = update_user
        project.update_time = int(time.time() * 1000)
        
        await self.db.commit()
        await self.db.refresh(project)
        
        # Invalidate cache
        cache_key = f"project:{project_id}"
        await redis_client.delete_cache(cache_key)
        
        return project
    
    async def delete_project(self, project_id: str, delete_user: Optional[str] = None) -> bool:
        """Soft delete project"""
        project = await self.get_project_by_id(project_id, use_cache=False)
        if not project:
            return False
        
        project.deleted = True
        project.delete_time = int(time.time() * 1000)
        project.delete_user = delete_user
        
        await self.db.commit()
        
        # Invalidate cache
        cache_key = f"project:{project_id}"
        await redis_client.delete_cache(cache_key)
        
        return True

