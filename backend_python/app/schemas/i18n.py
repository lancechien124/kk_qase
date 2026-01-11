"""
i18n Schemas
"""
from pydantic import BaseModel
from typing import Dict, List


class LocaleResponse(BaseModel):
    """Current locale response"""
    locale: str


class TranslationResponse(BaseModel):
    """Translation response"""
    locale: str
    translations: Dict[str, str]


class SupportedLocalesResponse(BaseModel):
    """Supported locales response"""
    locales: List[str]
    default_locale: str


class SetLocaleRequest(BaseModel):
    """Set locale request"""
    locale: str

