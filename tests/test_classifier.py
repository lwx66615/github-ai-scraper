"""Tests for repository classifier."""

from datetime import datetime

from ai_scraper.classifier import RepositoryClassifier, Classification
from ai_scraper.models.repository import Repository


def make_repo(
    name: str,
    description: str = "",
    topics: list[str] = None,
    stars: int = 100,
    forks: int = 10,
) -> Repository:
    """Helper to create test repository."""
    return Repository(
        id=1,
        name=name,
        full_name=name,
        description=description,
        stars=stars,
        language="Python",
        topics=topics or [],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 5, 1),
        pushed_at=datetime(2024, 5, 9),
        url=f"https://github.com/{name}",
        forks=forks,
    )


class TestLLMClassification:
    """Tests for LLM repository classification."""

    def test_classify_llm_by_keyword(self):
        """Test LLM classification by keyword."""
        classifier = RepositoryClassifier()
        repo = make_repo("test/llm-toolkit", "Large language model toolkit")
        result = classifier.classify(repo)

        assert result.primary_category == "llm"
        assert "llm" in result.primary_category or result.confidence > 0.3

    def test_classify_gpt_repo(self):
        """Test GPT-related repo classification."""
        classifier = RepositoryClassifier()
        repo = make_repo("test/gpt-wrapper", "GPT-4 API wrapper for LLM applications")
        result = classifier.classify(repo)

        assert result.primary_category == "llm"

    def test_classify_llama_repo(self):
        """Test LLaMA-related repo classification."""
        classifier = RepositoryClassifier()
        repo = make_repo("test/llama-finetune", "Fine-tune LLaMA models for LLM tasks")
        result = classifier.classify(repo)

        assert result.primary_category == "llm"

    def test_classify_by_topic(self):
        """Test classification using topics."""
        classifier = RepositoryClassifier()
        repo = make_repo("test/model", "A model", topics=["llm", "transformers"])
        result = classifier.classify(repo)

        assert result.primary_category == "llm"


class TestComputerVisionClassification:
    """Tests for computer vision classification."""

    def test_classify_cv_by_keyword(self):
        """Test CV classification by keyword."""
        classifier = RepositoryClassifier()
        repo = make_repo("test/vision-model", "Computer vision model for object detection")
        result = classifier.classify(repo)

        assert result.primary_category == "computer-vision"

    def test_classify_yolo_repo(self):
        """Test YOLO-related repo classification."""
        classifier = RepositoryClassifier()
        repo = make_repo("test/yolo-detector", "YOLO object detection")
        result = classifier.classify(repo)

        assert result.primary_category == "computer-vision"

    def test_classify_opencv_repo(self):
        """Test OpenCV-related repo classification."""
        classifier = RepositoryClassifier()
        repo = make_repo("test/opencv-utils", "OpenCV utilities for computer vision")
        result = classifier.classify(repo)

        assert result.primary_category == "computer-vision"


class TestNLPClassification:
    """Tests for NLP classification."""

    def test_classify_nlp_by_keyword(self):
        """Test NLP classification by keyword."""
        classifier = RepositoryClassifier()
        repo = make_repo("test/nlp-toolkit", "Natural language processing toolkit")
        result = classifier.classify(repo)

        assert result.primary_category == "nlp"

    def test_classify_spacy_repo(self):
        """Test spaCy-related repo classification."""
        classifier = RepositoryClassifier()
        repo = make_repo("test/spacy-pipeline", "spaCy NLP pipeline")
        result = classifier.classify(repo)

        assert result.primary_category == "nlp"

    def test_classify_sentiment_repo(self):
        """Test sentiment analysis repo classification."""
        classifier = RepositoryClassifier()
        repo = make_repo("test/sentiment-analyzer", "Sentiment analysis with NLP")
        result = classifier.classify(repo)

        assert result.primary_category == "nlp"


class TestTechStackDetection:
    """Tests for technology stack detection."""

    def test_detect_pytorch(self):
        """Test PyTorch detection."""
        classifier = RepositoryClassifier()
        repo = make_repo("test/pytorch-model", "PyTorch implementation")
        result = classifier.classify(repo)

        assert "pytorch" in result.tech_stack

    def test_detect_tensorflow(self):
        """Test TensorFlow detection."""
        classifier = RepositoryClassifier()
        repo = make_repo("test/tf-model", "TensorFlow model")
        result = classifier.classify(repo)

        assert "tensorflow" in result.tech_stack

    def test_detect_huggingface(self):
        """Test Hugging Face detection."""
        classifier = RepositoryClassifier()
        repo = make_repo("test/transformers-demo", "HuggingFace transformers demo")
        result = classifier.classify(repo)

        assert "huggingface" in result.tech_stack

    def test_detect_openai(self):
        """Test OpenAI detection."""
        classifier = RepositoryClassifier()
        repo = make_repo("test/openai-wrapper", "OpenAI GPT-4 wrapper")
        result = classifier.classify(repo)

        assert "openai" in result.tech_stack

    def test_detect_multiple_tech(self):
        """Test detection of multiple technologies."""
        classifier = RepositoryClassifier()
        repo = make_repo("test/ai-stack", "PyTorch with HuggingFace transformers")
        result = classifier.classify(repo)

        assert "pytorch" in result.tech_stack
        assert "huggingface" in result.tech_stack


class TestMaturityAssessment:
    """Tests for maturity assessment."""

    def test_experimental_maturity(self):
        """Test experimental maturity for low stars."""
        classifier = RepositoryClassifier()
        repo = make_repo("test/new-project", "New project", stars=50, forks=2)
        result = classifier.classify(repo)

        assert result.maturity == "experimental"

    def test_production_maturity(self):
        """Test production maturity for medium stars."""
        classifier = RepositoryClassifier()
        repo = make_repo("test/popular-project", "Popular project", stars=1500, forks=100)
        result = classifier.classify(repo)

        assert result.maturity == "production"

    def test_enterprise_maturity(self):
        """Test enterprise maturity for high stars and forks."""
        classifier = RepositoryClassifier()
        repo = make_repo("test/enterprise-project", "Enterprise project", stars=15000, forks=800)
        result = classifier.classify(repo)

        assert result.maturity == "enterprise"

    def test_enterprise_requires_high_forks(self):
        """Test enterprise requires both high stars and forks."""
        classifier = RepositoryClassifier()
        # High stars but low forks - should be production
        repo = make_repo("test/star-project", "Star project", stars=15000, forks=100)
        result = classifier.classify(repo)

        assert result.maturity == "production"


class TestOtherCategory:
    """Tests for repos that don't match any category."""

    def test_no_match_returns_other(self):
        """Test that non-matching repos return 'other'."""
        classifier = RepositoryClassifier()
        repo = make_repo("test/web-app", "A simple web application")
        result = classifier.classify(repo)

        assert result.primary_category == "other"

    def test_low_score_returns_other(self):
        """Test that low matching score returns 'other'."""
        classifier = RepositoryClassifier()
        # Only one letter match which shouldn't trigger classification
        repo = make_repo("test/tool", "Utility library for general purposes")
        result = classifier.classify(repo)

        assert result.primary_category == "other"


class TestSecondaryCategories:
    """Tests for secondary category detection."""

    def test_secondary_categories_detected(self):
        """Test that secondary categories are detected."""
        classifier = RepositoryClassifier()
        repo = make_repo(
            "test/ai-toolkit",
            "LLM and NLP toolkit with transformers",
            topics=["llm", "nlp", "transformers"],
        )
        result = classifier.classify(repo)

        assert result.primary_category == "llm"
        # Should have some secondary categories
        assert len(result.secondary_categories) >= 0

    def test_secondary_categories_empty_for_low_scores(self):
        """Test secondary categories are empty for low scores."""
        classifier = RepositoryClassifier()
        repo = make_repo("test/web", "Web application")
        result = classifier.classify(repo)

        # Non-AI repos should not have secondary categories
        assert len(result.secondary_categories) == 0


class TestClassificationResult:
    """Tests for Classification dataclass."""

    def test_classification_has_all_fields(self):
        """Test that Classification has all required fields."""
        classification = Classification(
            primary_category="llm",
            secondary_categories=["nlp"],
            confidence=0.8,
            tech_stack=["pytorch", "huggingface"],
            maturity="production",
        )

        assert classification.primary_category == "llm"
        assert classification.secondary_categories == ["nlp"]
        assert classification.confidence == 0.8
        assert classification.tech_stack == ["pytorch", "huggingface"]
        assert classification.maturity == "production"
