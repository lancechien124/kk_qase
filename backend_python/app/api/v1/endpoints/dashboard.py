"""
Dashboard Endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/statistics")
async def get_dashboard_statistics(
    project_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard statistics"""
    service = DashboardService(db)
    return await service.get_statistics(project_id, organization_id)


@router.get("/projects/{project_id}/statistics")
async def get_project_statistics(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get project-specific statistics"""
    service = DashboardService(db)
    return await service.get_project_statistics(project_id)


@router.get("/projects/{project_id}/coverage")
async def get_test_coverage(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get test coverage statistics"""
    service = DashboardService(db)
    return await service.get_test_coverage(project_id)


@router.get("/activities")
async def get_recent_activities(
    project_id: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get recent activities"""
    service = DashboardService(db)
    return await service.get_recent_activities(project_id, limit)

