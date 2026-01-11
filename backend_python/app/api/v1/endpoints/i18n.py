"""
Internationalization Endpoints
"""
from fastapi import APIRouter, Depends, Request, HTTPException, status
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.i18n import Translator, parse_locale
from app.core.config import settings
from app.models.user import User
from app.schemas.i18n import LocaleResponse, TranslationResponse, SupportedLocalesResponse

router = APIRouter()


@router.get("/locale", response_model=LocaleResponse)
async def get_current_locale(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Get current locale"""
    locale = getattr(request.state, 'locale', Translator.get_locale())
    return LocaleResponse(locale=locale)


@router.post("/locale")
async def set_locale(
    locale: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Set locale for current session"""
    parsed_locale = parse_locale(locale)
    
    if parsed_locale not in settings.SUPPORTED_LOCALES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported locale: {locale}. Supported locales: {settings.SUPPORTED_LOCALES}"
        )
    
    Translator.set_locale(parsed_locale)
    request.state.locale = parsed_locale
    
    # TODO: Save user locale preference to database
    # await user_service.update_user_locale(current_user.id, parsed_locale)
    
    return {"locale": parsed_locale, "message": "Locale updated successfully"}


@router.get("/translations", response_model=TranslationResponse)
async def get_translations(
    locale: Optional[str] = None,
    request: Request = None,
    current_user: User = Depends(get_current_user),
):
    """Get all translations for a locale"""
    target_locale = locale or getattr(request.state, 'locale', Translator.get_locale())
    parsed_locale = parse_locale(target_locale) if target_locale else Translator.get_locale()
    
    translations = Translator.get_all_translations(locale=parsed_locale)
    
    return TranslationResponse(
        locale=parsed_locale,
        translations=translations
    )


@router.get("/translate/{key:path}")
async def translate_key(
    key: str,
    locale: Optional[str] = None,
    request: Request = None,
    current_user: User = Depends(get_current_user),
):
    """Translate a specific key"""
    target_locale = locale or getattr(request.state, 'locale', Translator.get_locale())
    parsed_locale = parse_locale(target_locale) if target_locale else Translator.get_locale()
    
    translation = Translator.get(key, locale=parsed_locale)
    
    return {
        "key": key,
        "locale": parsed_locale,
        "translation": translation
    }


@router.get("/supported-locales", response_model=SupportedLocalesResponse)
async def get_supported_locales(
    current_user: User = Depends(get_current_user),
):
    """Get list of supported locales"""
    return SupportedLocalesResponse(
        locales=settings.SUPPORTED_LOCALES,
        default_locale=settings.DEFAULT_LOCALE
    )


@router.post("/reload")
async def reload_translations(
    current_user: User = Depends(get_current_user),
):
    """Reload translation files (admin only)"""
    # TODO: Add admin permission check
    Translator.reload()
    return {"message": "Translations reloaded successfully"}

