"""Internationalization support for multi-language search."""

from typing import Optional


# Default keyword translations
DEFAULT_TRANSLATIONS = {
    "en": {
        "ai": "ai",
        "artificial intelligence": "artificial intelligence",
        "machine learning": "machine learning",
        "deep learning": "deep learning",
        "neural network": "neural network",
        "llm": "llm",
        "large language model": "large language model",
        "gpt": "gpt",
        "transformer": "transformer",
        "nlp": "nlp",
        "natural language processing": "natural language processing",
        "computer vision": "computer vision",
        "reinforcement learning": "reinforcement learning",
        "pytorch": "pytorch",
        "tensorflow": "tensorflow",
        "huggingface": "huggingface",
    },
    "zh": {
        "ai": "人工智能",
        "artificial intelligence": "人工智能",
        "machine learning": "机器学习",
        "deep learning": "深度学习",
        "neural network": "神经网络",
        "llm": "大语言模型",
        "large language model": "大语言模型",
        "gpt": "GPT",
        "transformer": "Transformer",
        "nlp": "自然语言处理",
        "natural language processing": "自然语言处理",
        "computer vision": "计算机视觉",
        "reinforcement learning": "强化学习",
        "pytorch": "PyTorch",
        "tensorflow": "TensorFlow",
        "huggingface": "Hugging Face",
    },
}


class I18nManager:
    """Manage internationalization for keywords."""

    def __init__(self):
        """Initialize i18n manager with default translations."""
        self._translations = dict(DEFAULT_TRANSLATIONS)

    def get_keywords(self, language: str) -> set[str]:
        """Get all keywords for a language.

        Args:
            language: Language code (e.g., "en", "zh").

        Returns:
            Set of keywords for the language.
        """
        if language in self._translations:
            return set(self._translations[language].values())
        # Fallback to English
        return set(self._translations.get("en", {}).values())

    def add_translation(
        self,
        source_lang: str,
        source_term: str,
        target_lang: str,
        target_term: str,
    ) -> None:
        """Add a custom translation.

        Args:
            source_lang: Source language code.
            source_term: Term in source language.
            target_lang: Target language code.
            target_term: Translation in target language.
        """
        if target_lang not in self._translations:
            self._translations[target_lang] = {}

        self._translations[target_lang][source_term] = target_term

    def translate(
        self,
        term: str,
        source_lang: str = "en",
        target_lang: str = "zh",
    ) -> Optional[str]:
        """Translate a term between languages.

        Args:
            term: Term to translate.
            source_lang: Source language code.
            target_lang: Target language code.

        Returns:
            Translated term or None if not found.
        """
        if target_lang not in self._translations:
            return None

        return self._translations[target_lang].get(term.lower())


def get_translated_keywords(
    keywords: list[str],
    languages: Optional[list[str]] = None,
) -> list[str]:
    """Get keywords translated to multiple languages.

    Args:
        keywords: List of keywords to translate.
        languages: List of target language codes. Defaults to ["en", "zh"].

    Returns:
        List of keywords in all specified languages.
    """
    if languages is None:
        languages = ["en", "zh"]

    i18n = I18nManager()
    result = []

    for keyword in keywords:
        keyword_lower = keyword.lower()
        for lang in languages:
            # Add original keyword
            if lang == "en":
                result.append(keyword)
            else:
                # Add translation if available
                translated = i18n.translate(keyword_lower, "en", lang)
                if translated:
                    result.append(translated)

    return list(set(result))  # Remove duplicates
