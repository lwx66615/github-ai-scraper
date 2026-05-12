"""Keyword extraction from repository metadata."""

import re
from pathlib import Path

from ai_scraper.models import Repository


# Common English stopwords to filter out
STOPWORDS: set[str] = {
    "a", "an", "the", "and", "or", "but", "is", "are", "was", "were",
    "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "must", "shall",
    "can", "need", "dare", "ought", "used", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "under", "again",
    "further", "then", "once", "here", "there", "when", "where", "why",
    "how", "all", "each", "few", "more", "most", "other", "some", "such",
    "no", "nor", "not", "only", "own", "same", "so", "than", "too",
    "very", "just", "also", "now", "that", "this", "these", "those",
    "what", "which", "who", "whom", "whose", "if", "else", "because",
    "while", "although", "though", "since", "until", "unless", "however",
    "therefore", "thus", "hence", "either", "neither", "both", "not",
    "only", "also", "even", "still", "already", "yet", "just", "only",
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves",
    "you", "your", "yours", "yourself", "yourselves", "he", "him",
    "his", "himself", "she", "her", "hers", "herself", "it", "its",
    "itself", "they", "them", "their", "theirs", "themselves",
}

# 无效关键词模式（需要过滤掉）
INVALID_PATTERNS = [
    r'^\d+/\w+$',       # 数字/单词模式，如 "0/zero", "112/ai"
    r'^[\w-]+/[\w-]+$', # 路径模式，如 "owner/repo"
    r'^\d+$',           # 纯数字
]

# 最小关键词长度（AI 相关缩写例外）
MIN_KEYWORD_LENGTH = 3
VALID_SHORT_KEYWORDS = {
    "ai", "ml", "dl", "nlp", "cv", "llm", "gpt", "rag", "mcp",
    "rnn", "cnn", "gan", "vae", "rl", "cl", "asr", "tts",
}


class KeywordExtractor:
    """Extract and manage keywords from repository metadata."""

    def __init__(self, keywords_file: Path, max_keywords: int = 100):
        """Initialize the extractor.

        Args:
            keywords_file: Path to file for persisting keywords.
            max_keywords: Maximum number of keywords to keep.
        """
        self.keywords_file = keywords_file
        self.max_keywords = max_keywords

    def load_keywords(self) -> set[str]:
        """Load keywords from file.

        Returns:
            Set of keywords, or empty set if file doesn't exist.
        """
        if not self.keywords_file.exists():
            return set()

        keywords: set[str] = set()
        with open(self.keywords_file, "r", encoding="utf-8") as f:
            for line in f:
                keyword = line.strip()
                if keyword:
                    keywords.add(keyword)
        return keywords

    def save_keywords(self, keywords: set[str]) -> None:
        """Save keywords to file.

        Args:
            keywords: Set of keywords to save.
        """
        # Ensure parent directory exists
        self.keywords_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.keywords_file, "w", encoding="utf-8") as f:
            for keyword in sorted(keywords):
                f.write(f"{keyword}\n")

    def extract_from_repos(self, repos: list[Repository]) -> set[str]:
        """Extract keywords from a list of repositories.

        Args:
            repos: List of repositories to extract from.

        Returns:
            Set of extracted keywords.
        """
        keywords: set[str] = set()
        for repo in repos:
            keywords.update(self._extract_from_topics(repo))
            keywords.update(self._extract_from_description(repo))
            keywords.update(self._extract_from_name(repo))

        # Apply quality filter
        return self._filter_keywords(keywords)

    def _filter_keywords(self, keywords: set[str]) -> set[str]:
        """Filter out low-quality keywords.

        Args:
            keywords: Set of keywords to filter.

        Returns:
            Filtered set of high-quality keywords.
        """
        filtered: set[str] = set()

        for keyword in keywords:
            keyword_lower = keyword.lower()

            # Skip if matches invalid patterns
            skip = False
            for pattern in INVALID_PATTERNS:
                if re.match(pattern, keyword_lower):
                    skip = True
                    break

            if skip:
                continue

            # Check minimum length
            if len(keyword_lower) < MIN_KEYWORD_LENGTH:
                # Allow known short AI terms
                if keyword_lower not in VALID_SHORT_KEYWORDS:
                    continue

            # Skip if it looks like a file path with extension
            if '.' in keyword_lower and not keyword_lower.startswith('.'):
                continue

            # Skip if it's mostly numbers
            digit_count = sum(1 for c in keyword_lower if c.isdigit())
            if digit_count > len(keyword_lower) * 0.5:
                continue

            filtered.add(keyword_lower)

        return filtered

    def _extract_from_topics(self, repo: Repository) -> set[str]:
        """Extract keywords from repository topics.

        Args:
            repo: Repository to extract from.

        Returns:
            Set of keywords from topics (lowercase).
        """
        return {topic.lower() for topic in repo.topics}

    def _extract_from_description(self, repo: Repository) -> set[str]:
        """Extract keywords from repository description.

        Splits on non-alphanumeric characters, filters stopwords,
        requires min 2 chars, and excludes pure digits.

        Args:
            repo: Repository to extract from.

        Returns:
            Set of keywords from description.
        """
        if not repo.description:
            return set()

        keywords: set[str] = set()
        # Split on non-alphanumeric characters
        words = re.split(r"[^a-zA-Z0-9]+", repo.description.lower())

        for word in words:
            # Skip empty strings
            if not word:
                continue
            # Skip short words (less than 2 chars)
            if len(word) < 2:
                continue
            # Skip stopwords
            if word in STOPWORDS:
                continue
            # Skip pure digits
            if word.isdigit():
                continue

            keywords.add(word)

        return keywords

    def _extract_from_name(self, repo: Repository) -> set[str]:
        """Extract keywords from repository name.

        Splits on hyphens and underscores, filters stopwords,
        requires min 2 chars, and excludes pure digits.

        Args:
            repo: Repository to extract from.

        Returns:
            Set of keywords from name.
        """
        keywords: set[str] = set()
        # Split on hyphens and underscores
        parts = re.split(r"[-_]+", repo.name.lower())

        for part in parts:
            # Skip empty strings
            if not part:
                continue
            # Skip short parts (less than 2 chars)
            if len(part) < 2:
                continue
            # Skip stopwords
            if part in STOPWORDS:
                continue
            # Skip pure digits
            if part.isdigit():
                continue

            keywords.add(part)

        return keywords

    def merge_keywords(
        self, existing: set[str], new: set[str]
    ) -> set[str]:
        """Merge new keywords with existing, respecting max_keywords limit.

        Args:
            existing: Existing set of keywords.
            new: New keywords to merge.

        Returns:
            Merged set of keywords, limited to max_keywords.
        """
        merged = existing | new
        if len(merged) <= self.max_keywords:
            return merged

        # Prioritize existing keywords, then add new ones up to limit
        result: set[str] = set(existing)
        for keyword in sorted(new):
            if keyword not in result:
                result.add(keyword)
                if len(result) >= self.max_keywords:
                    break
        return result

    def get_keywords_for_search(self) -> list[str]:
        """Get keywords as a sorted list for search queries.

        Returns:
            Sorted list of keywords.
        """
        keywords = self.load_keywords()
        return sorted(keywords)
