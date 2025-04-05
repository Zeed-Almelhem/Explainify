"""
Unit tests for ELI5 explainer.
"""
import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import tensorflow as tf

from app.core.xai.eli5_explainer import ELI5Explainer
from app.schemas.explanation import ExplanationFormat, ExplanationRequest


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    y = np.array([0, 1, 0])
    feature_names = ["f1", "f2", "f3"]
    target_names = ["class_0", "class_1"]
    return X, y, feature_names, target_names


@pytest.fixture
def linear_model():
    """Create and fit a linear model."""
    return LogisticRegression(random_state=42)


@pytest.fixture
def tf_model():
    """Create and compile a TensorFlow model."""
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(2, activation="softmax", input_shape=(3,))
    ])
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy")
    return model


def test_feature_importance_sklearn(sample_data):
    """Test feature importance for sklearn models."""
    X, y, feature_names, target_names = sample_data
    model = RandomForestClassifier(random_state=42)
    model.fit(X, y)

    explainer = ELI5Explainer()
    request = ExplanationRequest(
        format=ExplanationFormat.FEATURE_IMPORTANCE,
        feature_names=feature_names,
        target_names=target_names
    )

    explanation = explainer.explain(model, X, request)

    assert explanation["method"] == "eli5"
    assert explanation["type"] == "feature_importance"
    assert "feature_importances" in explanation["explanation"]
    assert len(explanation["explanation"]["feature_importances"]) == len(feature_names)
    assert all(0 <= v <= 1 for v in explanation["explanation"]["feature_importances"].values())


def test_instance_explanation_linear(sample_data, linear_model):
    """Test instance-level explanation for linear models."""
    X, y, feature_names, target_names = sample_data
    linear_model.fit(X, y)  # Fit the model first

    explainer = ELI5Explainer()
    request = ExplanationRequest(
        format=ExplanationFormat.INSTANCE,
        feature_names=feature_names,
        target_names=target_names
    )

    explanation = explainer.explain(linear_model, X[0:1], request)

    assert explanation["method"] == "eli5"
    assert explanation["type"] == "instance"
    assert "targets" in explanation["explanation"]
    assert len(explanation["explanation"]["targets"]) == len(target_names)
    for target in explanation["explanation"]["targets"]:
        assert "target" in target
        assert "contributions" in target
        assert len(target["contributions"]) == len(feature_names)


def test_feature_importance_tensorflow(sample_data, tf_model):
    """Test feature importance for TensorFlow models."""
    X, y, feature_names, target_names = sample_data
    tf_model.fit(X, y, epochs=1, verbose=0)

    explainer = ELI5Explainer()
    request = ExplanationRequest(
        format=ExplanationFormat.FEATURE_IMPORTANCE,
        feature_names=feature_names,
        target_names=target_names
    )

    explanation = explainer.explain(tf_model, X, request)

    assert explanation["method"] == "eli5"
    assert explanation["type"] == "feature_importance"
    assert "feature_importances" in explanation["explanation"]
    assert len(explanation["explanation"]["feature_importances"]) == len(feature_names)
    assert all(0 <= v <= 1 for v in explanation["explanation"]["feature_importances"].values())


def test_instance_explanation_tensorflow_error(sample_data, tf_model):
    """Test that instance-level explanation for TensorFlow models raises error."""
    X, y, feature_names, target_names = sample_data
    tf_model.fit(X, y, epochs=1, verbose=0)

    explainer = ELI5Explainer()
    request = ExplanationRequest(
        format=ExplanationFormat.INSTANCE,
        feature_names=feature_names,
        target_names=target_names
    )

    with pytest.raises(ValueError, match="Instance-level explanations not supported for TensorFlow models"):
        explainer.explain(tf_model, X[0:1], request)


def test_invalid_model_type(sample_data):
    """Test that invalid model type raises error."""
    X, _, feature_names, target_names = sample_data
    invalid_model = "not a model"

    explainer = ELI5Explainer()
    request = ExplanationRequest(
        format=ExplanationFormat.FEATURE_IMPORTANCE,
        feature_names=feature_names,
        target_names=target_names
    )

    with pytest.raises(ValueError):
        explainer.explain(invalid_model, X, request)
