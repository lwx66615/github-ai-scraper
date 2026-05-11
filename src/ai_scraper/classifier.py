"""Repository classification system."""

from dataclasses import dataclass
from typing import Optional

from ai_scraper.models.repository import Repository


@dataclass
class Classification:
    """Repository classification result."""
    primary_category: str
    secondary_categories: list[str]
    confidence: float
    tech_stack: list[str]
    maturity: str  # experimental, production, enterprise


# Category definitions with keywords and topics
CATEGORIES = {
    "llm": {
        "keywords": ["llm", "large language model", "gpt", "claude", "llama", "mistral", "transformer"],
        "topics": ["llm", "gpt", "language-model", "transformers"],
    },
    "computer-vision": {
        "keywords": ["computer vision", "image recognition", "object detection", "segmentation", "yolo", "opencv"],
        "topics": ["computer-vision", "object-detection", "image-segmentation", "opencv"],
    },
    "nlp": {
        "keywords": ["nlp", "natural language", "text processing", "sentiment", "ner", "spacy", "nltk"],
        "topics": ["nlp", "natural-language-processing", "text-analysis", "spacy"],
    },
    "ml-framework": {
        "keywords": ["pytorch", "tensorflow", "jax", "keras", "machine learning framework"],
        "topics": ["pytorch", "tensorflow", "jax", "keras", "deep-learning"],
    },
    "reinforcement-learning": {
        "keywords": ["reinforcement learning", "rl", "q-learning", "policy gradient", "dqn", "ppo"],
        "topics": ["reinforcement-learning", "deep-reinforcement-learning", "rl"],
    },
    "generative-ai": {
        "keywords": ["generative", "diffusion", "gan", "stable diffusion", "midjourney", "image generation"],
        "topics": ["generative-ai", "diffusion-model", "gan", "stable-diffusion"],
    },
    "ai-tools": {
        "keywords": ["langchain", "llamaindex", "autogpt", "agent", "ai tool", "ai framework"],
        "topics": ["langchain", "llamaindex", "autogpt", "ai-agent"],
    },
}

TECH_STACK = {
    "pytorch": ["pytorch", "torch"],
    "tensorflow": ["tensorflow", "tf"],
    "jax": ["jax", "flax"],
    "huggingface": ["huggingface", "transformers", "hugging face"],
    "onnx": ["onnx"],
    "openai": ["openai", "gpt-4", "gpt-3.5"],
    "anthropic": ["anthropic", "claude"],
}


class RepositoryClassifier:
    """Classify repositories into AI categories."""

    def classify(self, repo: Repository) -> Classification:
        """Classify a repository.

        Args:
            repo: Repository to classify.

        Returns:
            Classification result.
        """
        text = f"{repo.name} {repo.description or ''}".lower()
        topics_lower = [t.lower() for t in repo.topics]

        # Score each category
        scores = {}
        for category, rules in CATEGORIES.items():
            score = 0.0

            # Keyword matches
            for kw in rules["keywords"]:
                if kw in text:
                    score += 0.3

            # Topic matches
            for topic in rules["topics"]:
                if topic in topics_lower:
                    score += 0.5

            scores[category] = min(score, 1.0)

        # Get primary and secondary categories
        sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_cats[0][0] if sorted_cats[0][1] > 0.3 else "other"
        secondary = [cat for cat, score in sorted_cats[1:4] if score > 0.2]

        # Detect tech stack
        tech_stack = []
        for tech, keywords in TECH_STACK.items():
            if any(kw in text for kw in keywords):
                tech_stack.append(tech)

        # Determine maturity
        maturity = self._assess_maturity(repo)

        return Classification(
            primary_category=primary,
            secondary_categories=secondary,
            confidence=sorted_cats[0][1],
            tech_stack=tech_stack,
            maturity=maturity,
        )

    def _assess_maturity(self, repo: Repository) -> str:
        """Assess repository maturity."""
        if repo.stars >= 10000 and repo.forks and repo.forks >= 500:
            return "enterprise"
        elif repo.stars >= 1000:
            return "production"
        else:
            return "experimental"
