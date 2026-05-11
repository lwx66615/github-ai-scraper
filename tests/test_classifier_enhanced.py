"""Tests for enhanced classifier."""

import pytest
from datetime import datetime
from ai_scraper.classifier import RepositoryClassifier
from ai_scraper.models.repository import Repository


def test_classify_mlops():
    """Test MLOps category classification."""
    classifier = RepositoryClassifier()

    repo = Repository(
        id=1,
        name="test/mlops-tool",
        full_name="test/mlops-tool",
        description="MLOps pipeline management tool",
        stars=1000,
        language="Python",
        topics=["mlops", "pipeline"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        pushed_at=datetime.now(),
        url="https://github.com/test/mlops-tool",
    )

    result = classifier.classify(repo)
    assert result.primary_category == "mlops"


def test_classify_ai_infrastructure():
    """Test AI Infrastructure category classification."""
    classifier = RepositoryClassifier()

    repo = Repository(
        id=1,
        name="test/gpu-inference",
        full_name="test/gpu-inference",
        description="GPU inference optimization with CUDA",
        stars=500,
        language="C++",
        topics=["gpu-computing", "inference"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        pushed_at=datetime.now(),
        url="https://github.com/test/gpu-inference",
    )

    result = classifier.classify(repo)
    assert result.primary_category == "ai-infrastructure"


def test_classify_ai_ethics():
    """Test AI Ethics category classification."""
    classifier = RepositoryClassifier()

    repo = Repository(
        id=1,
        name="test/bias-detector",
        full_name="test/bias-detector",
        description="AI bias detection and fairness tool",
        stars=300,
        language="Python",
        topics=["ai-ethics", "fairness"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        pushed_at=datetime.now(),
        url="https://github.com/test/bias-detector",
    )

    result = classifier.classify(repo)
    assert result.primary_category == "ai-ethics"


def test_classify_multi_label():
    """Test multi-label classification."""
    classifier = RepositoryClassifier()

    repo = Repository(
        id=1,
        name="test/llm-cv",
        full_name="test/llm-cv",
        description="LLM with computer vision capabilities",
        stars=500,
        language="Python",
        topics=["llm", "computer-vision", "multimodal"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        pushed_at=datetime.now(),
        url="https://github.com/test/llm-cv",
    )

    result = classifier.classify(repo)
    assert result.primary_category == "llm"
    assert "computer-vision" in result.secondary_categories


def test_confidence_threshold():
    """Test confidence threshold for classification."""
    classifier = RepositoryClassifier()

    repo = Repository(
        id=1,
        name="test/ambiguous",
        full_name="test/ambiguous",
        description="Some random project",
        stars=100,
        language="Python",
        topics=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        pushed_at=datetime.now(),
        url="https://github.com/test/ambiguous",
    )

    result = classifier.classify(repo)
    assert result.primary_category == "other"
    assert result.confidence < 0.3


def test_mlflow_detection():
    """Test MLflow detection in MLOps category."""
    classifier = RepositoryClassifier()

    repo = Repository(
        id=1,
        name="test/mlflow-project",
        full_name="test/mlflow-project",
        description="MLflow integration for experiment tracking",
        stars=200,
        language="Python",
        topics=["mlflow"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        pushed_at=datetime.now(),
        url="https://github.com/test/mlflow-project",
    )

    result = classifier.classify(repo)
    assert result.primary_category == "mlops"
