"""
Internationalization (i18n) Support
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from functools import lru_cache
import locale as py_locale

from app.core.config import settings
from app.core.logging import logger


class Translator:
    """Translation utility class"""
    
    _translations: Dict[str, Dict[str, str]] = {}
    _current_locale: str = settings.DEFAULT_LOCALE
    _translations_loaded: bool = False
    
    @classmethod
    def _load_translations(cls):
        """Load translation files"""
        if cls._translations_loaded:
            return
        
        try:
            # Get translations directory
            base_path = Path(__file__).parent.parent
            translations_dir = base_path / "translations"
            
            if not translations_dir.exists():
                logger.warning(f"Translations directory not found: {translations_dir}")
                cls._translations_loaded = True
                return
            
            # Load translation files
            for locale in settings.SUPPORTED_LOCALES:
                translation_file = translations_dir / f"{locale}.json"
                if translation_file.exists():
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        cls._translations[locale] = json.load(f)
                        logger.info(f"Loaded translations for locale: {locale}")
                else:
                    logger.warning(f"Translation file not found: {translation_file}")
                    cls._translations[locale] = {}
            
            cls._translations_loaded = True
        except Exception as e:
            logger.error(f"Error loading translations: {e}")
            cls._translations_loaded = True
    
    @classmethod
    def set_locale(cls, locale: str):
        """Set current locale"""
        if locale in settings.SUPPORTED_LOCALES:
            cls._current_locale = locale
        else:
            logger.warning(f"Unsupported locale: {locale}, using default: {settings.DEFAULT_LOCALE}")
            cls._current_locale = settings.DEFAULT_LOCALE
    
    @classmethod
    def get_locale(cls) -> str:
        """Get current locale"""
        return cls._current_locale
    
    @classmethod
    def get(cls, key: str, default: Optional[str] = None, locale: Optional[str] = None) -> str:
        """
        Get translation for a key
        
        Args:
            key: Translation key
            default: Default value if key not found
            locale: Optional locale override
        
        Returns:
            Translated string
        """
        cls._load_translations()
        
        target_locale = locale or cls._current_locale
        
        # Try to get translation from target locale
        if target_locale in cls._translations:
            translation = cls._translations[target_locale].get(key)
            if translation:
                return translation
        
        # Fallback to default locale
        if target_locale != settings.DEFAULT_LOCALE:
            if settings.DEFAULT_LOCALE in cls._translations:
                translation = cls._translations[settings.DEFAULT_LOCALE].get(key)
                if translation:
                    return translation
        
        # Return default or key
        if default:
            return default
        return f"Not Support Key: {key}"
    
    @classmethod
    def get_with_args(cls, key: str, *args, locale: Optional[str] = None) -> str:
        """
        Get translation with arguments
        
        Args:
            key: Translation key
            *args: Arguments to format into translation
            locale: Optional locale override
        
        Returns:
            Formatted translated string
        """
        translation = cls.get(key, locale=locale)
        
        try:
            return translation.format(*args)
        except (KeyError, IndexError, ValueError) as e:
            logger.warning(f"Error formatting translation for key '{key}': {e}")
            return translation
    
    @classmethod
    def get_with_kwargs(cls, key: str, **kwargs) -> str:
        """
        Get translation with keyword arguments
        
        Args:
            key: Translation key
            **kwargs: Keyword arguments to format into translation
        
        Returns:
            Formatted translated string
        """
        translation = cls.get(key)
        
        try:
            return translation.format(**kwargs)
        except (KeyError, ValueError) as e:
            logger.warning(f"Error formatting translation for key '{key}': {e}")
            return translation
    
    @classmethod
    def get_all_translations(cls, locale: Optional[str] = None) -> Dict[str, str]:
        """
        Get all translations for a locale
        
        Args:
            locale: Optional locale override
        
        Returns:
            Dictionary of all translations
        """
        cls._load_translations()
        
        target_locale = locale or cls._current_locale
        return cls._translations.get(target_locale, {})
    
    @classmethod
    def reload(cls):
        """Reload translations"""
        cls._translations.clear()
        cls._translations_loaded = False
        cls._load_translations()


def get_locale_from_header(accept_language: Optional[str]) -> str:
    """
    Extract locale from Accept-Language header
    
    Args:
        accept_language: Accept-Language header value (e.g., "zh-CN,zh;q=0.9,en;q=0.8")
    
    Returns:
        Locale string (e.g., "zh_CN", "en_US")
    """
    if not accept_language:
        return settings.DEFAULT_LOCALE
    
    # Parse Accept-Language header
    languages = accept_language.split(',')
    
    for lang in languages:
        # Extract language code (e.g., "zh-CN" -> "zh_CN")
        lang_code = lang.split(';')[0].strip().replace('-', '_')
        
        # Map common language codes to supported locales
        locale_map = {
            'zh_CN': 'zh_CN',
            'zh_TW': 'zh_TW',
            'zh': 'zh_CN',  # Default to simplified Chinese
            'en_US': 'en_US',
            'en': 'en_US',
        }
        
        if lang_code in locale_map:
            mapped_locale = locale_map[lang_code]
            if mapped_locale in settings.SUPPORTED_LOCALES:
                return mapped_locale
    
    return settings.DEFAULT_LOCALE


def parse_locale(locale_str: str) -> str:
    """
    Parse locale string to supported format
    
    Args:
        locale_str: Locale string (e.g., "zh-CN", "zh_CN", "zhCN")
    
    Returns:
        Normalized locale string (e.g., "zh_CN")
    """
    # Normalize locale string
    locale_str = locale_str.replace('-', '_').replace(' ', '_')
    
    # Map common variations
    locale_map = {
        'zh_cn': 'zh_CN',
        'zh_tw': 'zh_TW',
        'zh': 'zh_CN',
        'en_us': 'en_US',
        'en': 'en_US',
        'zhcn': 'zh_CN',
        'zhtw': 'zh_TW',
        'enus': 'en_US',
    }
    
    normalized = locale_str.lower()
    if normalized in locale_map:
        return locale_map[normalized]
    
    # Try to match with supported locales
    for supported_locale in settings.SUPPORTED_LOCALES:
        if supported_locale.lower() == normalized:
            return supported_locale
    
    return settings.DEFAULT_LOCALE

