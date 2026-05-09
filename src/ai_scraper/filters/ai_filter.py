"""AI-related content filter."""

from ai_scraper.models.repository import Repository, FilterConfig


class AIFilter:
    """Filter for detecting AI-related repositories."""

    def is_ai_related(self, repo: Repository, config: FilterConfig) -> bool:
        """Check if repository is AI-related.

        Args:
            repo: Repository to check.
            config: Filter configuration.

        Returns:
            True if repository is AI-related.
        """
        # Check exclude keywords first
        text_to_check = f"{repo.name} {repo.description or ''}".lower()
        for exclude in config.exclude_keywords:
            # Normalize: replace hyphens with spaces for matching
            exclude_normalized = exclude.lower().replace("-", " ")
            if exclude_normalized in text_to_check or exclude.lower() in text_to_check:
                return False

        # Check topics
        repo_topics_lower = [t.lower() for t in repo.topics]
        for topic in config.topics:
            if topic.lower() in repo_topics_lower:
                return True

        # Check keywords in name and description
        for keyword in config.keywords:
            # Normalize: replace hyphens with spaces for matching
            keyword_normalized = keyword.lower().replace("-", " ")
            if keyword_normalized in text_to_check or keyword.lower() in text_to_check:
                return True

        return False

    def score_relevance(self, repo: Repository) -> float:
        """Calculate AI relevance score for a repository.

        Args:
            repo: Repository to score.

        Returns:
            Relevance score between 0.0 and 1.0.
        """
        score = 0.0
        text_to_check = f"{repo.name} {repo.description or ''}".lower()

        # Default AI indicators
        ai_keywords = [
            "ai", "artificial intelligence", "machine learning", "deep learning",
            "neural network", "llm", "gpt", "transformer", "nlp", "computer vision",
            "pytorch", "tensorflow", "huggingface", "openai", "langchain"
        ]

        ai_topics = [
            "ai", "machine-learning", "deep-learning", "neural-network",
            "natural-language-processing", "computer-vision", "llm", "gpt",
            "pytorch", "tensorflow", "huggingface", "openai", "langchain"
        ]

        # Count keyword matches
        keyword_matches = sum(1 for kw in ai_keywords if kw in text_to_check)
        score += min(keyword_matches * 0.2, 0.6)

        # Count topic matches
        repo_topics_lower = [t.lower() for t in repo.topics]
        topic_matches = sum(1 for topic in ai_topics if topic in repo_topics_lower)
        score += min(topic_matches * 0.15, 0.4)

        return min(score, 1.0)
