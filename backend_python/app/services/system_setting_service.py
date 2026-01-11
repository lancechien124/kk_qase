"""
System Setting Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Optional, List
import json

from app.core.config import settings


class SystemSettingService:
    """System Setting service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_settings(self, organization_id: Optional[str] = None) -> Dict:
        """Get system settings"""
        # Note: SystemSetting model needs to be created first
        # For now, return default settings from config
        default_settings = {
            "app_name": settings.APP_NAME,
            "default_locale": settings.DEFAULT_LOCALE,
            "supported_locales": settings.SUPPORTED_LOCALES,
            "max_upload_size": settings.MAX_UPLOAD_SIZE,
            "batch_download_max": settings.BATCH_DOWNLOAD_MAX,
            "quartz_enabled": settings.QUARTZ_ENABLED,
            "ai_enabled": settings.AI_ENABLED,
        }
        
        # TODO: Load from database once SystemSetting model is created
        return default_settings
    
    async def update_settings(self, settings_data: Dict, update_user: Optional[str] = None) -> Dict:
        """Update system settings"""
        # TODO: Implement once SystemSetting model is created
        return settings_data
    
    async def get_organization_settings(self, organization_id: str) -> Dict:
        """Get organization-specific settings"""
        # TODO: Implement once OrganizationSetting model is created
        return {}
    
    async def update_organization_settings(
        self,
        organization_id: str,
        settings_data: Dict,
        update_user: Optional[str] = None
    ) -> Dict:
        """Update organization settings"""
        # TODO: Implement once OrganizationSetting model is created
        return settings_data

