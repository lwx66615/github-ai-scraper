"""Tests for internationalization support."""

import pytest
from ai_scraper.i18n import I18nManager, get_translated_keywords


def test_load_translations():
    """Test loading translation mappings."""
    i18n = I18nManager()

    # Should have default translations
    assert "ai" in i18n.get_keywords("en")
    assert "人工智能" in i18n.get_keywords("zh")


def test_get_translated_keywords():
    """Test getting keywords for multiple languages."""
    keywords = get_translated_keywords(["ai", "machine learning"], languages=["en", "zh"])

    assert "ai" in keywords
    assert "人工智能" in keywords
    assert "machine learning" in keywords
    assert "机器学习" in keywords


def test_add_custom_translation():
    """Test adding custom translations."""
    i18n = I18nManager()
    i18n.add_translation("en", "custom_term", "zh", "自定义术语")

    assert "自定义术语" in i18n.get_keywords("zh")


def test_fallback_to_english():
    """Test fallback to English for unknown language."""
    i18n = I18nManager()

    # Unknown language should fallback to English
    keywords = i18n.get_keywords("unknown_lang")
    assert "ai" in keywords


def test_translate_specific_term():
    """Test translating a specific term."""
    i18n = I18nManager()

    # Translate AI to Chinese
    translated = i18n.translate("ai", "en", "zh")
    assert translated == "人工智能"

    # Translate machine learning to Chinese
    translated = i18n.translate("machine learning", "en", "zh")
    assert translated == "机器学习"


def test_translate_nonexistent_term():
    """Test translating a term that doesn't have translation."""
    i18n = I18nManager()

    translated = i18n.translate("nonexistent_term", "en", "zh")
    assert translated is None


def test_get_keywords_returns_set():
    """Test that get_keywords returns a set."""
    i18n = I18nManager()

    keywords = i18n.get_keywords("en")
    assert isinstance(keywords, set)


def test_default_languages():
    """Test that default languages are en and zh."""
    keywords = get_translated_keywords(["ai"])

    # Should include both English and Chinese
    assert "ai" in keywords
    assert "人工智能" in keywords


def test_single_language():
    """Test getting keywords for a single language."""
    keywords = get_translated_keywords(["ai"], languages=["en"])

    assert "ai" in keywords
    # Should not include Chinese translation
    assert "人工智能" not in keywords
