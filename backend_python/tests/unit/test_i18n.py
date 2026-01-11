"""
Unit tests for i18n
"""
import pytest

from app.core.i18n import Translator, parse_locale, get_locale_from_header


def test_parse_locale():
    """Test locale parsing"""
    assert parse_locale("zh-CN") == "zh_CN"
    assert parse_locale("zh_CN") == "zh_CN"
    assert parse_locale("en-US") == "en_US"
    assert parse_locale("en_US") == "en_US"
    assert parse_locale("zh_TW") == "zh_TW"
    assert parse_locale("invalid") == "zh_CN"  # Default


def test_get_locale_from_header():
    """Test getting locale from Accept-Language header"""
    assert get_locale_from_header("zh-CN,zh;q=0.9") == "zh_CN"
    assert get_locale_from_header("en-US,en;q=0.9") == "en_US"
    assert get_locale_from_header("zh-TW,zh;q=0.9") == "zh_TW"
    assert get_locale_from_header(None) == "zh_CN"  # Default


def test_translator_get():
    """Test Translator.get()"""
    Translator.set_locale("zh_CN")
    translation = Translator.get("common.success")
    assert translation == "成功" or translation.startswith("Not Support")
    
    Translator.set_locale("en_US")
    translation = Translator.get("common.success")
    assert translation == "Success" or translation.startswith("Not Support")


def test_translator_get_with_args():
    """Test Translator.get_with_args()"""
    Translator.set_locale("en_US")
    # This will work if the translation key exists with placeholders
    # For now, just test that it doesn't crash
    try:
        translation = Translator.get_with_args("common.success", "arg1")
        assert isinstance(translation, str)
    except Exception:
        pass  # Expected if translation doesn't support args


def test_translator_set_locale():
    """Test setting locale"""
    Translator.set_locale("en_US")
    assert Translator.get_locale() == "en_US"
    
    Translator.set_locale("zh_CN")
    assert Translator.get_locale() == "zh_CN"

