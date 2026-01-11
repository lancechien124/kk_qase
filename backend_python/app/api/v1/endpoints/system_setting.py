"""
System Setting Endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict

from app.core.database import get_db
from app.services.system_setting_service import SystemSettingService

router = APIRouter()


@router.get("/settings")
async def get_system_settings(
    organization_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get system settings"""
    service = SystemSettingService(db)
    return await service.get_settings(organization_id)


@router.put("/settings")
async def update_system_settings(
    settings_data: Dict,
    update_user: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Update system settings"""
    service = SystemSettingService(db)
    return await service.update_settings(settings_data, update_user)


@router.get("/organizations/{organization_id}/settings")
async def get_organization_settings(
    organization_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get organization-specific settings"""
    service = SystemSettingService(db)
    return await service.get_organization_settings(organization_id)


@router.put("/organizations/{organization_id}/settings")
async def update_organization_settings(
    organization_id: str,
    settings_data: Dict,
    update_user: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Update organization settings"""
    service = SystemSettingService(db)
    return await service.update_organization_settings(organization_id, settings_data, update_user)

