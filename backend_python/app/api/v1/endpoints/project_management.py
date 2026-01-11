"""
Project Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.schemas.project_management import Project, ProjectCreate, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter()


@router.get("/projects", response_model=List[Project])
async def get_projects(
    organization_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get projects with pagination"""
    service = ProjectService(db)
    projects = await service.get_projects(organization_id, skip, limit, keyword)
    return projects


@router.get("/projects/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get project by ID"""
    service = ProjectService(db)
    project = await service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/projects", response_model=Project)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create project"""
    service = ProjectService(db)
    project = await service.create_project(
        organization_id=project_data.organization_id,
        name=project_data.name,
        create_user=project_data.create_user,
        description=project_data.description,
        enable=project_data.enable,
        all_resource_pool=project_data.all_resource_pool,
    )
    return project


@router.put("/projects/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update project"""
    service = ProjectService(db)
    update_dict = project_data.dict(exclude_unset=True)
    project = await service.update_project(project_id, **update_dict)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    delete_user: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Delete project (soft delete)"""
    service = ProjectService(db)
    success = await service.delete_project(project_id, delete_user)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}

